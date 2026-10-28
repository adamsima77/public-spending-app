from __future__ import annotations

import asyncio
import datetime
import hashlib
import logging
import random
import time
from typing import TYPE_CHECKING, Any

import aiofiles
import httpx
from config import DOWNLOAD_DIR, DOWNLOAD_LINKS_QUERY, settings
from core.database import Database, db
from SPARQLWrapper import JSON, SPARQLWrapper

if TYPE_CHECKING:
    from pathlib import Path

    from core.logger import Logger

logger = logging.getLogger(__name__)

PARSEABLE_EXTENSIONS = {".json"}
DOWNLOAD_BATCH_SIZE = 20
RANDOM = random.SystemRandom()


def _extension_from_format(fmt: str) -> str:
    fmt = fmt.lower()
    if "json" in fmt:
        return ".json"
    if "csv" in fmt:
        return ".csv"
    if "xml" in fmt:
        return ".xml"
    return ""


class Download:
    def __init__(self, logger: Logger, database: Database = db) -> None:
        self._db = database
        self._logger = logger
        self.number_of_downloaded_links: int = 0
        self.number_of_all_links: int = 0
        self.number_of_retries: int = 3
        self._counter_lock = asyncio.Lock()

    async def get_download_links(self) -> list[dict[str, str]]:
        def _run_query() -> Any:
            sparql = SPARQLWrapper(settings.SPARQL_ENDPOINT)
            sparql.setTimeout(30)
            sparql.setQuery(DOWNLOAD_LINKS_QUERY)
            sparql.setReturnFormat(JSON)
            return sparql.query().convert()

        try:
            results = await asyncio.to_thread(_run_query)
        except Exception as e:
            await self._logger.log(
                "error", f"Problem with fetching data from SPARQL endpoint. Error: {e}"
            )
            return []
        if not isinstance(results, dict):
            raise TypeError("SPARQL endpoint returned an unexpected response")
        return [
            {"url": row["downloadURL"]["value"], "format": row["format"]["value"]}
            for row in results["results"]["bindings"]
        ]

    async def load_skippable_urls(self) -> set[str]:
        try:
            rows = await self._db.fetch_all(
                """
                SELECT f.url, f.filename, s.name AS status
                FROM downloaded_files f
                LEFT JOIN etl_statuses s ON s.id = f.status_id
                """
            )
        except Exception:
            return set()

        skip: set[str] = set()
        for row in rows:
            on_disk = bool(row["filename"]) and (DOWNLOAD_DIR / row["filename"]).exists()
            if row["status"] == "parsed" or on_disk:
                skip.add(row["url"])
        return skip

    async def ensure_etl_statuses(self) -> None:
        query = """
            INSERT INTO etl_statuses (name, created_at, updated_at)
            VALUES (:name, now(), now())
            ON CONFLICT (name) DO NOTHING
        """
        statuses = ["pending", "downloading", "downloaded", "failed", "parsed"]
        await self._db.execute_many(query, [{"name": s} for s in statuses])

    async def _mark_downloading(self, file_id: str, url: str, filename: str, fmt: str) -> None:
        query = """
            INSERT INTO downloaded_files (file_id, url, filename, format, status_id, created_at, updated_at)
            VALUES (:file_id, :url, :filename, :format,
                    (SELECT id FROM etl_statuses WHERE name = 'downloading'),
                    now(), now())
            ON CONFLICT (file_id) DO UPDATE SET
                status_id = (SELECT id FROM etl_statuses WHERE name = 'downloading'),
                updated_at = now()
        """
        await self._db.execute(
            query,
            {"file_id": file_id, "url": url, "filename": filename, "format": fmt},
        )

    async def _mark_failed(self, file_id: str) -> None:
        query = """
            UPDATE downloaded_files
            SET status_id = (SELECT id FROM etl_statuses WHERE name = 'failed'),
                updated_at = now()
            WHERE file_id = :file_id
        """
        await self._db.execute(query, {"file_id": file_id})

    def _cleanup_partial_files(self) -> None:
        for part in DOWNLOAD_DIR.glob("*.part"):
            part.unlink(missing_ok=True)

    async def _download_attempt(
        self,
        client: httpx.AsyncClient,
        partial: Path,
        filename: Path,
        file_id: str,
        url: str,
        fmt: str,
        start: float,
    ) -> tuple[dict[str, Any] | None, Exception | None]:
        try:
            hasher = hashlib.sha256()
            async with client.stream("GET", url, timeout=30.0) as response:
                response.raise_for_status()
                async with aiofiles.open(partial, "wb") as file:
                    async for chunk in response.aiter_bytes(chunk_size=settings.CHUNK_SIZE):
                        if chunk:
                            await file.write(chunk)
                            hasher.update(chunk)

            await asyncio.to_thread(partial.replace, filename)
        except Exception as error:
            await asyncio.to_thread(partial.unlink, missing_ok=True)
            return None, error

        async with self._counter_lock:
            self.number_of_downloaded_links += 1
            await self._logger.log(
                "info",
                f"Progress: {self.number_of_downloaded_links} / {self.number_of_all_links}",
            )

        elapsed = time.perf_counter() - start
        await self._logger.log("info", f"Downloaded: {url} in {elapsed:.2f}s")
        await asyncio.sleep(RANDOM.uniform(0.1, 0.3))
        return (
            {
                "file_id": file_id,
                "url": url,
                "filename": filename.name,
                "format": fmt,
                "file_hash": hasher.hexdigest(),
                "downloaded_at": datetime.datetime.now(datetime.timezone.utc),
                "status": "success",
            },
            None,
        )

    async def download_one_file(
        self,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        file_id: str,
        url: str,
        fmt: str,
    ) -> dict[str, Any]:
        filename: Path = DOWNLOAD_DIR / f"{file_id}{_extension_from_format(fmt)}"

        partial: Path = filename.with_name(filename.name + ".part")
        start = time.perf_counter()

        async with semaphore:
            await self._mark_downloading(file_id, url, filename.name, fmt)

            for attempt in range(1, self.number_of_retries + 1):
                result, error = await self._download_attempt(
                    client, partial, filename, file_id, url, fmt, start
                )
                if error is None:
                    if result is None:
                        raise RuntimeError("Download attempt completed without a result")
                    return result

                await self._logger.log("warning", f"Retry {attempt} failed for {url}: {error}")
                await asyncio.sleep(RANDOM.uniform(1, 1.5))

            await self._mark_failed(file_id)
            await self._logger.log(
                "error", f"Failed to download {url} after {self.number_of_retries} attempts"
            )
            return {"file_id": file_id, "url": url, "status": "failed"}

    async def download_data(self) -> None:
        self.number_of_downloaded_links = 0
        start = time.perf_counter()

        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self._cleanup_partial_files()
        await self.ensure_etl_statuses()

        raw_links = await self.get_download_links()
        if not raw_links:
            await self._logger.log("error", "No download links retrieved. Stopping.")
            return

        parseable = [
            link
            for link in raw_links
            if _extension_from_format(link["format"]) in PARSEABLE_EXTENSIONS
        ]
        skippable = await self.load_skippable_urls()
        links_to_download = [link for link in parseable if link["url"] not in skippable]

        self.number_of_all_links = len(links_to_download)
        if self.number_of_all_links == 0:
            await self._logger.log("info", "No new files to download.")
            return

        semaphore = asyncio.Semaphore(settings.MAX_WORKERS)
        buffer: list[dict[str, Any]] = []

        async with httpx.AsyncClient(follow_redirects=True) as client:
            tasks = [
                self.download_one_file(
                    client, semaphore, link["url"].split("id=")[-1], link["url"], link["format"]
                )
                for link in links_to_download
            ]

            for task in asyncio.as_completed(tasks):
                result = await task
                buffer.append(result)
                if len(buffer) >= DOWNLOAD_BATCH_SIZE:
                    await self._flush(buffer)
                    buffer = []

        if buffer:
            await self._flush(buffer)

        elapsed = time.perf_counter() - start
        summary = (
            f"Download finished: {self.number_of_downloaded_links} / "
            f"{self.number_of_all_links} files in {elapsed:.2f} seconds"
        )
        await self._logger.log("info", summary)

    async def _flush(self, buffer: list[dict[str, Any]]) -> None:
        successful = [
            {
                k: r[k]
                for k in ("file_id", "url", "filename", "format", "file_hash", "downloaded_at")
            }
            for r in buffer
            if r["status"] == "success"
        ]
        if not successful:
            return

        query = """
            INSERT INTO downloaded_files
                (file_id, url, filename, format, status_id, downloaded_at, file_hash, created_at, updated_at)
            VALUES
                (:file_id, :url, :filename, :format,
                 (SELECT id FROM etl_statuses WHERE name = 'downloaded'),
                 :downloaded_at, :file_hash, :downloaded_at, :downloaded_at)
            ON CONFLICT (file_id) DO UPDATE SET
                filename = EXCLUDED.filename,
                format = EXCLUDED.format,
                status_id = (SELECT id FROM etl_statuses WHERE name = 'downloaded'),
                downloaded_at = EXCLUDED.downloaded_at,
                file_hash = EXCLUDED.file_hash,
                updated_at = EXCLUDED.updated_at
        """
        await self._db.execute_many(query, successful)
