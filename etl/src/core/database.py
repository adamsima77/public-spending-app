from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings


class Database:
    def __init__(self, db_url: str | None = None) -> None:
        self._db_url: str = db_url or settings.DATABASE_URL
        self._engine = create_async_engine(
            self._db_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def execute(self, query: str, params: dict[str, Any] | None = None) -> None:
        async with self._session_factory() as session:
            try:
                await session.execute(text(query), params or {})
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def execute_many(self, query: str, params_list: list[dict[str, Any]]) -> None:
        if not params_list:
            return
        async with self._session_factory() as session:
            try:
                await session.execute(text(query), params_list)
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def fetch_all(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        async with self._session_factory() as session:
            result = await session.execute(text(query), params or {})
            return [dict(row._mapping) for row in result]

    async def fetch_one(
        self, query: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        async with self._session_factory() as session:
            result = await session.execute(text(query), params or {})
            row = result.first()
            return dict(row._mapping) if row else None

    async def close(self) -> None:
        await self._engine.dispose()


db = Database()
