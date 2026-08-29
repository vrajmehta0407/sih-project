"""
endpoints/websockets.py
=======================
Stage 12 — Real-Time WebSocket Alerts & Operations Stream for Legal Metrology HQ
"""

import json
import logging
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections from Enforcement HQ dashboards."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket client connected. Active connections: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("WebSocket client disconnected. Active connections: %d", len(self.active_connections))

    async def broadcast(self, message: dict):
        """Broadcasts structured event message to all connected clients."""
        payload = json.dumps(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning("Failed to send WebSocket message to a client: %s", str(e))
                self.disconnect(connection)


ws_manager = ConnectionManager()


@router.websocket("/inspections")
async def websocket_inspections_endpoint(websocket: WebSocket):
    """
    WebSocket channel for streaming live field inspection dockets and critical violation alarms.
    """
    await ws_manager.connect(websocket)
    try:
        # Send initial connection handshake
        await websocket.send_json({
            "event": "CONNECTION_ESTABLISHED",
            "message": "Connected to Legal Metrology Real-Time Operations Stream.",
            "protocol_version": "1.0",
        })
        while True:
            # Keep connection alive and listen for client pings/filter changes
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("action") == "PING":
                    await websocket.send_json({"event": "PONG"})
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket stream error: %s", str(e))
        ws_manager.disconnect(websocket)
