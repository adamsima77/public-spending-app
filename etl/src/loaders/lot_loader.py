import json

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from loaders.loader_support import LoaderSupport
from models.lot import LotDto
from models.lot_result import LotResultDto
from models.notice import NoticeDto


class LotLoader(LoaderSupport):
    async def upsert_notice_lots(
        self,
        session: AsyncSession,
        notice_dto: NoticeDto,
        procedure_id: int | None,
        update_existing: bool = True,
    ) -> dict[str, int]:
        lot_ids: dict[str, int] = {}
        for lot in notice_dto.lots:
            await self.ensure_cpv_code(session, lot.main_cpv)
            lot_id = await self._upsert_lot(session, lot, procedure_id, update_existing)
            if lot_id is not None and lot.lot_reference:
                lot_ids[lot.lot_reference] = lot_id
        return lot_ids

    @staticmethod
    def _include_existing_lot_ids(
        lot_ids: dict[str, int],
        lot_results: list[LotResultDto],
        notice_dto: NoticeDto,
    ) -> set[str]:
        missing_refs = {result.lot_reference for result in lot_results if result.lot_reference}
        missing_refs.update(
            tender.lot_reference for tender in notice_dto.lot_tenders if tender.lot_reference
        )
        missing_refs.difference_update(lot_ids)
        return missing_refs

    async def include_existing_lot_ids_from_db(
        self,
        session: AsyncSession,
        procedure_id: int,
        lot_ids: dict[str, int],
        lot_results: list[LotResultDto],
        notice_dto: NoticeDto,
    ) -> None:
        missing_refs = self._include_existing_lot_ids(lot_ids, lot_results, notice_dto)
        if missing_refs:
            lot_ids.update(await self._lookup_existing_lot_ids(session, procedure_id, missing_refs))

    async def _lookup_existing_lot_ids(
        self, session: AsyncSession, procedure_id: int, lot_refs: set[str]
    ) -> dict[str, int]:
        if not lot_refs:
            return {}
        query = """
            SELECT lot_reference, id FROM notice_lots
            WHERE procedure_id = :procedure_id AND lot_reference = ANY(:refs)
        """
        result = await session.execute(
            text(query), {"procedure_id": procedure_id, "refs": list(lot_refs)}
        )
        return {row.lot_reference: row.id for row in result}

    async def _upsert_lot(
        self,
        session: AsyncSession,
        lot: LotDto,
        procedure_id: int | None,
        update_existing: bool = True,
    ) -> int | None:
        if not lot.lot_reference:
            if self._logger:
                await self._logger.log(
                    "warning",
                    "Lot bez lot_reference, preskakujem",
                    context={
                        "procedure_id": procedure_id,
                        "extra_fields_keys": list(lot.extra_fields.keys())[:10],
                    },
                )
            return None

        if procedure_id is None:
            if self._logger:
                await self._logger.log(
                    "warning",
                    "Lot bez procedúry nemožno bezpečne uložiť (NULL by vytváral duplicity), preskakujem",
                    context={"lot_reference": lot.lot_reference},
                )
            return None

        await self.ensure_nuts_code(session, lot.nuts_code)

        if not update_existing:
            existing_id = await session.execute(
                text("""
                    SELECT id FROM notice_lots
                    WHERE lot_reference = :lot_reference AND procedure_id = :procedure_id
                """),
                {"lot_reference": lot.lot_reference, "procedure_id": procedure_id},
            )
            row = existing_id.first()
            if row:
                return self._require_int(row.id, "lot.id")

        query = """
            INSERT INTO notice_lots (
                lot_reference, title, description, estimated_value, estimated_currency, main_cpv, nuts_code,
                place_of_performance, award_criterion, submission_deadline, document_url, detail_url,
                duration_value, duration_unit, framework_max_value, framework_max_currency,
                eu_funded, eordering_allowed, epayment_allowed, einvoicing, variants_allowed,
                reserved_execution, reserved_participation,
                procedure_id, extra_fields, created_at, updated_at
            )
            VALUES (
                :lot_reference, :title, :description, :estimated_value, :estimated_currency, :main_cpv, :nuts_code,
                :place_of_performance, :award_criterion, :submission_deadline, :document_url, :detail_url,
                :duration_value, :duration_unit, :framework_max_value, :framework_max_currency,
                :eu_funded, :eordering_allowed, :epayment_allowed, :einvoicing, :variants_allowed,
                :reserved_execution, :reserved_participation,
                :procedure_id, CAST(:extra_fields AS jsonb), now(), now()
            )
            ON CONFLICT (lot_reference, procedure_id) DO UPDATE SET
                title = COALESCE(EXCLUDED.title, notice_lots.title),
                description = COALESCE(EXCLUDED.description, notice_lots.description),
                estimated_value = COALESCE(EXCLUDED.estimated_value, notice_lots.estimated_value),
                estimated_currency = COALESCE(EXCLUDED.estimated_currency, notice_lots.estimated_currency),
                main_cpv = COALESCE(EXCLUDED.main_cpv, notice_lots.main_cpv),
                nuts_code = COALESCE(EXCLUDED.nuts_code, notice_lots.nuts_code),
                place_of_performance = COALESCE(EXCLUDED.place_of_performance, notice_lots.place_of_performance),
                award_criterion = COALESCE(EXCLUDED.award_criterion, notice_lots.award_criterion),
                submission_deadline = COALESCE(EXCLUDED.submission_deadline, notice_lots.submission_deadline),
                document_url = COALESCE(EXCLUDED.document_url, notice_lots.document_url),
                detail_url = COALESCE(EXCLUDED.detail_url, notice_lots.detail_url),
                duration_value = COALESCE(EXCLUDED.duration_value, notice_lots.duration_value),
                duration_unit = COALESCE(EXCLUDED.duration_unit, notice_lots.duration_unit),
                framework_max_value = COALESCE(EXCLUDED.framework_max_value, notice_lots.framework_max_value),
                framework_max_currency = COALESCE(EXCLUDED.framework_max_currency, notice_lots.framework_max_currency),
                eu_funded = COALESCE(EXCLUDED.eu_funded, notice_lots.eu_funded),
                eordering_allowed = COALESCE(EXCLUDED.eordering_allowed, notice_lots.eordering_allowed),
                epayment_allowed = COALESCE(EXCLUDED.epayment_allowed, notice_lots.epayment_allowed),
                einvoicing = COALESCE(EXCLUDED.einvoicing, notice_lots.einvoicing),
                variants_allowed = COALESCE(EXCLUDED.variants_allowed, notice_lots.variants_allowed),
                reserved_execution = COALESCE(EXCLUDED.reserved_execution, notice_lots.reserved_execution),
                reserved_participation = COALESCE(EXCLUDED.reserved_participation, notice_lots.reserved_participation),
                extra_fields = notice_lots.extra_fields || EXCLUDED.extra_fields,
                updated_at = now()
            RETURNING id
        """
        result = await session.execute(
            text(query),
            {
                "lot_reference": lot.lot_reference,
                "title": lot.title,
                "description": lot.description,
                "estimated_value": lot.estimated_value,
                "estimated_currency": lot.estimated_currency,
                "main_cpv": lot.main_cpv,
                "nuts_code": lot.nuts_code,
                "place_of_performance": lot.place_of_performance,
                "award_criterion": lot.award_criterion,
                "submission_deadline": lot.submission_deadline,
                "document_url": lot.document_url,
                "detail_url": lot.detail_url,
                "duration_value": lot.duration_value,
                "duration_unit": lot.duration_unit,
                "framework_max_value": lot.framework_max_value,
                "framework_max_currency": lot.framework_max_currency,
                "eu_funded": lot.eu_funded,
                "eordering_allowed": lot.eordering_allowed,
                "epayment_allowed": lot.epayment_allowed,
                "einvoicing": lot.einvoicing,
                "variants_allowed": lot.variants_allowed,
                "reserved_execution": lot.reserved_execution,
                "reserved_participation": lot.reserved_participation,
                "procedure_id": procedure_id,
                "extra_fields": json.dumps(lot.extra_fields or {}),
            },
        )
        return self._require_int(result.scalar_one(), "lot.id")
