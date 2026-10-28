import json
import re
from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass
from typing import Any

import aiofiles
import ijson

import config
from core.logger import Logger
from models.lot import LotDto
from models.lot_result import LotResultDto, SubmissionStatDto
from models.lot_tender import LotTenderDto, TenderingPartyDto
from models.notice import NoticeDto
from models.organization import OrganizationDto
from models.settled_contract import SettledContractDto

ORG_REF_PATTERN = re.compile(r"ORG-\d+")
TPA_REF_PATTERN = re.compile(r"TPA-\d+")
TEN_REF_PATTERN = re.compile(r"TEN-\d+")
CON_REF_PATTERN = re.compile(r"CON-\d+")
ORDER_ID_PATTERN = re.compile(r"\(ID:\s*(\d+)\)\s*$")


@dataclass(frozen=True)
class JsonParserConfig:
    notice_fields: Mapping[str, str]
    organization_fields: Mapping[str, str]
    procedure_fields: Mapping[str, str]
    lot_fields: Mapping[str, str]
    lot_result_fields: Mapping[str, str]
    submission_stat_fields: Mapping[str, str]
    lot_tender_fields: Mapping[str, str]
    settled_contract_fields: Mapping[str, str]
    anchor_organization: str
    anchor_lot: str
    anchor_lot_result: str
    anchor_submission_stat: str
    anchor_lot_tender: str
    anchor_tendering_party: str
    anchor_settled_contract: str
    tenderer_org_ref_key: str
    list_fields: frozenset[str] = frozenset()


class JsonParser:
    def __init__(
        self,
        parser_config: JsonParserConfig,
        logger: Logger | None = None,
    ) -> None:
        self.notice_fields = parser_config.notice_fields
        self.organization_fields = parser_config.organization_fields
        self.procedure_fields = parser_config.procedure_fields
        self.lot_fields = parser_config.lot_fields
        self.lot_result_fields = parser_config.lot_result_fields
        self.submission_stat_fields = parser_config.submission_stat_fields
        self.lot_tender_fields = parser_config.lot_tender_fields
        self.settled_contract_fields = parser_config.settled_contract_fields

        self.anchor_organization = parser_config.anchor_organization
        self.anchor_lot = parser_config.anchor_lot
        self.anchor_lot_result = parser_config.anchor_lot_result
        self.anchor_submission_stat = parser_config.anchor_submission_stat
        self.anchor_lot_tender = parser_config.anchor_lot_tender
        self.anchor_tendering_party = parser_config.anchor_tendering_party
        self.anchor_settled_contract = parser_config.anchor_settled_contract
        self.tenderer_org_ref_key = parser_config.tenderer_org_ref_key
        self.list_fields = (
            set(parser_config.list_fields)
            if parser_config.list_fields
            else set(getattr(config, "LIST_FIELDS", ()))
        )

        self._logger = logger

    def _extract_ref(self, node: dict[str, Any], pattern: re.Pattern[str]) -> str | None:
        sk_lang = node.get("lang", {}).get("sk", {})
        if isinstance(sk_lang, dict):
            for value in sk_lang.values():
                if isinstance(value, str):
                    match = pattern.search(value)
                    if match:
                        return match.group(0)
        return None

    async def _resolve_org_refs(self, notice_dto: NoticeDto, file_id: int | None = None) -> None:
        orgs = notice_dto.organizations
        org_by_index = {org.org_ref: org for org in orgs if org.org_ref}
        procedure = notice_dto.procedure

        if procedure.buyer_ref:
            procedure.buyer = org_by_index.get(procedure.buyer_ref)
            if procedure.buyer is None:
                await self._log_unresolved_org_ref(
                    procedure.buyer_ref, "buyer_ref", notice_dto, file_id
                )

        if procedure.provider_ref:
            procedure.provider = org_by_index.get(procedure.provider_ref)
            if procedure.provider is None:
                await self._log_unresolved_org_ref(
                    procedure.provider_ref, "provider_ref", notice_dto, file_id
                )

        for party in notice_dto.tendering_parties:
            for ref in party.tenderer_org_refs:
                if ref not in org_by_index:
                    await self._log_unresolved_org_ref(
                        ref, f"Tenderer org_ref (party {party.party_ref})", notice_dto, file_id
                    )

    async def _log_unresolved_org_ref(
        self,
        reference: str,
        field: str,
        notice_dto: NoticeDto,
        file_id: int | None,
    ) -> None:
        if self._logger is None:
            return
        await self._logger.log(
            "warning",
            f"Nepodarilo sa rozlúštiť {field} '{reference}'",
            context={
                "notice_id": notice_dto.notice_id,
                "organizations_count": len(notice_dto.organizations),
            },
            file_id=file_id,
        )

    def _post_process_dtos(self, notice_dto: NoticeDto) -> None:
        if notice_dto.title and not notice_dto.procedure.source_order_id:
            order_match = ORDER_ID_PATTERN.search(notice_dto.title)
            if order_match:
                notice_dto.procedure.source_order_id = order_match.group(1)

        for org in notice_dto.organizations:
            self._fill_organization_address(org)
        if notice_dto.lots and not any(lot.lot_reference for lot in notice_dto.lots):
            for position, lot in enumerate(notice_dto.lots, start=1):
                lot.lot_reference = f"LOT-{position:04d}"
                lot.extra_fields["lot_reference_inferred"] = True

        for lot in notice_dto.lots:
            self._fill_submission_deadline(lot)

        if notice_dto.issue_date:
            issue_val = str(notice_dto.issue_date).strip()
            if issue_val:
                notice_dto.issue_date = issue_val

        if not notice_dto.published_at:
            notice_dto.published_at = notice_dto.issue_date

    @staticmethod
    def _fill_organization_address(organization: OrganizationDto) -> None:
        if not organization.address and (organization.street_name or organization.street_number):
            parts = [
                part for part in (organization.street_name, organization.street_number) if part
            ]
            organization.address = " ".join(parts)

    @staticmethod
    def _fill_submission_deadline(lot: LotDto) -> None:
        date_value = lot.extra_fields.get("BT-131(d)-Lot")
        time_value = lot.extra_fields.get("BT-131(t)-Lot")
        if not date_value or lot.submission_deadline:
            return
        date_string = str(date_value)
        if "T" in date_string:
            lot.submission_deadline = date_string
        elif time_value:
            time_string = str(time_value).split("T")[-1]
            lot.submission_deadline = f"{date_string}T{time_string}"
        else:
            lot.submission_deadline = date_string

    async def parse_file(
        self, file_path: str, db_file_id: int | None = None
    ) -> AsyncIterator[NoticeDto]:
        notices_parsed = 0
        notices_skipped = 0

        async with aiofiles.open(file_path, mode="rb") as f:
            async for item in ijson.items_async(f, "bulletinItemList.item"):
                submission_id = item.get("submissionId") if isinstance(item, dict) else None
                try:
                    item_data = item.get("itemData") if isinstance(item, dict) else None
                    if not item_data:
                        continue
                    inner = json.loads(item_data)
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    notices_skipped += 1
                    if self._logger:
                        await self._logger.log(
                            "warning",
                            f"Preskakujem item, chyba pri dekódovaní itemData: {e}",
                            context={"submission_id": submission_id},
                            file_id=db_file_id,
                        )
                    continue

                notice_dto = NoticeDto()

                orphan_lot_fields: dict[str, Any] = {}
                ctx: dict[str, Any] = {
                    "org": None,
                    "lot": None,
                    "lot_result": None,
                    "submission_stat": None,
                    "lot_tender": None,
                    "tendering_party": None,
                    "settled_contract": None,
                }
                for component in inner.get("components", []):
                    self._process_node(component, notice_dto, ctx, orphan_lot_fields)

                if not notice_dto.notice_id or not notice_dto.notice_version:
                    notices_skipped += 1
                    if self._logger:
                        await self._logger.log(
                            "warning",
                            "Notice bez rozpoznateľnej BT štruktúry, preskakujem",
                            context={
                                "submission_id": submission_id,
                                "unrecognized_keys": list(notice_dto.extra_fields.keys())[:10],
                            },
                            file_id=db_file_id,
                        )
                    continue

                if orphan_lot_fields and self._logger:
                    await self._logger.log(
                        "warning",
                        f"Nájdené *-Lot polia bez current_lot (anchor '{self.anchor_lot}' pravdepodobne nesedí)",
                        context={
                            "notice_id": notice_dto.notice_id,
                            "submission_id": submission_id,
                            "form_type": notice_dto.form_type,
                            "orphan_lot_keys": list(orphan_lot_fields.keys())[:10],
                        },
                        file_id=db_file_id,
                    )

                if notice_dto.form_type == "competition" and not notice_dto.lots and self._logger:
                    await self._logger.log(
                        "warning",
                        "Notice typu 'competition' bez jediného lotu",
                        context={
                            "notice_id": notice_dto.notice_id,
                            "submission_id": submission_id,
                            "procedure_reference": notice_dto.procedure.reference,
                            "had_orphan_lot_fields": bool(orphan_lot_fields),
                        },
                        file_id=db_file_id,
                    )

                self._post_process_dtos(notice_dto)
                await self._resolve_org_refs(notice_dto, file_id=db_file_id)
                notices_parsed += 1
                yield notice_dto

        if self._logger:
            await self._logger.log(
                "info",
                f"Súbor spracovaný: {notices_parsed} notices, {notices_skipped} preskočených",
                file_id=db_file_id,
            )

    def _process_node(
        self,
        node: Any,
        notice_dto: NoticeDto,
        ctx: dict[str, Any],
        orphan_lot_fields: dict[str, Any] | None = None,
    ) -> None:
        if isinstance(node, list):
            for child in node:
                self._process_node(child, notice_dto, ctx, orphan_lot_fields)
            return

        if not isinstance(node, dict):
            return

        key = node.get("key")
        value = node.get("value")
        components = node.get("components")

        child_ctx = self._anchor_context(key, node, notice_dto, ctx)

        if isinstance(key, str) and value is not None and not components:
            self._apply_leaf(key, value, notice_dto, child_ctx, orphan_lot_fields)

        if components:
            self._process_node(components, notice_dto, child_ctx, orphan_lot_fields)

    def _anchor_context(
        self, key: Any, node: dict[str, Any], notice_dto: NoticeDto, ctx: dict[str, Any]
    ) -> dict[str, Any]:
        child_ctx = ctx
        if key == self.anchor_organization:
            org = OrganizationDto()
            org.org_ref = self._extract_ref(node, ORG_REF_PATTERN)
            notice_dto.organizations.append(org)
            child_ctx = {**ctx, "org": org}
        elif key == self.anchor_lot:
            lot = LotDto()
            notice_dto.lots.append(lot)
            child_ctx = {**ctx, "lot": lot}
        elif key == self.anchor_lot_result:
            lot_result = LotResultDto()
            notice_dto.lot_results.append(lot_result)
            child_ctx = {
                **ctx,
                "lot_result": lot_result,
                "submission_stat": None,
            }
        elif key == self.anchor_submission_stat:
            stat = SubmissionStatDto()
            if ctx.get("lot_result") is not None:
                ctx["lot_result"].submission_stats.append(stat)
            child_ctx = {**ctx, "submission_stat": stat}
        elif key == self.anchor_lot_tender:
            tender = LotTenderDto()
            tender.tender_ref = self._extract_ref(node, TEN_REF_PATTERN)
            notice_dto.lot_tenders.append(tender)
            child_ctx = {**ctx, "lot_tender": tender}
        elif key == self.anchor_tendering_party:
            party = TenderingPartyDto()
            party.party_ref = self._extract_ref(node, TPA_REF_PATTERN)
            notice_dto.tendering_parties.append(party)
            child_ctx = {**ctx, "tendering_party": party}
        elif key == self.anchor_settled_contract:
            contract = SettledContractDto()
            contract.contract_ref = self._extract_ref(node, CON_REF_PATTERN)
            notice_dto.settled_contracts.append(contract)
            child_ctx = {**ctx, "settled_contract": contract}
        return child_ctx

    def _as_str_list(self, value: Any) -> list[str]:
        items = value if isinstance(value, list) else [value]
        return [str(v).strip() for v in items if v is not None and str(v).strip()]

    def _set_field(self, dto: Any, attr: str, value: Any) -> None:
        if attr in self.list_fields:
            current: list[str] = getattr(dto, attr)
            merged = list(current)
            for item in self._as_str_list(value):
                if item not in merged:
                    merged.append(item)
            setattr(dto, attr, merged)
        else:
            setattr(dto, attr, self._first_if_list(value))

    def _clean_value(self, val: Any) -> Any:
        if isinstance(val, str):
            cleaned = val.replace("\x00", "").strip()
            if cleaned == "" or set(cleaned) == {"*"}:
                return None
            return cleaned
        if isinstance(val, dict):
            return {k: self._clean_value(v) for k, v in val.items()}
        if isinstance(val, list):
            return [self._clean_value(x) for x in val]
        return val

    def _first_if_list(self, value: Any) -> Any:
        if isinstance(value, list):
            return value[0] if value else None
        return value

    def _apply_special_reference(
        self, key: str, value: Any, notice_dto: NoticeDto, tendering_party: Any
    ) -> bool:
        if key == "OPT-300-Procedure-Buyer":
            notice_dto.procedure.buyer_ref = value
            return True
        if key == "OPT-300-Procedure-SProvider":
            notice_dto.procedure.provider_ref = value
            return True
        if key != self.tenderer_org_ref_key or tendering_party is None:
            return False
        reference = self._first_if_list(value)
        if reference:
            tendering_party.tenderer_org_refs.append(str(reference))
        return True

    def _apply_entity_field(
        self,
        entity: Any,
        field_map: Mapping[str, str],
        key: str,
        value: Any,
        suffix: str | None,
        merge_list_values: bool = False,
    ) -> bool:
        if entity is None:
            return False
        attr = field_map.get(key)
        if attr is not None:
            if merge_list_values:
                self._set_field(entity, attr, value)
            else:
                setattr(entity, attr, value)
            return True
        if suffix is not None and key.endswith(suffix):
            entity.extra_fields[key] = value
            return True
        return False

    def _apply_fallback_fields(
        self,
        key: str,
        value: Any,
        notice_dto: NoticeDto,
        current_org: Any,
        current_lot: Any,
        orphan_lot_fields: dict[str, Any] | None,
    ) -> None:
        if self._apply_entity_field(current_org, self.organization_fields, key, value, None):
            return
        if current_org is not None and "Organization" in key:
            current_org.extra_fields[key] = value
            return
        if self._apply_entity_field(notice_dto.procedure, self.procedure_fields, key, value, None):
            return
        if key.endswith("-Procedure") or "-Procedure-" in key:
            notice_dto.procedure.extra_fields[key] = value
            return
        if self._apply_entity_field(notice_dto, self.notice_fields, key, value, None):
            return
        if key.endswith("-Lot") and current_lot is None and orphan_lot_fields is not None:
            orphan_lot_fields[key] = value
        notice_dto.extra_fields[key] = value

    def _apply_leaf(
        self,
        key: str,
        value: Any,
        notice_dto: NoticeDto,
        ctx: dict[str, Any],
        orphan_lot_fields: dict[str, Any] | None = None,
    ) -> None:
        value = self._clean_value(value)
        if value is None:
            return

        current_org = ctx.get("org")
        current_lot = ctx.get("lot")
        current_lot_result = ctx.get("lot_result")
        current_submission_stat = ctx.get("submission_stat")
        current_lot_tender = ctx.get("lot_tender")
        current_tendering_party = ctx.get("tendering_party")
        current_settled_contract = ctx.get("settled_contract")

        if self._apply_special_reference(key, value, notice_dto, current_tendering_party):
            return

        for entity, field_map, suffix, merge_list_values in (
            (current_submission_stat, self.submission_stat_fields, None, False),
            (current_lot_result, self.lot_result_fields, "-LotResult", True),
            (current_lot_tender, self.lot_tender_fields, "-Tender", True),
            (current_settled_contract, self.settled_contract_fields, "-Contract", True),
            (current_lot, self.lot_fields, "-Lot", False),
        ):
            if self._apply_entity_field(entity, field_map, key, value, suffix, merge_list_values):
                return
        self._apply_fallback_fields(
            key, value, notice_dto, current_org, current_lot, orphan_lot_fields
        )
