from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from models.organization import OrganizationDto


class ProcedureDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    reference: str | None = None
    identifier: str | None = None
    source_order_id: str | None = None
    title: str | None = None
    description: str | None = None
    procedure_type: str | None = None
    contract_type: str | None = None
    main_cpv: str | None = None
    estimated_value: str | None = None
    currency: str | None = None
    nuts_code: str | None = None
    buyer_profile_url: str | None = None
    performance_note: str | None = None
    buyer_ref: str | None = None
    provider_ref: str | None = None
    buyer: OrganizationDto | None = None
    provider: OrganizationDto | None = None
    place_of_performance: str | None = None
    extra_fields: dict[str, Any] = Field(default_factory=dict)
