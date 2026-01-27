from schemas.base_schemas import BaseSchema
from pydantic import Field, EmailStr
from typing import Annotated
from datetime import datetime


class LoginSchema(BaseSchema):
    email: Annotated[EmailStr, Field(description="Email address")]
    password: Annotated[str, Field(description="Password")]


class TokenSchema(BaseSchema):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class CreateRefreshTokenSchema(BaseSchema):
    user_id: int
    token_hash: str
    expires_at: datetime
