import json
import re
import aiofiles
import ijson
from typing import Any, Optional, Dict
from core.logger import Logger
from models.notice import NoticeDto
from models.lot import LotDto
from models.organization import OrganizationDto
import config

ORG_REF_PATTERN = re.compile(r"ORG-\d+")

class JsonParser:
    def __init__(
        self,
        notice_fields: Dict[str, str],
        organization_fields: Dict[str, str],
        procedure_fields: Dict[str, str],
        lot_fields: Dict[str, str],
        anchor_organization: str,
        anchor_lot: str,
        logger: Optional[Logger] = None,
    ):
        self.notice_fields = notice_fields
        self.organization_fields = organization_fields
        self.procedure_fields = procedure_fields
        self.lot_fields = lot_fields
        self.anchor_organization = anchor_organization
        self.anchor_lot = anchor_lot
        self._logger = logger

    def _extract_org_ref(self, node: Dict[str, Any]) -> Optional[str]:
        sk_lang = node.get("lang", {}).get("sk", {})
        if isinstance(sk_lang, dict):
            for value in sk_lang.values():
                if isinstance(value, str):
                    match = ORG_REF_PATTERN.search(value)
                    if match:
                        return match.group(0)
        return None

    async def _resolve_org_refs(self, notice_dto: NoticeDto, file_id: Optional[str] = None) -> None:
        orgs = notice_dto.organizations
        org_by_index = {org.org_ref: org for org in orgs if org.org_ref}
        procedure = notice_dto.procedure

        if procedure.buyer_ref:
            procedure.buyer = org_by_index.get(procedure.buyer_ref)
            if procedure.buyer is None and self._logger:
                await self._logger.log(
                    "warning",
                    f"Nepodarilo sa rozlúštiť buyer_ref '{procedure.buyer_ref}'",
                    context={"notice_id": notice_dto.notice_id, "organizations_count": len(orgs)},
                    file_id=file_id,
                )

        if procedure.provider_ref:
            procedure.provider = org_by_index.get(procedure.provider_ref)
            if procedure.provider is None and self._logger:
                await self._logger.log(
                    "warning",
                    f"Nepodarilo sa zistiť provider_ref '{procedure.provider_ref}'",
                    context={"notice_id": notice_dto.notice_id, "organizations_count": len(orgs)},
                    file_id=file_id,
                )

        for lot in notice_dto.lots:
            if lot.winner_ref:
                lot.winner = org_by_index.get(lot.winner_ref)
                if lot.winner is None and self._logger:
                    await self._logger.log(
                        "warning",
                        f"Nepodarilo sa rozlúštiť winner_ref '{lot.winner_ref}'",
                        context={
                            "notice_id": notice_dto.notice_id,
                            "lot_reference": lot.lot_reference,
                            "organizations_count": len(orgs),
                        },
                        file_id=file_id,
                    )

    def _post_process_dtos(self, notice_dto: NoticeDto) -> None:
        for org in notice_dto.organizations:
            if not org.address and (org.street_name or org.street_number):
                parts = [p for p in [org.street_name, org.street_number] if p]
                org.address = " ".join(parts)

        for lot in notice_dto.lots:
            date_val = lot.extra_fields.get("BT-131(d)-Lot")
            time_val = lot.extra_fields.get("BT-131(t)-Lot")
            if date_val and not lot.submission_deadline:
                date_str = str(date_val)
                if "T" in date_str:
                    lot.submission_deadline = date_str
                elif time_val:
                    time_str = str(time_val).split("T")[-1] if "T" in str(time_val) else str(time_val)
                    lot.submission_deadline = f"{date_str}T{time_str}"
                else:
                    lot.submission_deadline = date_str

        if notice_dto.contract_conclusion_date:
            date_val = str(notice_dto.contract_conclusion_date).strip()
            if date_val:
                notice_dto.contract_conclusion_date = date_val

        if notice_dto.issue_date:
            issue_val = str(notice_dto.issue_date).strip()
            if issue_val:
                notice_dto.issue_date = issue_val

        if not notice_dto.published_at:
            notice_dto.published_at = notice_dto.issue_date

    async def parse_file(self, file_path: str, db_file_id: Optional[int] = None):
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

                orphan_lot_fields: Dict[str, Any] = {}
                for component in inner.get("components", []):
                    self._process_node(component, notice_dto, orphan_lot_fields=orphan_lot_fields)

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

                if notice_dto.form_type == "competition" and not notice_dto.lots:
                    if self._logger:
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
        current_org: Optional[OrganizationDto] = None,
        current_lot: Optional[LotDto] = None,
        orphan_lot_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        if isinstance(node, list):
            for child in node:
                self._process_node(child, notice_dto, current_org, current_lot, orphan_lot_fields)
            return

        if not isinstance(node, dict):
            return

        key = node.get("key")
        value = node.get("value")
        components = node.get("components")

        if key == self.anchor_organization:
            current_org = OrganizationDto()
            current_org.org_ref = self._extract_org_ref(node)
            notice_dto.organizations.append(current_org)

        if key == self.anchor_lot:
            current_lot = LotDto()
            notice_dto.lots.append(current_lot)

        if value is not None and not components:
            self._apply_leaf(key, value, notice_dto, current_org, current_lot, orphan_lot_fields)

        if components:
            self._process_node(components, notice_dto, current_org, current_lot, orphan_lot_fields)

    def _clean_value(self, val: Any) -> Any:
        if isinstance(val, str):
            cleaned = val.replace("\x00", "").strip()
            return cleaned if cleaned != "" else None
        if isinstance(val, dict):
            return {k: self._clean_value(v) for k, v in val.items()}
        if isinstance(val, list):
            return [self._clean_value(x) for x in val]
        return val

    def _apply_leaf(
        self,
        key: str,
        value: Any,
        notice_dto: NoticeDto,
        current_org: Optional[OrganizationDto],
        current_lot: Optional[LotDto],
        orphan_lot_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        value = self._clean_value(value)
        if value is None:
            return

        if key == "OPT-300-Procedure-Buyer":
            notice_dto.procedure.buyer_ref = value
            return
        if key == "OPT-300-Procedure-SProvider":
            notice_dto.procedure.provider_ref = value
            return
        if key == config.WINNER_REF_KEY and current_lot is not None:
            current_lot.winner_ref = value
            return

        if current_lot is not None and key in self.lot_fields:
            setattr(current_lot, self.lot_fields[key], value)
        elif current_lot is not None and key.endswith("-Lot"):
            current_lot.extra_fields[key] = value
        elif current_org is not None and key in self.organization_fields:
            setattr(current_org, self.organization_fields[key], value)
        elif current_org is not None and "Organization" in key:
            current_org.extra_fields[key] = value
        elif key in self.procedure_fields:
            setattr(notice_dto.procedure, self.procedure_fields[key], value)
        elif key.endswith("-Procedure") or "-Procedure-" in key:
            notice_dto.procedure.extra_fields[key] = value
        elif key in self.notice_fields:
            setattr(notice_dto, self.notice_fields[key], value)
        else:
            if key.endswith("-Lot") and current_lot is None:
                if orphan_lot_fields is not None:
                    orphan_lot_fields[key] = value
            notice_dto.extra_fields[key] = value