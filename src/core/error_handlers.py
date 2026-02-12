from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import DatabaseError
from core.exceptions import NotFoundError, AlreadyExistsError


def register_error_handlers(app: FastAPI) -> None:

    @app.exception_handler(NotFoundError)
    async def not_found(request: Request, exc: NotFoundError):
        return ORJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": str(exc),
            },
        )

    @app.exception_handler(AlreadyExistsError)
    async def already_exists(request: Request, exc: AlreadyExistsError):
        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": str(exc),
            },
        )

    @app.exception_handler(DatabaseError)
    async def database_error(request: Request, exc: DatabaseError):
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "There was an unforeseen error. "
                "Our administrators are already working on it."
            },
        )

    @app.exception_handler(ConnectionRefusedError)
    def connection_error_handler(
        request: Request,
        exc: DatabaseError,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "There was an unforeseen error. "
                "Our administrators are already working on it."
            },
        )
