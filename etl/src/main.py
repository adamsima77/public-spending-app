import asyncio
from pathlib import Path
from typing import Dict, List
import redis.asyncio as redis
from core.database import db
from core.logger import Logger
from downloaders.download_data import Download
from parsers.json_parser import JsonParser
from loaders.notice_loader import NoticeLoader
import config

async def main():
    async with redis.from_url(config.settings.REDIS_URL) as redis_client:
        logger = Logger(db, redis_client=redis_client)

        downloader = Download(logger=logger)
        json_parser = JsonParser(
            notice_fields=config.NOTICE_FIELDS,
            organization_fields=config.ORGANIZATION_FIELDS,
            procedure_fields=config.PROCEDURE_FIELDS,
            lot_fields=config.LOT_FIELDS,
            anchor_organization=config.ANCHOR_ORGANIZATION,
            anchor_lot=config.ANCHOR_LOT,
            logger=logger,
        )
        notice_loader = NoticeLoader(db, logger=logger)

        try:
            await downloader.download_data()
            files = get_files_to_process(config.DOWNLOAD_DIR)
            await logger.log("info", f"Nájdených {len(files)} súborov na spracovanie.")

            json_files = [f for f in files if f.suffix == ".json"]
            file_id_map = await _load_file_id_map(db, [f.stem for f in json_files])

            for file_path in json_files:
                db_file_id = file_id_map.get(file_path.stem)
                try:
                    async for notice_dto in json_parser.parse_file(str(file_path), db_file_id=db_file_id):
                        await notice_loader.upsert_notice(notice_dto, db_file_id=db_file_id)
                    file_path.unlink()
                except Exception as e:
                    await logger.log(
                        "error",
                        f"Spracovanie súboru zlyhalo: {e}",
                        file_id=db_file_id,
                    )
        finally:
            await db.close()


async def _load_file_id_map(database, stems: List[str]) -> Dict[str, int]:
    if not stems:
        return {}
    rows = await database.fetch_all(
        "SELECT id, file_id FROM downloaded_files WHERE file_id = ANY(:stems)",
        {"stems": stems},
    )
    return {row["file_id"]: row["id"] for row in rows}


def get_files_to_process(download_dir: Path) -> List[Path]:
    if not download_dir.exists():
        return []

    return [file_path for file_path in download_dir.glob("*") if file_path.is_file()]


if __name__ == "__main__":
    asyncio.run(main())