from typing import Any

import httpx

from config import settings
from core.logger import Logger


class Notification:
    def __init__(self, logger: Logger | None = None) -> None:
        self.logger = logger

    async def send_discord_alert(self, message: str, context: dict[str, Any] | None = None) -> bool:
        if not settings.DISCORD_WEBHOOK:
            return False

        payload = {
            "embeds": [
                {
                    "title": "ETL Pipeline Alert",
                    "description": message,
                    "color": 15158332,
                    "fields": [
                        {"name": str(k), "value": str(v), "inline": True}
                        for k, v in (context or {}).items()
                    ],
                }
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(settings.DISCORD_WEBHOOK, json=payload)
                response.raise_for_status()
                return True
        except Exception as e:
            if self.logger:
                await self.logger.log(
                    "error",
                    f"Zlyhalo odoslanie Discord notifikácie: {e}",
                    context={"error_details": str(e)},
                )
            return False
