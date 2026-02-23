import json
from uuid import UUID

from httpx import Response

from abcs.repositories.operation import ABCOperationRepository
from config import settings
from enums import Method
from utils.deps import get_dep


async def log_operation(
    client_id: UUID,
    response: Response,
):
    request = response.request

    path = str(request.url).removeprefix(settings.REMNAWAVE_URL)
    method = Method(request.method)
    payload = json.loads(request.content) if request.content else {}
    status_code = response.status_code
    error = response.text if response.is_error else None

    repo = get_dep(ABCOperationRepository)
    await repo.create_operation(
        {
            "client_id": client_id,
            "path": path,
            "method": method,
            "payload": payload,
            "status_code": status_code,
            "error": error,
        }
    )
