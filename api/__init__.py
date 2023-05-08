from fastapi import APIRouter

from core.config import settings
from . import docs, v1


router = APIRouter(prefix="/api")
router.include_router(v1.router, prefix=f"/{settings.API_V1_STR}")
router.include_router(docs.router, prefix=f"/{settings.API_V1_STR}/docs")
