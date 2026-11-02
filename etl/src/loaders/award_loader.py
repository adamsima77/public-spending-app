import json
from functools import partial

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from loaders.loader_support import LoaderSupport
from models.lot_result import LotResultDto
from models.lot_tender import LotTenderDto
from models.notice import NoticeDto
from models.settled_contract import SettledContractDto


class AwardLoader(LoaderSupport):
    async def upsert_notice_lot_results(
        self,
        session: AsyncSession,
        notice_id: str,
        notice_record_id: int,
        lot_results: list[LotResultDto],
        lot_id_by_ref: dict[str, int],
    ) -> None:
        for lot_result in lot_results:
            await self._guarded(
                session,
                "lot_result",
                {"notice_id": notice_id, "lot_reference": lot_result.lot_reference},
                partial(
                    self._upsert_lot_result,
                    session,
                    notice_id,
                    notice_record_id,
                    lot_result,
                    lot_id_by_ref.get(lot_result.lot_reference)
                    if lot_result.lot_reference
                    else None,
                ),
            )

    async def upsert_notice_lot_tenders(
        self,
        session: AsyncSession,
        notice_dto: NoticeDto,
        notice_id: str,
        notice_record_id: int,
        party_org_ids: dict[str, list[int]],
        lot_id_by_ref: dict[str, int],
    ) -> dict[str, int]:
        tender_ids_by_ref: dict[str, int] = {}
        if not notice_dto.lot_tenders:
            return tender_ids_by_ref
        for tender in notice_dto.lot_tenders:
            lot_id = lot_id_by_ref.get(tender.lot_reference) if tender.lot_reference else None
            tenderer_org_ids = party_org_ids.get(tender.tendering_party_ref or "", [])
            tender_id = await self._guarded(
                session,
                "lot_tender",
                {"notice_id": notice_id, "lot_reference": tender.lot_reference},
                partial(
                    self._upsert_lot_tender,
                    session,
                    notice_id,
                    notice_record_id,
                    tender,
                    lot_id,
                    tenderer_org_ids,
                ),
            )
            if tender_id is not None and tender.tender_ref:
                tender_ids_by_ref[tender.tender_ref] = tender_id
        return tender_ids_by_ref

    async def link_notice_results(
        self, session: AsyncSession, notice_id: str, procedure_id: int | None
    ) -> None:
        if procedure_id is not None:
            await self._guarded(
                session,
                "link_results",
                {"notice_id": notice_id, "procedure_id": procedure_id},
                partial(self._link_results, session, procedure_id),
            )

    async def upsert_notice_contracts(
        self,
        session: AsyncSession,
        notice_dto: NoticeDto,
        notice_id: str,
        notice_record_id: int,
        tender_ids_by_ref: dict[str, int],
    ) -> None:
        if not notice_dto.settled_contracts:
            return
        for index, contract in enumerate(notice_dto.settled_contracts):
            await self._guarded(
                session,
                "settled_contract",
                {
                    "notice_id": notice_id,
                    "contract_ref": contract.contract_ref,
                    "tender_refs": contract.tender_refs,
                },
                partial(
                    self._upsert_settled_contract,
                    session,
                    notice_id,
                    notice_record_id,
                    contract,
                    tender_ids_by_ref,
                    index,
                ),
            )

    async def _upsert_lot_result(
        self,
        session: AsyncSession,
        notice_id: str,
        notice_record_id: int,
        lot_result: LotResultDto,
        lot_id: int | None,
    ) -> int | None:
        if not lot_result.lot_reference:
            return None

        query = """
            INSERT INTO lot_results (
                notice_id, notice_record_id, lot_reference, lot_id, award_outcome, non_award_reason,
                lowest_offer_value, lowest_offer_currency, highest_offer_value, highest_offer_currency,
                tender_refs, contract_refs, extra_fields, created_at, updated_at
            )
            VALUES (
                :notice_id, :notice_record_id, :lot_reference, :lot_id, :award_outcome, :non_award_reason,
                :lowest_offer_value, :lowest_offer_currency, :highest_offer_value, :highest_offer_currency,
                CAST(:tender_refs AS jsonb), CAST(:contract_refs AS jsonb), CAST(:extra_fields AS jsonb), now(), now()
            )
            ON CONFLICT (notice_record_id, lot_reference) DO UPDATE SET
                lot_id = COALESCE(EXCLUDED.lot_id, lot_results.lot_id),
                award_outcome = COALESCE(EXCLUDED.award_outcome, lot_results.award_outcome),
                non_award_reason = COALESCE(EXCLUDED.non_award_reason, lot_results.non_award_reason),
                lowest_offer_value = COALESCE(EXCLUDED.lowest_offer_value, lot_results.lowest_offer_value),
                lowest_offer_currency = COALESCE(EXCLUDED.lowest_offer_currency, lot_results.lowest_offer_currency),
                highest_offer_value = COALESCE(EXCLUDED.highest_offer_value, lot_results.highest_offer_value),
                highest_offer_currency = COALESCE(EXCLUDED.highest_offer_currency, lot_results.highest_offer_currency),
                tender_refs = CASE WHEN EXCLUDED.tender_refs <> '[]'::jsonb
                                   THEN EXCLUDED.tender_refs ELSE lot_results.tender_refs END,
                contract_refs = CASE WHEN EXCLUDED.contract_refs <> '[]'::jsonb
                                     THEN EXCLUDED.contract_refs ELSE lot_results.contract_refs END,
                extra_fields = lot_results.extra_fields || EXCLUDED.extra_fields,
                updated_at = now()
            RETURNING id
        """
        result = await session.execute(
            text(query),
            {
                "notice_id": notice_id,
                "notice_record_id": notice_record_id,
                "lot_reference": lot_result.lot_reference,
                "lot_id": lot_id,
                "award_outcome": lot_result.award_outcome,
                "non_award_reason": lot_result.non_award_reason,
                "lowest_offer_value": lot_result.lowest_offer_value,
                "lowest_offer_currency": lot_result.lowest_offer_currency,
                "highest_offer_value": lot_result.highest_offer_value,
                "highest_offer_currency": lot_result.highest_offer_currency,
                "tender_refs": json.dumps(lot_result.tender_refs),
                "contract_refs": json.dumps(lot_result.contract_refs),
                "extra_fields": json.dumps(lot_result.extra_fields or {}),
            },
        )
        lot_result_id = self._require_int(result.scalar_one(), "lot_result.id")

        for stat in lot_result.submission_stats:
            if not stat.category_code:
                continue
            stat_query = """
                INSERT INTO lot_result_submission_stats (lot_result_id, category_code, count, created_at, updated_at)
                VALUES (:lot_result_id, :category_code, :count, now(), now())
                ON CONFLICT (lot_result_id, category_code) DO UPDATE SET
                    count = COALESCE(EXCLUDED.count, lot_result_submission_stats.count),
                    updated_at = now()
            """
            await session.execute(
                text(stat_query),
                {
                    "lot_result_id": lot_result_id,
                    "category_code": stat.category_code,
                    "count": stat.count,
                },
            )

        return lot_result_id

    async def _upsert_lot_tender(
        self,
        session: AsyncSession,
        notice_id: str,
        notice_record_id: int,
        tender: LotTenderDto,
        lot_id: int | None,
        tenderer_org_ids: list[int] | None = None,
    ) -> int | None:
        if not tender.lot_reference:
            return None

        tender_key = (
            tender.tender_ref or f"auto:{tender.lot_reference}|{tender.tendering_party_ref or ''}"
        )[:64]

        query = """
            INSERT INTO lot_tenders (
                notice_id, notice_record_id, lot_reference, lot_id, tender_ref, tender_value, tender_currency,
                tendering_party_ref, rank, subcontracting, extra_fields, created_at, updated_at
            )
            VALUES (
                :notice_id, :notice_record_id, :lot_reference, :lot_id, :tender_ref, :tender_value, :tender_currency,
                :tendering_party_ref, :rank, :subcontracting, CAST(:extra_fields AS jsonb), now(), now()
            )
            ON CONFLICT (notice_record_id, tender_ref) DO UPDATE SET
                lot_reference = EXCLUDED.lot_reference,
                tendering_party_ref = EXCLUDED.tendering_party_ref,
                lot_id = COALESCE(EXCLUDED.lot_id, lot_tenders.lot_id),
                tender_ref = COALESCE(EXCLUDED.tender_ref, lot_tenders.tender_ref),
                tender_value = COALESCE(EXCLUDED.tender_value, lot_tenders.tender_value),
                tender_currency = COALESCE(EXCLUDED.tender_currency, lot_tenders.tender_currency),
                rank = COALESCE(EXCLUDED.rank, lot_tenders.rank),
                subcontracting = COALESCE(EXCLUDED.subcontracting, lot_tenders.subcontracting),
                extra_fields = lot_tenders.extra_fields || EXCLUDED.extra_fields,
                updated_at = now()
            RETURNING id
        """
        result = await session.execute(
            text(query),
            {
                "notice_id": notice_id,
                "notice_record_id": notice_record_id,
                "lot_reference": tender.lot_reference,
                "lot_id": lot_id,
                "tender_ref": tender_key,
                "tender_value": tender.tender_value,
                "tender_currency": tender.tender_currency,
                "tendering_party_ref": tender.tendering_party_ref or "",
                "rank": tender.rank,
                "subcontracting": tender.subcontracting,
                "extra_fields": json.dumps(tender.extra_fields or {}),
            },
        )
        lot_tender_id = self._require_int(result.scalar_one(), "lot_tender.id")

        org_ids = sorted({int(i) for i in (tenderer_org_ids or [])})
        if org_ids:
            await session.execute(
                text("""
                    DELETE FROM lot_tender_organizations
                    WHERE lot_tender_id = :id AND organization_id <> ALL(CAST(:ids AS bigint[]))
                """),
                {"id": lot_tender_id, "ids": org_ids},
            )
            await session.execute(
                text("""
                    INSERT INTO lot_tender_organizations (lot_tender_id, organization_id, created_at, updated_at)
                    SELECT :id, x, now(), now() FROM unnest(CAST(:ids AS bigint[])) AS x
                    ON CONFLICT (lot_tender_id, organization_id) DO UPDATE SET updated_at = now()
                """),
                {"id": lot_tender_id, "ids": org_ids},
            )
        return lot_tender_id

    async def _link_results(self, session: AsyncSession, procedure_id: int) -> None:
        update_queries = (
            """
                    UPDATE lot_results t SET lot_id = nl.id, updated_at = now()
                    FROM notices n
                    JOIN notice_lots nl ON nl.procedure_id = n.procedure_id
                    WHERE n.procedure_id = :pid
                      AND t.notice_record_id = n.id
                      AND t.lot_id IS NULL
                      AND nl.lot_reference = t.lot_reference
                """,
            """
                    UPDATE lot_tenders t SET lot_id = nl.id, updated_at = now()
                    FROM notices n
                    JOIN notice_lots nl ON nl.procedure_id = n.procedure_id
                    WHERE n.procedure_id = :pid
                      AND t.notice_record_id = n.id
                      AND t.lot_id IS NULL
                      AND nl.lot_reference = t.lot_reference
                """,
        )
        for query in update_queries:
            await session.execute(text(query), {"pid": procedure_id})

        await self._rebuild_lot_suppliers(session, procedure_id)

    async def _rebuild_lot_suppliers(self, session: AsyncSession, procedure_id: int) -> None:
        await session.execute(
            text("""
                DELETE FROM lot_suppliers
                WHERE lot_id IN (SELECT id FROM notice_lots WHERE procedure_id = :pid)
            """),
            {"pid": procedure_id},
        )
        await session.execute(
            text("""
                INSERT INTO lot_suppliers (
                    lot_id, organization_id, winning_amount, winning_currency, notice_record_id,
                    created_at, updated_at
                )
                SELECT DISTINCT ON (lt.lot_id, lto.organization_id)
                       lt.lot_id, lto.organization_id, lt.tender_value, lt.tender_currency,
                       lt.notice_record_id, now(), now()
                FROM lot_tenders lt
                JOIN notices n ON n.id = lt.notice_record_id AND n.is_latest
                JOIN notice_lots nl ON nl.id = lt.lot_id AND nl.procedure_id = :pid
                JOIN lot_tender_organizations lto ON lto.lot_tender_id = lt.id
                JOIN lot_results lr
                     ON lr.notice_record_id = lt.notice_record_id
                    AND lr.lot_reference = lt.lot_reference
                    AND lr.award_outcome = 'selec-w'
                WHERE lr.tender_refs @> jsonb_build_array(lt.tender_ref)
                ORDER BY lt.lot_id, lto.organization_id, lt.id DESC
            """),
            {"pid": procedure_id},
        )

    async def _upsert_settled_contract(
        self,
        session: AsyncSession,
        notice_id: str,
        notice_record_id: int,
        contract: SettledContractDto,
        tender_ids_by_ref: dict[str, int],
        index: int = 0,
    ) -> int | None:
        if not (contract.contract_number or contract.contract_ref or contract.tender_refs):
            return None

        contract_key = (
            contract.contract_ref
            or (contract.tender_refs[0] if contract.tender_refs else None)
            or contract.contract_number
            or f"idx-{index}"
        )[:64]

        query = """
            INSERT INTO settled_contracts (
                notice_id, notice_record_id, contract_ref, contract_number, conclusion_date, title,
                contract_url, tender_refs, extra_fields, created_at, updated_at
            )
            VALUES (
                :notice_id, :notice_record_id, :contract_ref, :contract_number, :conclusion_date, :title,
                :contract_url, CAST(:tender_refs AS jsonb), CAST(:extra_fields AS jsonb), now(), now()
            )
            ON CONFLICT (notice_record_id, contract_ref) DO UPDATE SET
                contract_number = COALESCE(EXCLUDED.contract_number, settled_contracts.contract_number),
                conclusion_date = COALESCE(EXCLUDED.conclusion_date, settled_contracts.conclusion_date),
                title = COALESCE(EXCLUDED.title, settled_contracts.title),
                contract_url = COALESCE(EXCLUDED.contract_url, settled_contracts.contract_url),
                tender_refs = CASE WHEN EXCLUDED.tender_refs <> '[]'::jsonb
                                   THEN EXCLUDED.tender_refs ELSE settled_contracts.tender_refs END,
                extra_fields = settled_contracts.extra_fields || EXCLUDED.extra_fields,
                updated_at = now()
            RETURNING id
        """
        result = await session.execute(
            text(query),
            {
                "notice_id": notice_id,
                "notice_record_id": notice_record_id,
                "contract_ref": contract_key,
                "contract_number": contract.contract_number,
                "conclusion_date": contract.conclusion_date,
                "title": contract.title,
                "contract_url": contract.contract_url,
                "tender_refs": json.dumps(contract.tender_refs),
                "extra_fields": json.dumps(contract.extra_fields or {}),
            },
        )
        contract_id = self._require_int(result.scalar_one(), "settled_contract.id")

        if contract.tender_refs:
            await session.execute(
                text("DELETE FROM settled_contract_tenders WHERE settled_contract_id = :id"),
                {"id": contract_id},
            )
            tender_ids = sorted(
                {tender_ids_by_ref[ref] for ref in contract.tender_refs if ref in tender_ids_by_ref}
            )
            if tender_ids:
                await session.execute(
                    text("""
                        INSERT INTO settled_contract_tenders
                            (settled_contract_id, lot_tender_id, created_at, updated_at)
                        VALUES (:contract_id, :tender_id, now(), now())
                        ON CONFLICT (settled_contract_id, lot_tender_id) DO NOTHING
                    """),
                    [
                        {"contract_id": contract_id, "tender_id": tender_id}
                        for tender_id in tender_ids
                    ],
                )
        return contract_id
