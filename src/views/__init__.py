from fastapi import APIRouter
from views.auth import router

view_router = APIRouter(prefix="/view", tags=["Views"])
view_router.include_router(router)
