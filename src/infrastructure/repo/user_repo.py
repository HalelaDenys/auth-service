from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure import User
from infrastructure.repo.base_sqlalchemy_repo import BaseSqlalchemyRepo


class UserRepository(BaseSqlalchemyRepo[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
