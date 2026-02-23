from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from dtos.rw_schema import (
    CreateUserResponseSchema,
    GetAllUsersResponseSchema,
    GetSubscriptionInfoResponseSchema,
    GetUserResponseSchema,
)


class ABCRemnawaveClient(ABC):
    @abstractmethod
    async def create_client(self, username: str, expire_at: datetime) -> CreateUserResponseSchema: ...

    @abstractmethod
    async def list_users(self, size: int = 500, start: int = 0) -> GetAllUsersResponseSchema: ...

    @abstractmethod
    async def get_user_by_uuid(self, client_id: UUID) -> GetUserResponseSchema: ...

    @abstractmethod
    async def delete_user(self, client_id: UUID) -> None: ...

    @abstractmethod
    async def get_subscription_info_by_uuid(self, client_id: UUID) -> GetSubscriptionInfoResponseSchema: ...

    @abstractmethod
    async def extend_expiration(self, client_id: UUID, days: int) -> None: ...

    @abstractmethod
    async def disable_user(self, client_id: UUID) -> None: ...

    @abstractmethod
    async def enable_user(self, client_id: UUID) -> None: ...

    @abstractmethod
    async def revoke_subscription(self, client_id: UUID, revoke_only_passwords: bool = False) -> None: ...
