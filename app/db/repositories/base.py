import abc
from typing import Generic, TypeVar, Type, Optional, List, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

T = TypeVar("T")

class BaseRepository(Generic[T], abc.ABC):
    """Rigid abstract foundational layer enforcing asynchronous write stability."""
    def __init__(self, session: AsyncSession, model_cls: Type[T]):
        self.session = session
        self.model_cls = model_cls

    async def get_by_id(self, id: Any) -> Optional[T]:
        result = await self.session.execute(select(self.model_cls).filter(self.model_cls.id == id))
        return result.scalars().first()

    async def get_all(self, limit: int = 100) -> List[T]:
        result = await self.session.execute(select(self.model_cls).limit(limit))
        return list(result.scalars().all())

    async def save(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
