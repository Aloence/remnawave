import abc
import asyncio
import logging
from functools import wraps
from typing import Protocol

from .exc import RequestError

logger = logging.getLogger(__name__)


class MaxRetriesError(Exception):
    retries: int | None = None
    last_exception: Exception

    def __init__(self, *args, last_exception: Exception, retries: int | None = None):
        self.retries = retries
        self.last_exception = last_exception
        super().__init__(*args)

    def __repr__(self):
        return f"MaxRetriesError('{str(self)}', retries={self.retries}, last_exception={repr(self.last_exception)})"


class ABCRetryPolicy(abc.ABC):
    exceptions_to_catch: tuple[type[Exception], ...] = (asyncio.TimeoutError, RequestError)

    @abc.abstractmethod
    async def before_next(self, context, retry: int, exc: Exception):
        """
        Метод вызывается до следущего запроса
        context: какой то контекст, по умолчанию args, kwargs функции которую обернули
        """


class NotRetryPolicy(ABCRetryPolicy):
    async def before_next(self, context, retry: int, exc: Exception):
        raise exc


class MaxRetriesRetryPolicy(ABCRetryPolicy):
    max_retries: int

    def __init__(self, max_retries: int = 0):
        self.max_retries = max_retries

    async def before_next(self, context, retry: int, exc: Exception):
        if self.max_retries <= 0:
            raise exc
        if retry > self.max_retries:
            logger.error(
                "Max retries %s for failed %s",
                self.max_retries,
                context,
            )
            raise MaxRetriesError(*exc.args, retries=self.max_retries, last_exception=exc)


class DelayConstRetryPolicy(MaxRetriesRetryPolicy):
    """Ожидание между запросами"""

    delay: float

    def __init__(self, max_retries: int = 0, delay: float = 0):
        self.delay = delay
        super().__init__(max_retries)

    async def before_next(self, context, retry: int, exc: Exception):
        await super().before_next(context, retry, exc)
        await asyncio.sleep(self.delay)


async def retry(policy: ABCRetryPolicy, func, *args, **kwargs):
    _retry = 0
    while True:
        try:
            return await func(*args, **kwargs)
        except policy.exceptions_to_catch as e:
            _retry += 1
            await policy.before_next((args, kwargs), _retry, e)


class CanRetryProtocol(Protocol):
    retry_policy: ABCRetryPolicy


def can_retry(request_func):
    @wraps(request_func)
    async def wrapper(can_retry_obj: CanRetryProtocol, *args, **kwargs):
        retry_policy: ABCRetryPolicy | None = kwargs.pop("retry_policy", None)
        policy = retry_policy or can_retry_obj.retry_policy

        return await retry(policy, request_func, can_retry_obj, *args, **kwargs)

    return wrapper
