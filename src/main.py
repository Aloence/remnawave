from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from abcs.clients.remnawave import ABCRemnawaveClient
from abcs.repositories.operation import ABCOperationRepository
from api import router as api_router
from clients.remnawave import RemnawaveClient
from config import settings
from db.db_helper import db_engine
from repositories.operation import OperationRepository
from utils.deps import add_deps
from utils.exc import NotFoundError, RequestError

settings.configure_logging()


def exception_container(app: FastAPI) -> None:
    @app.exception_handler(RequestError)
    async def request_error_handler(_request: Request, exc: RequestError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": str(exc), "body": exc.body if isinstance(exc.body, str) else None},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.message})


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient(verify=settings.REMNAWAVE_SSL_VERIFY) as client:
        deps = {
            ABCRemnawaveClient: RemnawaveClient(client),
            ABCOperationRepository: OperationRepository(db_engine),
        }
        add_deps(deps)
        yield


app = FastAPI(lifespan=lifespan)

app.include_router(api_router)

exception_container(app)
