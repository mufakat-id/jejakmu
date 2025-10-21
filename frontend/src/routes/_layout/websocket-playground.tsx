import {
  Badge,
  Box,
  Button,
  Code,
  Container,
  Grid,
  Heading,
  HStack,
  Input,
  Separator,
  Tabs,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useCallback, useEffect, useRef, useState } from "react"
import useCustomToast from "@/hooks/useCustomToast"

export const Route = createFileRoute("/_layout/websocket-playground")({
  component: WebSocketPlayground,
})

interface Message {
  type: "sent" | "received" | "system" | "error"
  content: string
  timestamp: Date
}

function WebSocketPlayground() {
  const [ws, setWs] = useState<WebSocket | null>(null)
  const [wsUrl, setWsUrl] = useState("ws://localhost:8000/api/v1/ws")
  const [token, setToken] = useState("")
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      type: "system",
      content: "WebSocket Playground initialized. Connect to start testing.",
      timestamp: new Date(),
    },
  ])
  const [sentCount, setSentCount] = useState(0)
  const [receivedCount, setReceivedCount] = useState(0)
  const [errorCount, setErrorCount] = useState(0)
  const [currentRoom, setCurrentRoom] = useState<string | null>(null)

  // Form fields
  const [roomName, setRoomName] = useState("")
  const [messageContent, setMessageContent] = useState("")
  const [rawJson, setRawJson] = useState("")
  const [loginEmail, setLoginEmail] = useState("admin@example.com")
  const [loginPassword, setLoginPassword] = useState("changethis")

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { showSuccessToast, showErrorToast, showWarningToast, showInfoToast } =
    useCustomToast()

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [scrollToBottom])

  const addMessage = useCallback((type: Message["type"], content: string) => {
    setMessages((prev) => [...prev, { type, content, timestamp: new Date() }])
  }, [])

  const handleLogin = async () => {
    const apiUrl = wsUrl
      .replace("ws://", "http://")
      .replace("wss://", "https://")
      .replace("/api/v1/ws", "")

    addMessage("system", "Attempting to login...")

    try {
      const response = await fetch(`${apiUrl}/api/v1/login/access-token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `username=${encodeURIComponent(loginEmail)}&password=${encodeURIComponent(loginPassword)}`,
      })

      if (response.ok) {
        const data = await response.json()
        setToken(data.access_token)
        addMessage("system", "✓ Login successful! Token has been set.")
        showSuccessToast("Login successful")
      } else {
        const error = await response.json()
        addMessage("error", `Login failed: ${error.detail || "Unknown error"}`)
        setErrorCount((prev) => prev + 1)
        showErrorToast(`Login failed: ${error.detail || "Unknown error"}`)
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error"
      addMessage("error", `Login error: ${errorMessage}`)
      setErrorCount((prev) => prev + 1)
      showErrorToast(`Login error: ${errorMessage}`)
    }
  }

  const handleConnect = () => {
    if (!token) {
      addMessage("error", "Please enter an access token or login first!")
      setErrorCount((prev) => prev + 1)
      showWarningToast("Please enter an access token or login first")
      return
    }

    const fullUrl = `${wsUrl}?token=${token}`
    addMessage("system", `Connecting to ${wsUrl}...`)

    const newWs = new WebSocket(fullUrl)

    newWs.onopen = () => {
      addMessage("system", "✓ Connected to WebSocket server")
      setIsConnected(true)
      showSuccessToast("Connected")
    }

    newWs.onmessage = (event) => {
      setReceivedCount((prev) => prev + 1)
      const data = event.data

      // Handle special messages
      if (data.startsWith("ROOM_UPDATE:")) {
        const roomName = data.split(":")[1]
        setCurrentRoom(roomName === "None" ? null : roomName)
        addMessage(
          "system",
          `Room updated: ${roomName === "None" ? "None" : roomName}`,
        )
        return
      }

      // Detect message type
      if (data.startsWith("[System]")) {
        addMessage("system", data)
      } else if (data.startsWith("You wrote:")) {
        addMessage("sent", data)
      } else if (data.startsWith("User") || data.startsWith("Bot:")) {
        addMessage("received", data)
      } else {
        addMessage("received", data)
      }
    }

    newWs.onerror = () => {
      addMessage("error", "WebSocket error: Connection error")
      setErrorCount((prev) => prev + 1)
    }

    newWs.onclose = () => {
      addMessage("system", "Disconnected from WebSocket server")
      setIsConnected(false)
      setCurrentRoom(null)
      showInfoToast("Disconnected")
    }

    setWs(newWs)
  }

  const handleDisconnect = () => {
    if (ws) {
      ws.close()
      setWs(null)
    }
  }

  const sendWsMessage = (data: any) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      addMessage("error", "WebSocket is not connected!")
      setErrorCount((prev) => prev + 1)
      showErrorToast("WebSocket is not connected")
      return
    }

    const jsonString = JSON.stringify(data)
    ws.send(jsonString)
    addMessage("sent", `→ ${jsonString}`)
    setSentCount((prev) => prev + 1)
  }

  const createRoom = () => {
    if (!roomName) {
      showWarningToast("Room name required")
      return
    }
    sendWsMessage({ type: "create_room", room_name: roomName })
  }

  const joinRoom = () => {
    if (!roomName) {
      showWarningToast("Room name required")
      return
    }
    sendWsMessage({ type: "join_room", room_name: roomName })
  }

  const leaveRoom = () => {
    sendWsMessage({ type: "leave_room" })
  }

  const closeRoom = () => {
    sendWsMessage({ type: "close_room" })
  }

  const listRooms = () => {
    sendWsMessage({ type: "list_rooms" })
  }

  const sendMessage = () => {
    if (!messageContent) {
      showWarningToast("Message required")
      return
    }
    sendWsMessage({ type: "message", content: messageContent })
    setMessageContent("")
  }

  const sendQuickMessage = (content: string) => {
    sendWsMessage({ type: "message", content })
  }

  const sendRawJsonMessage = () => {
    try {
      const jsonData = JSON.parse(rawJson)
      sendWsMessage(jsonData)
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error"
      addMessage("error", `Invalid JSON: ${errorMessage}`)
      setErrorCount((prev) => prev + 1)
      showErrorToast(`Invalid JSON: ${errorMessage}`)
    }
  }

  const clearMessages = () => {
    setMessages([
      {
        type: "system",
        content: "Messages cleared.",
        timestamp: new Date(),
      },
    ])
    setSentCount(0)
    setReceivedCount(0)
    setErrorCount(0)
  }

  const getMessageColor = (type: Message["type"]) => {
    switch (type) {
      case "sent":
        return "blue"
      case "received":
        return "green"
      case "system":
        return "orange"
      case "error":
        return "red"
    }
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack gap={6} align="stretch">
        <Box
          textAlign="center"
          bgGradient="to-r"
          gradientFrom="purple.500"
          gradientTo="purple.600"
          p={8}
          borderRadius="lg"
          color="white"
        >
          <Heading size="2xl" mb={2}>
            🚀 WebSocket Playground
          </Heading>
          <Text fontSize="lg">Real-time Communication Testing Tool</Text>
        </Box>

        <Grid templateColumns={{ base: "1fr", lg: "1fr 1fr" }} gap={6}>
          {/* Left Panel: Controls */}
          <VStack gap={6} align="stretch">
            {/* Connection Section */}
            <Box bg="bg.panel" p={6} borderRadius="lg" borderWidth="1px">
              <HStack mb={4}>
                <Box
                  w={3}
                  h={3}
                  borderRadius="full"
                  bg={isConnected ? "green.500" : "red.500"}
                />
                <Heading size="md">Connection</Heading>
              </HStack>
              <VStack gap={4}>
                <Box w="full">
                  <Text mb={2} fontWeight="medium">
                    WebSocket URL
                  </Text>
                  <Input
                    value={wsUrl}
                    onChange={(e) => setWsUrl(e.target.value)}
                    placeholder="ws://localhost:8000/api/v1/ws"
                  />
                </Box>

                <Box w="full">
                  <Text mb={2} fontWeight="medium">
                    Access Token
                  </Text>
                  <Input
                    type="password"
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    placeholder="Enter your JWT token"
                  />
                </Box>

                <HStack w="full" gap={4}>
                  <Button
                    colorPalette="purple"
                    onClick={handleConnect}
                    disabled={isConnected}
                    flex={1}
                  >
                    Connect
                  </Button>
                  <Button
                    colorPalette="red"
                    onClick={handleDisconnect}
                    disabled={!isConnected}
                    flex={1}
                  >
                    Disconnect
                  </Button>
                </HStack>
              </VStack>
            </Box>

            {/* Login Helper */}
            <Box bg="bg.panel" p={6} borderRadius="lg" borderWidth="1px">
              <Heading size="md" mb={4}>
                🔑 Quick Login
              </Heading>
              <VStack gap={4}>
                <Box p={4} bg="blue.50" borderRadius="md" w="full">
                  <Text fontWeight="bold" mb={2} color="blue.800">
                    Get Access Token
                  </Text>
                  <Text fontSize="sm" color="blue.700" mb={2}>
                    Login to get your access token:
                  </Text>
                  <Code
                    p={2}
                    w="full"
                    fontSize="xs"
                    display="block"
                    whiteSpace="pre-wrap"
                  >
                    curl -X POST
                    "http://localhost:8000/api/v1/login/access-token" \{"\n"}
                    {"  "}-d "username=admin@example.com&password=changethis"
                  </Code>
                </Box>

                <Box w="full">
                  <Text mb={2} fontWeight="medium">
                    Email
                  </Text>
                  <Input
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                  />
                </Box>

                <Box w="full">
                  <Text mb={2} fontWeight="medium">
                    Password
                  </Text>
                  <Input
                    type="password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                  />
                </Box>

                <Button colorPalette="green" onClick={handleLogin} w="full">
                  Login & Get Token
                </Button>
              </VStack>
            </Box>

            {/* Actions Tabs */}
            <Box bg="bg.panel" p={6} borderRadius="lg" borderWidth="1px">
              <Tabs.Root defaultValue="rooms">
                <Tabs.List>
                  <Tabs.Trigger value="rooms">Rooms</Tabs.Trigger>
                  <Tabs.Trigger value="messages">Messages</Tabs.Trigger>
                  <Tabs.Trigger value="raw">Raw JSON</Tabs.Trigger>
                </Tabs.List>

                <Tabs.Content value="rooms" pt={4}>
                  <VStack gap={4}>
                    <Box w="full">
                      <Text mb={2} fontWeight="medium">
                        Room Name
                      </Text>
                      <Input
                        value={roomName}
                        onChange={(e) => setRoomName(e.target.value)}
                        placeholder="Enter room name"
                      />
                    </Box>

                    <Grid templateColumns="1fr 1fr" gap={2} w="full">
                      <Button
                        colorPalette="green"
                        onClick={createRoom}
                        size="sm"
                      >
                        Create Room
                      </Button>
                      <Button colorPalette="blue" onClick={joinRoom} size="sm">
                        Join Room
                      </Button>
                      <Button colorPalette="gray" onClick={leaveRoom} size="sm">
                        Leave Room
                      </Button>
                      <Button colorPalette="red" onClick={closeRoom} size="sm">
                        Close Room
                      </Button>
                    </Grid>

                    <Button colorPalette="purple" onClick={listRooms} w="full">
                      Refresh Rooms List
                    </Button>

                    {currentRoom && (
                      <Box w="full">
                        <Text color="green.500" fontWeight="bold">
                          Current Room:{" "}
                          <Badge colorPalette="green" fontSize="md">
                            {currentRoom}
                          </Badge>
                        </Text>
                      </Box>
                    )}
                  </VStack>
                </Tabs.Content>

                <Tabs.Content value="messages" pt={4}>
                  <VStack gap={4}>
                    <Box w="full">
                      <Text mb={2} fontWeight="medium">
                        Message Content
                      </Text>
                      <Textarea
                        value={messageContent}
                        onChange={(e) => setMessageContent(e.target.value)}
                        placeholder="Type your message..."
                        rows={4}
                      />
                    </Box>

                    <Button
                      colorPalette="purple"
                      onClick={sendMessage}
                      w="full"
                    >
                      Send Message
                    </Button>

                    <Separator />

                    <Text fontWeight="bold" alignSelf="start">
                      Quick Messages:
                    </Text>
                    <Grid templateColumns="1fr 1fr" gap={2} w="full">
                      <Button
                        size="sm"
                        onClick={() => sendQuickMessage("halo")}
                      >
                        Send "halo"
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => sendQuickMessage("nama")}
                      >
                        Send "nama"
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => sendQuickMessage("test vowels")}
                        gridColumn="span 2"
                      >
                        Test Bot
                      </Button>
                    </Grid>
                  </VStack>
                </Tabs.Content>

                <Tabs.Content value="raw" pt={4}>
                  <VStack gap={4}>
                    <Box w="full">
                      <Text mb={2} fontWeight="medium">
                        Raw JSON Message
                      </Text>
                      <Textarea
                        value={rawJson}
                        onChange={(e) => setRawJson(e.target.value)}
                        placeholder='{"type": "message", "content": "Hello"}'
                        fontFamily="mono"
                        rows={6}
                      />
                    </Box>

                    <Button
                      colorPalette="purple"
                      onClick={sendRawJsonMessage}
                      w="full"
                    >
                      Send Raw JSON
                    </Button>

                    <Box p={4} bg="blue.50" borderRadius="md" w="full">
                      <Text fontWeight="bold" mb={2} color="blue.800">
                        Example Messages:
                      </Text>
                      <VStack align="stretch" gap={2}>
                        <Code fontSize="xs" p={2}>
                          {`{"type": "create_room", "room_name": "test"}`}
                        </Code>
                        <Code fontSize="xs" p={2}>
                          {`{"type": "join_room", "room_name": "test"}`}
                        </Code>
                        <Code fontSize="xs" p={2}>
                          {`{"type": "message", "content": "Hello!"}`}
                        </Code>
                        <Code fontSize="xs" p={2}>
                          {`{"type": "list_rooms"}`}
                        </Code>
                      </VStack>
                    </Box>
                  </VStack>
                </Tabs.Content>
              </Tabs.Root>
            </Box>

            {/* Statistics */}
            <Grid templateColumns="repeat(3, 1fr)" gap={4}>
              <Box
                bg="bg.panel"
                p={4}
                borderRadius="lg"
                borderWidth="1px"
                textAlign="center"
              >
                <Text fontSize="3xl" fontWeight="bold" color="purple.500">
                  {sentCount}
                </Text>
                <Text fontSize="sm" color="fg.muted">
                  Sent
                </Text>
              </Box>
              <Box
                bg="bg.panel"
                p={4}
                borderRadius="lg"
                borderWidth="1px"
                textAlign="center"
              >
                <Text fontSize="3xl" fontWeight="bold" color="green.500">
                  {receivedCount}
                </Text>
                <Text fontSize="sm" color="fg.muted">
                  Received
                </Text>
              </Box>
              <Box
                bg="bg.panel"
                p={4}
                borderRadius="lg"
                borderWidth="1px"
                textAlign="center"
              >
                <Text fontSize="3xl" fontWeight="bold" color="red.500">
                  {errorCount}
                </Text>
                <Text fontSize="sm" color="fg.muted">
                  Errors
                </Text>
              </Box>
            </Grid>
          </VStack>

          {/* Right Panel: Messages */}
          <VStack gap={6} align="stretch">
            <Box bg="bg.panel" p={6} borderRadius="lg" borderWidth="1px">
              <HStack justify="space-between" mb={4}>
                <Heading size="md">📨 Messages Log</Heading>
                <Button size="sm" colorPalette="red" onClick={clearMessages}>
                  Clear Messages
                </Button>
              </HStack>
              <Box
                bg="bg.subtle"
                borderRadius="md"
                p={4}
                maxH="700px"
                overflowY="auto"
                borderWidth="1px"
              >
                <VStack gap={3} align="stretch">
                  {messages.map((msg, index) => (
                    <Box
                      key={index}
                      p={3}
                      borderRadius="md"
                      borderLeftWidth="4px"
                      borderLeftColor={`${getMessageColor(msg.type)}.500`}
                      bg={`${getMessageColor(msg.type)}.subtle`}
                    >
                      <HStack justify="space-between" mb={1}>
                        <Badge colorPalette={getMessageColor(msg.type)}>
                          {msg.type.toUpperCase()}
                        </Badge>
                        <Text fontSize="xs" color="fg.muted">
                          {msg.timestamp.toLocaleTimeString()}
                        </Text>
                      </HStack>
                      <Text
                        fontSize="sm"
                        fontFamily={
                          msg.content.startsWith("→") ? "mono" : "inherit"
                        }
                        whiteSpace="pre-wrap"
                      >
                        {msg.content}
                      </Text>
                    </Box>
                  ))}
                  <div ref={messagesEndRef} />
                </VStack>
              </Box>
            </Box>
          </VStack>
        </Grid>

        <Box textAlign="center" py={4} color="fg.muted">
          <Text fontSize="sm">
            WebSocket Playground v1.0 | Full Stack FastAPI Template | Made with
            ❤️ for Testing
          </Text>
        </Box>
      </VStack>
    </Container>
  )
}
