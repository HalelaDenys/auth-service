from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING
from jose import jwt, JWTError
from core import settings
import secrets
import bcrypt
import uuid

if TYPE_CHECKING:
    from infrastructure import User

ACCESS_TOKEN = "access"
REFRESH_TOKEN = "refresh"


class Security:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(
                token,
                settings.jwt.secret_key,
                algorithms=[settings.jwt.algorithm],
            )
        except JWTError:
            raise ValueError("Invalid or expired token")

    @staticmethod
    def _create_token(
        token_type: str,
        payload: dict,
        secret_key: str = settings.jwt.secret_key,
        expire_days: int = settings.jwt.access_expire_day,
        expire_timedelta: timedelta | None = None,
    ) -> str:
        to_encode = payload.copy()
        now = datetime.now(timezone.utc)

        if expire_timedelta:
            expire = now + expire_timedelta
        else:
            expire = now + timedelta(days=expire_days)

        to_encode.update(type=token_type, exp=expire, iat=now, jti=str(uuid.uuid4()))

        return jwt.encode(to_encode, secret_key, algorithm=settings.jwt.algorithm)

    @classmethod
    def create_access_token(cls, data: "User") -> str:
        return cls._create_token(
            token_type=ACCESS_TOKEN,
            payload={"sub": str(data.id)},
            expire_days=settings.jwt.access_expire_day,
        )

    @staticmethod
    def create_refresh_token() -> str:
        return secrets.token_urlsafe(48)

    @classmethod
    def hash_refresh_token(cls, token: str) -> str:
        return cls.hash_password(token)

    @classmethod
    def verify_refresh_token(cls, token: str, token_hash: str) -> bool:
        return cls.verify_password(token, token_hash)
