import uuid

from infrastructure import TokenRepository, db_helper, UserRepository, User
from typing import AsyncGenerator, Annotated
from fastapi import Depends, Form
from schemas.auth_schemas import LoginSchema, TokenSchema, CreateRefreshTokenSchema
from core.exceptions import (
    UNAUTHORIZED_EXC_INCORRECT,
    FORBIDDEN_EXC_INACTIVE,
    UNAUTHORIZED_EXC_INVALID_TOKEN,
)
from datetime import datetime, timedelta, timezone
from core import settings, Security


class AuthService:
    def __init__(self, refresh_token_repo: TokenRepository, user_repo: UserRepository):
        self._token_repo: TokenRepository = refresh_token_repo
        self._user_repo: UserRepository = user_repo

    async def authenticate_user(
        self,
        user_data: Annotated[LoginSchema, Form()],
    ) -> User:
        if not (user := await self._user_repo.find_single(email=user_data.email)):
            raise UNAUTHORIZED_EXC_INCORRECT

        if not Security.verify_password(
            user_data.password,
            str(user.hashed_password),
        ):
            raise UNAUTHORIZED_EXC_INCORRECT

        if not user.is_active:
            raise FORBIDDEN_EXC_INACTIVE

        return user

    async def login_user(self, user_data: User) -> TokenSchema:
        refresh_token_jti = str(uuid.uuid4())
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.jwt.refresh_expire_day
        )

        access_token = Security.create_access_token(data=user_data)
        refresh_token = Security.create_refresh_token(
            data=user_data, jti=refresh_token_jti, refresh_exp=expire
        )

        await self._token_repo.create(
            CreateRefreshTokenSchema(
                user_id=user_data.id,
                jti=refresh_token_jti,
                expires_at=datetime.now(timezone.utc)
                + timedelta(days=settings.jwt.refresh_expire_day),
            )
        )

        return TokenSchema(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def logout_user(self, user_id: int, refresh_token: str) -> None:

        payload = Security.decode_token(token=refresh_token)

        if not (
            token := await self._token_repo.find_single(
                user_id=user_id,
                jti=payload["jti"],
            )
        ):
            raise UNAUTHORIZED_EXC_INVALID_TOKEN

        await self._token_repo.delete(id=token.id)


async def get_auth_service() -> AsyncGenerator[AuthService, None]:
    async with db_helper.get_session() as session:
        token_repo = TokenRepository(session)
        user_repo = UserRepository(session)
        yield AuthService(
            refresh_token_repo=token_repo,
            user_repo=user_repo,
        )


async def authenticate_user_dependency(
    user_data: Annotated[LoginSchema, Form()],
    auth_service: Annotated["AuthService", Depends(get_auth_service)],
):
    return await auth_service.authenticate_user(user_data=user_data)
