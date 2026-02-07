from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.user_service import get_user_service, UserService
from typing import Annotated, TYPE_CHECKING
from fastapi import HTTPException, Depends
from core import Security, exceptions
from jose import JWTError

if TYPE_CHECKING:
    from infrastructure import User

http_bearer = HTTPBearer(auto_error=False)


def get_current_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication header missing")

    token = credentials.credentials

    try:
        payload = Security.decode_token(token=token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return payload


def validate_token(payload: dict, token_type: str) -> bool:
    current_token_type = payload.get("type")
    if current_token_type != token_type:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token type {current_token_type!r} expected {token_type!r}",
        )
    return True


async def get_user_by_token_sub(
    payload: dict,
    user_service: "UserService",
) -> "User":
    sub: str | None = payload.get("sub")
    if user := await user_service.get(id=int(sub)):
        return user
    raise exceptions.unauthorized_exc_inactive_token()


def get_auth_user_from_token_of_type(token_type: str):
    async def get_auth_user_from_token(
        user_service: Annotated["UserService", Depends(get_user_service)],
        payload: Annotated[dict, Depends(get_current_token_payload)],
    ) -> "User":
        validate_token(payload=payload, token_type=token_type)
        return await get_user_by_token_sub(
            payload=payload,
            user_service=user_service,
        )

    return get_auth_user_from_token


get_current_auth_user = get_auth_user_from_token_of_type("access")
get_current_auth_user_for_refresh = get_auth_user_from_token_of_type("refresh")


def check_user_is_active(
    user: Annotated["User", Depends(get_current_auth_user)],
) -> bool:
    if not user.is_active:
        raise exceptions.forbidden_exc_inactive()
    return True
