from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from dtos.operation import OperationDTO


class ABCOperationRepository(ABC):
    @abstractmethod
    async def get_operations(self, client_id: UUID, limit: int, page: int) -> list[OperationDTO]: ...

    @abstractmethod
    async def create_operation(self, operation_data: dict[str, Any]) -> OperationDTO: ...
