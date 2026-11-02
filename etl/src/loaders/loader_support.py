from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import Logger

ResultT = TypeVar("ResultT")


class LoaderSupport:
    def __init__(self, logger: Logger | None = None) -> None:
        self._logger = logger
        self._known_nuts_codes: set[str] = set()
        self._known_cpv_codes: set[str] = set()

    async def _guarded(
        self,
        session: AsyncSession,
        description: str,
        context: dict[str, Any],
        fn: Callable[[], Awaitable[ResultT]],
    ) -> ResultT | None:
        try:
            async with session.begin_nested():
                return await fn()
        except DBAPIError as e:
            if self._logger:
                await self._logger.log(
                    "warning",
                    f"Záznam preskočený ({description}): {getattr(e, 'orig', e)}",
                    context=context,
                )
            return None

    @staticmethod
    def _require_int(value: Any, field: str) -> int:
        if not isinstance(value, int):
            raise TypeError(f"Expected {field} to be an integer, got {type(value).__name__}")
        return value

    async def ensure_nuts_code(self, session: AsyncSession, nuts_code: str | None) -> None:
        if not nuts_code:
            return

        code = str(nuts_code).strip().upper()[:10]
        if not code or code in self._known_nuts_codes:
            return

        query = """
            INSERT INTO nut_codes (code, name_sk, level, parent_code, created_at, updated_at)
            VALUES (:code, :name_sk, :level, NULL, now(), now())
            ON CONFLICT (code) DO NOTHING
        """
        await session.execute(
            text(query),
            {"code": code, "name_sk": f"NUTS {code}", "level": max(1, min(len(code), 5))},
        )
        self._known_nuts_codes.add(code)

    async def ensure_cpv_code(self, session: AsyncSession, cpv_code: str | None) -> None:
        if not cpv_code:
            return

        code = str(cpv_code).strip()[:10]
        if not code or code in self._known_cpv_codes:
            return

        query = """
            INSERT INTO cpv_codes (code, name_sk, level, parent_code, created_at, updated_at)
            VALUES (:code, :name_sk, :level, NULL, now(), now())
            ON CONFLICT (code) DO NOTHING
        """
        await session.execute(
            text(query),
            {"code": code, "name_sk": f"CPV {code}", "level": len(code)},
        )
        self._known_cpv_codes.add(code)
