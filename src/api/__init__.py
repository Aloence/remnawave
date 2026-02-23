from fastapi import APIRouter

from .clients import router as clients_router
from .operations import router as operations_router

router = APIRouter()
router.include_router(clients_router)
router.include_router(operations_router)
