from __future__ import annotations
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
import secrets
from .config import load_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = load_settings()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def _encode_token(payload: dict, expires_delta: timedelta) -> str:
    to_encode = dict(payload)
    to_encode["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def issue_access_token(user_id: int, username: str, role: str) -> str:
    return _encode_token({"sub": str(user_id), "username": username, "role": role, "kind": "access"}, timedelta(minutes=settings.access_token_minutes))

def issue_refresh_token(user_id: int, username: str, role: str, token_id: str) -> str:
    return _encode_token({"sub": str(user_id), "username": username, "role": role, "kind": "refresh", "jti": token_id}, timedelta(days=settings.refresh_token_days))

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None

def new_token_id() -> str:
    return secrets.token_urlsafe(24)
