from enum import StrEnum

from schemas.base_schemas import BaseSchema, BaseReadSchema
import re
from pydantic import Field, field_validator, EmailStr
from typing import Annotated, Optional


class UserRole(StrEnum):
    user = "user"
    admin = "admin"


class RegisterUserSchema(BaseSchema):
    first_name: Annotated[
        str, Field(max_length=50, min_length=3, description="First name")
    ]
    last_name: Annotated[
        Optional[str], Field(max_length=50, min_length=3, description="First name")
    ] = None
    email: Annotated[
        EmailStr, Field(max_length=50, min_length=7, description="Email address")
    ]
    phone_number: Annotated[
        Optional[str], Field(max_length=15, min_length=7, description="Phone number")
    ] = None

    role: Annotated[
        Optional[UserRole],
        Field(description="Role"),
    ] = UserRole.user

    password: Annotated[str, Field(max_length=50, min_length=3, description="Password")]

    @field_validator("phone_number")
    def validate_phone_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        value = value.strip().replace(" ", "")

        if not re.fullmatch(r"\+\d{5,15}", value):
            raise ValueError("Phone number must be entered in the format: +999999999")
        return value


class ReadUserSchema(BaseReadSchema):
    first_name: str
    last_name: str | None
    email: EmailStr | str
    phone_number: str | None
    role: UserRole | str


class CreateUserSchema(BaseSchema):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr | str
    phone_number: Optional[str] = None
    role: Optional[UserRole | str] = (UserRole.user,)
    hashed_password: str
