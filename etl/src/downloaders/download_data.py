import asyncio
import datetime
import hashlib
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Set
import redis.asyncio as redis
import aiofiles
import httpx
from SPARQLWrapper import JSON, SPARQLWrapper

from core.database import db, Database
from core.logger import Logger
from config import DOWNLOAD_DIR, DOWNLOAD_LINKS_QUERY, settings

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
    def __init__(self, database: Database = db) -> None:
        self._db = database
        self.number_of_downloaded_links: int = 0
        self.number_of_all_links: int = 0
        self.number_of_retries: int = 3
        self._counter_lock = asyncio.Lock()

    async def get_download_links(self, logger: Logger) -> List[Dict[str, str]]:
        try:
            def _run_query() -> Dict[str, Any]:
                sparql = SPARQLWrapper(settings.SPARQL_ENDPOINT)
                sparql.setTimeout(30)  
                sparql.setQuery(DOWNLOAD_LINKS_QUERY)
                sparql.setReturnFormat(JSON)
                return sparql.query().convert()

            results = await asyncio.to_thread(_run_query)
            return [
                {"url": row["downloadURL"]["value"], "format": row["format"]["value"]}
                for row in results["results"]["bindings"]
            ]
        except Exception as e:
            await logger.log("error", f"Problem with fetching data from SPARQL endpoint. Error: {e}")
            return []

    async def load_downloaded_urls(self) -> Set[str]:
        try:
            rows = await self._db.fetch_all("SELECT url FROM downloaded_files")
            return {row["url"] for row in rows}
        except Exception:
            return set()

    async def download_one_file(
        self,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        file_id: str,
        url: str,
        fmt: str,
        logger: Logger,
    ) -> Dict[str, Any]:
        filename: Path = DOWNLOAD_DIR / f"{file_id}{_extension_from_format(fmt)}"
        start = time.perf_counter()

        async with semaphore:
            for attempt in range(1, self.number_of_retries + 1):
                try:
                    hasher = hashlib.sha256()
                    async with client.stream("GET", url, timeout=30.0) as response:
                        response.raise_for_status()
                        async with aiofiles.open(filename, "wb") as f:
                            async for chunk in response.aiter_bytes(chunk_size=settings.CHUNK_SIZE):
                                if chunk:
                                    await f.write(chunk)
                                    hasher.update(chunk)

                    async with self._counter_lock:
                        self.number_of_downloaded_links += 1
                        print(f"Progress: {self.number_of_downloaded_links} / {self.number_of_all_links}")

                    elapsed = time.perf_counter() - start
                    await logger.log("info", f"Downloaded: {url} in {elapsed:.2f}s")
                    await asyncio.sleep(random.uniform(0.1, 0.3))

                    return {
                        "file_id": file_id,
                        "url": url,
                        "filename": filename.name,
                        "format": fmt,
                        "file_hash": hasher.hexdigest(),
                        "downloaded_at": datetime.datetime.now(datetime.timezone.utc),
                        "status": "success",
                    }

                except (httpx.HTTPError, Exception) as e:
                    if filename.exists():
                        filename.unlink(missing_ok=True)

                    await logger.log("warning", f"Retry {attempt} failed for {url}: {e}")
                    await asyncio.sleep(random.uniform(1, 1.5))

        await logger.log("error", f"Failed to download {url} after {self.number_of_retries} attempts")
        return {"file_id": file_id, "url": url, "status": "failed"}

    async def download_data(self) -> None:
        self.number_of_downloaded_links = 0
        start = time.perf_counter()

        # Vytvorí celý adresár pre sťahovanie, ak neexistuje
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        async with redis.from_url(settings.REDIS_URL) as redis_client:
            logger = Logger(self._db, redis_client=redis_client)

            raw_links = await self.get_download_links(logger)
            if not raw_links:
                await logger.log("error", "No download links retrieved. Stopping.")
                return

            already_downloaded = await self.load_downloaded_urls()
            links_to_download = [l for l in raw_links if l["url"] not in already_downloaded]

            self.number_of_all_links = len(links_to_download)
            if self.number_of_all_links == 0:
                print("No new files to download.")
                return

            semaphore = asyncio.Semaphore(settings.MAX_WORKERS)
            buffer: List[Dict[str, Any]] = []

            async with httpx.AsyncClient(follow_redirects=True) as client:
                tasks = [
                    self.download_one_file(
                        client, semaphore, link["url"].split("id=")[-1], link["url"], link["format"], logger
                    )
                    for link in links_to_download
                ]

                for coro in asyncio.as_completed(tasks):
                    result = await coro
                    buffer.append(result)
                    if len(buffer) >= 20:
                        await self._flush(buffer)
                        buffer = []

            if buffer:
                await self._flush(buffer)

            elapsed = time.perf_counter() - start
            summary = (
                f"Download finished: {self.number_of_downloaded_links} / "
                f"{self.number_of_all_links} files in {elapsed:.2f} seconds"
            )
            print(summary)
            await logger.log("info", summary)

    async def _flush(self, buffer: List[Dict[str, Any]]) -> None:
        successful = [r for r in buffer if r["status"] == "success"]
        if not successful:
            return

        query = """
            INSERT INTO downloaded_files
                (file_id, url, filename, format, status_id, downloaded_at, file_hash, created_at, updated_at)
            VALUES
                (:file_id, :url, :filename, :format,
                 (SELECT id FROM etl_statuses WHERE name = 'downloaded'),
                 :downloaded_at, :file_hash, :downloaded_at, :downloaded_at)
            ON CONFLICT (file_id) DO NOTHING
        """
        await self._db.execute_many(query, successful)