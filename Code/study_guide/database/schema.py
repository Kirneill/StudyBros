"""
Database schema initialization and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine

from study_guide.config import config
from study_guide.database.models import Base

# Module-level engine and session factory
_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def get_engine() -> Engine:
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        config.ensure_directories()
        db_url = f"sqlite:///{config.DB_PATH}"
        _engine = create_engine(db_url, echo=False)
    return _engine


def get_session_factory() -> sessionmaker:
    """Get or create the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _SessionLocal


def get_session() -> Session:
    """Create a new database session."""
    return get_session_factory()()


def init_db() -> None:
    """Initialize the database schema."""
    engine = get_engine()
    Base.metadata.create_all(engine)


def reset_db() -> None:
    """Drop and recreate all tables (for testing)."""
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
