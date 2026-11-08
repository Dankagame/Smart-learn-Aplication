from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any

import bcrypt
import jwt

from app.core.config import get_settings

BCRYPT_MAX_PASSWORD_BYTES = 72


class InvalidTokenError(Exception):
    pass


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    if len(password.encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


@lru_cache
def dummy_password_hash() -> str:
    return hash_password("timing-attack-protection")


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    issued_at = datetime.now(timezone.utc)
    payload = {
        **(extra_claims or {}),
        "sub": subject,
        "iat": issued_at,
        "exp": issued_at + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "iat", "exp"]},
        )
    except jwt.PyJWTError as error:
        raise InvalidTokenError from error
