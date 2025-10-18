from fastapi import APIRouter

from app.api.v1.endpoint import (
    items,
    login,
    oauth,
    private,
    upload,
    users,
    utils,
    websocket,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(oauth.router)
api_router.include_router(upload.router)
api_router.include_router(upload.file_router)
api_router.include_router(websocket.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
