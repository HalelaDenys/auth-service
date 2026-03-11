from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseReadSchema(BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class TokenTypeEnum(StrEnum):
    reset_password = "reset_password"
    verify_email = "verify_email"


class UserRole(StrEnum):
    user = "user"
    admin = "admin"
