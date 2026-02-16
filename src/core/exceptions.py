from fastapi import HTTPException


class NotFoundError(Exception):
    pass


class AlreadyExistsError(Exception):
    pass


def unauthorized_exc_incorrect() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Incorrect email or password",
    )


def forbidden_exc_inactive() -> HTTPException:
    return HTTPException(
        status_code=403,
        detail="Inactive user",
    )


def unauthorized_exc_inactive_token() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Invalid token",
    )


def forbidden_exc_not_enough_rights() -> HTTPException:
    return HTTPException(
        status_code=403,
        detail="Not enough rights",
    )


def incorrect_old_password() -> HTTPException:
    return HTTPException(
        status_code=400,
        detail="Old password is incorrect",
    )
