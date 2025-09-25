# FastAPI app configuration
import os

class Config:
    # API settings
    API_TITLE = "Metamorph - Schema Converter"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "API for converting Medical Record Schema to another format"
    
    # server settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # DNPM-DIP API settings
    DNPM_API_URL = os.getenv(
        "DNPM_API_URL", 
        "https://preview.dnpm-dip.net/api/rd/etl/patient-record:validate"
    )
    
    # cors settings
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]

config = Config()