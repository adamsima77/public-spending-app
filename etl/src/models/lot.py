from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LotDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    lot_reference: str | None = None
    title: str | None = None
    description: str | None = None
    estimated_value: str | None = None
    estimated_currency: str | None = None
    framework_max_value: str | None = None
    framework_max_currency: str | None = None
    main_cpv: str | None = None
    nuts_code: str | None = None
    award_criterion: str | None = None
    submission_deadline: str | None = None
    document_url: str | None = None
    detail_url: str | None = None
    place_of_performance: str | None = None
    duration_value: str | None = None
    duration_unit: str | None = None
    eu_funded: str | None = None
    eordering_allowed: bool | None = None
    epayment_allowed: bool | None = None
    einvoicing: str | None = None
    variants_allowed: str | None = None
    reserved_execution: str | None = None
    reserved_participation: str | None = None

    extra_fields: dict[str, Any] = Field(default_factory=dict)
