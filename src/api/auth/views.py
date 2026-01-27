from fastapi import APIRouter, Depends
from services.user_service import get_user_service, UserService
from services.auth_service import (
    get_auth_service,
    AuthService,
    authenticate_user_dependency,
)
from schemas.user_schemas import RegisterUserSchema, ReadUserSchema
from typing import Annotated
from infrastructure import User
from schemas.auth_schemas import TokenSchema

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/register")
async def register(
    user_data: RegisterUserSchema,
    user_service: Annotated["UserService", Depends(get_user_service)],
):
    user = await user_service.add(user_data)
    return ReadUserSchema(**user.to_dict())


@router.post("/login")
async def login(
    user_data: Annotated["User", Depends(authenticate_user_dependency)],
    auth_service: Annotated["AuthService", Depends(get_auth_service)],
) -> TokenSchema:
    return await auth_service.login_user(user_data)


@router.post("/logout")
async def logout():
    pass


@router.post("/refresh")
async def refresh():
    pass


@router.post("/reset-password")
async def reset_password():
    pass


@router.post("/forgot-password")
async def forgot_password():
    pass


@router.post("/verify-email")
async def verify_email():
    pass
