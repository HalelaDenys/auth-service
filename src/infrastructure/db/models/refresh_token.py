from infrastructure import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import VARCHAR, ForeignKey, TIMESTAMP
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from infrastructure import User


class RefreshToken(Base):

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(VARCHAR(1000), unique=True)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id}, user_id={self.user_id},"
            f"expires_at={self.expires_at})"
        )
