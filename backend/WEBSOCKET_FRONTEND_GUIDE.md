# WebSocket Frontend Integration Guide

Panduan lengkap untuk mengintegrasikan WebSocket ke frontend React/TypeScript.

## Table of Contents

1. [React Hook Setup](#react-hook-setup)
2. [TypeScript Types](#typescript-types)
3. [WebSocket Context](#websocket-context)
4. [Component Examples](#component-examples)
5. [React Query Integration](#react-query-integration)
6. [Error Handling](#error-handling)
7. [Reconnection Strategy](#reconnection-strategy)

## TypeScript Types

Buat file types untuk WebSocket messages:

```typescript
// src/types/websocket.ts

export type WebSocketMessageType = 
  | 'create_room'
  | 'join_room'
  | 'leave_room'
  | 'close_room'
  | 'list_rooms'
  | 'message';

export interface WebSocketMessage {
  type: WebSocketMessageType;
  room_name?: string;
  content?: string;
}

export interface RoomInfo {
  name: string;
  creator_id: string;
  members: number;
  created_at: string;
}

export interface WebSocketContextType {
  isConnected: boolean;
  currentRoom: string | null;
  rooms: RoomInfo[];
  messages: Message[];
  sendMessage: (message: WebSocketMessage) => void;
  createRoom: (roomName: string) => void;
  joinRoom: (roomName: string) => void;
  leaveRoom: () => void;
  closeRoom: () => void;
  sendChatMessage: (content: string) => void;
  refreshRooms: () => void;
}

export interface Message {
  id: string;
  content: string;
  timestamp: Date;
  sender?: string;
  isSystem: boolean;
}
```

## React Hook Setup

### Custom Hook: useWebSocket

```typescript
// src/hooks/useWebSocket.ts

import { useEffect, useRef, useState, useCallback } from 'react';
import { WebSocketMessage, Message } from '@/types/websocket';

interface UseWebSocketOptions {
  url: string;
  token: string;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
}

export const useWebSocket = ({
  url,
  token,
  onConnect,
  onDisconnect,
  onError,
  autoReconnect = true,
  reconnectInterval = 3000,
}: UseWebSocketOptions) => {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentRoom, setCurrentRoom] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = `${url}?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      onConnect?.();
    };

    ws.onmessage = (event) => {
      const data = event.data;
      
      // Handle ROOM_UPDATE special message
      if (data.startsWith('ROOM_UPDATE:')) {
        const roomName = data.split(':')[1];
        setCurrentRoom(roomName === 'None' ? null : roomName);
        return;
      }

      // Add message to messages list
      const message: Message = {
        id: crypto.randomUUID(),
        content: data,
        timestamp: new Date(),
        isSystem: data.startsWith('[System]'),
      };
      
      setMessages((prev) => [...prev, message]);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      onError?.(error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      wsRef.current = null;
      onDisconnect?.();

      // Auto reconnect
      if (autoReconnect) {
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect...');
          connect();
        }, reconnectInterval);
      }
    };

    wsRef.current = ws;
  }, [url, token, onConnect, onDisconnect, onError, autoReconnect, reconnectInterval]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    wsRef.current?.close();
    wsRef.current = null;
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    messages,
    currentRoom,
    sendMessage,
    connect,
    disconnect,
  };
};
```

## WebSocket Context

### Context Provider

```typescript
// src/contexts/WebSocketContext.tsx

import React, { createContext, useContext, ReactNode, useCallback, useState } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { WebSocketMessage, WebSocketContextType, RoomInfo } from '@/types/websocket';

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

interface WebSocketProviderProps {
  children: ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const [rooms, setRooms] = useState<RoomInfo[]>([]);
  
  // Get token from localStorage or your auth state
  const token = localStorage.getItem('access_token') || '';
  
  // WebSocket URL - adjust based on environment
  const wsUrl = import.meta.env.PROD 
    ? 'wss://your-domain.com/api/v1/ws'
    : 'ws://localhost:8000/api/v1/ws';

  const {
    isConnected,
    messages,
    currentRoom,
    sendMessage,
  } = useWebSocket({
    url: wsUrl,
    token,
    onConnect: () => {
      console.log('Connected to WebSocket server');
    },
    onDisconnect: () => {
      console.log('Disconnected from WebSocket server');
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
    },
  });

  const createRoom = useCallback((roomName: string) => {
    sendMessage({
      type: 'create_room',
      room_name: roomName,
    });
  }, [sendMessage]);

  const joinRoom = useCallback((roomName: string) => {
    sendMessage({
      type: 'join_room',
      room_name: roomName,
    });
  }, [sendMessage]);

  const leaveRoom = useCallback(() => {
    sendMessage({
      type: 'leave_room',
    });
  }, [sendMessage]);

  const closeRoom = useCallback(() => {
    sendMessage({
      type: 'close_room',
    });
  }, [sendMessage]);

  const sendChatMessage = useCallback((content: string) => {
    sendMessage({
      type: 'message',
      content,
    });
  }, [sendMessage]);

  const refreshRooms = useCallback(() => {
    sendMessage({
      type: 'list_rooms',
    });
    
    // Parse rooms from messages (you might want to improve this)
    const roomMessages = messages.filter(m => 
      m.content.includes('Active Rooms:')
    );
    // Parse and set rooms...
  }, [sendMessage, messages]);

  const value: WebSocketContextType = {
    isConnected,
    currentRoom,
    rooms,
    messages,
    sendMessage,
    createRoom,
    joinRoom,
    leaveRoom,
    closeRoom,
    sendChatMessage,
    refreshRooms,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within WebSocketProvider');
  }
  return context;
};
```

### App Setup

```typescript
// src/main.tsx

import React from 'react';
import ReactDOM from 'react-dom/client';
import { WebSocketProvider } from './contexts/WebSocketContext';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <WebSocketProvider>
      <App />
    </WebSocketProvider>
  </React.StrictMode>,
);
```

## Component Examples

### Chat Room Component

```typescript
// src/components/ChatRoom.tsx

import React, { useState, useEffect, useRef } from 'react';
import { useWebSocketContext } from '@/contexts/WebSocketContext';

export const ChatRoom: React.FC = () => {
  const {
    isConnected,
    currentRoom,
    messages,
    sendChatMessage,
    joinRoom,
    leaveRoom,
  } = useWebSocketContext();

  const [inputMessage, setInputMessage] = useState('');
  const [roomName, setRoomName] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputMessage.trim() && currentRoom) {
      sendChatMessage(inputMessage);
      setInputMessage('');
    }
  };

  const handleJoinRoom = (e: React.FormEvent) => {
    e.preventDefault();
    if (roomName.trim()) {
      joinRoom(roomName);
      setRoomName('');
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      {/* Connection Status */}
      <div className="mb-4 p-3 rounded-lg bg-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="font-semibold">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          {currentRoom && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Room:</span>
              <span className="font-semibold">{currentRoom}</span>
              <button
                onClick={leaveRoom}
                className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600"
              >
                Leave
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Join Room Form */}
      {!currentRoom && (
        <form onSubmit={handleJoinRoom} className="mb-4 flex gap-2">
          <input
            type="text"
            value={roomName}
            onChange={(e) => setRoomName(e.target.value)}
            placeholder="Enter room name..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={!isConnected}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300"
          >
            Join Room
          </button>
        </form>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto bg-white border rounded-lg p-4 mb-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`mb-2 p-2 rounded ${
              message.isSystem ? 'bg-yellow-50 text-gray-700' : 'bg-blue-50'
            }`}
          >
            <div className="text-xs text-gray-500 mb-1">
              {message.timestamp.toLocaleTimeString()}
            </div>
            <div className="whitespace-pre-wrap">{message.content}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <form onSubmit={handleSendMessage} className="flex gap-2">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder={currentRoom ? "Type a message..." : "Join a room first..."}
          disabled={!currentRoom || !isConnected}
          className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        />
        <button
          type="submit"
          disabled={!currentRoom || !isConnected || !inputMessage.trim()}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300"
        >
          Send
        </button>
      </form>
    </div>
  );
};
```

### Room List Component

```typescript
// src/components/RoomList.tsx

import React, { useEffect } from 'react';
import { useWebSocketContext } from '@/contexts/WebSocketContext';

export const RoomList: React.FC = () => {
  const { isConnected, rooms, refreshRooms, joinRoom, createRoom } = useWebSocketContext();
  const [newRoomName, setNewRoomName] = React.useState('');

  useEffect(() => {
    if (isConnected) {
      refreshRooms();
    }
  }, [isConnected, refreshRooms]);

  const handleCreateRoom = (e: React.FormEvent) => {
    e.preventDefault();
    if (newRoomName.trim()) {
      createRoom(newRoomName);
      setNewRoomName('');
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h2 className="text-2xl font-bold mb-4">Chat Rooms</h2>

      {/* Create Room Form */}
      <form onSubmit={handleCreateRoom} className="mb-6 flex gap-2">
        <input
          type="text"
          value={newRoomName}
          onChange={(e) => setNewRoomName(e.target.value)}
          placeholder="New room name..."
          className="flex-1 px-4 py-2 border rounded-lg"
        />
        <button
          type="submit"
          disabled={!isConnected}
          className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-300"
        >
          Create Room
        </button>
      </form>

      {/* Rooms List */}
      <div className="space-y-2">
        {rooms.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            No active rooms. Create one to get started!
          </div>
        ) : (
          rooms.map((room) => (
            <div
              key={room.name}
              className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
            >
              <div>
                <h3 className="font-semibold">{room.name}</h3>
                <p className="text-sm text-gray-600">
                  {room.members} member{room.members !== 1 ? 's' : ''} • Created {room.created_at}
                </p>
              </div>
              <button
                onClick={() => joinRoom(room.name)}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              >
                Join
              </button>
            </div>
          ))
        )}
      </div>

      <button
        onClick={refreshRooms}
        disabled={!isConnected}
        className="mt-4 w-full px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300 disabled:bg-gray-100"
      >
        Refresh Rooms
      </button>
    </div>
  );
};
```

### Connection Status Component

```typescript
// src/components/ConnectionStatus.tsx

import React from 'react';
import { useWebSocketContext } from '@/contexts/WebSocketContext';

export const ConnectionStatus: React.FC = () => {
  const { isConnected, currentRoom } = useWebSocketContext();

  return (
    <div className="fixed top-4 right-4 z-50">
      <div className={`px-4 py-2 rounded-lg shadow-lg ${
        isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
      }`}>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${
            isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
          }`} />
          <span className="font-medium">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        {currentRoom && (
          <div className="text-xs mt-1">
            Room: {currentRoom}
          </div>
        )}
      </div>
    </div>
  );
};
```

## React Query Integration

Jika menggunakan React Query, bisa combine dengan REST API:

```typescript
// src/hooks/useWebSocketWithQuery.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useWebSocketContext } from '@/contexts/WebSocketContext';

export const useWebSocketWithQuery = () => {
  const queryClient = useQueryClient();
  const { sendChatMessage, joinRoom, createRoom } = useWebSocketContext();

  // Mutation for sending messages
  const sendMessageMutation = useMutation({
    mutationFn: async (content: string) => {
      sendChatMessage(content);
    },
    onSuccess: () => {
      // Optionally invalidate queries or update cache
      queryClient.invalidateQueries({ queryKey: ['messages'] });
    },
  });

  // Mutation for joining room
  const joinRoomMutation = useMutation({
    mutationFn: async (roomName: string) => {
      joinRoom(roomName);
    },
  });

  return {
    sendMessage: sendMessageMutation.mutate,
    joinRoom: joinRoomMutation.mutate,
    isLoading: sendMessageMutation.isPending,
  };
};
```

## Error Handling

```typescript
// src/hooks/useWebSocketWithErrorHandling.ts

import { useCallback, useState } from 'react';
import { useWebSocket } from './useWebSocket';

export const useWebSocketWithErrorHandling = (url: string, token: string) => {
  const [error, setError] = useState<string | null>(null);

  const handleError = useCallback((event: Event) => {
    setError('Failed to connect to WebSocket server');
    console.error('WebSocket error:', event);
  }, []);

  const handleDisconnect = useCallback(() => {
    setError('Disconnected from server. Attempting to reconnect...');
  }, []);

  const handleConnect = useCallback(() => {
    setError(null);
  }, []);

  const ws = useWebSocket({
    url,
    token,
    onConnect: handleConnect,
    onDisconnect: handleDisconnect,
    onError: handleError,
  });

  return {
    ...ws,
    error,
    clearError: () => setError(null),
  };
};
```

## Reconnection Strategy

```typescript
// src/hooks/useWebSocketReconnect.ts

import { useEffect, useRef } from 'react';

interface ReconnectOptions {
  maxRetries?: number;
  initialDelay?: number;
  maxDelay?: number;
  backoffMultiplier?: number;
}

export const useWebSocketReconnect = (
  connect: () => void,
  isConnected: boolean,
  options: ReconnectOptions = {}
) => {
  const {
    maxRetries = 10,
    initialDelay = 1000,
    maxDelay = 30000,
    backoffMultiplier = 2,
  } = options;

  const retriesRef = useRef(0);
  const timeoutRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    if (!isConnected && retriesRef.current < maxRetries) {
      const delay = Math.min(
        initialDelay * Math.pow(backoffMultiplier, retriesRef.current),
        maxDelay
      );

      console.log(`Reconnecting in ${delay}ms (attempt ${retriesRef.current + 1}/${maxRetries})`);

      timeoutRef.current = setTimeout(() => {
        retriesRef.current += 1;
        connect();
      }, delay);
    } else if (isConnected) {
      retriesRef.current = 0;
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [isConnected, connect, maxRetries, initialDelay, maxDelay, backoffMultiplier]);
};
```

## Complete Example App

```typescript
// src/App.tsx

import React from 'react';
import { ChatRoom } from './components/ChatRoom';
import { RoomList } from './components/RoomList';
import { ConnectionStatus } from './components/ConnectionStatus';

function App() {
  const [view, setView] = React.useState<'rooms' | 'chat'>('rooms');

  return (
    <div className="min-h-screen bg-gray-50">
      <ConnectionStatus />
      
      <nav className="bg-white shadow-sm p-4 mb-4">
        <div className="max-w-4xl mx-auto flex gap-4">
          <button
            onClick={() => setView('rooms')}
            className={`px-4 py-2 rounded ${
              view === 'rooms' ? 'bg-blue-500 text-white' : 'bg-gray-200'
            }`}
          >
            Rooms
          </button>
          <button
            onClick={() => setView('chat')}
            className={`px-4 py-2 rounded ${
              view === 'chat' ? 'bg-blue-500 text-white' : 'bg-gray-200'
            }`}
          >
            Chat
          </button>
        </div>
      </nav>

      {view === 'rooms' ? <RoomList /> : <ChatRoom />}
    </div>
  );
}

export default App;
```

## Environment Variables

```env
# .env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/api/v1/ws

# .env.production
VITE_API_URL=https://your-domain.com
VITE_WS_URL=wss://your-domain.com/api/v1/ws
```

## Testing

```typescript
// src/__tests__/useWebSocket.test.ts

import { renderHook, waitFor } from '@testing-library/react';
import { useWebSocket } from '../hooks/useWebSocket';
import WS from 'jest-websocket-mock';

describe('useWebSocket', () => {
  let server: WS;

  beforeEach(() => {
    server = new WS('ws://localhost:8000/api/v1/ws');
  });

  afterEach(() => {
    WS.clean();
  });

  it('should connect to WebSocket', async () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/api/v1/ws',
        token: 'test-token',
      })
    );

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });
  });

  it('should send messages', async () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/api/v1/ws',
        token: 'test-token',
      })
    );

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });

    result.current.sendMessage({
      type: 'message',
      content: 'Hello',
    });

    await expect(server).toReceiveMessage(
      JSON.stringify({ type: 'message', content: 'Hello' })
    );
  });
});
```

## Best Practices

1. ✅ **Always handle disconnections gracefully**
2. ✅ **Implement exponential backoff for reconnection**
3. ✅ **Show connection status to users**
4. ✅ **Validate token before connecting**
5. ✅ **Clean up WebSocket connections on unmount**
6. ✅ **Use TypeScript for type safety**
7. ✅ **Implement message queuing for offline messages**
8. ✅ **Add loading states for better UX**
9. ✅ **Handle errors and show user-friendly messages**
10. ✅ **Test WebSocket connections thoroughly**

## Next Steps

- 📖 Customize components sesuai design system Anda
- 🎨 Tambahkan animations dan transitions
- 🔔 Implement notifications untuk new messages
- 💾 Persist chat history di localStorage
- 🔒 Tambahkan input sanitization
- 📱 Optimize untuk mobile devices
- 🧪 Tambahkan comprehensive tests

## Troubleshooting

### Issue: Token expired during connection

```typescript
// Refresh token before WebSocket connection
const getValidToken = async () => {
  const token = localStorage.getItem('access_token');
  // Check if token is expired and refresh if needed
  // Return valid token
  return token;
};
```

### Issue: Messages not displaying

Check browser console untuk WebSocket errors dan pastikan message parsing benar.

### Issue: Connection drops frequently

Implement ping/pong atau heartbeat mechanism di hook.

---

Untuk pertanyaan atau issues, silakan buka issue di repository atau hubungi tim development.

