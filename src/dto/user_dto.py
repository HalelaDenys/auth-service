from dataclasses import dataclass
from typing import Optional

from schemas.base_schemas import UserRole


@dataclass(slots=True, frozen=True)
class CreateUserDTO:
    first_name: str
    email: str
    hashed_password: str
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: UserRole | str = UserRole.user


@dataclass(slots=True)
class UpdateUserPassDTO:
    hashed_password: str
