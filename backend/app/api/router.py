from fastapi import APIRouter

from app.api.playground import router as playground_router
from app.api.v1 import router as v1_router
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(v1_router.api_router, prefix=settings.API_V1_STR)

api_router.include_router(
    playground_router.router, prefix="/playground", tags=["playground"]
)
