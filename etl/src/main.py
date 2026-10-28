import asyncio
from pathlib import Path

import redis.asyncio as redis

import config
from core.database import Database, db
from core.logger import Logger
from core.notification import Notification
from downloaders.download_data import Download
from loaders.notice_loader import NoticeLoader
from parsers.json_parser import JsonParser, JsonParserConfig


async def main() -> None:
    async with redis.from_url(config.settings.REDIS_URL) as redis_client:
        logger = Logger(db, redis_client=redis_client)
        notifier = Notification(logger=logger)

        downloader = Download(logger=logger)
        json_parser = JsonParser(
            JsonParserConfig(
                notice_fields=config.NOTICE_FIELDS,
                organization_fields=config.ORGANIZATION_FIELDS,
                procedure_fields=config.PROCEDURE_FIELDS,
                lot_fields=config.LOT_FIELDS,
                lot_result_fields=config.LOT_RESULT_FIELDS,
                submission_stat_fields=config.SUBMISSION_STAT_FIELDS,
                lot_tender_fields=config.LOT_TENDER_FIELDS,
                settled_contract_fields=config.SETTLED_CONTRACT_FIELDS,
                anchor_organization=config.ANCHOR_ORGANIZATION,
                anchor_lot=config.ANCHOR_LOT,
                anchor_lot_result=config.ANCHOR_LOT_RESULT,
                anchor_submission_stat=config.ANCHOR_SUBMISSION_STAT,
                anchor_lot_tender=config.ANCHOR_LOT_TENDER,
                anchor_tendering_party=config.ANCHOR_TENDERING_PARTY,
                anchor_settled_contract=config.ANCHOR_SETTLED_CONTRACT,
                tenderer_org_ref_key=config.TENDERER_ORG_REF_KEY,
                list_fields=frozenset(config.LIST_FIELDS),
            ),
            logger=logger,
        )
        notice_loader = NoticeLoader(db, logger=logger)

        parsed_ok = 0
        parsed_failed = 0
        failed_files: list[str] = []

        try:
            await downloader.download_data()
            files = get_files_to_process(config.DOWNLOAD_DIR)
            await logger.log("info", f"Nájdených {len(files)} súborov na spracovanie.")

            json_files = [f for f in files if f.suffix == ".json"]
            file_id_map = await _load_file_id_map(db, [f.stem for f in json_files])

            for file_path in json_files:
                db_file_id = file_id_map.get(file_path.stem)
                try:
                    async for notice_dto in json_parser.parse_file(
                        str(file_path), db_file_id=db_file_id
                    ):
                        await notice_loader.upsert_notice(notice_dto, db_file_id=db_file_id)
                    if db_file_id is not None:
                        await _mark_file_parsed(db, db_file_id)
                    file_path.unlink()
                    parsed_ok += 1
                except Exception as e:
                    await logger.log(
                        "error",
                        f"Spracovanie súboru zlyhalo: {e}",
                        file_id=db_file_id,
                    )
                    if db_file_id is not None:
                        await _mark_file_failed(db, db_file_id)
                    parsed_failed += 1
                    failed_files.append(file_path.stem)

        except Exception as e:
            await logger.log("error", f"ETL beh zlyhal kriticky: {e}")
            await notifier.send_discord_alert(
                "ETL beh zlyhal kriticky a bol prerušený",
                context={"error": str(e)},
            )
            raise
        finally:
            await db.close()

        if parsed_failed > 0:
            await notifier.send_discord_alert(
                "ETL beh dokončený s chybami",
                context={
                    "stiahnuté": (
                        f"{downloader.number_of_downloaded_links}/{downloader.number_of_all_links}"
                    ),
                    "spracované úspešne": parsed_ok,
                    "zlyhané súbory": parsed_failed,
                    "zoznam zlyhaných": ", ".join(failed_files[:10]) or "-",
                },
            )
        else:
            await logger.log(
                "info",
                f"ETL beh dokončený bez chýb: {parsed_ok} súborov spracovaných.",
            )


async def _load_file_id_map(database: Database, stems: list[str]) -> dict[str, int]:
    if not stems:
        return {}
    rows = await database.fetch_all(
        "SELECT id, file_id FROM downloaded_files WHERE file_id = ANY(:stems)",
        {"stems": stems},
    )
    return {row["file_id"]: row["id"] for row in rows}


def get_files_to_process(download_dir: Path) -> list[Path]:
    if not download_dir.exists():
        return []

    return sorted(file_path for file_path in download_dir.glob("*") if file_path.is_file())


async def _mark_file_parsed(database: Database, db_file_id: int) -> None:
    await database.execute(
        """
        UPDATE downloaded_files
        SET status_id = (SELECT id FROM etl_statuses WHERE name = 'parsed'),
            parsed_at = now(),
            updated_at = now()
        WHERE id = :db_file_id
        """,
        {"db_file_id": db_file_id},
    )


async def _mark_file_failed(database: Database, db_file_id: int) -> None:
    await database.execute(
        """
        UPDATE downloaded_files
        SET status_id = (SELECT id FROM etl_statuses WHERE name = 'failed'),
            updated_at = now()
        WHERE id = :db_file_id
        """,
        {"db_file_id": db_file_id},
    )


if __name__ == "__main__":
    asyncio.run(main())
