from schemas.base_schemas import BaseSchema, TokenTypeEnum
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


class ResetPasswordRequestSchema(BaseSchema):
    email: Annotated[EmailStr, Field(max_length=150, description="Email address")]


class NewPasswordSchema(BaseSchema):
    new_password: Annotated[str, Field(max_length=150, description="New password")]


class ResetPasswordConfirmSchema(NewPasswordSchema):
    token: str


class ChangePasswordSchema(NewPasswordSchema):
    old_password: Annotated[str, Field(max_length=150, description="Old password")]


class ResetPasswordEmailPayloadBroker(BaseSchema):
    email: EmailStr | str
    token: str


class VerifyEmailToken(BaseSchema):
    token: str
