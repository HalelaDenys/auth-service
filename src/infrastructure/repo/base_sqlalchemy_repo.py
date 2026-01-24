from typing import TypeVar, Generic, Type, Union, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as delete_sql, update as update_sql
from pydantic import BaseModel

from infrastructure import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseSqlalchemyRepo(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self._model = model
        self._session = session

    async def create(self, data: BaseModel) -> ModelType:
        obj = self._model(**data.model_dump())
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update(self, data: BaseModel, **filters) -> ModelType | None:
        stmt = (
            update_sql(self._model)
            .where(
                *[getattr(self._model, key) == value for key, value in filters.items()],
            )
            .values(**data.model_dump())
            .returning(self._model.id)
        )

        res = await self._session.execute(stmt)
        await self._session.flush()
        update_id = res.scalar_one_or_none()

        if update_id is None:
            return None

        return await self.find_single(id=update_id)

    async def find_single(self, **filters) -> ModelType | None:
        stmt = select(self._model).filter_by(**filters)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def delete(self, **filters) -> None:
        await self._session.execute(delete_sql(self._model).filter_by(**filters))
        await self._session.flush()
