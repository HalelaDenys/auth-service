from fastapi import APIRouter, Request
from core import templates

router = APIRouter()


@router.get(
    "/reset",
    include_in_schema=False,
)
async def reset(request: Request):
    return templates.TemplateResponse(
        "reset-password.html",
        {
            "request": request,
        },
    )
