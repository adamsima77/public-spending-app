import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from loaders.loader_support import LoaderSupport
from models.notice import NoticeDto


class ProcedureLoader(LoaderSupport):
    async def upsert_procedure(
        self,
        session: AsyncSession,
        notice_dto: NoticeDto,
        buyer_id: int | None,
        update_existing: bool = True,
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

        await self.ensure_nuts_code(session, procedure.nuts_code)

        extra_fields = dict(procedure.extra_fields or {})
        if procedure.provider_ref:
            extra_fields["provider_ref"] = procedure.provider_ref

        existing = await self._find_procedure(
            session, identifier, order_id, reference, buyer_id, natural_key
        )

        if existing is not None and not update_existing:
            return self._require_int(existing.id, "procedure.id")

        params: dict[str, Any] = {
            "procedure_type": procedure.procedure_type,
            "contract_type": procedure.contract_type,
            "main_cpv": procedure.main_cpv,
            "estimated_value": procedure.estimated_value,
            "currency": procedure.currency,
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

    async def _find_procedure(
        self,
        session: AsyncSession,
        identifier: str | None,
        order_id: str | None,
        reference: str | None,
        buyer_id: int | None,
        natural_key: bool,
    ) -> Any:
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
        return existing
