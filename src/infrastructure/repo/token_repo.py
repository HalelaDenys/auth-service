from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure import RefreshToken
from infrastructure.repo.base_sqlalchemy_repo import BaseSqlalchemyRepo


class TokenRepository(BaseSqlalchemyRepo[RefreshToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)
