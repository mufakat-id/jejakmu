import random
import uuid
from collections.abc import Callable

from fastapi import WebSocket

from app.core.websocket import WebsocketConnectionManager, ws_manager


def bot_response(message: str) -> str | None:
    """Bot function that responds to specific messages"""
    message_lower = message.lower().strip()

    if message_lower == "halo":
        return "apa kabar"

    if "nama" in message_lower:
        return "nama saya abdu"

    vowels = ["a", "i", "u", "e", "o"]
    if any(vowel in message_lower for vowel in vowels):
        lorem_sentences = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.",
            "Duis aute irure dolor in reprehenderit in voluptate velit esse.",
            "Excepteur sint occaecat cupidatat non proident sunt in culpa.",
            "Curabitur pretium tincidunt lacus nunc nonummy metus.",
            "Vestibulum ante ipsum primis in faucibus orci luctus.",
            "Pellentesque habitant morbi tristique senectus et netus.",
            "Mauris blandit aliquet elit eget tincidunt nibh pulvinar.",
            "Vivamus suscipit tortor eget felis porttitor volutpat.",
        ]
        return random.choice(lorem_sentences)

    return None


class WebSocketService:
    """Handler class for WebSocket message types"""

    def __init__(self, manager: WebsocketConnectionManager):
        self.manager = manager
        # Message type to handler method mapping
        self.handlers: dict[str, Callable] = {
            "create_room": self.handle_create_room,
            "close_room": self.handle_close_room,
            "join_room": self.handle_join_room,
            "leave_room": self.handle_leave_room,
            "list_rooms": self.handle_list_rooms,
            "message": self.handle_message,
        }

    async def handle_create_room(
        self, websocket: WebSocket, user_id: uuid.UUID, data: dict
    ):
        """Handle room creation"""
        room_name = data.get("room_name")

        if not room_name:
            await self.manager.send_personal_message(
                "[System] Room name is required!", websocket
            )
            return

        # Create room
        if self.manager.create_room(room_name, user_id):
            await self.manager.send_personal_message(
                f"[System] Room '{room_name}' created successfully!", websocket
            )
        else:
            await self.manager.send_personal_message(
                f"[System] Room '{room_name}' already exists!", websocket
            )

    async def handle_close_room(
        self, websocket: WebSocket, user_id: uuid.UUID, data: dict
    ):
        """Handle room closure"""
        current_room = self.manager.get_client_room(websocket)
        if not current_room:
            await self.manager.send_personal_message(
                "[System] You are not in any room!", websocket
            )
            return

        if self.manager.close_room(current_room, websocket):
            await self.manager.send_personal_message(
                f"[System] Room '{current_room}' closed successfully!", websocket
            )
            await self.manager.send_personal_message("ROOM_UPDATE:None", websocket)
        else:
            await self.manager.send_personal_message(
                "[System] Only the room creator can close the room!", websocket
            )

    async def handle_join_room(
        self, websocket: WebSocket, user_id: uuid.UUID, data: dict
    ):
        """Handle joining a room"""
        room_name = data.get("room_name")
        if not room_name:
            await self.manager.send_personal_message(
                "[System] Room name is required!", websocket
            )
            return

        if await self.manager.join_room(room_name, websocket):
            await self.manager.send_personal_message(
                f"[System] Joined room '{room_name}' successfully!", websocket
            )
            await self.manager.send_personal_message(
                f"ROOM_UPDATE:{room_name}", websocket
            )
        else:
            await self.manager.send_personal_message(
                f"[System] Room '{room_name}' does not exist!", websocket
            )

    async def handle_leave_room(
        self, websocket: WebSocket, user_id: uuid.UUID, data: dict
    ):
        """Handle leaving a room"""
        current_room = self.manager.get_client_room(websocket)
        if await self.manager.leave_room(websocket):
            await self.manager.send_personal_message(
                f"[System] Left room '{current_room}' successfully!", websocket
            )
            await self.manager.send_personal_message("ROOM_UPDATE:None", websocket)
        else:
            await self.manager.send_personal_message(
                "[System] You are not in any room!", websocket
            )

    async def handle_list_rooms(
        self, websocket: WebSocket, user_id: uuid.UUID, data: dict
    ):
        """Handle listing all active rooms"""
        rooms = self.manager.get_active_rooms()
        if rooms:
            rooms_info = "[System] Active Rooms:"
            for room in rooms:
                rooms_info += f"\n  - {room['name']} (Creator: {room['creator_id']}, Members: {room['members']}, Created: {room['created_at']})"
            await self.manager.send_personal_message(rooms_info, websocket)
        else:
            await self.manager.send_personal_message(
                "[System] No active rooms available.", websocket
            )

    async def handle_message(
        self, websocket: WebSocket, user_id: uuid.UUID, data: dict
    ):
        """Handle chat messages"""
        content = data.get("content", "")

        if not content:
            await self.manager.send_personal_message(
                "[System] Message content cannot be empty!", websocket
            )
            return

        current_room = self.manager.get_client_room(websocket)

        # Check if user is in a room
        if current_room:
            room = self.manager.rooms[current_room]

            # Send confirmation to user
            await self.manager.send_personal_message(f"You wrote: {content}", websocket)

            # Broadcast to other room members
            await room.broadcast_except(f"User {user_id} says: {content}", websocket)

            # Bot auto-reply
            bot_reply = bot_response(content)
            if bot_reply:
                await room.broadcast(f"Bot: {bot_reply}")
        else:
            await self.manager.send_personal_message(
                "[System] You need to join a room first to send messages!", websocket
            )

    async def handle_unknown(
        self, websocket: WebSocket, user_id: uuid.UUID, data: dict
    ):
        """Handle unknown message types"""
        message_type = data.get("type", "unknown")
        await self.manager.send_personal_message(
            f"[System] Unknown message type: {message_type}", websocket
        )

    async def process_message(
        self, websocket: WebSocket, user_id: uuid.UUID, message_data: dict
    ):
        """Process incoming message and route to appropriate handler"""
        message_type = message_data.get("type")

        # Get the appropriate handler or use unknown handler
        handler = self.handlers.get(message_type, self.handle_unknown)

        # Execute the handler
        await handler(websocket, user_id, message_data)


# Initialize the handler
ws_handler = WebSocketService(ws_manager)
