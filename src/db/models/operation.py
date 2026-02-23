from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from enums import Method


class OperationModel(Base):
    __tablename__ = "operations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    client_id: Mapped[UUID] = mapped_column(index=True)
    path: Mapped[str]
    method: Mapped[Method]
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    status_code: Mapped[int]
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
