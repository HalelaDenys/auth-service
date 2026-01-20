from infrastructure import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy import VARCHAR, Enum as SQLEnum
from enum import StrEnum


class UserRole(StrEnum):
    user = "user"
    admin = "admin"


class User(Base):
    first_name: Mapped[str] = mapped_column(VARCHAR(50))
    last_name: Mapped[str] = mapped_column(VARCHAR(50), nullable=True)

    email: Mapped[str] = mapped_column(
        VARCHAR(100), unique=True, index=True, nullable=False
    )
    phone_number: Mapped[str] = mapped_column(VARCHAR(15), nullable=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role", create_type=True),
        nullable=False,
        default=UserRole.user,
        server_default=UserRole.user.value,  # беремо .value для правильного SQL
    )

    is_active: Mapped[bool] = mapped_column(
        default=True, server_default="true", nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        default=False, server_default="false", nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id}, is_active={self.is_active}, "
            f"first_name={self.first_name}, phone_number={self.phone_number}, "
            f"email={self.email}, is_verified={self.is_verified}, )"
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "role": self.role.value,
        }
