from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from ..modules.network.websocket_manager import WebSocketManager
from ..config.settings import Settings
from ..config.logging_config import setup_logging
from ..modules.database.sqlite_handler import SQLiteHandler
from contextlib import asynccontextmanager
from typing import Optional
from starlette.staticfiles import StaticFiles

logger = setup_logging()

class GameServer:
    _instance: Optional['GameServer'] = None
    
    @classmethod
    def get_instance(cls) -> 'GameServer':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if GameServer._instance is not None:
            raise RuntimeError("Use GameServer.get_instance()")
            
        self.app = FastAPI()
        self.websocket_manager = WebSocketManager()
        self.db = SQLiteHandler()
        self._setup_app()

    def _setup_app(self):
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await self.db.init_db()
            logger.info("Database initialized")
            yield
            await self.db.close()

        self.app = FastAPI(lifespan=lifespan)
        self._setup_routes()
        self._setup_middleware()

    def _setup_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=Settings.ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
        )
        # Serve static files from app/static directory
        # self.app.mount("/built", StaticFiles(directory="web/built"), name="built")
    
    
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
        server = GameServer.get_instance()
        uvicorn.run(server.app, host=Settings.HOST, port=Settings.PORT)