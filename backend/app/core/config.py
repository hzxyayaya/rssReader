import os
from dotenv import load_dotenv

load_dotenv() # Load variables from .env if present

class Settings:
    PROJECT_NAME = "Intelligent RSS Reader"
    
    # Database
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:54321/rss_reader")
    
    # Milvus
    MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-it")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

settings = Settings()
