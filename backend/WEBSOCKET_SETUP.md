# WebSocket Setup Guide

Panduan lengkap untuk setup dan konfigurasi fitur WebSocket real-time communication.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Production Setup](#production-setup)
4. [Security Considerations](#security-considerations)
5. [Scaling WebSocket](#scaling-websocket)
6. [Monitoring & Debugging](#monitoring--debugging)

## Architecture Overview

### Components

#### 1. WebSocket Connection Manager (`app/core/websocket.py`)

**Class: `WebsocketConnectionManager`**

Mengelola semua WebSocket connections dan rooms:

```python
class WebsocketConnectionManager:
    - active_connections: dict[WebSocket, uuid.UUID]  # Tracking user connections
    - rooms: dict[str, Room]                          # Room instances
    - client_rooms: dict[WebSocket, str]              # User's current room
```

**Methods:**
- `connect()` - Accept WebSocket connection
- `disconnect()` - Clean up connection
- `create_room()` - Create new chat room
- `join_room()` - Join existing room
- `leave_room()` - Leave current room
- `close_room()` - Close room (creator only)
- `send_personal_message()` - Send to specific user
- `broadcast()` - Send to all connected users
- `get_active_rooms()` - List all active rooms

#### 2. WebSocket Service Handler (`app/services/websocket_service.py`)

**Class: `WebSocketService`**

Handler untuk semua tipe message yang diterima dari client:

```python
handlers = {
    "create_room": handle_create_room,
    "close_room": handle_close_room,
    "join_room": handle_join_room,
    "leave_room": handle_leave_room,
    "list_rooms": handle_list_rooms,
    "message": handle_message,
}
```

**Extensibility:**
Tambahkan handler baru dengan menambahkan method dan register di `handlers` dict:

```python
async def handle_custom_action(self, websocket: WebSocket, user_id: uuid.UUID, data: dict):
    # Your custom logic here
    await self.manager.send_personal_message("Custom action executed!", websocket)

# Register in __init__
self.handlers["custom_action"] = self.handle_custom_action
```

#### 3. WebSocket Endpoint (`app/api/v1/endpoint/websocket.py`)

Entry point untuk WebSocket connections dengan authentication.

**Authentication Flow:**
```
1. Client connects with token in query parameter
2. get_current_user_ws() validates JWT token
3. Connection accepted atau rejected (code 1008)
4. Welcome messages sent
5. Enter message loop
```

## Development Setup

### 1. Local Development

WebSocket sudah ready to use untuk development:

```bash
# Start development server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

WebSocket endpoint tersedia di: `ws://localhost:8000/api/v1/ws`

### 2. Testing dengan WebSocket Client Tools

#### Using wscat (CLI tool)

```bash
# Install wscat
npm install -g wscat

# Connect dengan token
wscat -c "ws://localhost:8000/api/v1/ws?token=YOUR_TOKEN"

# Send messages
> {"type": "create_room", "room_name": "test"}
< [System] Room 'test' created successfully!
```

#### Using Postman

1. Create new WebSocket request
2. URL: `ws://localhost:8000/api/v1/ws?token=YOUR_TOKEN`
3. Connect
4. Send JSON messages in the message panel

### 3. Environment Configuration

Tidak ada environment variables khusus yang diperlukan untuk WebSocket. Menggunakan konfigurasi JWT yang sama dengan REST API.

## Production Setup

### 1. Reverse Proxy Configuration

#### Nginx Configuration

```nginx
# /etc/nginx/sites-available/your-app

upstream backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # WebSocket endpoint
    location /api/v1/ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout settings
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
        proxy_connect_timeout 60;
    }

    # REST API endpoints
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### SSL/TLS (WSS) Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    # WebSocket over SSL (wss://)
    location /api/v1/ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;

        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }
}
```

### 2. Docker Configuration

WebSocket sudah works dengan Docker configuration yang ada. Pastikan port mapping sudah benar:

```yaml
# docker-compose.yml
services:
  backend:
    ports:
      - "8000:8000"  # HTTP & WebSocket
    environment:
      - SECRET_KEY=${SECRET_KEY}
```

### 3. Uvicorn Production Settings

```bash
# Production command
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --ws websockets \
    --log-level info
```

**⚠️ Important:** WebSocket memerlukan sticky sessions, jadi gunakan **1 worker** atau implement Redis pub/sub untuk multi-worker setup.

## Security Considerations

### 1. Authentication

✅ **Currently Implemented:**
- JWT token validation
- User must be active
- Token expiration check

🔒 **Additional Security:**

```python
# Tambahkan rate limiting per user
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_messages=100, window_seconds=60):
        self.max_messages = max_messages
        self.window = timedelta(seconds=window_seconds)
        self.user_messages = defaultdict(list)

    def is_allowed(self, user_id: uuid.UUID) -> bool:
        now = datetime.now()
        # Clean old messages
        self.user_messages[user_id] = [
            msg_time for msg_time in self.user_messages[user_id]
            if now - msg_time < self.window
        ]

        if len(self.user_messages[user_id]) >= self.max_messages:
            return False

        self.user_messages[user_id].append(now)
        return True
```

### 2. Input Validation

Tambahkan validasi untuk message content:

```python
from pydantic import BaseModel, Field, validator

class WebSocketMessage(BaseModel):
    type: str = Field(..., regex="^[a-z_]+$")
    content: str | None = Field(None, max_length=10000)
    room_name: str | None = Field(None, max_length=100, regex="^[a-zA-Z0-9-_]+$")

    @validator('content')
    def sanitize_content(cls, v):
        if v:
            # Remove potentially harmful characters
            return v.strip()
        return v
```

### 3. CORS Configuration

Pastikan CORS sudah dikonfigurasi di `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Scaling WebSocket

### Single Server (Current Implementation)

✅ Works untuk small-medium applications (< 10,000 concurrent connections)

### Multi-Server dengan Redis Pub/Sub

Untuk scaling horizontal, implement Redis pub/sub:

```python
# app/core/websocket_redis.py
import redis.asyncio as redis
import json

class RedisWebSocketManager(WebsocketConnectionManager):
    def __init__(self):
        super().__init__()
        self.redis = redis.from_url("redis://localhost")
        self.pubsub = self.redis.pubsub()

    async def subscribe_to_room(self, room_name: str):
        await self.pubsub.subscribe(f"room:{room_name}")

    async def publish_to_room(self, room_name: str, message: dict):
        await self.redis.publish(
            f"room:{room_name}",
            json.dumps(message)
        )

    async def listen_for_messages(self):
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                # Broadcast to local connections
                await self.broadcast_to_room_local(data['room'], data['message'])
```

### Load Balancing

```nginx
# Nginx dengan IP hash untuk sticky sessions
upstream websocket_backend {
    ip_hash;  # Sticky sessions
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

## Monitoring & Debugging

### 1. Logging

Tambahkan logging untuk debugging:

```python
import logging

logger = logging.getLogger(__name__)

class WebsocketConnectionManager:
    async def connect(self, websocket: WebSocket, user_id: uuid.UUID):
        await websocket.accept()
        self.active_connections[websocket] = user_id
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        user_id = self.active_connections.get(websocket)
        # ... existing code ...
        logger.info(f"User {user_id} disconnected. Total connections: {len(self.active_connections)}")
```

### 2. Metrics Endpoint

Tambahkan endpoint untuk monitoring:

```python
# app/api/v1/endpoint/api.py

@router.get("/ws/stats")
async def websocket_stats(current_user: CurrentUser):
    """Get WebSocket connection statistics"""
    return {
        "total_connections": len(ws_manager.active_connections),
        "total_rooms": len(ws_manager.rooms),
        "rooms": ws_manager.get_active_rooms(),
    }
```

### 3. Health Check

```python
@router.get("/ws/health")
async def websocket_health():
    """WebSocket health check"""
    return {
        "status": "healthy",
        "service": "websocket",
        "active_connections": len(ws_manager.active_connections)
    }
```

### 4. Connection Debugging

```python
# Test WebSocket connection issues
import asyncio

async def debug_connection():
    try:
        async with websockets.connect(
            "ws://localhost:8000/api/v1/ws?token=TOKEN",
            ping_interval=20,
            ping_timeout=10
        ) as ws:
            print("Connected successfully!")

            # Keep alive
            while True:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=30)
                    print(f"Received: {message}")
                except asyncio.TimeoutError:
                    print("No message received in 30s, sending ping...")
                    await ws.ping()

    except Exception as e:
        print(f"Connection error: {e}")
```

## Common Issues & Solutions

### Issue: Connection Timeout

**Solution:**
```python
# Increase timeout di nginx
proxy_read_timeout 86400;
proxy_send_timeout 86400;
```

### Issue: Connection Drops

**Solution:** Implement ping/pong keep-alive:

```python
# In endpoint
async def keep_alive(websocket: WebSocket):
    while True:
        await asyncio.sleep(30)
        try:
            await websocket.send_text("PING")
        except:
            break
```

### Issue: Memory Leak

**Solution:** Cleanup disconnected rooms:

```python
async def cleanup_empty_rooms():
    """Remove rooms with no connections"""
    empty_rooms = [
        name for name, room in ws_manager.rooms.items()
        if len(room.connections) == 0
    ]
    for room_name in empty_rooms:
        del ws_manager.rooms[room_name]
```

## Best Practices

1. ✅ Always validate JWT token
2. ✅ Implement rate limiting
3. ✅ Sanitize user input
4. ✅ Use WSS (TLS) in production
5. ✅ Set appropriate timeouts
6. ✅ Monitor connection counts
7. ✅ Cleanup disconnections properly
8. ✅ Log important events
9. ✅ Handle errors gracefully
10. ✅ Test with load testing tools

## Next Steps

- 📖 Baca [WEBSOCKET_QUICKSTART.md](./WEBSOCKET_QUICKSTART.md) untuk usage examples
- 🎨 Lihat [WEBSOCKET_FRONTEND_GUIDE.md](./WEBSOCKET_FRONTEND_GUIDE.md) untuk frontend integration
- 🔧 Customize handlers di `app/services/websocket_service.py`
- 📊 Setup monitoring dan metrics
- 🚀 Deploy ke production dengan SSL/TLS
# Quick Start: WebSocket Real-Time Communication

## Overview

Fitur WebSocket memungkinkan komunikasi real-time bidirectional antara client dan server. Implementasi ini mendukung:
- ✅ Authentication dengan JWT token
- ✅ Room-based chat system
- ✅ Broadcast messages
- ✅ Personal messages
- ✅ Auto-reply bot (untuk testing)

## Setup Cepat

### 1. Dependencies
Semua dependencies sudah termasuk dalam FastAPI:
- `fastapi` - WebSocket support built-in
- `websockets` - WebSocket protocol implementation

### 2. Endpoint WebSocket

**URL:** `ws://localhost:8000/api/v1/ws?token=<your_access_token>`

**Protocol:** WebSocket (ws:// untuk development, wss:// untuk production)

### 3. Authentication

WebSocket endpoint memerlukan JWT access token yang sama dengan REST API:

```bash
# 1. Dapatkan access token via login
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=yourpassword"

# Response:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "token_type": "bearer"
# }

# 2. Connect WebSocket dengan token
# ws://localhost:8000/api/v1/ws?token=eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Message Format

Semua pesan menggunakan format JSON:

```json
{
  "type": "message_type",
  "room_name": "optional_room_name",
  "content": "optional_message_content"
}
```

## Available Commands

### 1. Create Room
Membuat room chat baru:

```json
{
  "type": "create_room",
  "room_name": "general-chat"
}
```

**Response:**
```
[System] Room 'general-chat' created successfully!
```

### 2. Join Room
Bergabung ke room yang sudah ada:

```json
{
  "type": "join_room",
  "room_name": "general-chat"
}
```

**Response:**
```
[System] Joined room 'general-chat' successfully!
ROOM_UPDATE:general-chat
```

### 3. Send Message
Mengirim pesan ke room (harus join room dulu):

```json
{
  "type": "message",
  "content": "Hello everyone!"
}
```

**Response:**
```
You wrote: Hello everyone!
```

**Other room members receive:**
```
User <user-id> says: Hello everyone!
```

### 4. List Rooms
Melihat semua room yang aktif:

```json
{
  "type": "list_rooms"
}
```

**Response:**
```
[System] Active Rooms:
  - general-chat (Creator: 123e4567-e89b-12d3-a456-426614174000, Members: 3, Created: 2025-10-19 10:30:00)
  - dev-team (Creator: 987e6543-e21b-12d3-a456-426614174000, Members: 5, Created: 2025-10-19 11:00:00)
```

### 5. Leave Room
Keluar dari room saat ini:

```json
{
  "type": "leave_room"
}
```

**Response:**
```
[System] Left room 'general-chat' successfully!
ROOM_UPDATE:None
```

### 6. Close Room
Menutup room (hanya creator yang bisa):

```json
{
  "type": "close_room"
}
```

**Response:**
```
[System] Room 'general-chat' closed successfully!
ROOM_UPDATE:None
```

## Testing dengan Python

```python
import asyncio
import websockets
import json

async def test_websocket():
    # Ganti dengan access token yang valid
    token = "eyJ0eXAiOiJKV1QiLCJhbGc..."
    uri = f"ws://localhost:8000/api/v1/ws?token={token}"

    async with websockets.connect(uri) as websocket:
        # Terima welcome message
        welcome = await websocket.recv()
        print(f"Received: {welcome}")

        # Create room
        await websocket.send(json.dumps({
            "type": "create_room",
            "room_name": "test-room"
        }))
        response = await websocket.recv()
        print(f"Received: {response}")

        # Join room
        await websocket.send(json.dumps({
            "type": "join_room",
            "room_name": "test-room"
        }))
        response = await websocket.recv()
        print(f"Received: {response}")

        # Send message
        await websocket.send(json.dumps({
            "type": "message",
            "content": "Hello from Python!"
        }))
        response = await websocket.recv()
        print(f"Received: {response}")

asyncio.run(test_websocket())
```

## Testing dengan JavaScript (Browser)

```javascript
// Ganti dengan access token yang valid
const token = "eyJ0eXAiOiJKV1QiLCJhbGc...";
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws?token=${token}`);

ws.onopen = () => {
    console.log('Connected to WebSocket');

    // Create room
    ws.send(JSON.stringify({
        type: 'create_room',
        room_name: 'test-room'
    }));
};

ws.onmessage = (event) => {
    console.log('Received:', event.data);
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('Disconnected from WebSocket');
};

// Mengirim pesan
function sendMessage(content) {
    ws.send(JSON.stringify({
        type: 'message',
        content: content
    }));
}

// Join room
function joinRoom(roomName) {
    ws.send(JSON.stringify({
        type: 'join_room',
        room_name: roomName
    }));
}
```

## Bot Auto-Reply

Bot akan otomatis reply untuk testing:

| User Message | Bot Reply |
|--------------|-----------|
| "halo" | "apa kabar" |
| Contains "nama" | "nama saya abdu" |
| Contains vowels (a,i,u,e,o) | Random Lorem Ipsum sentence |

## Error Handling

### Authentication Failed
```
WebSocket closed with code 1008: Authentication failed
```
**Solution:** Pastikan token valid dan tidak expired

### Invalid JSON
```
[System] Invalid JSON format. Please send valid JSON.
```
**Solution:** Pastikan pesan dalam format JSON yang valid

### Room Not Found
```
[System] Room 'room-name' does not exist!
```
**Solution:** Buat room terlebih dahulu atau join room yang sudah ada

### Not in Room
```
[System] You need to join a room first to send messages!
```
**Solution:** Join room sebelum mengirim pesan

## Architecture Overview

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│   Client    │◄───────►│  WebSocket       │◄───────►│   Room      │
│  (Browser)  │  WS     │  Endpoint        │         │  Manager    │
└─────────────┘         └──────────────────┘         └─────────────┘
                                │                            │
                                ▼                            ▼
                        ┌──────────────────┐         ┌─────────────┐
                        │  WebSocket       │         │  Multiple   │
                        │  Service Handler │         │  Rooms      │
                        └──────────────────┘         └─────────────┘
```

## Files Structure

```
backend/app/
├── core/
│   └── websocket.py              # WebSocket manager & Room class
├── services/
│   └── websocket_service.py      # Message handlers
└── api/v1/
    ├── endpoint/
    │   └── websocket.py          # WebSocket endpoint
    ├── deps.py                   # Authentication (get_current_user_ws)
    └── router.py                 # Router registration
```

## Next Steps

- 📖 Baca [WEBSOCKET_SETUP.md](./WEBSOCKET_SETUP.md) untuk setup production
- 🔧 Lihat [WEBSOCKET_FRONTEND_GUIDE.md](./WEBSOCKET_FRONTEND_GUIDE.md) untuk integrasi frontend
- 🚀 Customize message handlers di `app/services/websocket_service.py`
- 💾 Tambahkan persistence (save messages to database) jika diperlukan
