from datetime import datetime
from typing import Any
from uuid import UUID

from enums import Method
from utils.pydantic_utils import BaseModel


class OperationDTO(BaseModel):
    id: UUID
    client_id: UUID
    path: str
    method: Method
    payload: dict[str, Any]
    status_code: int
    error: str | None
    created_at: datetime
