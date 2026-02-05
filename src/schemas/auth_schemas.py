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


class CreateTokenSchema(BaseSchema):
    user_id: int
    expires_at: datetime


class CreateRefreshTokenSchema(CreateTokenSchema):
    jti: str


class CreateResetPasswordTokenSchema(CreateTokenSchema):
    lookup_hash: str
    hashed_token: str


class ResetPasswordRequestSchema(BaseSchema):
    email: Annotated[EmailStr, Field(max_length=150, description="Email address")]


class ResetPasswordConfirmSchema(BaseSchema):
    token: str
    new_password: Annotated[str, Field(max_length=150, description="New password")]
