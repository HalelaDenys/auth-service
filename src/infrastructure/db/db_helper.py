from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
    AsyncSession,
)
from typing import AsyncGenerator
from sqlalchemy.engine import URL
from core import settings


class DBHelper:
    def __init__(
        self,
        *,
        url: str | URL,
        echo: bool,
    ) -> None:
        self._engine: AsyncEngine = create_async_engine(
            url,
            echo=echo,
        )
        self._async_session_maker: async_sessionmaker[AsyncSession] = (
            async_sessionmaker(
                engine=self._engine,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def dispose(self):
        await self._engine.dispose()


db_helper = DBHelper(
    url=settings.db.dsn,
    echo=settings.db.echo,
)
