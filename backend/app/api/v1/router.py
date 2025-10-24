from fastapi import APIRouter

from app.api.v1.endpoint import (
    cv,
    login,
    oauth,
    private,
    profiles,
    roles,
    upload,
    user_roles,
    utils,
    websocket,
)
from app.core.config import settings
from app.items import api as items
from app.sites import api as sites
from app.users import api as users

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(oauth.router)
api_router.include_router(upload.router)
api_router.include_router(upload.file_router)
api_router.include_router(websocket.router)
api_router.include_router(sites.router)
api_router.include_router(roles.router)
api_router.include_router(profiles.router)
api_router.include_router(user_roles.router)
api_router.include_router(cv.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
