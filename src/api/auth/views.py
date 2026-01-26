from fastapi import APIRouter, Depends
from services.user_service import get_user_service, UserService
from schemas.user_schemas import RegisterUserSchema, ReadUserSchema
from typing import Annotated

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
async def login():
    pass


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
