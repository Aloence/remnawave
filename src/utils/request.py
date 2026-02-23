import logging
from typing import Any
from uuid import UUID

import httpx
from pydantic import TypeAdapter

from enums import Method

from .exc import RequestError
from .operation_logging import log_operation
from .retry import ABCRetryPolicy, NotRetryPolicy, can_retry

logger = logging.getLogger(__name__)


class BareRequest:
    async def __call__(
        self,
        method: Method,
        url: str,
        headers: dict | None = None,
        json: dict | None = None,
        params: dict | None = None,
        ssl_verify: bool = True,
        client: httpx.AsyncClient | None = None,
        session_kwargs: dict | None = None,
        **kwargs,
    ):
        _request_kwargs = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
            "json": json,
            **kwargs,
        }

        if not session_kwargs:
            session_kwargs = {}
        session_kwargs |= {"verify": ssl_verify}
        try:
            if client:
                res = await client.request(**_request_kwargs)  # pyrefly: ignore
                return res
            else:
                async with httpx.AsyncClient(**session_kwargs) as client:
                    res = await client.request(**_request_kwargs)  # pyrefly: ignore
                    return res
        except httpx.TimeoutException:
            logger.error("Request %s %s timeout", method, url)
            raise


class ApiRequest:
    def __init__(
        self,
        headers: dict | None = None,
        base_url: str | None = None,
        retry_policy: ABCRetryPolicy = NotRetryPolicy(),
    ):
        self.retry_policy = retry_policy
        self.headers = headers or {}
        self.base_url = base_url
        self.bare_request = BareRequest()

    @can_retry
    async def __call__(
        self,
        method: Method,
        url: str,
        response_type: Any | None,
        log_request: bool = False,
        client_id: UUID | None = None,
        retry_policy: ABCRetryPolicy | None = None,
        has_response: bool = True,
        headers: dict | None = None,
        json: dict | None = None,
        params: dict | None = None,
        ssl_verify: bool = True,
        client: httpx.AsyncClient | None = None,
        session_kwargs: dict | None = None,
        **kwargs,
    ) -> Any:
        if headers is None:
            headers = {}

        if log_request:
            assert client_id, "Can't log operation without client_id"

        res = await self.bare_request(
            method=method,
            url=f"{self.base_url}{url}" if self.base_url else url,
            headers={**self.headers, **headers},
            json=json,
            params=params,
            ssl_verify=ssl_verify,
            client=client,
            session_kwargs=session_kwargs,
            **kwargs,
        )
        if res.is_success:
            return await self._on_success(res, has_response, response_type, log_request, client_id)
        return await self._on_fail(res, log_request, client_id)

    async def _on_success(
        self,
        response: httpx.Response,
        has_response: bool,
        response_type: Any,
        log_request: bool,
        client_id: UUID | None,
    ) -> Any:
        if log_request and client_id:
            await log_operation(client_id, response)
        return self._parse_response(response, has_response, response_type)

    async def _on_fail(self, response: httpx.Response, log_request: bool, client_id: UUID | None):
        if log_request and client_id:
            await log_operation(client_id, response)
        raise RequestError(
            f"Request failed with status code {response.status_code}",
            status_code=response.status_code,
            body=response.text,
        )

    def _parse_response(self, response: httpx.Response, has_response: bool, response_type: Any) -> Any | None:
        if not has_response or response_type is None:
            return None
        t = TypeAdapter(response_type)
        res = t.validate_json(response.text)
        return res
