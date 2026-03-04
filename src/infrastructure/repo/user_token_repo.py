from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure import UserToken
from infrastructure.repo.base_sqlalchemy_repo import BaseSqlalchemyRepo
from sqlalchemy import delete, func


class UserTokenRepository(BaseSqlalchemyRepo[UserToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserToken, session)

    async def delete_expired_tokens(self):
        await self._session.execute(
            delete(self._model).where(self._model.expires_at < func.now())
        )
        await self._session.flush()
