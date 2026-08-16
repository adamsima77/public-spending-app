# src/core/http_client.py
from typing import Any, Dict, Optional
import httpx
from config import settings

class HTTPClient:

    def __init__(self, base_url: Optional[str] = None, access_key: Optional[str] = None, timeout: float = 30.0) -> None:
        self.base_url = (base_url or settings.BACKEND_URL).rstrip("/")
        self.access_key = access_key or settings.PYTHON_ACCESS_KEY

        if not self.access_key:
            raise ValueError(
                "PYTHON_ACCESS_KEY nie je nastavený v ENV. "
                "Bez neho nebude požiadavka autorizovaná."
            )

        self.headers = {
            "Authorization": f"Bearer {self.access_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.timeout = timeout

    def _build_url(self, endpoint: str) -> str:
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}" if endpoint else self.base_url

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        url = self._build_url(endpoint)
        headers = {**self.headers, **(custom_headers or {})}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            
            if response.status_code == 204 or not response.content:
                return None

            return response.json()

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        return await self._request("GET", endpoint, params=params, custom_headers=headers)

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        return await self._request("POST", endpoint, data=data, params=params, custom_headers=headers)

    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        return await self._request("PUT", endpoint, data=data, params=params, custom_headers=headers)

    async def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        return await self._request("PATCH", endpoint, data=data, params=params, custom_headers=headers)

    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        return await self._request("DELETE", endpoint, params=params, custom_headers=headers)


http_client = HTTPClient()