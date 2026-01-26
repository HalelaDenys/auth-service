from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from infrastructure import db_helper
from core.middlewares import register_middleware
from api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:

    yield

    await db_helper.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        title="AuthService",
        default_response_class=ORJSONResponse,
    )

    register_middleware(app)

    app.include_router(api_router)
    return app
