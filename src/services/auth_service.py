import uuid
from infrastructure import (
    TokenRepository,
    db_helper,
    UserRepository,
    User,
    RefreshToken,
    PasswordResetTokenRepository,
)
from schemas.auth_schemas import (
    LoginSchema,
    TokenSchema,
    CreateRefreshTokenSchema,
    CreateResetPasswordTokenSchema,
    ResetPasswordConfirmSchema,
)
from core.exceptions import (
    UNAUTHORIZED_EXC_INCORRECT,
    FORBIDDEN_EXC_INACTIVE,
    UNAUTHORIZED_EXC_INVALID_TOKEN,
)
from schemas.user_schemas import UpdateUserPassSchema
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator, Annotated
from core import settings, Security
from fastapi import Depends, Form


class AuthService:
    def __init__(
        self,
        refresh_token_repo: TokenRepository,
        user_repo: UserRepository,
        reset_token_repo: PasswordResetTokenRepository,
    ):
        self._token_repo: TokenRepository = refresh_token_repo
        self._user_repo: UserRepository = user_repo
        self._reset_token_repo: PasswordResetTokenRepository = reset_token_repo

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

        token = await self.get_token(user_id=user_id, jti=payload["jti"])

        await self._token_repo.delete(id=token.id)

    async def update_refresh_token(self, user_data: User, jti: str) -> TokenSchema:
        token = await self.get_token(user_id=user_data.id, jti=jti)

        await self._token_repo.delete(id=token.id)

        return await self.login_user(user_data=user_data)

    async def get_token(self, user_id: int, jti: str) -> RefreshToken:
        if not (
            token := await self._token_repo.find_single(
                user_id=user_id,
                jti=jti,
            )
        ):
            raise UNAUTHORIZED_EXC_INVALID_TOKEN

        if token.expires_at < datetime.now(timezone.utc):
            await self._token_repo.delete(id=token.id)
            raise UNAUTHORIZED_EXC_INVALID_TOKEN
        return token

    async def create_reset_token(self, email: str) -> None:
        if not (user := await self._user_repo.find_single(email=email)):
            return

        raw_token = Security.generate_reset_token()

        lookup_hash = Security.hash_token_sha256(token=raw_token)
        hashed_token = Security.hash_password(raw_token)
        expire_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt.reset_token_expire_minute
        )

        await self._reset_token_repo.create(
            CreateResetPasswordTokenSchema(
                user_id=user.id,
                lookup_hash=lookup_hash,
                hashed_token=hashed_token,
                expires_at=expire_at,
            )
        )

        # TODO notification to the user's email address
        # await send_email_reset_pass(token=raw_token, email=user.email)

    async def reset_password(self, data: ResetPasswordConfirmSchema) -> None:
        lookup_hash = Security.hash_token_sha256(token=data.token)

        reset_token = await self._reset_token_repo.find_single(lookup_hash=lookup_hash)

        if not reset_token:
            raise UNAUTHORIZED_EXC_INVALID_TOKEN

        if reset_token.expires_at < datetime.now(timezone.utc):
            await self._reset_token_repo.delete(id=reset_token.id)
            raise UNAUTHORIZED_EXC_INVALID_TOKEN

        if not Security.verify_password(data.token, reset_token.hashed_token):
            raise UNAUTHORIZED_EXC_INCORRECT

        if not (user := await self._user_repo.find_single(id=reset_token.user_id)):
            raise UNAUTHORIZED_EXC_INVALID_TOKEN

        await self._reset_token_repo.delete(id=reset_token.id)
        await self.update_user_password(user_id=user.id, new_password=data.new_password)

    async def update_user_password(self, user_id: int, new_password: str) -> None:
        new_hashed_password = Security.hash_password(password=new_password)
        await self._user_repo.update(
            UpdateUserPassSchema(
                hashed_password=new_hashed_password,
            ),
            id=user_id,
        )


async def get_auth_service() -> AsyncGenerator[AuthService, None]:
    async with db_helper.get_session() as session:
        token_repo = TokenRepository(session)
        user_repo = UserRepository(session)
        reset_token = PasswordResetTokenRepository(session)
        yield AuthService(
            refresh_token_repo=token_repo,
            user_repo=user_repo,
            reset_token_repo=reset_token,
        )


async def authenticate_user_dependency(
    user_data: Annotated[LoginSchema, Form()],
    auth_service: Annotated["AuthService", Depends(get_auth_service)],
):
    return await auth_service.authenticate_user(user_data=user_data)
