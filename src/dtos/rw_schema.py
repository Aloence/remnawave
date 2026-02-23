from datetime import datetime
from uuid import UUID

from pydantic import Field

from enums import ClientStatus
from utils.pydantic_utils import BaseSchemaModel


class RwUserItemSchema(BaseSchemaModel):
    uuid: UUID
    id: int
    short_uuid: str
    username: str
    status: ClientStatus
    expire_at: datetime
    created_at: datetime
    updated_at: datetime


class CreateUserResponseSchema(BaseSchemaModel):
    response: RwUserItemSchema


class GetAllUsersResponseSchema(BaseSchemaModel):
    class Response(BaseSchemaModel):
        users: list[RwUserItemSchema]
        total: int

    response: Response


class GetUserResponseSchema(BaseSchemaModel):
    response: RwUserItemSchema


class BulkExtendRequestSchema(BaseSchemaModel):
    uuids: list[str] = Field(..., min_length=1, max_length=500)
    extend_days: int = Field(..., ge=1, le=9999)


class SubInfoUserSchema(BaseSchemaModel):
    short_uuid: str
    username: str
    expires_at: datetime
    is_active: bool
    user_status: ClientStatus
    traffic_used: str
    traffic_limit: str


class GetSubscriptionInfoResponseSchema(BaseSchemaModel):
    class Response(BaseSchemaModel):
        is_found: bool
        user: SubInfoUserSchema | None = None
        links: list[str] = Field(default_factory=list)
        ss_conf_links: dict[str, str] = Field(default_factory=dict)
        subscription_url: str

    response: Response


class RevokeUserSubscriptionBodySchema(BaseSchemaModel):
    revoke_only_passwords: bool = False
