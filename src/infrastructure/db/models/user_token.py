from infrastructure import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, TIMESTAMP, Enum as SQLEnum
from datetime import datetime

from typing import TYPE_CHECKING

from schemas.base_schemas import TokenTypeEnum

if TYPE_CHECKING:
    from infrastructure import User


class UserToken(Base):

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    lookup_hash: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_token: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    token_type: Mapped[TokenTypeEnum] = mapped_column(
        SQLEnum(TokenTypeEnum, native_enum=False), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="tokens")

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id}, user_id={self.user_id},"
            f"expires_at={self.expires_at}), token_type={self.token_type}"
        )
