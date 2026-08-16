import concurrent.futures
import datetime
import random

from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Set
import time

from SPARQLWrapper import JSON, SPARQLWrapper
import requests

from core.database import db

from config import (
    ACTIVITY_LOG,
    DOWNLOAD_DIR,
    DOWNLOAD_LINKS_QUERY,
    DOWNLOADED_LINKS_LOG_FILE,
    ERROR_LOG,
    settings,
)

class Download:

    def __init__(self) -> None:
        self.number_of_downloaded_links: int = 0
        self.number_of_all_links: int = 0
        self.number_of_retries: int = 3
        self.lock: Lock = Lock()

    def get_download_links(self) -> List[str]:
        try:
            sparql: SPARQLWrapper = SPARQLWrapper(settings.SPARQL_ENDPOINT)
            sparql.setQuery(DOWNLOAD_LINKS_QUERY)
            sparql.setReturnFormat(JSON)
            results: Dict[str, Any] = sparql.query().convert()
            links: List[str] = []
            for row in results["results"]["bindings"]:
                links.append(row["downloadURL"]["value"])
            return links
        except Exception as e:
            print(f"Problem with fetching data, Error: {e}")
            self.log_error(f"Problem with fetching data from API. Error: {e}")
            return []

    def download_one_file(self, link: str) -> None:
        file_id: str = link.split("id=")[-1]
        filename: Path = DOWNLOAD_DIR / file_id
        start_of_download: float = time.perf_counter()
        self.log_process(f"Starting download: {link}")

        for attempt in range(1, self.number_of_retries + 1):
            try:
                with requests.get(link, stream=True, timeout=30) as response:
                    response.raise_for_status()
                    with open(filename, "wb") as f:
                        for chunk in response.iter_content(chunk_size=settings.CHUNK_SIZE):
                            if chunk:
                                f.write(chunk)

                with self.lock:
                    self.number_of_downloaded_links += 1
                    print(f"Progress: {self.number_of_downloaded_links} / {self.number_of_all_links}")
                    self.save_downloaded_link(link)

                elapsed: float = time.perf_counter() - start_of_download
                self.log_process(f"Downloaded: {link} in {elapsed:.2f} seconds")
                time.sleep(random.uniform(0.5, 0.8))
                return

            except requests.exceptions.RequestException as e:
                print(f"Retry {attempt} failed for {link}: {e}")
                self.log_error(f"Retry {attempt} failed for {link}: {e}")
                time.sleep(random.uniform(1, 1.5))

        print(f"Failed to download {link}")
        self.log_error(f"Failed to download {link}")

    def download_data(self) -> None:
        self.number_of_downloaded_links = 0
        start_of_download: float = time.perf_counter()
        download_links: List[str] = self.get_download_links()

        if not download_links:
            self.log_error("No download links retrieved. Stopping.")
            return

        already_downloaded: Set[str] = self.load_downloaded_links()
        links_to_download = [
            link for link in download_links if link not in already_downloaded
        ]

        self.number_of_all_links = len(links_to_download)

        if self.number_of_all_links == 0:
            print("No new files to download.")
            return

        with concurrent.futures.ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
            futures = [
                executor.submit(self.download_one_file, link)
                for link in links_to_download
            ]

            for future in concurrent.futures.as_completed(futures):
                future.result()

        elapsed: float = time.perf_counter() - start_of_download

        summary_msg = f"Download finished: {self.number_of_downloaded_links} / {self.number_of_all_links} files in {elapsed:.2f} seconds"
        print(summary_msg)
        self.log_process(summary_msg)

    def save_downloaded_link(self, link: str) -> None:
        try:
            with open(DOWNLOADED_LINKS_LOG_FILE, "a") as f:
                f.write(link + "\n")
        except Exception as e:
            print(f"Error saving link {link}: {e}")
            self.log_error(f"Error saving link {link}: {e}")

    def load_downloaded_links(self) -> Set[str]:
        links: Set[str] = set()
        try:
            with open(DOWNLOADED_LINKS_LOG_FILE, "r") as f:
                for row in f:
                    links.add(row.strip())
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Failed to load downloaded links: {e}")
            self.log_error(f"Failed to load downloaded links: {e}")
        return links

    def log_error(self, message: str) -> None:
        log_message: str = f"[{datetime.datetime.now()}] - {message}\n"
        try:
            with self.lock:
                with open(ERROR_LOG, "a") as f:
                    f.write(log_message)
        except Exception as e:
            print(f"Error writing error log: {e}")

    def log_process(self, message: str) -> None:
        log_message: str = f"[{datetime.datetime.now()}] - {message}\n"
        try:
            with self.lock:
                with open(ACTIVITY_LOG, "a") as f:
                    f.write(log_message)
        except Exception as e:
            print(f"Error writing activity log: {e}")