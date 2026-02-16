from fastapi import APIRouter, Depends, Body, status
from services.user_service import get_user_service, UserService
from services.auth_service import (
    authenticate_user_dependency,
    get_auth_service,
    AuthService,
)
from schemas.user_schemas import RegisterUserSchema, ReadUserSchema
from typing import Annotated
from infrastructure import User
from schemas.auth_schemas import (
    TokenSchema,
    ResetPasswordRequestSchema,
    ResetPasswordConfirmSchema,
    ChangePasswordSchema,
)
from core.security.authentication import (
    get_current_auth_user,
    get_current_auth_user_for_refresh,
    get_current_token_payload,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterUserSchema,
    user_service: Annotated["UserService", Depends(get_user_service)],
):
    user = await user_service.add(user_data)
    return ReadUserSchema(**user.to_dict())


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    user_data: Annotated["User", Depends(authenticate_user_dependency)],
    auth_service: Annotated["AuthService", Depends(get_auth_service)],
) -> TokenSchema:
    return await auth_service.login_user(user_data)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    refresh_token: Annotated[str, Body()],
    user: Annotated["User", Depends(get_current_auth_user)],
    auth_service: Annotated["AuthService", Depends(get_auth_service)],
) -> dict:
    await auth_service.logout_user(user_id=user.id, refresh_token=refresh_token)

    return {"detail": "Successfully logged out"}


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
)
async def refresh(
    current_user: Annotated["User", Depends(get_current_auth_user_for_refresh)],
    payload: Annotated[dict, Depends(get_current_token_payload)],
    auth_service: Annotated["AuthService", Depends(get_auth_service)],
) -> TokenSchema:

    return await auth_service.update_refresh_token(
        user_data=current_user, jti=payload["jti"]
    )


@router.post("/reset-password/request", status_code=status.HTTP_202_ACCEPTED)
async def request_reset_password(
    data: ResetPasswordRequestSchema,
    auth_service: Annotated["AuthService", Depends(get_auth_service)],
) -> None:
    await auth_service.create_reset_token(data.email)
    return


@router.post(
    "/reset-password/confirm",
    status_code=status.HTTP_202_ACCEPTED,
    name="reset_password_confirm",
)
async def reset_password(
    data: ResetPasswordConfirmSchema,
    auth_service: Annotated["AuthService", Depends(get_auth_service)],
) -> None:
    await auth_service.reset_password(data=data)
    return


@router.post(
    "/change_password",
    status_code=status.HTTP_202_ACCEPTED,
)
async def change_password(
    data: ChangePasswordSchema,
    user: Annotated["User", Depends(get_current_auth_user)],
    auth_service: Annotated["AuthService", Depends(get_auth_service)],
) -> None:
    await auth_service.change_password(user=user, data=data)
    return


@router.post("/verify-email")
async def verify_email():
    pass
