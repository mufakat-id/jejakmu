from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


def get_html_content(HTML_FILE) -> str:
    """Read HTML content from file"""
    return HTML_FILE.read_text(encoding="utf-8")


@router.get("/websocket/")
async def get():
    """WebSocket testing playground - HTML interface for testing WebSocket connections with authentication"""
    HTML_FILE = Path(__file__).parent / "playground.html"
    return HTMLResponse(get_html_content(HTML_FILE))


@router.get("/profile/")
async def get_profile():
    """WebSocket testing playground - HTML interface for testing WebSocket connections with authentication"""
    HTML_FILE = Path(__file__).parent / "tenant-profile.html"
    return HTMLResponse(get_html_content(HTML_FILE))
