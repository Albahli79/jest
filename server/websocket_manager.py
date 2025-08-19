from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Map of username -> set of WebSocket connections
connections: Dict[str, Set[WebSocket]] = {}


async def ws_send(username: str, message: dict) -> None:
    if username in connections:
        to_send = list(connections[username])
        for conn in to_send:
            try:
                await conn.send_json(message)
            except Exception:
                pass


@router.websocket("/notify/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str) -> None:
    await websocket.accept()
    if username not in connections:
        connections[username] = set()
    connections[username].add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections[username].remove(websocket)
        if not connections[username]:
            del connections[username]