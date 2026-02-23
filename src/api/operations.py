from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Query

from api.dependencies import operation_repo_dep
from enums import Method
from utils.pydantic_utils import BaseSchemaModel


class OperationSchema(BaseSchemaModel):
    id: UUID
    client_id: UUID
    path: str
    method: Method
    payload: dict[str, Any]
    status_code: int
    error: str | None
    created_at: datetime


router = APIRouter(tags=["operations"], prefix="/operations")


@router.get("/", response_model=list[OperationSchema])
async def get_operations(
    operation_repository: operation_repo_dep,
    client_id: Annotated[UUID, Query()],
    limit: Annotated[int, Query(ge=1, le=100)] = 30,
    page: Annotated[int, Query(ge=1)] = 1,
):
    return await operation_repository.get_operations(client_id, limit=limit, page=page)
