import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.v1.deps import get_current_user_ws
from app.core.websocket import ws_manager
from app.models import User
from app.websocket.service import ws_handler

router = APIRouter()

logger = logging.getLogger("websocket")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str | None = None):
    """
    WebSocket endpoint for real-time communication.

    Usage:
    - Connect with authentication token as query parameter: ws://localhost/api/v1/ws?token=<your_token>
    - Send JSON messages with structure: {"type": "message_type", "data": {...}}

    Available message types:
    - create_room: Create a new chat room
    - join_room: Join an existing room
    - leave_room: Leave current room
    - close_room: Close a room (creator only)
    - list_rooms: List all active rooms
    - message: Send a message in current room
    """
    user: User | None = None

    # Authenticate user
    if token:
        try:
            user = await get_current_user_ws(token)
        except Exception:
            await websocket.close(code=1008, reason="Authentication failed")
            return

    if not user:
        await websocket.close(code=1008, reason="Authentication required")
        return

    user_id = user.id

    # Connect to WebSocket manager
    await ws_manager.connect(websocket, user_id)

    try:
        # Send welcome message
        await ws_manager.send_personal_message(
            f"[System] Welcome! You are connected as user {user_id}", websocket
        )
        await ws_manager.send_personal_message(
            "[System] Available commands: create_room, join_room, leave_room, close_room, list_rooms, message",
            websocket,
        )

        # Main message loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                # Parse JSON message
                message_data = json.loads(data)

                # Process message through handler
                await ws_handler.process_message(websocket, user_id, message_data)

            except json.JSONDecodeError:
                await ws_manager.send_personal_message(
                    "[System] Invalid JSON format. Please send valid JSON.", websocket
                )
            except Exception as e:
                await ws_manager.send_personal_message(
                    f"[System] Error processing message: {str(e)}", websocket
                )

    except WebSocketDisconnect:
        # Handle disconnection
        ws_manager.disconnect(websocket)
        logger.info(f"User {user_id} disconnected")
