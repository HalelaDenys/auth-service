from fastapi import HTTPException


class NotFoundError(Exception):
    pass


class AlreadyExistsError(Exception):
    pass


UNAUTHORIZED_EXC_INCORRECT = HTTPException(
    status_code=401,
    detail="Incorrect phone number or password",
)


FORBIDDEN_EXC_INACTIVE = HTTPException(
    status_code=403,
    detail="Inactive user",
)

UNAUTHORIZED_EXC_INVALID_TOKEN = HTTPException(
    status_code=401,
    detail="Invalid token",
)

FORBIDDEN_EXC_NOT_ENOUGH_RIGHTS = HTTPException(
    status_code=403,
    detail="Not enough rights",
)
