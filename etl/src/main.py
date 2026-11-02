import asyncio
import json
from pathlib import Path
from typing import Any

import aiofiles
import ijson
import redis.asyncio as redis

import config
from core.database import Database, db
from core.logger import Logger
from core.notification import Notification
from downloaders.download_data import Download
from loaders.notice_loader import NoticeLoader
from parsers.eforms_parser import EformsParser, EformsParserConfig
from parsers.other_format_parser import OtherFormatParser
from parsers.xml_parser import XmlParser


async def main() -> None:
    async with redis.from_url(config.settings.REDIS_URL) as redis_client:
        logger = Logger(db, redis_client=redis_client)
        notifier = Notification(logger=logger)

        downloader = Download(logger=logger)
        eforms_parser = _create_eforms_parser(logger)
        xml_parser = XmlParser(logger=logger)
        other_format_parser = OtherFormatParser(logger=logger)
        notice_loader = NoticeLoader(db, logger=logger)

        try:
            print("ETL: začínam sťahovanie údajov.", flush=True)
            await downloader.download_data()
            files = get_files_to_process(config.DOWNLOAD_DIR)
            await logger.log("info", f"Nájdených {len(files)} súborov na spracovanie.")

            json_files = [f for f in files if f.suffix == ".json"]
            print(f"ETL: nájdených {len(json_files)} JSON súborov na spracovanie.", flush=True)
            file_id_map = await _load_file_id_map(db, [f.stem for f in json_files])
            parsed_ok, parsed_failed, failed_files = await _process_files(
                json_files,
                file_id_map,
                eforms_parser,
                xml_parser,
                other_format_parser,
                notice_loader,
                logger,
            )

            if parsed_failed > 0:
                print(
                    f"ETL: beh dokončený s chybami — úspešné súbory={parsed_ok}, "
                    f"zlyhané súbory={parsed_failed}.",
                    flush=True,
                )
                await notifier.send_discord_alert(
                    "ETL beh dokončený s chybami",
                    context={
                        "stiahnuté": (
                            f"{downloader.number_of_downloaded_links}/"
                            f"{downloader.number_of_all_links}"
                        ),
                        "spracované úspešne": parsed_ok,
                        "zlyhané súbory": parsed_failed,
                        "zoznam zlyhaných": ", ".join(failed_files[:10]) or "-",
                    },
                )
            else:
                print(
                    f"ETL: beh dokončený úspešne — {parsed_ok} súborov spracovaných.",
                    flush=True,
                )
                await logger.log(
                    "info",
                    f"ETL beh dokončený bez chýb: {parsed_ok} súborov spracovaných.",
                )
        except Exception as e:
            print(f"ETL: kritická chyba, beh bol prerušený: {e}", flush=True)
            await logger.log("error", f"ETL beh zlyhal kriticky: {e}")
            await notifier.send_discord_alert(
                "ETL beh zlyhal kriticky a bol prerušený",
                context={"error": str(e)},
            )
            raise
        finally:
            await db.close()


async def _process_files(
    files: list[Path],
    file_id_map: dict[str, int],
    eforms_parser: EformsParser,
    xml_parser: XmlParser,
    other_format_parser: OtherFormatParser,
    notice_loader: NoticeLoader,
    logger: Logger,
) -> tuple[int, int, list[str]]:
    parsed_ok = 0
    failed_files: list[str] = []
    for file_path in files:
        db_file_id = file_id_map.get(file_path.stem)
        print(f"ETL: spracúvam súbor {file_path.name}.", flush=True)
        try:
            await _process_bulletin_file(
                file_path,
                eforms_parser,
                xml_parser,
                other_format_parser,
                notice_loader,
                db_file_id,
            )
            if db_file_id is not None:
                await _mark_file_parsed(db, db_file_id)
            file_path.unlink()
            parsed_ok += 1
            print(f"ETL: súbor {file_path.name} dokončený.", flush=True)
        except Exception as error:
            print(f"ETL: súbor {file_path.name} zlyhal: {error}", flush=True)
            await logger.log(
                "error",
                f"Spracovanie súboru zlyhalo: {error}",
                file_id=db_file_id,
            )
            if db_file_id is not None:
                await _mark_file_failed(db, db_file_id)
            failed_files.append(file_path.stem)
        finally:
            notice_loader.report_file_summary(file_path.name)
            await xml_parser.report_file(file_path.name, db_file_id)
            await other_format_parser.report_file(file_path.name, db_file_id)
    return parsed_ok, len(failed_files), failed_files


def _create_eforms_parser(logger: Logger) -> EformsParser:
    return EformsParser(
        EformsParserConfig(
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


async def _process_bulletin_file(
    file_path: Path,
    eforms_parser: EformsParser,
    xml_parser: XmlParser,
    other_format_parser: OtherFormatParser,
    notice_loader: NoticeLoader,
    db_file_id: int | None,
) -> None:
    async with aiofiles.open(file_path, mode="rb") as bulletin:
        bulletin_publish_date = None
        async for value in ijson.items_async(bulletin, "bulletinPublishDate"):
            bulletin_publish_date = eforms_parser.parse_datetime(value)
            break
        await bulletin.seek(0)

        async for item in ijson.items_async(bulletin, "bulletinItemList.item"):
            submission_id = item.get("submissionId") if isinstance(item, dict) else None
            item_data = item.get("itemData") if isinstance(item, dict) else None
            if not isinstance(item_data, str) or not item_data.strip():
                other_format_parser.handle_unknown(submission_id, "missing itemData")
                continue

            if item_data.lstrip("\ufeff \t\r\n").startswith("<"):
                xml_parser.handle(submission_id)
                continue

            try:
                inner: Any = json.loads(item_data)
            except json.JSONDecodeError as error:
                other_format_parser.handle_unknown(submission_id, str(error))
                continue

            if not isinstance(inner, dict) or not isinstance(inner.get("components"), list):
                other_format_parser.handle_unknown(submission_id, "unrecognized JSON structure")
                continue

            if not eforms_parser.has_eforms_sdk(inner):
                other_format_parser.handle_json(inner, submission_id)
                continue

            notice_dto = await eforms_parser.parse_notice(
                inner,
                bulletin_publish_date,
                db_file_id=db_file_id,
                submission_id=submission_id,
            )
            if notice_dto is not None:
                await notice_loader.upsert_notice(notice_dto, db_file_id=db_file_id)


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
