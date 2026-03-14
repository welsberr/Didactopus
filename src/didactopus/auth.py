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
    return _encode_token({"sub": str(user_id), "username": username, "role": role, "kind": "access"}, timedelta(minutes=30))

def issue_refresh_token(user_id: int, username: str, role: str, token_id: str) -> str:
    return _encode_token({"sub": str(user_id), "username": username, "role": role, "kind": "refresh", "jti": token_id}, timedelta(days=14))

def issue_service_access_token(service_account_id: int, name: str, scopes: list[str]) -> str:
    return _encode_token({"sub": str(service_account_id), "service_account_name": name, "kind": "service", "scopes": scopes}, timedelta(hours=8))

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None

def new_token_id() -> str:
    return secrets.token_urlsafe(24)

def new_secret() -> str:
    return secrets.token_urlsafe(24)
