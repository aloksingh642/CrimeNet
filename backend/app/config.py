from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    ENVIRONMENT: str = "demo"
    SECRET_KEY: str = "demo-secret-key-change-in-production-32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./crimenet.db")
    
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "crimenet123")
    
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    SYNTHETIC_SEED: int = 42
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

def get_cors_origins() -> List[str]:
    return [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
