from services.base_service import BaseService
from infrastructure import UserRepository, db_helper, User
from typing import AsyncGenerator
from schemas.user_schemas import RegisterUserSchema, CreateUserSchema
from core.exceptions import NotFoundError, AlreadyExistsError
from core.security.security import Security


class UserService(BaseService):
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    async def add(self, user_data: RegisterUserSchema) -> User:
        if await self._user_repo.find_single(email=user_data.email):
            raise AlreadyExistsError("User already exists")

        new_user = CreateUserSchema(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            phone_number=user_data.phone_number,
            role=user_data.role.value,
            hashed_password=Security.hash_password(user_data.password),
        )
        return await self._user_repo.create(data=new_user)

    async def update(self, **kwargs):
        pass

    async def delete(self, **kwargs):
        pass

    async def get(self, **kwargs) -> User:
        if not (user := await self._user_repo.find_single(**kwargs)):
            raise NotFoundError("User not found")
        return user

    async def get_all(self, **kwargs):
        pass


async def get_user_service() -> AsyncGenerator[UserService, None]:
    async with db_helper.get_session() as session:
        user_repo = UserRepository(session)
        yield UserService(user_repo)
