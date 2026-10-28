import asyncio
import csv
import json
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import aiofiles
import ijson

logger = logging.getLogger(__name__)

COLUMN_COVERAGE_THRESHOLD = 80.0
OPTIONAL_COLUMN_COVERAGE_THRESHOLD = 20.0
PROGRESS_INTERVAL = 25


@dataclass
class DiscoveryStats:
    total_notices: int = 0
    processed_files: int = 0
    total_files: int = 0
    code_counts: Counter[str] = field(default_factory=Counter)
    code_levels: defaultdict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


def derive_level(code_id: str) -> str:
    if code_id.endswith("-notice"):
        return "NOTICE"
    if "-Organization-Company" in code_id or "-Organization" in code_id:
        return "ORGANIZATION"
    if "-Procedure" in code_id:
        return "PROCEDURE"
    if "-Lot" in code_id:
        return "LOT"
    return "OTHER"


def collect_codes(
    node: Any,
    notice_codes: set[str],
    notice_levels: defaultdict[str, set[str]],
) -> None:
    if isinstance(node, dict):
        code_id = node.get("key") or node.get("code") or node.get("id")
        if isinstance(code_id, str) and code_id:
            notice_codes.add(code_id)
            notice_levels[code_id].add(derive_level(code_id))

        for key, value in node.items():
            if key == "itemData" and isinstance(value, str):
                try:
                    nested_json = json.loads(value)
                except json.JSONDecodeError:
                    logger.warning("Skipping malformed nested itemData JSON")
                else:
                    collect_codes(nested_json, notice_codes, notice_levels)
            elif isinstance(value, (dict, list)):
                collect_codes(value, notice_codes, notice_levels)
    elif isinstance(node, list):
        for item in node:
            collect_codes(item, notice_codes, notice_levels)


async def process_file_worker(
    worker_id: int,
    queue: asyncio.Queue[Path | None],
    stats: DiscoveryStats,
) -> None:
    while True:
        file_path = await queue.get()
        try:
            if file_path is None:
                return

            file_notices = 0
            local_code_counts: Counter[str] = Counter()
            local_code_levels: defaultdict[str, set[str]] = defaultdict(set)

            try:
                async with aiofiles.open(file_path, mode="rb") as file:
                    parser = ijson.items_async(file, "bulletinItemList.item")
                    async for item in parser:
                        file_notices += 1
                        notice_codes: set[str] = set()
                        notice_levels: defaultdict[str, set[str]] = defaultdict(set)
                        collect_codes(item, notice_codes, notice_levels)

                        for code_id in notice_codes:
                            local_code_counts[code_id] += 1
                            local_code_levels[code_id].update(notice_levels[code_id])
            except Exception:
                logger.exception("Worker %d failed to process %s", worker_id, file_path)
                continue

            async with stats.lock:
                stats.total_notices += file_notices
                stats.processed_files += 1
                for code_id, count in local_code_counts.items():
                    stats.code_counts[code_id] += count
                    stats.code_levels[code_id].update(local_code_levels[code_id])

                if (
                    stats.processed_files % PROGRESS_INTERVAL == 0
                    or stats.processed_files == stats.total_files
                ):
                    logger.info(
                        "Processed %d/%d files; found %d notices",
                        stats.processed_files,
                        stats.total_files,
                        stats.total_notices,
                    )
        finally:
            queue.task_done()


def _find_json_files(folder_path: Path) -> list[Path]:
    return sorted(path for path in folder_path.rglob("*.json") if path.is_file())


def _write_report(output_path: Path, stats: DiscoveryStats) -> None:
    with output_path.open(mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            ["Code_ID", "Notice_Count", "Coverage_Pct", "Detected_Level", "DB_Recommendation"]
        )

        for code_id, count in stats.code_counts.most_common():
            coverage = (
                round((count / stats.total_notices) * 100, 2) if stats.total_notices > 0 else 0
            )
            levels = "|".join(sorted(stats.code_levels[code_id]))
            if coverage >= COLUMN_COVERAGE_THRESHOLD:
                recommendation = "COLUMN (Vytvoriť stĺpec v DB)"
            elif coverage >= OPTIONAL_COLUMN_COVERAGE_THRESHOLD:
                recommendation = "OPTIONAL COLUMN (Zvážiť stĺpec)"
            else:
                recommendation = "RAW_DATA (Nechať v JSONB)"

            writer.writerow([code_id, count, f"{coverage}%", levels, recommendation])


async def run_async_discovery(
    folder_path: str,
    num_workers: int = 8,
    output_csv: str = "discovery_report_async.csv",
) -> None:
    if num_workers < 1:
        raise ValueError("num_workers must be at least 1")

    input_path = Path(folder_path)
    output_path = Path(output_csv)
    json_files = await asyncio.to_thread(_find_json_files, input_path)
    stats = DiscoveryStats(total_files=len(json_files))
    logger.info(
        "Found %d files. Starting %d asynchronous workers.",
        stats.total_files,
        num_workers,
    )

    file_queue: asyncio.Queue[Path | None] = asyncio.Queue()
    for file_path in json_files:
        await file_queue.put(file_path)

    workers = [
        asyncio.create_task(process_file_worker(worker_id, file_queue, stats))
        for worker_id in range(1, num_workers + 1)
    ]
    for _ in workers:
        await file_queue.put(None)

    await file_queue.join()
    await asyncio.gather(*workers)
    await asyncio.to_thread(_write_report, output_path, stats)

    logger.info(
        "Completed: processed %d notices from %d files. Report saved to %s",
        stats.total_notices,
        stats.total_files,
        output_path,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(
        run_async_discovery(
            folder_path="/app/data", num_workers=8, output_csv="/app/data/discovery_report.csv"
        )
    )
