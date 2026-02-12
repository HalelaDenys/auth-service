from fastapi import APIRouter
from views.reset_password import router as reset_password_router

view_router = APIRouter(prefix="/view", tags=["Views"])
view_router.include_router(reset_password_router)
