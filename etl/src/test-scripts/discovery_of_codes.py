import os
import csv
import json
import asyncio
import aiofiles
import ijson
from collections import Counter, defaultdict

global_code_counts = Counter()
global_code_levels = defaultdict(set)
total_notices_count = 0
processed_files_count = 0
total_files_count = 0
counter_lock = asyncio.Lock()


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


def collect_codes(node, notice_codes: set, notice_levels: defaultdict):
    if isinstance(node, dict):
        code_id = node.get("key") or node.get("code") or node.get("id")
        if code_id and isinstance(code_id, str):
            notice_codes.add(code_id)
            notice_levels[code_id].add(derive_level(code_id))

        for key, val in node.items():
            if key == "itemData" and isinstance(val, str):
                try:
                    lot_json = json.loads(val)
                    collect_codes(lot_json, notice_codes, notice_levels)
                except json.JSONDecodeError:
                    pass
            elif isinstance(val, (dict, list)):
                collect_codes(val, notice_codes, notice_levels)

    elif isinstance(node, list):
        for item in node:
            collect_codes(item, notice_codes, notice_levels)


async def process_file_worker(worker_id: int, queue: asyncio.Queue):
    global total_notices_count, processed_files_count

    while True:
        file_path = await queue.get()
        if file_path is None:
            queue.task_done()
            break

        file_notices = 0
        local_code_counts = Counter()
        local_code_levels = defaultdict(set)

        try:
            async with aiofiles.open(file_path, mode='rb') as f:
                parser = ijson.items_async(f, 'bulletinItemList.item')

                async for item in parser:
                    file_notices += 1

                    notice_codes = set()
                    notice_levels = defaultdict(set)

                    collect_codes(item, notice_codes, notice_levels)

                    for code_id in notice_codes:
                        local_code_counts[code_id] += 1
                        local_code_levels[code_id].update(notice_levels[code_id])

            async with counter_lock:
                total_notices_count += file_notices
                processed_files_count += 1

                for code_id, count in local_code_counts.items():
                    global_code_counts[code_id] += count
                    global_code_levels[code_id].update(local_code_levels[code_id])

                pct = (processed_files_count / total_files_count) * 100
                if processed_files_count % 25 == 0 or processed_files_count == total_files_count:
                    print(
                        f"[PROGRES] Spracovaných {processed_files_count}/{total_files_count} súborov "
                        f"({pct:.1f}%) | Nájdenej špecifikácie oznámení: {total_notices_count}"
                    )

        except Exception as e:
            print(f"[Worker {worker_id}] Chyba pri súbore {file_path}: {e}")
        finally:
            queue.task_done()


async def run_async_discovery(folder_path: str, num_workers: int = 8, output_csv: str = "discovery_report_async.csv"):
    global total_files_count
    file_queue = asyncio.Queue()

    json_files = [
        os.path.join(root, file)
        for root, _, files in os.walk(folder_path)
        for file in files if file.endswith('.json')
    ]

    total_files_count = len(json_files)
    print(f"Našiel som {total_files_count} súborov. Spúšťam {num_workers} async workerov...")

    for file_path in json_files:
        await file_queue.put(file_path)

    workers = [asyncio.create_task(process_file_worker(i + 1, file_queue)) for i in range(num_workers)]

    for _ in range(num_workers):
        await file_queue.put(None)

    await file_queue.join()
    await asyncio.gather(*workers)

    with open(output_csv, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Code_ID", "Notice_Count", "Coverage_Pct", "Detected_Level", "DB_Recommendation"])

        for code_id, count in global_code_counts.most_common():
            pct = round((count / total_notices_count) * 100, 2) if total_notices_count > 0 else 0
            levels = "|".join(sorted(global_code_levels[code_id]))

            if pct >= 80.0:
                rec = "COLUMN (Vytvoriť stĺpec v DB)"
            elif pct >= 20.0:
                rec = "OPTIONAL COLUMN (Zvážiť stĺpec)"
            else:
                rec = "RAW_DATA (Nechať v JSONB)"

            writer.writerow([code_id, count, f"{pct}%", levels, rec])

    print(f"\n[DOKONČENÉ] Spracovaných {total_notices_count} oznámení z {total_files_count} súborov.")
    print(f"Výsledok uložený v: {output_csv}")


if __name__ == "__main__":
    asyncio.run(
        run_async_discovery(
            folder_path="/app/data",
            num_workers=8,
            output_csv="/app/data/discovery_report.csv"
        )
    )