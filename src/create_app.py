from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from infrastructure import db_helper, broker
from core.middlewares import register_middleware
from api import api_router
from core import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if settings.br.enable_broker:
        await broker.start()

    yield

    await db_helper.dispose()

    if settings.br.enable_broker:
        await broker.stop()


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        title="AuthService",
        default_response_class=ORJSONResponse,
    )

    register_middleware(app)

    app.include_router(api_router)
    return app
