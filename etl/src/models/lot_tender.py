from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LotTenderDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    lot_reference: str | None = None
    tender_ref: str | None = None
    tender_value: str | None = None
    tender_currency: str | None = None
    tendering_party_ref: str | None = None
    rank: str | None = None
    subcontracting: str | None = None

    extra_fields: dict[str, Any] = Field(default_factory=dict)


class TenderingPartyDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    party_ref: str | None = None
    tenderer_org_refs: list[str] = Field(default_factory=list)
