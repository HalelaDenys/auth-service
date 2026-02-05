from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure import PasswordResetToken
from infrastructure.repo.base_sqlalchemy_repo import BaseSqlalchemyRepo


class PasswordResetTokenRepository(BaseSqlalchemyRepo[PasswordResetToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(PasswordResetToken, session)
