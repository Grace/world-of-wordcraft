from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Base project directory (where web folder lives)
    BASE_DIR = Path(__file__).parent.parent.parent
    
    # Web directory at project root level
    WEB_DIR = BASE_DIR / "web/built"
    
    ENV = os.getenv('ENVIRONMENT', 'development')
    HOST = "0.0.0.0"
    PORT = 5001
    ALLOWED_ORIGINS = (
        ["http://localhost:5001"] if ENV == 'development'
        else ["https://world-of-wordcraft.up.railway.app"]
    )
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def validate_paths(cls):
        """Ensure required paths exist"""
        if not cls.WEB_DIR.exists():
            raise FileNotFoundError(
                f"Web directory not found at {cls.WEB_DIR}. "
                "Please create the directory and add required files."
            )
        if not (cls.WEB_DIR / "index.html").exists():
            raise FileNotFoundError(
                f"index.html not found in {cls.WEB_DIR}"
            )