import json

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import Database
from core.logger import Logger
from loaders.award_loader import AwardLoader
from loaders.loader_support import LoaderSupport
from loaders.lot_loader import LotLoader
from loaders.organization_loader import OrganizationLoader
from loaders.procedure_loader import ProcedureLoader
from models.notice import NoticeDto
from models.organization import OrganizationDto


class NoticeLoader(LoaderSupport):
    def __init__(self, db: Database, logger: Logger | None = None) -> None:
        super().__init__(logger)
        self.db = db

        self.organizations = OrganizationLoader(logger)
        self.procedures = ProcedureLoader(logger)
        self.lots = LotLoader(logger)
        self.awards = AwardLoader(logger)
        self._file_counts = {
            "notices": 0,
            "organizations": 0,
            "lots": 0,
            "results": 0,
            "tenders": 0,
            "contracts": 0,
        }

    async def upsert_notice(self, notice_dto: NoticeDto, db_file_id: int | None = None) -> None:
        notice_id = notice_dto.notice_id
        if not notice_id or notice_dto.notice_version is None:
            if self._logger:
                await self._logger.log(
                    "warning",
                    "Notice bez notice_id/notice_version, preskakujem",
                    context={"extra_fields_keys": list(notice_dto.extra_fields.keys())[:10]},
                    file_id=db_file_id,
                )
            return

        async with self.db.transaction() as session:
            is_older_version = await self._is_older_notice_version(
                session, notice_id, notice_dto.notice_version
            )
            org_ids, org_id_by_ref = await self.organizations.upsert_notice_organizations(
                session, notice_dto, notice_id, update_existing=not is_older_version
            )
            buyer_id = self._resolve_org_db_id(notice_dto, notice_dto.procedure.buyer, org_ids)
            await self.procedures.ensure_cpv_code(session, notice_dto.procedure.main_cpv)
            procedure_id = await self.procedures.upsert_procedure(
                session, notice_dto, buyer_id, update_existing=not is_older_version
            )

            lot_id_by_ref = await self.lots.upsert_notice_lots(
                session, notice_dto, procedure_id, update_existing=not is_older_version
            )
            notice_record_id = await self._upsert_notice_row(session, notice_dto, procedure_id)
            await self._refresh_is_latest(session, notice_id)

            lot_results = notice_dto.lot_results
            if procedure_id is not None:
                await self.lots.include_existing_lot_ids_from_db(
                    session, procedure_id, lot_id_by_ref, lot_results, notice_dto
                )
            party_org_ids = await self.organizations.resolve_tendering_party_org_ids(
                notice_dto, org_id_by_ref, db_file_id
            )
            await self.awards.upsert_notice_lot_results(
                session, notice_id, notice_record_id, lot_results, lot_id_by_ref
            )
            tender_ids_by_ref = await self.awards.upsert_notice_lot_tenders(
                session, notice_dto, notice_id, notice_record_id, party_org_ids, lot_id_by_ref
            )
            await self.awards.upsert_notice_contracts(
                session, notice_dto, notice_id, notice_record_id, tender_ids_by_ref
            )
            await self.awards.link_notice_results(session, notice_id, procedure_id)

        if self._logger:
            await self._logger.log(
                "info",
                f"Notice uložený: {notice_dto.notice_id}",
                context={
                    "organizations": len(notice_dto.organizations),
                    "lots": len(notice_dto.lots),
                    "lot_results": len(notice_dto.lot_results),
                    "lot_tenders": len(notice_dto.lot_tenders),
                },
                file_id=db_file_id,
            )

        self._file_counts["notices"] += 1
        self._file_counts["organizations"] += len(notice_dto.organizations)
        self._file_counts["lots"] += len(notice_dto.lots)
        self._file_counts["results"] += len(notice_dto.lot_results)
        self._file_counts["tenders"] += len(notice_dto.lot_tenders)
        self._file_counts["contracts"] += len(notice_dto.settled_contracts)

    def report_file_summary(self, file_name: str) -> None:
        counts = self._file_counts
        print(
            f"Loader: {file_name}: spracované oznámenia={counts['notices']}, "
            f"organizácie={counts['organizations']}, loty={counts['lots']}, "
            f"výsledky={counts['results']}, tendre={counts['tenders']}, "
            f"zmluvy={counts['contracts']}.",
            flush=True,
        )
        for key in counts:
            counts[key] = 0

    async def _is_older_notice_version(
        self, session: AsyncSession, notice_id: str, notice_version: int
    ) -> bool:
        result = await session.execute(
            text("""
                SELECT MAX(notice_version)
                FROM notices
                WHERE notice_id = :notice_id
            """),
            {"notice_id": notice_id},
        )
        latest_version = result.scalar_one()
        return latest_version is not None and notice_version < latest_version

    def _resolve_org_db_id(
        self,
        notice_dto: NoticeDto,
        org: OrganizationDto | None,
        org_ids: dict[int, int],
    ) -> int | None:
        if org is None:
            return None
        for index, candidate in enumerate(notice_dto.organizations):
            if candidate is org:
                return org_ids.get(index)
        return None

    async def _upsert_notice_row(
        self, session: AsyncSession, notice_dto: NoticeDto, procedure_id: int | None
    ) -> int:
        query = """
            INSERT INTO notices (notice_id, notice_version, notice_type, form_type, legal_basis, title, issue_date, published_at, procedure_id, extra_fields, created_at, updated_at)
            VALUES (:notice_id, :notice_version, :notice_type, :form_type, :legal_basis, :title, :issue_date, :published_at, :procedure_id, CAST(:extra_fields AS jsonb), now(), now())
            ON CONFLICT (notice_id, notice_version) DO UPDATE SET
                notice_type = COALESCE(EXCLUDED.notice_type, notices.notice_type),
                form_type = COALESCE(EXCLUDED.form_type, notices.form_type),
                legal_basis = COALESCE(EXCLUDED.legal_basis, notices.legal_basis),
                title = COALESCE(EXCLUDED.title, notices.title),
                issue_date = COALESCE(EXCLUDED.issue_date, notices.issue_date),
                published_at = COALESCE(EXCLUDED.published_at, notices.published_at),
                procedure_id = COALESCE(EXCLUDED.procedure_id, notices.procedure_id),
                extra_fields = notices.extra_fields || EXCLUDED.extra_fields,
                updated_at = now()
            RETURNING id
        """
        result = await session.execute(
            text(query),
            {
                "notice_id": notice_dto.notice_id,
                "notice_version": notice_dto.notice_version,
                "notice_type": notice_dto.notice_type,
                "form_type": notice_dto.form_type,
                "legal_basis": notice_dto.legal_basis,
                "title": notice_dto.title,
                "issue_date": notice_dto.issue_date,
                "published_at": notice_dto.published_at,
                "procedure_id": procedure_id,
                "extra_fields": json.dumps(notice_dto.extra_fields or {}),
            },
        )
        return self._require_int(result.scalar_one(), "notice.id")

    async def _refresh_is_latest(self, session: AsyncSession, notice_id: str) -> None:
        query = """
            UPDATE notices
            SET is_latest = (notice_version = sub.max_version), updated_at = now()
            FROM (
                SELECT MAX(notice_version) AS max_version
                FROM notices
                WHERE notice_id = :notice_id
            ) sub
            WHERE notices.notice_id = :notice_id
              AND notices.is_latest IS DISTINCT FROM (notices.notice_version = sub.max_version)
        """
        await session.execute(text(query), {"notice_id": notice_id})
