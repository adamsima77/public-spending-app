import datetime
import hashlib
import json
from typing import Any

import redis.asyncio as redis

from core.database import Database


class Logger:
    def __init__(
        self,
        db: Database,
        redis_client: redis.Redis | None = None,
        dedup_window_seconds: int = 180,
    ) -> None:
        self._db = db
        self._redis = redis_client
        self._dedup_window = dedup_window_seconds

    async def _should_log(self, level: str, message: str) -> bool:
        if not self._redis or level not in ("warning", "error"):
            return True

        message_hash = hashlib.sha256(
            f"{level}:{message}".encode()
        ).hexdigest()
        key = f"etl:log_dedup:{message_hash}"

        try:
            was_set = await self._redis.set(
                key, "1", nx=True, ex=self._dedup_window
            )
            return was_set is True
        except Exception as e:
            print(f"Redis dedup check failed: {e}")
            return True

    async def log(
        self,
        level: str,
        message: str,
        context: dict[str, Any] | None = None,
        file_id: int | None = None,
    ) -> None:
        if not await self._should_log(level, message):
            return

        query = """
            INSERT INTO etl_logs (level, message, context, file_id, created_at)
            VALUES (:level, :message, :context, :file_id, :created_at)
        """
        params = {
            "level": level,
            "message": message,
            "context": json.dumps(context) if context is not None else None,
            "file_id": file_id,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        }
        try:
            await self._db.execute(query, params)
        except Exception as e:
            print(f"Logger failed to write to DB: {e}")
