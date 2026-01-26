from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core import settings


def register_middleware(app: FastAPI) -> None:

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.midd.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
