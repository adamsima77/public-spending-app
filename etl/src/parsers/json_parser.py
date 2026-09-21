import json
import aiofiles
import ijson
from typing import Any, Optional, Dict
from models.notice import NoticeDto
from models.lot import LotDto
from models.organization import OrganizationDto


class JsonParser:
    def __init__(self, notice_fields: Dict[str, str], organization_fields: Dict[str, str], procedure_fields: Dict[str, str],
                 lot_fields: Dict[str, str], anchor_organization: str, anchor_lot: str):
        self.notice_fields = notice_fields
        self.organization_fields = organization_fields
        self.procedure_fields = procedure_fields
        self.lot_fields = lot_fields
        self.anchor_organization = anchor_organization
        self.anchor_lot = anchor_lot
        

    def _resolve_org_refs(self, notice_dto: NoticeDto) -> None:
        orgs = notice_dto.organizations
        org_by_index = {f"ORG-{i+1:04d}": org for i, org in enumerate(orgs)}
        procedure = notice_dto.procedure
        procedure.buyer = org_by_index.get(procedure.buyer_ref)
        procedure.provider = org_by_index.get(procedure.provider_ref)

    async def parse_file(self, file_path: str):
        async with aiofiles.open(file_path, mode="rb") as f:
            async for item in ijson.items_async(f, "bulletinItemList.item"):
                try:
                    inner = json.loads(item["itemData"])
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    print(f"Preskakujem item, chyba: {e}")
                    continue

                notice_dto = NoticeDto()
                for component in inner.get("components", []):
                    self._process_node(component, notice_dto)

                self._resolve_org_refs(notice_dto)
                yield notice_dto

    def _process_node(self, node: Dict[str, Any], notice_dto: NoticeDto, current_org: Optional[OrganizationDto] = None, current_lot: Optional[LotDto] = None) -> None:
        if isinstance(node, list):
            for child in node:
                self._process_node(child, notice_dto, current_org, current_lot)
            return

        key = node.get("key")
        value = node.get("value")
        components = node.get("components")

        if key == self.anchor_organization:
            current_org = OrganizationDto()
            notice_dto.organizations.append(current_org)

        if key == self.anchor_lot:
            current_lot = LotDto()
            notice_dto.lots.append(current_lot)

        if value is not None and not components:
            self._apply_leaf(key, value, notice_dto, current_org, current_lot)

        if components:
            self._process_node(components, notice_dto, current_org, current_lot)

    def _apply_leaf(self, key: str, value: Any, notice_dto: NoticeDto, current_org: Optional[OrganizationDto], current_lot: Optional[LotDto]) -> None:
        if key == "OPT-300-Procedure-Buyer":
            notice_dto.procedure.buyer_ref = value
            return
        if key == "OPT-300-Procedure-SProvider":
            notice_dto.procedure.provider_ref = value
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
            notice_dto.extra_fields[key] = value