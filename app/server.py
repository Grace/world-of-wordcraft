import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import APIKeyCookie
from pathlib import Path
import hashlib
from datetime import datetime, timedelta, timezone
import re
from typing import Dict
from collections import defaultdict
import html
from dotenv import load_dotenv
import jwt
import json
import logging
from .modules.network.websocket_manager import WebSocketManager
from .config import Settings
from .logging_config import setup_logging

logger = setup_logging()

class GameServer:
    def __init__(self):
        self.app = FastAPI()
        self.websocket_manager = WebSocketManager()
        self._setup_middleware()
        self._setup_routes()
    
    def _setup_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=Settings.ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        @self.app.get("/")
        async def index():
            return FileResponse(Settings.WEB_DIR / "index.html")

        @self.app.get("/{filename}")
        async def static_files(filename: str):
            file_path = Settings.WEB_DIR / filename
            if file_path.exists():
                return FileResponse(file_path)
            return {"error": "File not found"}, 404

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            client_id = await self.websocket_manager.connect(websocket)
            logger.info(f"New websocket connection: {client_id}")
            
            try:
                while True:
                    message = await websocket.receive_text()
                    logger.debug(f"Received message from {client_id}: {message}")
                    response = await self.websocket_manager.handle_message(websocket, message)
                    await websocket.send_json(response.to_dict())
            except Exception as e:
                logger.error(f"WebSocket error for {client_id}: {str(e)}", exc_info=True)
            finally:
                await self.websocket_manager.disconnect(websocket)

    @staticmethod
    def start():
        import uvicorn
        logger.info(f"Starting server on http://{Settings.HOST}:{Settings.PORT}")
        server = GameServer()
        uvicorn.run(server.app, host=Settings.HOST, port=Settings.PORT)

if __name__ == "__main__":
    GameServer.start()
