from typing import Annotated

from fastapi import Depends

from abcs.clients.remnawave import ABCRemnawaveClient
from abcs.repositories.operation import ABCOperationRepository
from utils.deps import get_dep


def get_rw_client() -> ABCRemnawaveClient:
    return get_dep(ABCRemnawaveClient)


def get_operation_repository() -> ABCOperationRepository:
    return get_dep(ABCOperationRepository)


operation_repo_dep = Annotated[ABCOperationRepository, Depends(get_operation_repository)]
remnawave_client_dep = Annotated[ABCRemnawaveClient, Depends(get_rw_client)]
