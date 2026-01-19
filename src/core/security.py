from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import uuid
import bcrypt
from core.config import settings

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
    def create_access_token(cls, data) -> str:
        return cls._create_token(
            token_type=ACCESS_TOKEN,
            payload={"sub": str(data["id"])},
            expire_days=settings.jwt.access_expire_day,
        )

    @classmethod
    def create_refresh_token(cls, data) -> str:
        return cls._create_token(
            token_type=REFRESH_TOKEN,
            payload={"sub": str(data["id"])},
            expire_days=settings.jwt.refresh_expire_day,
        )
