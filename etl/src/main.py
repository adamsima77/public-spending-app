import asyncio
from pathlib import Path
from core.database import db
from downloaders.download_data import Download
from parsers.json_parser import JsonParser
import config
from typing import List

async def main():
    json_parser = JsonParser(
        notice_fields = config.NOTICE_FIELDS,
        organization_fields = config.ORGANIZATION_FIELDS,
        procedure_fields = config.PROCEDURE_FIELDS,
        lot_fields = config.LOT_FIELDS,
        anchor_organization = config.ANCHOR_ORGANIZATION,
        anchor_lot = config.ANCHOR_LOT,
    )

    downloader = Download()
    try:
        await downloader.download_data()
        files = get_files_to_process(config.DOWNLOAD_DIR)
        print(f"Nájdených {len(files)} súborov na spracovanie.")

        for file_path in files:
            if file_path.suffix == ".json":
                async for notice_dto in json_parser.parse_file(str(file_path)):
                    await save_data(notice_dto)
                file_path.unlink()    
    finally:
        await db.close()


def get_files_to_process(download_dir: Path) -> List[Path]:
    if not download_dir.exists():
        return []

    return [file_path for file_path in download_dir.glob("*") if file_path.is_file()]

async def save_data(notice_dto):
    pass

if __name__ == "__main__":
    asyncio.run(main())