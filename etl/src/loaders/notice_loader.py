import json
import re
from typing import Any, Dict, Optional, Set
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

        self._known_nuts_codes: Set[str] = set()

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

                await self._ensure_nuts_code(session, org.nuts_code)
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

    async def _ensure_nuts_code(self, session: AsyncSession, nuts_code: Optional[str]) -> None:
        if not nuts_code:
            return

        code = str(nuts_code).strip().upper()[:10]
        if not code or code in self._known_nuts_codes:
            return

        level = max(1, min(len(code), 5))

        query = """
            INSERT INTO nut_codes (code, name_sk, level, parent_code, created_at, updated_at)
            VALUES (:code, :name_sk, :level, NULL, now(), now())
            ON CONFLICT (code) DO NOTHING
        """
        await session.execute(
            text(query),
            {
                "code": code,
                "name_sk": f"NUTS {code}",
                "level": level,
            },
        )
        self._known_nuts_codes.add(code)

    async def _upsert_organization(self, session: AsyncSession, org: OrganizationDto) -> int:
        if org.cin:
            query = """
                INSERT INTO organizations (cin, tin, name, address, street_name, street_number, phone, town, postal_code, country, nuts_code, extra_fields, created_at, updated_at)
                VALUES (:cin, :tin, :name, :address, :street_name, :street_number, :phone, :town, :postal_code, :country, :nuts_code, CAST(:extra_fields AS jsonb), now(), now())
                ON CONFLICT (cin) DO UPDATE SET
                    tin = COALESCE(EXCLUDED.tin, organizations.tin),
                    name = COALESCE(EXCLUDED.name, organizations.name),
                    address = COALESCE(EXCLUDED.address, organizations.address),
                    street_name = COALESCE(EXCLUDED.street_name, organizations.street_name),
                    street_number = COALESCE(EXCLUDED.street_number, organizations.street_number),
                    phone = COALESCE(EXCLUDED.phone, organizations.phone),
                    town = COALESCE(EXCLUDED.town, organizations.town),
                    postal_code = COALESCE(EXCLUDED.postal_code, organizations.postal_code),
                    country = COALESCE(EXCLUDED.country, organizations.country),
                    nuts_code = COALESCE(EXCLUDED.nuts_code, organizations.nuts_code),
                    extra_fields = organizations.extra_fields || EXCLUDED.extra_fields,
                    updated_at = now()
                RETURNING id
            """
        else:
            query = """
                INSERT INTO organizations (cin, tin, name, address, street_name, street_number, phone, town, postal_code, country, nuts_code, extra_fields, created_at, updated_at)
                VALUES (:cin, :tin, :name, :address, :street_name, :street_number, :phone, :town, :postal_code, :country, :nuts_code, CAST(:extra_fields AS jsonb), now(), now())
                RETURNING id
            """

        result = await session.execute(
            text(query),
            {
                "cin": org.cin,
                "tin": org.tin,
                "name": org.name,
                "address": org.address,
                "street_name": org.street_name,
                "street_number": org.street_number,
                "phone": org.phone,
                "town": org.town,
                "postal_code": org.postal_code,
                "country": org.country,
                "nuts_code": org.nuts_code,
                "extra_fields": json.dumps(org.extra_fields or {}),
            },
        )
        return result.scalar_one()

    def _parse_decimal(self, value: Optional[str]) -> Optional[float]:
        if value is None:
            return None
        cleaned = str(value).replace(" ", "").replace("\xa0", "").replace(",", ".")
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    def _parse_version(self, value: Any) -> int:
        if isinstance(value, int):
            return value
        if not value:
            return 1
        match = re.search(r"\d+", str(value))
        return int(match.group(0)) if match else 1

    async def _upsert_procedure(
        self, session: AsyncSession, procedure: ProcedureDto, buyer_id: Optional[int]
    ) -> Optional[int]:
        if not procedure.reference:
            return None

        await self._ensure_nuts_code(session, procedure.nuts_code)

        extra_fields = dict(procedure.extra_fields or {})
        if procedure.provider_ref:
            extra_fields["provider_ref"] = procedure.provider_ref

        query = """
            INSERT INTO procedures (procedure_reference, buyer_id, procedure_type, contract_type, main_cpv, total_value, currency, nuts_code, title, description, buyer_profile_url, extra_fields, created_at, updated_at)
            VALUES (:reference, :buyer_id, :procedure_type, :contract_type, :main_cpv, :total_value, :currency, :nuts_code, :title, :description, :buyer_profile_url, CAST(:extra_fields AS jsonb), now(), now())
            ON CONFLICT (procedure_reference, buyer_id) DO UPDATE SET
                procedure_type = COALESCE(EXCLUDED.procedure_type, procedures.procedure_type),
                contract_type = COALESCE(EXCLUDED.contract_type, procedures.contract_type),
                main_cpv = COALESCE(EXCLUDED.main_cpv, procedures.main_cpv),
                total_value = COALESCE(EXCLUDED.total_value, procedures.total_value),
                currency = COALESCE(EXCLUDED.currency, procedures.currency),
                nuts_code = COALESCE(EXCLUDED.nuts_code, procedures.nuts_code),
                title = COALESCE(EXCLUDED.title, procedures.title),
                description = COALESCE(EXCLUDED.description, procedures.description),
                buyer_profile_url = COALESCE(EXCLUDED.buyer_profile_url, procedures.buyer_profile_url),
                extra_fields = procedures.extra_fields || EXCLUDED.extra_fields,
                updated_at = now()
            RETURNING id
        """
        result = await session.execute(
            text(query),
            {
                "reference": procedure.reference,
                "buyer_id": buyer_id,
                "procedure_type": procedure.procedure_type,
                "contract_type": procedure.contract_type,
                "main_cpv": procedure.main_cpv,
                "total_value": self._parse_decimal(procedure.total_value),
                "currency": procedure.currency,
                "nuts_code": procedure.nuts_code,
                "title": procedure.title,
                "description": procedure.description,
                "buyer_profile_url": procedure.buyer_profile_url,
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

        await self._ensure_nuts_code(session, lot.nuts_code)

        query = """
            INSERT INTO notice_lots (lot_reference, title, description, value, currency, main_cpv, nuts_code, award_criterion, submission_deadline, document_url, detail_url, procedure_id, extra_fields, created_at, updated_at)
            VALUES (:lot_reference, :title, :description, :value, :currency, :main_cpv, :nuts_code, :award_criterion, :submission_deadline, :document_url, :detail_url, :procedure_id, CAST(:extra_fields AS jsonb), now(), now())
            ON CONFLICT (lot_reference, procedure_id) DO UPDATE SET
                title = COALESCE(EXCLUDED.title, notice_lots.title),
                description = COALESCE(EXCLUDED.description, notice_lots.description),
                value = COALESCE(EXCLUDED.value, notice_lots.value),
                currency = COALESCE(EXCLUDED.currency, notice_lots.currency),
                main_cpv = COALESCE(EXCLUDED.main_cpv, notice_lots.main_cpv),
                nuts_code = COALESCE(EXCLUDED.nuts_code, notice_lots.nuts_code),
                award_criterion = COALESCE(EXCLUDED.award_criterion, notice_lots.award_criterion),
                submission_deadline = COALESCE(EXCLUDED.submission_deadline, notice_lots.submission_deadline),
                document_url = COALESCE(EXCLUDED.document_url, notice_lots.document_url),
                detail_url = COALESCE(EXCLUDED.detail_url, notice_lots.detail_url),
                extra_fields = notice_lots.extra_fields || EXCLUDED.extra_fields,
                updated_at = now()
            """
        await session.execute(
            text(query),
            {
                "lot_reference": lot.lot_reference,
                "title": lot.title,
                "description": lot.description,
                "value": self._parse_decimal(lot.value),
                "currency": lot.currency,
                "main_cpv": lot.main_cpv,
                "nuts_code": lot.nuts_code,
                "award_criterion": lot.award_criterion,
                "submission_deadline": lot.submission_deadline,
                "document_url": lot.document_url,
                "detail_url": lot.detail_url,
                "procedure_id": procedure_id,
                "extra_fields": json.dumps(lot.extra_fields or {}),
            },
        )

    async def _upsert_notice_row(
        self, session: AsyncSession, notice_dto: NoticeDto, procedure_id: Optional[int]
    ) -> None:
        query = """
            INSERT INTO notices (notice_id, notice_version, notice_type, form_type, legal_basis, title, procedure_id, extra_fields, created_at, updated_at)
            VALUES (:notice_id, :notice_version, :notice_type, :form_type, :legal_basis, :title, :procedure_id, CAST(:extra_fields AS jsonb), now(), now())
            ON CONFLICT (notice_id, notice_version) DO NOTHING
        """
        await session.execute(
            text(query),
            {
                "notice_id": notice_dto.notice_id,
                "notice_version": self._parse_version(notice_dto.notice_version),
                "notice_type": notice_dto.notice_type,
                "form_type": notice_dto.form_type,
                "legal_basis": notice_dto.legal_basis,
                "title": notice_dto.title,
                "procedure_id": procedure_id,
                "extra_fields": json.dumps(notice_dto.extra_fields or {}),
            },
        )