from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SubmissionStatDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    category_code: str | None = None
    count: str | None = None


class LotResultDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    lot_reference: str | None = None
    award_outcome: str | None = None
    non_award_reason: str | None = None
    lowest_offer_value: str | None = None
    lowest_offer_currency: str | None = None
    highest_offer_value: str | None = None
    highest_offer_currency: str | None = None
    tender_refs: list[str] = Field(default_factory=list)
    contract_refs: list[str] = Field(default_factory=list)
    submission_stats: list[SubmissionStatDto] = Field(default_factory=list)
    extra_fields: dict[str, Any] = Field(default_factory=dict)
