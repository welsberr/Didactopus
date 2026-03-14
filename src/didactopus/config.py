from pathlib import Path
from pydantic import BaseModel

class Settings(BaseModel):
    database_url: str = "sqlite:///./didactopus.db"
    host: str = "127.0.0.1"
    port: int = 8011

def load_settings() -> Settings:
    return Settings()
