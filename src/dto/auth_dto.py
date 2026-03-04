from dataclasses import dataclass
from datetime import datetime
from schemas.base_schemas import TokenTypeEnum


@dataclass(slots=True)
class UserTokenDTO:
    raw_token: str
    lookup_hash: str
    hashed_token: str
    expires_at: datetime


@dataclass(slots=True)
class CreateTokenDTO:
    user_id: int
    expires_at: datetime


@dataclass(slots=True)
class CreateRefreshTokenDTO(CreateTokenDTO):
    jti: str


@dataclass(slots=True)
class CreateUserTokenDTO(CreateTokenDTO):
    lookup_hash: str
    hashed_token: str
    token_type: TokenTypeEnum
