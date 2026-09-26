import httpx
from typing import Any, Dict, Optional
from config import settings

class Notification:
    def __init__(self, logger: Optional[Any] = None) -> None:
        self.logger = logger

    async def send_discord_alert(self, message: str, context: Optional[Dict[str, Any]] = None) -> bool:
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
                response = await client.post(str(settings.discord_webhook_url), json=payload)
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