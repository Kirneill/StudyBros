"""FastAPI dependency injection for database sessions."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from study_guide.database.schema import get_session_factory


def get_db() -> Generator[Session, None, None]:
    """Yield a database session, rolling back on error."""
    session = get_session_factory()()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
