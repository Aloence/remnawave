from datetime import datetime
from uuid import UUID

from abcs.clients.remnawave import ABCRemnawaveClient
from config import settings
from dtos.rw_schema import (
    BulkExtendRequestSchema,
    CreateUserResponseSchema,
    GetAllUsersResponseSchema,
    GetSubscriptionInfoResponseSchema,
    GetUserResponseSchema,
    RevokeUserSubscriptionBodySchema,
)
from enums import Method
from utils.request import ApiRequest

rw_request = ApiRequest(
    base_url=settings.REMNAWAVE_URL,
    headers={"Authorization": f"Bearer {settings.REMNAWAVE_API_KEY.get_secret_value()}"},
)


class RemnawaveClient(ABCRemnawaveClient):
    def __init__(self, client):
        self.client = client

    async def create_client(self, username: str, expire_at: datetime) -> CreateUserResponseSchema:
        return await rw_request(
            Method.POST,
            "/api/users",
            CreateUserResponseSchema,
            json=({"username": username, "expireAt": expire_at.isoformat()}),
            client=self.client,
        )

    async def list_users(self, size: int = 500, start: int = 0) -> GetAllUsersResponseSchema:
        return await rw_request(
            Method.GET,
            "/api/users",
            GetAllUsersResponseSchema,
            params={"size": size, "start": start},
            client=self.client,
        )

    async def get_user_by_uuid(self, client_id: UUID) -> GetUserResponseSchema:
        return await rw_request(
            Method.GET,
            f"/api/users/{client_id}",
            GetUserResponseSchema,
            client=self.client,
        )

    async def delete_user(self, client_id: UUID) -> None:
        await rw_request(
            Method.DELETE,
            f"/api/users/{client_id}",
            None,
            log_request=True,
            client_id=client_id,
            has_response=False,
            client=self.client,
        )

    async def extend_expiration(self, client_id: UUID, days: int) -> None:
        body = BulkExtendRequestSchema(uuids=[str(client_id)], extend_days=days)
        await rw_request(
            Method.POST,
            "/api/users/bulk/extend-expiration-date",
            None,
            has_response=False,
            log_request=True,
            client_id=client_id,
            json=body.model_dump(by_alias=True),
            client=self.client,
        )

    async def disable_user(self, client_id: UUID) -> None:
        await rw_request(
            Method.POST,
            f"/api/users/{client_id}/actions/disable",
            None,
            log_request=True,
            client_id=client_id,
            has_response=False,
            client=self.client,
        )

    async def enable_user(self, client_id: UUID) -> None:
        await rw_request(
            Method.POST,
            f"/api/users/{client_id}/actions/enable",
            None,
            has_response=False,
            log_request=True,
            client_id=client_id,
            client=self.client,
        )

    async def get_subscription_info_by_uuid(self, client_id: UUID) -> GetSubscriptionInfoResponseSchema:
        return await rw_request(
            Method.GET,
            f"/api/subscriptions/by-uuid/{client_id}",
            GetSubscriptionInfoResponseSchema,
            client=self.client,
        )

    async def revoke_subscription(self, client_id: UUID, revoke_only_passwords: bool = False) -> None:
        body = RevokeUserSubscriptionBodySchema(revoke_only_passwords=revoke_only_passwords)
        await rw_request(
            Method.POST,
            f"/api/users/{client_id}/actions/revoke",
            None,
            log_request=True,
            client_id=client_id,
            has_response=False,
            json=body.model_dump(by_alias=True),
            client=self.client,
        )
