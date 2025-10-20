"""
Middleware to redirect requests with trailing slashes to versions without trailing slashes.
This ensures consistent URL handling across the API.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response


class TrailingSlashRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically redirects URLs with trailing slashes to their
    non-trailing-slash equivalents.

    Example:
        GET /api/v1/users/ -> redirects to -> GET /api/v1/users

    Uses HTTP 307 (Temporary Redirect) to preserve the original HTTP method
    (POST remains POST, etc.)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Only redirect if:
        # 1. Path is not root "/"
        # 2. Path ends with "/"
        if request.url.path != "/" and request.url.path.endswith("/"):
            # Remove trailing slash
            url_without_slash = request.url.path.rstrip("/")

            # Preserve query parameters if they exist
            if request.url.query:
                url_without_slash += f"?{request.url.query}"

            # 307 Temporary Redirect - preserves HTTP method and body
            return RedirectResponse(url=url_without_slash, status_code=307)

        # No trailing slash, proceed normally
        return await call_next(request)

