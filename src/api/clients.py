from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import Field, field_validator

from api.dependencies import remnawave_client_dep
from dtos.rw_schema import RwUserItemSchema
from enums import ClientStatus
from utils.exc import NotFoundError
from utils.pydantic_utils import BaseSchemaModel


class CreateClientRequestSchema(BaseSchemaModel):
    username: str
    expire_at: datetime

    @field_validator("expire_at")
    @classmethod
    def validate_expire_at(cls, v: datetime) -> datetime:
        if v <= datetime.now(UTC):
            raise ValueError("expire_at must be greater than current time")
        return v


class ExtendRequestSchema(BaseSchemaModel):
    days: int = Field(..., ge=1, le=9999)


class ClientSchema(BaseSchemaModel):
    uuid: UUID
    id: int
    short_uuid: str
    username: str
    status: ClientStatus
    expire_at: datetime
    created_at: datetime
    updated_at: datetime


class SubInfoUserSchema(BaseSchemaModel):
    short_uuid: str
    username: str
    expires_at: datetime
    is_active: bool
    user_status: ClientStatus
    traffic_used: str
    traffic_limit: str


class ConfigSchema(BaseSchemaModel):
    is_found: bool
    user: SubInfoUserSchema
    links: list[str]
    ss_conf_links: dict[str, str]
    subscription_url: str


def filter_user(client: RwUserItemSchema, now: datetime, status: ClientStatus | None, expired: bool | None):
    if status is not None and client.status != status:
        return False
    if expired is not None:
        is_expired = client.expire_at < now
        return expired == is_expired
    return True


router = APIRouter(tags=["clients"], prefix="/clients")


@router.post("/", response_model=ClientSchema)
async def create_client(
    rw: remnawave_client_dep,
    body: CreateClientRequestSchema,
):
    res = await rw.create_client(username=body.username, expire_at=body.expire_at)
    client = res.response
    return client


@router.get("/", response_model=list[ClientSchema])
async def list_clients(
    rw: remnawave_client_dep,
    status: Annotated[ClientStatus | None, Query()] = None,
    expired: Annotated[bool | None, Query()] = None,
    page: Annotated[int, Query(qe=1)] = 1,
    limit: Annotated[int, Query(qe=1, le=30)] = 30,
):
    now = datetime.now(UTC)
    offset = (page - 1) * limit
    filtered_clients = []

    current_offset = 0
    external_offset = 0
    page_size = 1000
    # так как remnawave не поддерживает фильтры на эндпоинте, то один из вариантов сделать так
    while len(filtered_clients) < offset + limit:
        res = await rw.list_users(size=page_size, start=external_offset)

        if not res or not res.response or not res.response.users:
            break

        batch = res.response.users
        total_external = res.response.total

        for client in batch:
            if filter_user(client, now, status, expired):
                if current_offset >= offset:
                    filtered_clients.append(client)
                    if len(filtered_clients) >= offset + limit:
                        break
                current_offset += 1

        external_offset += page_size

        # if external_offset > 10000:  # Максимум 10 страниц
        #     return filtered_clients
        if external_offset > total_external:
            return filtered_clients
    return filtered_clients


@router.get("/{client_id}", response_model=ClientSchema)
async def get_client(client_id: UUID, rw: remnawave_client_dep):
    res = await rw.get_user_by_uuid(client_id)
    return res.response


@router.delete("/{client_id}", status_code=204)
async def delete_client(client_id: UUID, rw: remnawave_client_dep):
    await rw.delete_user(client_id)


@router.post("/{client_id}/extend", status_code=204)
async def extend_client(client_id: UUID, rw: remnawave_client_dep, body: ExtendRequestSchema):
    await rw.extend_expiration(client_id, body.days)


@router.post("/{client_id}/block", status_code=204)
async def block_client(client_id: UUID, rw: remnawave_client_dep):
    await rw.disable_user(client_id)


@router.post("/{client_id}/unblock", status_code=204)
async def unblock_client(client_id: UUID, rw: remnawave_client_dep):
    await rw.enable_user(client_id)


@router.get("/{client_id}/config", response_model=ConfigSchema)
async def get_client_config(client_id: UUID, rw: remnawave_client_dep):
    sub = await rw.get_subscription_info_by_uuid(client_id)
    res = sub.response
    if not res.is_found or not res.user:
        raise NotFoundError("Client not found")
    return res


@router.post("/{client_id}/config/rotate", status_code=204)
async def rotate_client_config(client_id: UUID, rw: remnawave_client_dep):
    await rw.revoke_subscription(client_id)
