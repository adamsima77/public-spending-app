from typing import Any

from models.lot import LotDto
from models.lot_result import LotResultDto
from models.lot_tender import LotTenderDto, TenderingPartyDto
from models.organization import OrganizationDto
from models.procedure import ProcedureDto
from models.settled_contract import SettledContractDto
from pydantic import BaseModel, ConfigDict, Field


class NoticeDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    notice_id: str | None = None
    notice_version: str | None = None
    notice_type: str | None = None
    form_type: str | None = None
    title: str | None = None
    legal_basis: str | None = None
    issue_date: str | None = None
    published_at: str | None = None
    extra_fields: dict[str, Any] = Field(default_factory=dict)
    organizations: list[OrganizationDto] = Field(default_factory=list)
    lots: list[LotDto] = Field(default_factory=list)
    procedure: ProcedureDto = Field(default_factory=ProcedureDto)
    lot_results: list[LotResultDto] = Field(default_factory=list)
    lot_tenders: list[LotTenderDto] = Field(default_factory=list)
    tendering_parties: list[TenderingPartyDto] = Field(default_factory=list)
    settled_contracts: list[SettledContractDto] = Field(default_factory=list)
