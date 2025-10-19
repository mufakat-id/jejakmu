# WebSocket Playground - User Guide

## Overview

WebSocket Playground adalah tool testing interaktif berbasis HTML untuk menguji semua fitur WebSocket real-time communication tanpa perlu menulis kode.

## Features

✅ **Real-time Connection Testing** - Connect/disconnect dengan visual feedback
✅ **Quick Login Integration** - Login langsung dari playground untuk mendapatkan token
✅ **Room Management** - Create, join, leave, dan close rooms
✅ **Message Testing** - Send messages dengan berbagai cara
✅ **Raw JSON Mode** - Test dengan custom JSON messages
✅ **Live Message Log** - Lihat semua messages secara real-time
✅ **Statistics Counter** - Track sent, received, dan error messages
✅ **Beautiful UI** - Modern, responsive, dan user-friendly interface

## Quick Start

### 1. Buka Playground

```bash
# Dari folder backend
open websocket-playground.html

# Atau double-click file websocket-playground.html di file explorer
```

Playground akan terbuka di browser default Anda.

### 2. Login untuk Mendapatkan Token

**Cara 1: Quick Login (Recommended)**

1. Scroll ke section "🔑 Quick Login"
2. Isi kredensial (default: `admin@example.com` / `changethis`)
3. Klik tombol "Login & Get Token"
4. Token akan otomatis diisi ke field Access Token

**Cara 2: Manual Token**

```bash
# Dapatkan token via curl
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis"

# Copy access_token dari response dan paste ke field "Access Token"
```

### 3. Connect ke WebSocket

1. Pastikan backend server sudah running (`uvicorn app.main:app --reload`)
2. WebSocket URL default: `ws://localhost:8000/api/v1/ws`
3. Klik tombol "Connect"
4. Status indicator akan berubah hijau jika connected

### 4. Test Room Features

**Create Room:**
1. Pilih tab "Rooms"
2. Isi "Room Name" (contoh: `test-room`)
3. Klik "Create Room"
4. Lihat response di Messages Log

**Join Room:**
1. Isi "Room Name" dengan nama room yang ada
2. Klik "Join Room"
3. Current room akan ditampilkan di bawah buttons

**Send Message:**
1. Pilih tab "Messages"
2. Ketik pesan di "Message Content"
3. Klik "Send Message"
4. Atau gunakan Quick Actions untuk test bot

**Leave/Close Room:**
- "Leave Room" - Keluar dari room saat ini
- "Close Room" - Tutup room (hanya creator)

### 5. Test dengan Raw JSON

1. Pilih tab "Raw JSON"
2. Ketik JSON message, contoh:
   ```json
   {"type": "message", "content": "Hello from raw JSON!"}
   ```
3. Klik "Send Raw JSON"

## Interface Guide

### Connection Section (Top)

```
┌─────────────────────────────────┐
│ 🟢/🔴 Connection                │
│ WebSocket URL: ws://...         │
│ Access Token: ********          │
│ [Connect] [Disconnect]          │
└─────────────────────────────────┘
```

- **Green dot (🟢)**: Connected
- **Red dot (🔴)**: Disconnected
- **Connect button**: Disabled saat connected
- **Disconnect button**: Disabled saat disconnected

### Quick Login Section

```
┌─────────────────────────────────┐
│ 🔑 Quick Login                  │
│ Email: admin@example.com        │
│ Password: ********              │
│ [Login & Get Token]             │
└─────────────────────────────────┘
```

Gunakan ini untuk mendapatkan token dengan cepat tanpa curl.

### Action Tabs

**Tab 1: Rooms**
- Create Room
- Join Room
- Leave Room
- Close Room
- Refresh Rooms List
- Current Room indicator

**Tab 2: Messages**
- Message textarea
- Send Message button
- Quick Actions (test bot responses)

**Tab 3: Raw JSON**
- Custom JSON textarea
- Send Raw JSON button
- Example messages

### Messages Log (Right Panel)

```
┌─────────────────────────────────┐
│ 📨 Messages Log                 │
│ ┌─────────────────────────────┐ │
│ │ SYSTEM  10:30:45            │ │
│ │ Connected to server         │ │
│ ├─────────────────────────────┤ │
│ │ SENT    10:30:47            │ │
│ │ → {"type":"create_room"...} │ │
│ ├─────────────────────────────┤ │
│ │ RECEIVED 10:30:48           │ │
│ │ [System] Room created!      │ │
│ └─────────────────────────────┘ │
│ [Clear Messages]                │
└─────────────────────────────────┘
```

**Color Coding:**
- 🟡 Yellow: SYSTEM messages
- 🔵 Blue: SENT messages
- 🟢 Green: RECEIVED messages
- 🔴 Red: ERROR messages

### Statistics (Bottom)

```
┌─────┬─────┬─────┐
│ 15  │ 23  │  0  │
│Sent │Recv │Error│
└─────┴─────┴─────┘
```

Real-time counter untuk tracking messages.

## Testing Scenarios

### Scenario 1: Basic Room Chat

```
1. Connect to WebSocket
2. Create room "general"
3. Join room "general"
4. Send message "Hello everyone!"
5. Test bot auto-reply dengan "halo"
6. Leave room
```

### Scenario 2: Multiple Tabs Testing

```
1. Buka playground di 2 browser tabs
2. Login dan connect di kedua tabs
3. Tab 1: Create room "test"
4. Tab 2: Join room "test"
5. Kirim messages dari kedua tabs
6. Lihat broadcast messages
```

### Scenario 3: Bot Testing

Bot akan auto-reply untuk pesan tertentu:

| Kirim Pesan | Bot Reply |
|-------------|-----------|
| "halo" | "apa kabar" |
| "nama" atau "nama kamu" | "nama saya abdu" |
| Any text with vowels (a,i,u,e,o) | Random Lorem Ipsum |

**Test Steps:**
1. Join room
2. Klik "Send 'halo'" di Quick Actions
3. Lihat bot reply
4. Coba quick actions lainnya

### Scenario 4: Raw JSON Testing

```json
// Test create room
{"type": "create_room", "room_name": "developers"}

// Test list rooms
{"type": "list_rooms"}

// Test with wrong format (should error)
{"invalid": "json", "structure": true}
```

## Message Types Reference

### 1. Create Room
```json
{
  "type": "create_room",
  "room_name": "room-name-here"
}
```

**Expected Response:**
```
[System] Room 'room-name-here' created successfully!
```

### 2. Join Room
```json
{
  "type": "join_room",
  "room_name": "room-name-here"
}
```

**Expected Response:**
```
[System] Joined room 'room-name-here' successfully!
ROOM_UPDATE:room-name-here
```

### 3. Send Message
```json
{
  "type": "message",
  "content": "Your message here"
}
```

**Expected Response:**
```
You wrote: Your message here
```

### 4. List Rooms
```json
{
  "type": "list_rooms"
}
```

**Expected Response:**
```
[System] Active Rooms:
  - room1 (Creator: uuid, Members: 3, Created: timestamp)
  - room2 (Creator: uuid, Members: 1, Created: timestamp)
```

### 5. Leave Room
```json
{
  "type": "leave_room"
}
```

**Expected Response:**
```
[System] Left room 'room-name' successfully!
ROOM_UPDATE:None
```

### 6. Close Room
```json
{
  "type": "close_room"
}
```

**Expected Response:**
```
[System] Room 'room-name' closed successfully!
ROOM_UPDATE:None
```

## Troubleshooting

### Issue: Cannot connect

**Solutions:**
1. ✓ Pastikan backend server running (`uvicorn app.main:app --reload`)
2. ✓ Cek WebSocket URL benar (`ws://localhost:8000/api/v1/ws`)
3. ✓ Pastikan token valid (tidak expired)
4. ✓ Cek browser console untuk error details

### Issue: Login failed

**Solutions:**
1. ✓ Pastikan email dan password benar
2. ✓ Cek API URL di WebSocket URL field
3. ✓ Pastikan backend database sudah di-setup
4. ✓ Cek user exists dan active

### Issue: Token expired

**Solutions:**
1. ✓ Klik "Login & Get Token" lagi
2. ✓ Atau generate token baru via curl
3. ✓ Disconnect dan reconnect dengan token baru

### Issue: Messages not sending

**Solutions:**
1. ✓ Cek connection status (harus hijau)
2. ✓ Join room dulu sebelum send message
3. ✓ Cek Messages Log untuk error details
4. ✓ Verify JSON format jika pakai Raw JSON

### Issue: Room not found

**Solutions:**
1. ✓ Klik "Refresh Rooms List" untuk update
2. ✓ Create room dulu sebelum join
3. ✓ Check room name spelling

## Advanced Usage

### Custom WebSocket URL

Untuk testing di server lain atau production:

```
Development: ws://localhost:8000/api/v1/ws
Production:  wss://your-domain.com/api/v1/ws
```

### Browser Console Debugging

Buka Browser DevTools (F12) untuk melihat:
- WebSocket connection details
- Raw messages sent/received
- JavaScript errors
- Network activity

### Multiple User Testing

1. Buka multiple browser windows/tabs
2. Login dengan user berbeda di setiap tab
3. Test multi-user room interactions
4. Lihat real-time broadcast messages

## Keyboard Shortcuts

(Coming soon - bisa ditambahkan di versi berikutnya)

## Tips & Best Practices

1. **Always check connection status** sebelum send messages
2. **Use Quick Login** untuk testing cepat
3. **Clear messages** periodically untuk clean log
4. **Test with multiple tabs** untuk simulate multiple users
5. **Use Raw JSON** untuk custom testing scenarios
6. **Monitor statistics** untuk track performance
7. **Check Messages Log** untuk debugging

## Feature Comparison

| Feature | Playground | Postman WS | Python Script |
|---------|-----------|-----------|---------------|
| Visual Interface | ✅ | ✅ | ❌ |
| Quick Login | ✅ | ❌ | ❌ |
| Message Log | ✅ | ✅ | ✅ |
| Statistics | ✅ | ❌ | ❌ |
| Raw JSON | ✅ | ✅ | ✅ |
| Preset Actions | ✅ | ❌ | ❌ |
| Multi-tab Testing | ✅ | ✅ | ✅ |

## Future Enhancements

Fitur yang bisa ditambahkan:
- [ ] Message history export
- [ ] Keyboard shortcuts
- [ ] Auto-reconnect toggle
- [ ] Message templates
- [ ] Dark mode toggle
- [ ] Connection latency indicator
- [ ] Message filtering
- [ ] Room members list

## Support

Untuk issues atau feature requests:
- Check backend logs: `tail -f backend/logs/app.log`
- Check browser console (F12)
- Refer to main WebSocket documentation

## Credits

WebSocket Playground v1.0
Part of Full Stack FastAPI Template
Created for easy WebSocket testing and development

---

**Happy Testing! 🚀**
