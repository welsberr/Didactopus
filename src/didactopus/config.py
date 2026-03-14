from __future__ import annotations
import os
from pydantic import BaseModel

class Settings(BaseModel):
    database_url: str = os.getenv("DIDACTOPUS_DATABASE_URL", "sqlite+pysqlite:///:memory:")
    host: str = os.getenv("DIDACTOPUS_HOST", "127.0.0.1")
    port: int = int(os.getenv("DIDACTOPUS_PORT", "8011"))
    jwt_secret: str = os.getenv("DIDACTOPUS_JWT_SECRET", "change-me")
    jwt_algorithm: str = "HS256"
    deployment_policy_profile: str = os.getenv("DIDACTOPUS_POLICY_PROFILE", "single_user")

def load_settings() -> Settings:
    return Settings()
