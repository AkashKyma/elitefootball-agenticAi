import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings
from app.services.logging_service import get_logger, log_event


logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for future ORM models."""


engine = create_engine(settings.database_url, future=True)
log_event(logger, logging.INFO, "db.engine.initialized", database_url=settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
log_event(logger, logging.INFO, "db.session.configured", autoflush=False, autocommit=False)
