import uuid
from datetime import datetime

from fastapi import WebSocket


class Room:
    def __init__(
        self,
        name: str,
        creator_id: uuid.UUID,
    ):
        self.name = name
        self.creator_id = creator_id
        self.connections: list[WebSocket] = []
        self.created_at = datetime.now()

    def add_connection(self, websocket: WebSocket):
        if websocket not in self.connections:
            self.connections.append(websocket)

    def remove_connection(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.connections:
            await connection.send_text(message)

    async def broadcast_except(self, message: str, exclude_websocket: WebSocket):
        for connection in self.connections:
            if connection != exclude_websocket:
                await connection.send_text(message)


class WebsocketConnectionManager:
    def __init__(self):
        self.active_connections: dict[WebSocket, uuid.UUID] = {}  # websocket -> user_id
        self.rooms: dict[str, Room] = {}  # room_name -> Room
        self.client_rooms: dict[WebSocket, str] = {}  # websocket -> room_name

    async def connect(self, websocket: WebSocket, user_id: uuid.UUID):
        await websocket.accept()
        self.active_connections[websocket] = user_id

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            del self.active_connections[websocket]

        # Remove from room if in one
        if websocket in self.client_rooms:
            room_name = self.client_rooms[websocket]
            if room_name in self.rooms:
                self.rooms[room_name].remove_connection(websocket)
            del self.client_rooms[websocket]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def broadcast_except(self, message: str, exclude_websocket: WebSocket):
        for connection in self.active_connections:
            if connection != exclude_websocket:
                await connection.send_text(message)

    def create_room(
        self,
        room_name: str,
        creator_id: uuid.UUID,
    ) -> bool:
        if room_name in self.rooms:
            return False
        self.rooms[room_name] = Room(room_name, creator_id)
        return True

    def close_room(self, room_name: str, websocket: WebSocket) -> bool:
        if room_name not in self.rooms:
            return False

        room = self.rooms[room_name]
        user_id = self.active_connections.get(websocket)

        # Only creator can close the room
        if room.creator_id != user_id:
            return False

        # Remove all clients from the room
        for ws in list(room.connections):
            if ws in self.client_rooms:
                del self.client_rooms[ws]

        del self.rooms[room_name]
        return True

    async def join_room(self, room_name: str, websocket: WebSocket) -> bool:
        if room_name not in self.rooms:
            return False

        # Leave current room if in one
        if websocket in self.client_rooms:
            old_room_name = self.client_rooms[websocket]
            if old_room_name in self.rooms:
                self.rooms[old_room_name].remove_connection(websocket)

        # Join new room
        self.rooms[room_name].add_connection(websocket)
        self.client_rooms[websocket] = room_name

        # Notify room members
        user_id = self.active_connections.get(websocket)
        await self.rooms[room_name].broadcast_except(
            f"[System] User {user_id} joined the room", websocket
        )

        return True

    async def leave_room(self, websocket: WebSocket) -> bool:
        if websocket not in self.client_rooms:
            return False

        room_name = self.client_rooms[websocket]
        if room_name in self.rooms:
            user_id = self.active_connections.get(websocket)
            self.rooms[room_name].remove_connection(websocket)
            await self.rooms[room_name].broadcast(
                f"[System] User {user_id} left the room"
            )

        del self.client_rooms[websocket]
        return True

    def get_active_rooms(self) -> list[dict]:
        return [
            {
                "name": room.name,
                "creator_id": str(room.creator_id),
                "members": len(room.connections),
                "created_at": room.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for room in self.rooms.values()
        ]

    def get_client_room(self, websocket: WebSocket) -> str | None:
        return self.client_rooms.get(websocket)


ws_manager = WebsocketConnectionManager()
