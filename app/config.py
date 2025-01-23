from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ENV = os.getenv('ENVIRONMENT', 'development')
    WEB_DIR = Path(__file__).parent.parent / "web"
    HOST = "0.0.0.0"
    PORT = 5001
    ALLOWED_ORIGINS = (
        ["http://localhost:5001"] if ENV == 'development'
        else ["https://world-of-wordcraft.up.railway.app"]
    )
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'