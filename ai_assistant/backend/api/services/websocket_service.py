# backend/api/services/websocket_service.py

from fastapi import WebSocket
from typing import List
import json
from ...core.ai_integration import AIIntegration

class WebSocketService:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.ai_integration = AIIntegration()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def handle_message(self, websocket: WebSocket, data: str):
        message = json.loads(data)
        if message["type"] == "ai_request":
            response = await self.ai_integration.generate_response(message["content"])
            await self.send_message(json.dumps({"type": "ai_response", "content": response}), websocket)
        # Add more message type handlers as needed