from schemas.user_schemas import UpdateUserPassSchema
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator, Annotated
from core import settings, Security
from fastapi import Depends, Form
from infrastructure import (
    PasswordResetTokenRepository,
    TokenRepository,
    UserRepository,
    RefreshToken,
    db_helper,
    broker,
    User,
)
from schemas import auth_schemas
from core import exceptions
import uuid


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
        user_data: Annotated[auth_schemas.LoginSchema, Form()],
    ) -> User:
        if not (user := await self._user_repo.find_single(email=user_data.email)):
            raise exceptions.unauthorized_exc_incorrect()

        if not Security.verify_password(
            user_data.password,
            str(user.hashed_password),
        ):
            raise exceptions.unauthorized_exc_incorrect()

        if not user.is_active:
            raise exceptions.forbidden_exc_inactive()

        return user

    async def login_user(self, user_data: User) -> auth_schemas.TokenSchema:
        refresh_token_jti = str(uuid.uuid4())
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.jwt.refresh_expire_day
        )

        access_token = Security.create_access_token(data=user_data)
        refresh_token = Security.create_refresh_token(
            data=user_data, jti=refresh_token_jti, refresh_exp=expire
        )

        await self._token_repo.create(
            auth_schemas.CreateRefreshTokenSchema(
                user_id=user_data.id,
                jti=refresh_token_jti,
                expires_at=datetime.now(timezone.utc)
                + timedelta(days=settings.jwt.refresh_expire_day),
            )
        )

        return auth_schemas.TokenSchema(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def logout_user(self, user_id: int, refresh_token: str) -> None:

        payload = Security.decode_token(token=refresh_token)

        token = await self.get_token(user_id=user_id, jti=payload["jti"])

        # delete token for a specific session
        await self._token_repo.delete(id=token.id)

    async def update_refresh_token(
        self, user_data: User, jti: str
    ) -> auth_schemas.TokenSchema:
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
            raise exceptions.unauthorized_exc_inactive_token()

        if token.expires_at < datetime.now(timezone.utc):
            await self._token_repo.delete(id=token.id)
            raise exceptions.unauthorized_exc_inactive_token()
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
            auth_schemas.CreateResetPasswordTokenSchema(
                user_id=user.id,
                lookup_hash=lookup_hash,
                hashed_token=hashed_token,
                expires_at=expire_at,
            )
        )

        await broker.publish(
            auth_schemas.ResetPasswordEmailPayloadBroker(
                email=user.email,
                token=raw_token,
            ),
            queue="password-reset-request",
        )

    async def reset_password(
        self, data: auth_schemas.ResetPasswordConfirmSchema
    ) -> None:
        lookup_hash = Security.hash_token_sha256(token=data.token)

        reset_token = await self._reset_token_repo.find_single(lookup_hash=lookup_hash)

        if not reset_token:
            raise exceptions.unauthorized_exc_inactive_token()

        if reset_token.expires_at < datetime.now(timezone.utc):
            await self._reset_token_repo.delete(id=reset_token.id)
            raise exceptions.unauthorized_exc_inactive_token()

        if not Security.verify_password(data.token, reset_token.hashed_token):
            raise exceptions.unauthorized_exc_incorrect()

        if not (user := await self._user_repo.find_single(id=reset_token.user_id)):
            raise exceptions.unauthorized_exc_inactive_token()

        await self._reset_token_repo.delete(id=reset_token.id)
        await self.update_user_password(user_id=user.id, new_password=data.new_password)

    async def change_password(
        self, data: auth_schemas.ChangePasswordSchema, user: User
    ) -> None:
        if not Security.verify_password(data.old_password, user.hashed_password):
            raise exceptions.incorrect_old_password()

        await self.update_user_password(user_id=user.id, new_password=data.new_password)

        # full logout user
        await self._token_repo.delete(user_id=user.id)

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
    user_data: Annotated[auth_schemas.LoginSchema, Form()],
    auth_service: Annotated["AuthService", Depends(get_auth_service)],
):
    return await auth_service.authenticate_user(user_data=user_data)
