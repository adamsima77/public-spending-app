from typing import Any, Dict, List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from config import settings


class Database:
    def __init__(self, db_url: str | None = None) -> None:
        self._db_url: str = db_url or settings.DATABASE_URL
        self._engine = create_engine(
            self._db_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
        self._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
        )

    def execute(self, query: str, params: dict | None = None) -> None:
        session: Session = self._session_factory()
        try:
            session.execute(text(query), params or {})
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def fetch_all(self, query: str, params: dict | None = None) -> List[Dict[str, Any]]:
        session: Session = self._session_factory()
        try:
            result = session.execute(text(query), params or {})
            return [dict(row._mapping) for row in result]
        finally:
            session.close()

    def fetch_one(self, query: str, params: dict | None = None) -> Dict[str, Any] | None:
        session: Session = self._session_factory()
        try:
            result = session.execute(text(query), params or {})
            row = result.first()
            return dict(row._mapping) if row else None
        finally:
            session.close()


# Singleton
db = Database()