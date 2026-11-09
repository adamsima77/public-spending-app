import json
from functools import partial
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from loaders.loader_support import LoaderSupport
from models.notice import NoticeDto
from models.organization import OrganizationDto


class OrganizationLoader(LoaderSupport):
    _CIN_DIGIT_LENGTH = 8

    _PLACEHOLDER_IDENTIFIERS = frozenset(
        {"-", "--", "---", "\u2013", "\u2014", "n/a", "na", "none", "null"}
    )

    async def upsert_notice_organizations(
        self,
        session: AsyncSession,
        notice_dto: NoticeDto,
        notice_id: str,
        update_existing: bool = True,
    ) -> tuple[dict[int, int], dict[str, int]]:
        org_ids: dict[int, int] = {}
        for index, org in enumerate(notice_dto.organizations):
            await self.ensure_nuts_code(session, org.nuts_code)
            new_id = await self._guarded(
                session,
                "organization",
                {
                    "notice_id": notice_id,
                    "org_ref": org.org_ref,
                    "cin": org.cin,
                    "tin": org.tin,
                },
                partial(self._upsert_organization, session, org, update_existing),
            )
            if new_id is not None:
                org_ids[index] = new_id

        org_id_by_ref = {
            org.org_ref: org_ids[index]
            for index, org in enumerate(notice_dto.organizations)
            if org.org_ref and index in org_ids
        }
        return org_ids, org_id_by_ref

    async def resolve_tendering_party_org_ids(
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

    @classmethod
    def _norm_identifier(cls, value: str | None) -> str | None:
        if value is None:
            return None
        v = str(value).strip()
        if not v or v.lower() in cls._PLACEHOLDER_IDENTIFIERS or set(v) <= {"*", "-", " "}:
            return None
        return v

    @classmethod
    def _normalize_cin(cls, value: str | None, country: str | None) -> str | None:
        normalized = cls._norm_identifier(value)
        if normalized is None or any(
            not ("0" <= character <= "9" or character.isspace() or character in "./-")
            for character in normalized
        ):
            return normalized

        digits = "".join(character for character in normalized if "0" <= character <= "9")
        if (
            country
            and country.strip().upper() in {"SK", "CZ"}
            and 0 < len(digits) <= cls._CIN_DIGIT_LENGTH
        ):
            return digits.zfill(cls._CIN_DIGIT_LENGTH)
        return digits or None

    async def _find_organization_id(
        self, session: AsyncSession, org: OrganizationDto
    ) -> int | None:
        identifier_queries = (
            (
                org.cin,
                """
                    SELECT id FROM organizations
                    WHERE (
                            (
                                CAST(:country AS varchar) IN ('SK', 'CZ')
                                AND regexp_replace(cin, '[^0-9]', '', 'g') ~ '^[0-9]{1,8}$'
                                AND lpad(regexp_replace(cin, '[^0-9]', '', 'g'), 8, '0') = :value
                            )
                            OR (
                                (
                                    CAST(:country AS varchar) IS NULL
                                    OR CAST(:country AS varchar) NOT IN ('SK', 'CZ')
                                )
                                AND cin = :value
                            )
                          )
                      AND (country IS NULL OR CAST(:country AS varchar) IS NULL
                           OR country = CAST(:country AS varchar))
                    ORDER BY (country IS NOT DISTINCT FROM CAST(:country AS varchar)) DESC,
                             (cin = :value) DESC, id
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

    async def _upsert_organization(
        self, session: AsyncSession, org: OrganizationDto, update_existing: bool = True
    ) -> int:
        if org.country:
            org.country = org.country.strip().upper()
        org.cin = self._normalize_cin(org.cin, org.country)
        org.tin = self._norm_identifier(org.tin)
        existing_id = await self._find_organization_id(session, org)
        if existing_id is not None and not update_existing:
            return existing_id

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
                    cin = CASE WHEN CAST(:cin AS varchar) IS NOT NULL
                                    AND organizations.cin IS DISTINCT FROM CAST(:cin AS varchar)
                                    AND NOT EXISTS (
                                        SELECT 1 FROM organizations o2
                                        WHERE o2.id <> organizations.id
                                          AND o2.cin = CAST(:cin AS varchar)
                                          AND COALESCE(o2.country, '') =
                                              COALESCE(CAST(:country AS varchar), organizations.country, '')
                                    )
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
