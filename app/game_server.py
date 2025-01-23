from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import hashlib
import re
import logging

from .modules.network.websocket_manager import WebSocketManager
from .config import Settings
from .logging_config import setup_logging
from .modules.database.sqlite_handler import SQLiteHandler
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db = SQLiteHandler()
    await db.init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    await db.close()

class GameServer:
    def __init__(self):
        self.app = FastAPI(lifespan=lifespan)
        self.websocket_manager = WebSocketManager()
        self.db = SQLiteHandler()
        self._setup_middleware()
        self._setup_routes()
    
    async def startup(self):
        """Initialize server components"""
        await self.db.init_db()
        logger.info("Database initialized")
    
    async def shutdown(self):
        """Cleanup resources"""
        await self.db.close()
    
    def _setup_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=Settings.ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
        )
        
        # Serve static files from app/static directory
        # self.app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")
    
    def _setup_routes(self):
        @self.app.get("/")
        async def serve_index():
            if not Settings.WEB_DIR.exists():
                logger.error(f"Web directory not found: {Settings.WEB_DIR}")
                return {"error": "Web directory not found"}, 404
            return FileResponse(Settings.WEB_DIR / "index.html")

        @self.app.get("/{filename}")
        async def serve_static(filename: str):
            file_path = Settings.WEB_DIR / filename
            if file_path.exists():
                return FileResponse(file_path)
            return FileResponse(Settings.WEB_DIR / "index.html")

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
                logger.error(f"WebSocket error for {client_id}: {str(e)}")
            finally:
                await self.websocket_manager.disconnect(websocket)

    @staticmethod
    def start():
        import uvicorn
        logger.info(f"Starting server on http://{Settings.HOST}:{Settings.PORT}")
        server = GameServer()
        uvicorn.run(
            server.app, 
            host=Settings.HOST, 
            port=Settings.PORT,
            log_level="info"
        )