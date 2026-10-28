import json
import re
from collections.abc import Awaitable, Callable
from datetime import datetime
from functools import partial
from operator import gt, lt
from typing import Any, TypeVar

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import Database
from core.logger import Logger
from models.lot import LotDto
from models.lot_result import LotResultDto
from models.lot_tender import LotTenderDto
from models.notice import NoticeDto
from models.organization import OrganizationDto
from models.settled_contract import SettledContractDto

ResultT = TypeVar("ResultT")
MIN_DATETIME_LENGTH = 10


class NoticeLoader:
    def __init__(self, db: Database, logger: Logger | None = None) -> None:
        self.db = db
        self._logger = logger

        self._known_nuts_codes: set[str] = set()
        self._known_cpv_codes: set[str] = set()

    async def upsert_notice(self, notice_dto: NoticeDto, db_file_id: int | None = None) -> None:
        notice_id = notice_dto.notice_id
        if not notice_id or not notice_dto.notice_version:
            if self._logger:
                await self._logger.log(
                    "warning",
                    "Notice bez notice_id/notice_version, preskakujem",
                    context={"extra_fields_keys": list(notice_dto.extra_fields.keys())[:10]},
                    file_id=db_file_id,
                )
            return

        async with self.db.transaction() as session:
            org_ids, org_id_by_ref = await self._upsert_notice_organizations(
                session, notice_dto, notice_id
            )
            buyer_id = self._resolve_org_db_id(notice_dto, notice_dto.procedure.buyer, org_ids)
            await self._ensure_cpv_code(session, notice_dto.procedure.main_cpv)
            procedure_id = await self._upsert_procedure(session, notice_dto, buyer_id)

            lot_id_by_ref = await self._upsert_notice_lots(session, notice_dto, procedure_id)
            lot_results = self._merge_lot_results(notice_dto.lot_results)
            if procedure_id is not None:
                await self._include_existing_lot_ids_from_db(
                    session, procedure_id, lot_id_by_ref, lot_results, notice_dto
                )
            party_org_ids = await self._resolve_tendering_party_org_ids(
                notice_dto, org_id_by_ref, db_file_id
            )
            await self._upsert_notice_lot_results(session, notice_id, lot_results, lot_id_by_ref)
            await self._upsert_notice_lot_tenders(
                session, notice_dto, notice_id, party_org_ids, lot_id_by_ref
            )
            await self._link_notice_results(session, notice_id, procedure_id)
            await self._upsert_notice_contracts(session, notice_dto, notice_id)
            await self._upsert_notice_row(session, notice_dto, procedure_id)
            await self._refresh_is_latest(session, notice_id)

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

    async def _upsert_notice_organizations(
        self, session: AsyncSession, notice_dto: NoticeDto, notice_id: str
    ) -> tuple[dict[int, int], dict[str, int]]:
        org_ids: dict[int, int] = {}
        for index, org in enumerate(notice_dto.organizations):
            await self._ensure_nuts_code(session, org.nuts_code)
            new_id = await self._guarded(
                session,
                "organization",
                {
                    "notice_id": notice_id,
                    "org_ref": org.org_ref,
                    "cin": org.cin,
                    "tin": org.tin,
                },
                partial(self._upsert_organization, session, org),
            )
            if new_id is not None:
                org_ids[index] = new_id

        org_id_by_ref = {
            org.org_ref: org_ids[index]
            for index, org in enumerate(notice_dto.organizations)
            if org.org_ref and index in org_ids
        }
        return org_ids, org_id_by_ref

    async def _upsert_notice_lots(
        self, session: AsyncSession, notice_dto: NoticeDto, procedure_id: int | None
    ) -> dict[str, int]:
        lot_ids: dict[str, int] = {}
        for lot in notice_dto.lots:
            await self._ensure_cpv_code(session, lot.main_cpv)
            lot_id = await self._upsert_lot(session, lot, procedure_id)
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

    async def _include_existing_lot_ids_from_db(
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

    async def _resolve_tendering_party_org_ids(
        self,
        notice_dto: NoticeDto,
        org_id_by_ref: dict[str, int],
        db_file_id: int | None,
    ) -> dict[str, list[int]]:
        party_org_ids: dict[str, list[int]] = {}
        for party in notice_dto.tendering_parties:
            if not party.party_ref:
                continue
            organization_ids = [
                org_id_by_ref[ref] for ref in party.tenderer_org_refs if ref in org_id_by_ref
            ]
            if organization_ids:
                party_org_ids[party.party_ref] = organization_ids
            elif party.tenderer_org_refs and self._logger:
                await self._logger.log(
                    "warning",
                    f"Tendering party '{party.party_ref}' — žiadny z tenderer_org_refs "
                    f"{party.tenderer_org_refs} sa nepodarilo priradiť na organizáciu",
                    context={"notice_id": notice_dto.notice_id},
                    file_id=db_file_id,
                )
        return party_org_ids

    async def _upsert_notice_lot_results(
        self,
        session: AsyncSession,
        notice_id: str,
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
                    lot_result,
                    lot_id_by_ref.get(lot_result.lot_reference)
                    if lot_result.lot_reference
                    else None,
                ),
            )

    async def _upsert_notice_lot_tenders(
        self,
        session: AsyncSession,
        notice_dto: NoticeDto,
        notice_id: str,
        party_org_ids: dict[str, list[int]],
        lot_id_by_ref: dict[str, int],
    ) -> None:
        if not notice_dto.lot_tenders:
            return
        await session.execute(
            text("DELETE FROM lot_tenders WHERE notice_id = :n AND tender_ref LIKE 'legacy:%'"),
            {"n": notice_id},
        )
        for tender in notice_dto.lot_tenders:
            lot_id = lot_id_by_ref.get(tender.lot_reference) if tender.lot_reference else None
            tenderer_org_ids = party_org_ids.get(tender.tendering_party_ref or "", [])
            await self._guarded(
                session,
                "lot_tender",
                {"notice_id": notice_id, "lot_reference": tender.lot_reference},
                partial(
                    self._upsert_lot_tender,
                    session,
                    notice_id,
                    tender,
                    lot_id,
                    tenderer_org_ids,
                ),
            )

    async def _link_notice_results(
        self, session: AsyncSession, notice_id: str, procedure_id: int | None
    ) -> None:
        if procedure_id is not None:
            await self._guarded(
                session,
                "link_results",
                {"notice_id": notice_id, "procedure_id": procedure_id},
                partial(self._link_results, session, procedure_id),
            )

    async def _upsert_notice_contracts(
        self, session: AsyncSession, notice_dto: NoticeDto, notice_id: str
    ) -> None:
        if not notice_dto.settled_contracts:
            return
        await self._purge_legacy_contracts(session, notice_id)
        for index, contract in enumerate(notice_dto.settled_contracts):
            await self._guarded(
                session,
                "settled_contract",
                {
                    "notice_id": notice_id,
                    "contract_ref": contract.contract_ref,
                    "tender_refs": contract.tender_refs,
                },
                partial(self._upsert_settled_contract, session, notice_id, contract, index),
            )

    def _merge_lot_results(self, lot_results: list[LotResultDto]) -> list[LotResultDto]:
        merged: dict[str, LotResultDto] = {}
        result: list[LotResultDto] = []
        for lot_result in lot_results:
            ref = lot_result.lot_reference
            if not ref:
                result.append(lot_result)
                continue

            base = merged.get(ref)
            if base is None:
                merged[ref] = lot_result
                result.append(lot_result)
                continue

            for attr in ("tender_refs", "contract_refs"):
                target = getattr(base, attr)
                for item in getattr(lot_result, attr):
                    if item not in target:
                        target.append(item)

            if base.award_outcome is None or (
                base.award_outcome != "selec-w" and lot_result.award_outcome == "selec-w"
            ):
                base.award_outcome = lot_result.award_outcome
                base.non_award_reason = lot_result.non_award_reason

            for value_attr, currency_attr, is_better in (
                ("lowest_offer_value", "lowest_offer_currency", lt),
                ("highest_offer_value", "highest_offer_currency", gt),
            ):
                old_value = self._parse_decimal(getattr(base, value_attr))
                new_value = self._parse_decimal(getattr(lot_result, value_attr))
                if new_value is not None and (old_value is None or is_better(new_value, old_value)):
                    setattr(base, value_attr, getattr(lot_result, value_attr))
                    setattr(base, currency_attr, getattr(lot_result, currency_attr))

            known_categories = {stat.category_code for stat in base.submission_stats}
            for stat in lot_result.submission_stats:
                if stat.category_code and stat.category_code not in known_categories:
                    base.submission_stats.append(stat)
                    known_categories.add(stat.category_code)

            for key, value in lot_result.extra_fields.items():
                base.extra_fields.setdefault(key, value)
            base.extra_fields["merged_result_count"] = (
                base.extra_fields.get("merged_result_count", 1) + 1
            )

        return result

    def _safe_currency(self, value: Any) -> str | None:
        if value is None:
            return None
        v = str(value).strip().upper()
        return v if re.fullmatch(r"[A-Z]{3}", v) else None

    def _safe_int(self, value: Any, max_value: int = 2_000_000_000) -> int | None:
        n = self._parse_int(value)
        if n is None or n < 0 or n > max_value:
            return None
        return n

    async def _guarded(
        self,
        session: AsyncSession,
        description: str,
        context: dict[str, Any],
        fn: Callable[[], Awaitable[ResultT]],
    ) -> ResultT | None:
        try:
            async with session.begin_nested():
                return await fn()
        except DBAPIError as e:
            if self._logger:
                await self._logger.log(
                    "warning",
                    f"Záznam preskočený ({description}): {getattr(e, 'orig', e)}",
                    context=context,
                )
            return None

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

    async def _ensure_nuts_code(self, session: AsyncSession, nuts_code: str | None) -> None:
        if not nuts_code:
            return

        code = str(nuts_code).strip().upper()[:10]
        if not code or code in self._known_nuts_codes:
            return

        query = """
            INSERT INTO nut_codes (code, name_sk, level, parent_code, created_at, updated_at)
            VALUES (:code, :name_sk, :level, NULL, now(), now())
            ON CONFLICT (code) DO NOTHING
        """
        await session.execute(
            text(query),
            {"code": code, "name_sk": f"NUTS {code}", "level": max(1, min(len(code), 5))},
        )
        self._known_nuts_codes.add(code)

    async def _ensure_cpv_code(self, session: AsyncSession, cpv_code: str | None) -> None:
        if not cpv_code:
            return

        code = str(cpv_code).strip()[:10]
        if not code or code in self._known_cpv_codes:
            return

        query = """
            INSERT INTO cpv_codes (code, name_sk, level, parent_code, created_at, updated_at)
            VALUES (:code, :name_sk, :level, NULL, now(), now())
            ON CONFLICT (code) DO NOTHING
        """
        await session.execute(
            text(query),
            {"code": code, "name_sk": f"CPV {code}", "level": len(code)},
        )
        self._known_cpv_codes.add(code)

    _PLACEHOLDER_IDENTIFIERS = frozenset(
        {"-", "--", "---", "\u2013", "\u2014", "n/a", "na", "none", "null"}
    )

    def _norm_identifier(self, value: str | None) -> str | None:
        if value is None:
            return None
        v = str(value).strip()
        if not v or v.lower() in self._PLACEHOLDER_IDENTIFIERS or set(v) <= {"*", "-", " "}:
            return None
        return v

    async def _find_organization_id(
        self, session: AsyncSession, org: OrganizationDto
    ) -> int | None:
        identifier_queries = (
            (
                org.cin,
                """
                    SELECT id FROM organizations
                    WHERE cin = :value
                      AND (country IS NULL OR CAST(:country AS varchar) IS NULL
                           OR country = CAST(:country AS varchar))
                    ORDER BY (country IS NOT DISTINCT FROM CAST(:country AS varchar)) DESC, id
                    LIMIT 1
                """,
            ),
            (
                org.tin,
                """
                    SELECT id FROM organizations
                    WHERE tin = :value
                      AND (country IS NULL OR CAST(:country AS varchar) IS NULL
                           OR country = CAST(:country AS varchar))
                    ORDER BY (country IS NOT DISTINCT FROM CAST(:country AS varchar)) DESC, id
                    LIMIT 1
                """,
            ),
        )
        for value, query in identifier_queries:
            if not value:
                continue
            row = (
                await session.execute(
                    text(query),
                    {"value": value, "country": org.country},
                )
            ).first()
            if row:
                return self._require_int(row.id, "organization.id")

        if not org.cin and not org.tin and org.name:
            row = (
                await session.execute(
                    text("""
                    SELECT id FROM organizations
                    WHERE cin IS NULL AND tin IS NULL AND name = :name
                      AND COALESCE(country, '') = COALESCE(CAST(:country AS varchar), '')
                      AND COALESCE(town, '') = COALESCE(CAST(:town AS varchar), '')
                    ORDER BY id LIMIT 1
                """),
                    {"name": org.name, "country": org.country, "town": org.town},
                )
            ).first()
            if row:
                return self._require_int(row.id, "organization.id")
        return None

    @staticmethod
    def _require_int(value: Any, field: str) -> int:
        if not isinstance(value, int):
            raise TypeError(f"Expected {field} to be an integer, got {type(value).__name__}")
        return value

    async def _upsert_organization(self, session: AsyncSession, org: OrganizationDto) -> int:
        org.cin = self._norm_identifier(org.cin)
        org.tin = self._norm_identifier(org.tin)
        existing_id = await self._find_organization_id(session, org)

        params: dict[str, Any] = {
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
            "company_size": org.company_size,
            "extra_fields": json.dumps(org.extra_fields or {}),
        }

        if existing_id is not None:
            params["id"] = existing_id
            query = """
                UPDATE organizations SET
                    cin = CASE WHEN organizations.cin IS NULL AND CAST(:cin AS varchar) IS NOT NULL
                               AND NOT EXISTS (SELECT 1 FROM organizations o2 WHERE o2.cin = CAST(:cin AS varchar)
                                               AND COALESCE(o2.country, '') = COALESCE(CAST(:country AS varchar), organizations.country, ''))
                               THEN CAST(:cin AS varchar) ELSE organizations.cin END,
                    tin = CASE WHEN organizations.tin IS NULL AND CAST(:tin AS varchar) IS NOT NULL
                               AND NOT EXISTS (SELECT 1 FROM organizations o2 WHERE o2.tin = CAST(:tin AS varchar)
                                               AND COALESCE(o2.country, '') = COALESCE(CAST(:country AS varchar), organizations.country, ''))
                               THEN CAST(:tin AS varchar) ELSE organizations.tin END,
                    name = COALESCE(CAST(:name AS varchar), organizations.name),
                    address = COALESCE(CAST(:address AS varchar), organizations.address),
                    street_name = COALESCE(CAST(:street_name AS varchar), organizations.street_name),
                    street_number = COALESCE(CAST(:street_number AS varchar), organizations.street_number),
                    phone = COALESCE(CAST(:phone AS varchar), organizations.phone),
                    town = COALESCE(CAST(:town AS varchar), organizations.town),
                    postal_code = COALESCE(CAST(:postal_code AS varchar), organizations.postal_code),
                    country = COALESCE(CAST(:country AS varchar), organizations.country),
                    nuts_code = COALESCE(CAST(:nuts_code AS varchar), organizations.nuts_code),
                    company_size = COALESCE(CAST(:company_size AS varchar), organizations.company_size),
                    extra_fields = organizations.extra_fields || CAST(:extra_fields AS jsonb),
                    updated_at = now()
                WHERE id = :id
                RETURNING id
            """
        else:
            if not org.cin and not org.tin and self._logger:
                await self._logger.log(
                    "warning",
                    f"Organizácia bez CIN/TIN ('{org.name}') — nie je možné dedupovať",
                    context={"org_ref": org.org_ref},
                )
            query = """
                INSERT INTO organizations (cin, tin, name, address, street_name, street_number, phone, town,
                    postal_code, country, nuts_code, company_size, extra_fields, created_at, updated_at)
                VALUES (:cin, :tin, :name, :address, :street_name, :street_number, :phone, :town,
                    :postal_code, :country, :nuts_code, :company_size, CAST(:extra_fields AS jsonb), now(), now())
                RETURNING id
            """

        result = await session.execute(text(query), params)
        return self._require_int(result.scalar_one(), "organization.id")

    def _parse_decimal(self, value: str | None) -> float | None:
        if value is None:
            return None
        cleaned = str(value).replace(" ", "").replace("\xa0", "").replace(",", ".")
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    def _parse_int(self, value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(str(value).strip())
        except (ValueError, TypeError):
            return None

    def _eu_funded_flag(self, value: str | None) -> bool | None:
        if value is None:
            return None
        val = str(value).strip().lower()
        if val == "eu-funds":
            return True
        if val == "no-eu-funds":
            return False
        return None

    def _parse_version(self, value: Any) -> int:
        if isinstance(value, int):
            return value
        if not value:
            return 1
        match = re.search(r"\d+", str(value))
        return int(match.group(0)) if match else 1

    def _parse_datetime(self, value: Any) -> str | None:
        if not value:
            return None
        val_str = str(value).strip()
        date_with_tz = re.fullmatch(r"(\d{4}-\d{2}-\d{2})(?:Z|[+-]\d{2}:\d{2})", val_str)
        if date_with_tz:
            return date_with_tz.group(1)
        try:
            return datetime.fromisoformat(val_str).isoformat()
        except ValueError:
            return val_str if len(val_str) >= MIN_DATETIME_LENGTH else None

    async def _upsert_procedure(
        self, session: AsyncSession, notice_dto: NoticeDto, buyer_id: int | None
    ) -> int | None:
        procedure = notice_dto.procedure
        identifier = procedure.identifier
        order_id = procedure.source_order_id
        reference = procedure.reference
        natural_key = bool(reference) and buyer_id is not None
        has_content = bool(notice_dto.lots or notice_dto.lot_results or notice_dto.lot_tenders)

        if not identifier and not order_id and not natural_key:
            if not reference and not has_content:
                return None
            identifier = f"notice:{notice_dto.notice_id}"

        await self._ensure_nuts_code(session, procedure.nuts_code)

        extra_fields = dict(procedure.extra_fields or {})
        if procedure.provider_ref:
            extra_fields["provider_ref"] = procedure.provider_ref

        existing = None
        if identifier:
            existing = (
                await session.execute(
                    text("""
                        SELECT id, procedure_reference, buyer_id, procedure_identifier, source_order_id
                        FROM procedures WHERE procedure_identifier = :identifier
                    """),
                    {"identifier": identifier},
                )
            ).first()
        if existing is None and order_id:
            existing = (
                await session.execute(
                    text("""
                        SELECT id, procedure_reference, buyer_id, procedure_identifier, source_order_id
                        FROM procedures
                        WHERE source_order_id = :order_id
                          AND (CAST(:identifier AS varchar) IS NULL
                               OR procedure_identifier IS NULL
                               OR procedure_identifier LIKE 'notice:%'
                               OR procedure_identifier = CAST(:identifier AS varchar))
                        ORDER BY id LIMIT 1
                    """),
                    {"order_id": order_id, "identifier": identifier},
                )
            ).first()
        if existing is None and natural_key and not identifier and not order_id:
            existing = (
                await session.execute(
                    text("""
                        SELECT id, procedure_reference, buyer_id, procedure_identifier, source_order_id
                        FROM procedures
                        WHERE procedure_reference = :reference AND buyer_id = :buyer_id
                          AND source_order_id IS NULL
                        ORDER BY id LIMIT 1
                    """),
                    {"reference": reference, "buyer_id": buyer_id},
                )
            ).first()

        params: dict[str, Any] = {
            "procedure_type": procedure.procedure_type,
            "contract_type": procedure.contract_type,
            "main_cpv": procedure.main_cpv,
            "estimated_value": self._parse_decimal(procedure.estimated_value),
            "currency": self._safe_currency(procedure.currency),
            "nuts_code": procedure.nuts_code,
            "place_of_performance": procedure.place_of_performance,
            "title": procedure.title,
            "description": procedure.description,
            "buyer_profile_url": procedure.buyer_profile_url,
            "performance_note": procedure.performance_note,
            "extra_fields": json.dumps(extra_fields),
        }

        if existing is not None:
            current_ident = existing.procedure_identifier
            if identifier and (not current_ident or current_ident.startswith("notice:")):
                new_ident = identifier
            else:
                new_ident = current_ident
            if new_ident != current_ident:
                clash = (
                    await session.execute(
                        text(
                            "SELECT 1 FROM procedures WHERE procedure_identifier = :v AND id <> :id"
                        ),
                        {"v": new_ident, "id": existing.id},
                    )
                ).first()
                if clash:
                    new_ident = current_ident
            new_order = existing.source_order_id or order_id
            new_ref = existing.procedure_reference or reference
            new_buyer = existing.buyer_id if existing.buyer_id is not None else buyer_id

            query = """
                UPDATE procedures SET
                    procedure_identifier = CAST(:new_ident AS varchar),
                    source_order_id = CAST(:new_order AS varchar),
                    procedure_reference = CAST(:new_ref AS varchar),
                    buyer_id = CAST(:new_buyer AS integer),
                    procedure_type = COALESCE(CAST(:procedure_type AS varchar), procedure_type),
                    contract_type = COALESCE(CAST(:contract_type AS varchar), contract_type),
                    main_cpv = COALESCE(CAST(:main_cpv AS varchar), main_cpv),
                    estimated_value = COALESCE(CAST(:estimated_value AS numeric), estimated_value),
                    currency = COALESCE(CAST(:currency AS varchar), currency),
                    nuts_code = COALESCE(CAST(:nuts_code AS varchar), nuts_code),
                    place_of_performance = COALESCE(CAST(:place_of_performance AS text), place_of_performance),
                    title = COALESCE(CAST(:title AS text), title),
                    description = COALESCE(CAST(:description AS text), description),
                    buyer_profile_url = COALESCE(CAST(:buyer_profile_url AS text), buyer_profile_url),
                    performance_note = COALESCE(CAST(:performance_note AS text), performance_note),
                    extra_fields = COALESCE(extra_fields, '{}'::jsonb) || CAST(:extra_fields AS jsonb),
                    updated_at = now()
                WHERE id = :id
                RETURNING id
            """
            params.update(
                {
                    "id": existing.id,
                    "new_ident": new_ident,
                    "new_order": new_order,
                    "new_ref": new_ref,
                    "new_buyer": new_buyer,
                }
            )
        else:
            query = """
                INSERT INTO procedures (procedure_identifier, source_order_id, procedure_reference, buyer_id,
                    procedure_type, contract_type, main_cpv, estimated_value, currency, nuts_code,
                    place_of_performance, title, description, buyer_profile_url, performance_note,
                    extra_fields, created_at, updated_at)
                VALUES (:identifier, :order_id, :reference, :buyer_id, :procedure_type, :contract_type, :main_cpv,
                    :estimated_value, :currency, :nuts_code, :place_of_performance, :title, :description,
                    :buyer_profile_url, :performance_note, CAST(:extra_fields AS jsonb), now(), now())
                RETURNING id
            """
            params.update(
                {
                    "identifier": identifier,
                    "order_id": order_id,
                    "reference": reference,
                    "buyer_id": buyer_id,
                }
            )

        result = await session.execute(text(query), params)
        return self._require_int(result.scalar_one(), "procedure.id")

    async def _upsert_lot(
        self, session: AsyncSession, lot: LotDto, procedure_id: int | None
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

        await self._ensure_nuts_code(session, lot.nuts_code)

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
                "estimated_value": self._parse_decimal(lot.estimated_value),
                "estimated_currency": self._safe_currency(lot.estimated_currency),
                "main_cpv": lot.main_cpv,
                "nuts_code": lot.nuts_code,
                "place_of_performance": lot.place_of_performance,
                "award_criterion": lot.award_criterion,
                "submission_deadline": lot.submission_deadline,
                "document_url": lot.document_url,
                "detail_url": lot.detail_url,
                "duration_value": self._safe_int(lot.duration_value),
                "duration_unit": lot.duration_unit,
                "framework_max_value": self._parse_decimal(lot.framework_max_value),
                "framework_max_currency": self._safe_currency(lot.framework_max_currency),
                "eu_funded": self._eu_funded_flag(lot.eu_funded),
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

    async def _upsert_lot_result(
        self, session: AsyncSession, notice_id: str, lot_result: LotResultDto, lot_id: int | None
    ) -> int | None:
        if not lot_result.lot_reference:
            return None

        query = """
            INSERT INTO lot_results (
                notice_id, lot_reference, lot_id, award_outcome, non_award_reason,
                lowest_offer_value, lowest_offer_currency, highest_offer_value, highest_offer_currency,
                tender_refs, contract_refs, extra_fields, created_at, updated_at
            )
            VALUES (
                :notice_id, :lot_reference, :lot_id, :award_outcome, :non_award_reason,
                :lowest_offer_value, :lowest_offer_currency, :highest_offer_value, :highest_offer_currency,
                CAST(:tender_refs AS text[]), CAST(:contract_refs AS text[]), CAST(:extra_fields AS jsonb), now(), now()
            )
            ON CONFLICT (notice_id, lot_reference) DO UPDATE SET
                lot_id = COALESCE(EXCLUDED.lot_id, lot_results.lot_id),
                award_outcome = COALESCE(EXCLUDED.award_outcome, lot_results.award_outcome),
                non_award_reason = COALESCE(EXCLUDED.non_award_reason, lot_results.non_award_reason),
                lowest_offer_value = COALESCE(EXCLUDED.lowest_offer_value, lot_results.lowest_offer_value),
                lowest_offer_currency = COALESCE(EXCLUDED.lowest_offer_currency, lot_results.lowest_offer_currency),
                highest_offer_value = COALESCE(EXCLUDED.highest_offer_value, lot_results.highest_offer_value),
                highest_offer_currency = COALESCE(EXCLUDED.highest_offer_currency, lot_results.highest_offer_currency),
                tender_refs = CASE WHEN cardinality(EXCLUDED.tender_refs) > 0
                                   THEN EXCLUDED.tender_refs ELSE lot_results.tender_refs END,
                contract_refs = CASE WHEN cardinality(EXCLUDED.contract_refs) > 0
                                     THEN EXCLUDED.contract_refs ELSE lot_results.contract_refs END,
                extra_fields = lot_results.extra_fields || EXCLUDED.extra_fields,
                updated_at = now()
            RETURNING id
        """
        result = await session.execute(
            text(query),
            {
                "notice_id": notice_id,
                "lot_reference": lot_result.lot_reference,
                "lot_id": lot_id,
                "award_outcome": lot_result.award_outcome,
                "non_award_reason": lot_result.non_award_reason,
                "lowest_offer_value": self._parse_decimal(lot_result.lowest_offer_value),
                "lowest_offer_currency": self._safe_currency(lot_result.lowest_offer_currency),
                "highest_offer_value": self._parse_decimal(lot_result.highest_offer_value),
                "highest_offer_currency": self._safe_currency(lot_result.highest_offer_currency),
                "tender_refs": list(lot_result.tender_refs),
                "contract_refs": list(lot_result.contract_refs),
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
                    "count": self._safe_int(stat.count),
                },
            )

        return lot_result_id

    async def _upsert_lot_tender(
        self,
        session: AsyncSession,
        notice_id: str,
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
                notice_id, lot_reference, lot_id, tender_ref, tender_value, tender_currency,
                tendering_party_ref, rank, subcontracting, extra_fields, created_at, updated_at
            )
            VALUES (
                :notice_id, :lot_reference, :lot_id, :tender_ref, :tender_value, :tender_currency,
                :tendering_party_ref, :rank, :subcontracting, CAST(:extra_fields AS jsonb), now(), now()
            )
            ON CONFLICT (notice_id, tender_ref) DO UPDATE SET
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
                "lot_reference": tender.lot_reference,
                "lot_id": lot_id,
                "tender_ref": tender_key,
                "tender_value": self._parse_decimal(tender.tender_value),
                "tender_currency": self._safe_currency(tender.tender_currency),
                "tendering_party_ref": tender.tendering_party_ref or "",
                "rank": self._safe_int(tender.rank),
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
                      AND t.notice_id = n.notice_id
                      AND t.lot_id IS NULL
                      AND nl.lot_reference = t.lot_reference
                """,
            """
                    UPDATE lot_tenders t SET lot_id = nl.id, updated_at = now()
                    FROM notices n
                    JOIN notice_lots nl ON nl.procedure_id = n.procedure_id
                    WHERE n.procedure_id = :pid
                      AND t.notice_id = n.notice_id
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
                INSERT INTO lot_suppliers (lot_id, organization_id, winning_amount, created_at, updated_at)
                SELECT DISTINCT ON (lt.lot_id, lto.organization_id)
                       lt.lot_id, lto.organization_id, lt.tender_value, now(), now()
                FROM lot_tenders lt
                JOIN notice_lots nl ON nl.id = lt.lot_id AND nl.procedure_id = :pid
                JOIN lot_tender_organizations lto ON lto.lot_tender_id = lt.id
                LEFT JOIN lot_results lr
                       ON lr.notice_id = lt.notice_id AND lr.lot_reference = lt.lot_reference
                WHERE (lr.id IS NULL OR lr.award_outcome IS NULL OR lr.award_outcome = 'selec-w')
                  AND (lr.id IS NULL OR cardinality(lr.tender_refs) = 0
                       OR lt.tender_ref = ANY(lr.tender_refs))
                ORDER BY lt.lot_id, lto.organization_id, lt.id DESC
            """),
            {"pid": procedure_id},
        )

    async def _purge_legacy_contracts(self, session: AsyncSession, notice_id: str) -> None:
        await session.execute(
            text(
                "DELETE FROM settled_contracts WHERE notice_id = :n AND contract_ref LIKE 'legacy:%'"
            ),
            {"n": notice_id},
        )

    async def _upsert_settled_contract(
        self, session: AsyncSession, notice_id: str, contract: SettledContractDto, index: int = 0
    ) -> None:
        if not (contract.contract_number or contract.contract_ref or contract.tender_refs):
            return

        contract_key = (
            contract.contract_ref
            or (contract.tender_refs[0] if contract.tender_refs else None)
            or contract.contract_number
            or f"idx-{index}"
        )[:64]

        query = """
            INSERT INTO settled_contracts (
                notice_id, contract_ref, contract_number, conclusion_date, title, contract_url,
                tender_refs, extra_fields, created_at, updated_at
            )
            VALUES (
                :notice_id, :contract_ref, :contract_number, :conclusion_date, :title, :contract_url,
                CAST(:tender_refs AS text[]), CAST(:extra_fields AS jsonb), now(), now()
            )
            ON CONFLICT (notice_id, contract_ref) DO UPDATE SET
                contract_number = COALESCE(EXCLUDED.contract_number, settled_contracts.contract_number),
                conclusion_date = COALESCE(EXCLUDED.conclusion_date, settled_contracts.conclusion_date),
                title = COALESCE(EXCLUDED.title, settled_contracts.title),
                contract_url = COALESCE(EXCLUDED.contract_url, settled_contracts.contract_url),
                tender_refs = CASE WHEN cardinality(EXCLUDED.tender_refs) > 0
                                   THEN EXCLUDED.tender_refs ELSE settled_contracts.tender_refs END,
                extra_fields = settled_contracts.extra_fields || EXCLUDED.extra_fields,
                updated_at = now()
        """
        await session.execute(
            text(query),
            {
                "notice_id": notice_id,
                "contract_ref": contract_key,
                "contract_number": contract.contract_number,
                "conclusion_date": self._parse_datetime(contract.conclusion_date),
                "title": contract.title,
                "contract_url": contract.contract_url,
                "tender_refs": list(contract.tender_refs),
                "extra_fields": json.dumps(contract.extra_fields or {}),
            },
        )

    async def _upsert_notice_row(
        self, session: AsyncSession, notice_dto: NoticeDto, procedure_id: int | None
    ) -> None:
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
                "issue_date": self._parse_datetime(notice_dto.issue_date),
                "published_at": self._parse_datetime(notice_dto.published_at),
                "procedure_id": procedure_id,
                "extra_fields": json.dumps(notice_dto.extra_fields or {}),
            },
        )

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
