from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.websocket_service import WebSocketService

router = APIRouter()
websocket_service = WebSocketService()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_service.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_service.handle_message(websocket, data)
    except WebSocketDisconnect:
        websocket_service.disconnect(websocket)