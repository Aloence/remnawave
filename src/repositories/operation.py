from typing import Any
from uuid import UUID

from sqlalchemy import select

from abcs.repositories.operation import ABCOperationRepository
from db.models.operation import OperationModel
from dtos.operation import OperationDTO
from repositories.base import BaseRepository


class OperationRepository(ABCOperationRepository, BaseRepository):
    async def get_operations(self, client_id: UUID, limit: int, page: int) -> list[OperationDTO]:
        offset = (page - 1) * limit
        stmt = (
            select(OperationModel)
            .where(OperationModel.client_id == client_id)
            .order_by(OperationModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        async with self.session() as session:
            result = await session.execute(stmt)
        operations = result.scalars().all()
        return [OperationDTO.model_validate(operation) for operation in operations]

    async def create_operation(self, operation_data: dict[str, Any]) -> OperationDTO:
        operation = OperationModel(**operation_data)
        async with self.session() as session:
            session.add(operation)
            await session.flush()
            await session.refresh(operation)
        return OperationDTO.model_validate(operation)
