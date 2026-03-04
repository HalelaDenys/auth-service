from typing import TypeVar, Generic, Type, Union, TypeAlias
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as delete_sql, update as update_sql
from pydantic import BaseModel
from dataclasses import is_dataclass, asdict
from infrastructure import Base

ModelType = TypeVar("ModelType", bound=Base)
DataType: TypeAlias = Union[BaseModel, object]


class BaseSqlalchemyRepo(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self._model = model
        self._session = session

    @staticmethod
    def _dump_data(data: DataType) -> dict:
        if isinstance(data, BaseModel):
            return data.model_dump()
        if is_dataclass(data):
            return asdict(data)
        raise TypeError("data must be pydantic model or dataclass")

    async def create(self, data: DataType) -> ModelType:
        payload = self._dump_data(data)
        obj = self._model(**payload)
        self._session.add(obj)
        await self._session.flush()
        await self._session.refresh(obj)
        return obj

    async def update(self, data: DataType, **filters) -> ModelType | None:
        payload = self._dump_data(data)
        stmt = (
            update_sql(self._model)
            .where(
                *[getattr(self._model, key) == value for key, value in filters.items()],
            )
            .values(**payload)
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
