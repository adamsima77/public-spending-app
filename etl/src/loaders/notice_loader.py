import json
from typing import Dict, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import Database
from core.logger import Logger
from models.notice import NoticeDto
from models.organization import OrganizationDto
from models.lot import LotDto
from models.procedure import ProcedureDto

class NoticeLoader:
    def __init__(self, db: Database, logger: Optional[Logger] = None):
        self.db = db
        self._logger = logger

    async def upsert_notice(self, notice_dto: NoticeDto, db_file_id: Optional[int] = None) -> None:
        if not notice_dto.notice_id or not notice_dto.notice_version:
            if self._logger:
                await self._logger.log(
                    "warning",
                    "Notice bez notice_id/notice_version, preskakujem",
                    context={"extra_fields_keys": list(notice_dto.extra_fields.keys())[:10]},
                    file_id=db_file_id,
                )
            return

        async with self.db.transaction() as session:
            org_ids: Dict[int, int] = {}
            for index, org in enumerate(notice_dto.organizations):
                org_ids[index] = await self._upsert_organization(session, org)

            buyer_id = self._resolve_org_db_id(notice_dto, notice_dto.procedure.buyer, org_ids)

            procedure_id = await self._upsert_procedure(
                session, notice_dto.procedure, buyer_id
            )

            for lot in notice_dto.lots:
                await self._upsert_lot(session, lot, procedure_id)

            await self._upsert_notice_row(session, notice_dto, procedure_id)

        if self._logger:
            await self._logger.log(
                "info",
                f"Notice uložený: {notice_dto.notice_id}",
                context={
                    "organizations": len(notice_dto.organizations),
                    "lots": len(notice_dto.lots),
                },
                file_id=db_file_id,
            )

    def _resolve_org_db_id(
        self,
        notice_dto: NoticeDto,
        org: Optional[OrganizationDto],
        org_ids: Dict[int, int],
    ) -> Optional[int]:
        if org is None:
            return None
        for index, candidate in enumerate(notice_dto.organizations):
            if candidate is org:
                return org_ids.get(index)
        return None

    async def _upsert_organization(self, session: AsyncSession, org: OrganizationDto) -> int:
        if org.cin:
            query = """
                INSERT INTO organizations (cin, tin, name, town, country, extra_fields, created_at, updated_at)
                VALUES (:cin, :tin, :name, :town, :country, CAST(:extra_fields AS jsonb), now(), now())
                ON CONFLICT (cin) DO UPDATE SET
                    tin = EXCLUDED.tin,
                    name = EXCLUDED.name,
                    town = EXCLUDED.town,
                    country = EXCLUDED.country,
                    extra_fields = EXCLUDED.extra_fields,
                    updated_at = now()
                RETURNING id
            """
        else:
            query = """
                INSERT INTO organizations (cin, tin, name, town, country, extra_fields, created_at, updated_at)
                VALUES (:cin, :tin, :name, :town, :country, CAST(:extra_fields AS jsonb), now(), now())
                RETURNING id
            """

        result = await session.execute(
            text(query),
            {
                "cin": org.cin,
                "tin": org.tin,
                "name": org.name,
                "town": org.town,
                "country": org.country,
                "extra_fields": json.dumps(org.extra_fields),
            },
        )
        return result.scalar_one()

    def _parse_decimal(self, value: Optional[str]) -> Optional[float]:
        if value is None:
            return None
        cleaned = value.replace(" ", "").replace("\xa0", "").replace(",", ".")
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    async def _upsert_procedure(
    self, session: AsyncSession, procedure: ProcedureDto, buyer_id: Optional[int]
    ) -> Optional[int]:
        if not procedure.reference:
            return None

        extra_fields = dict(procedure.extra_fields)
        if procedure.provider_ref:
            extra_fields["provider_ref"] = procedure.provider_ref

        query = """
            INSERT INTO procedures (procedure_reference, buyer_id, procedure_type, main_cpv, total_value, currency, title, description, extra_fields, created_at, updated_at)
            VALUES (:reference, :buyer_id, :procedure_type, :main_cpv, :total_value, :currency, :title, :description, CAST(:extra_fields AS jsonb), now(), now())
            ON CONFLICT (procedure_reference, buyer_id) DO UPDATE SET
                procedure_type = EXCLUDED.procedure_type,
                main_cpv = EXCLUDED.main_cpv,
                total_value = EXCLUDED.total_value,
                currency = EXCLUDED.currency,
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                extra_fields = EXCLUDED.extra_fields,
                updated_at = now()
           RETURNING id
        """
        result = await session.execute(
            text(query),
            { 
                "reference": procedure.reference,
                "buyer_id": buyer_id,
                "procedure_type": procedure.procedure_type,
                "main_cpv": procedure.main_cpv,
                "total_value": self._parse_decimal(procedure.total_value),
                "currency": procedure.currency,
                "title": procedure.title,
                "description": procedure.description,
                "extra_fields": json.dumps(extra_fields),
            },
        )
        return result.scalar_one()

    async def _upsert_lot(self, session: AsyncSession, lot: LotDto, procedure_id: Optional[int]) -> None:
        if not lot.lot_reference:
            if self._logger:
                await self._logger.log(
                    "warning",
                    "Lot bez lot_reference, preskakujem",
                    context={"procedure_id": procedure_id, "extra_fields_keys": list(lot.extra_fields.keys())[:10]},
                )
            return

        query = """
            INSERT INTO notice_lots (lot_reference, title, main_cpv, award_criterion, value, currency, procedure_id, extra_fields, created_at, updated_at)
            VALUES (:lot_reference, :title, :main_cpv, :award_criterion, :value, :currency, :procedure_id, CAST(:extra_fields AS jsonb), now(), now())
            ON CONFLICT (lot_reference, procedure_id) DO UPDATE SET
                title = EXCLUDED.title,
                main_cpv = EXCLUDED.main_cpv,
                award_criterion = EXCLUDED.award_criterion,
                value = EXCLUDED.value,
                currency = EXCLUDED.currency,
                extra_fields = EXCLUDED.extra_fields,
               updated_at = now()
            """
        await session.execute(
            text(query),
            {
                "lot_reference": lot.lot_reference,
                "title": lot.title,
                "main_cpv": lot.main_cpv,
                "award_criterion": lot.award_criterion,
                "value": self._parse_decimal(lot.value),
                "currency": lot.currency,
                "procedure_id": procedure_id,
                "extra_fields": json.dumps(lot.extra_fields),
            },
        )

    async def _upsert_notice_row(
        self, session: AsyncSession, notice_dto: NoticeDto, procedure_id: Optional[int]
    ) -> None:
        query = """
            INSERT INTO notices (notice_id, notice_version, notice_type, form_type, title, procedure_id, extra_fields, created_at, updated_at)
            VALUES (:notice_id, :notice_version, :notice_type, :form_type, :title, :procedure_id, CAST(:extra_fields AS jsonb), now(), now())
            ON CONFLICT (notice_id, notice_version) DO NOTHING
        """
        await session.execute(
            text(query),
            {
                "notice_id": notice_dto.notice_id,
                "notice_version": notice_dto.notice_version,
                "notice_type": notice_dto.notice_type,
                "form_type": notice_dto.form_type,
                "title": notice_dto.title,
                "procedure_id": procedure_id,
                "extra_fields": json.dumps(notice_dto.extra_fields),
            },
        )