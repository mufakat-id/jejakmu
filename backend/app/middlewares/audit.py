from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.audit import audit_context, get_client_info_from_request


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware untuk mengatur audit context berdasarkan request"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract client info dari request
        client_info = get_client_info_from_request(request)

        # Set audit context untuk request ini
        audit_context.ip_address = client_info.get("ip_address")
        audit_context.user_agent = client_info.get("user_agent")
        audit_context.session_id = client_info.get("session_id")

        # Coba ambil user_id dari request state jika ada
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            audit_context.user_id = user_id

        # Process request
        response = await call_next(request)

        # Clear audit context setelah request selesai
        audit_context.user_id = None
        audit_context.ip_address = None
        audit_context.user_agent = None
        audit_context.session_id = None
        audit_context.additional_info = None

        return response
