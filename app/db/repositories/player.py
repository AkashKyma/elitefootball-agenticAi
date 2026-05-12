from typing import Optional
from sqlalchemy import select
from app.db.repositories.base import BaseRepository
from app.db.models import Player

class PlayerRepository(BaseRepository[Player]):
    """Enterprise grade asynchronous operational database access layer for Player objects."""
    def __init__(self, session):
        super().__init__(session, Player)

    async def get_by_slug(self, slug: str) -> Optional[Player]:
        """Enables modern semantic string resolving from relational backplane."""
        # Legacy shim for current system integration
        stmt = select(self.model_cls).filter(self.model_cls.full_name.ilike(slug.replace("_", " ")))
        result = await self.session.execute(stmt)
        return result.scalars().first()
