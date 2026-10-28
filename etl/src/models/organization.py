from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OrganizationDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    cin: str | None = None
    tin: str | None = None
    name: str | None = None
    address: str | None = None
    street_name: str | None = None
    street_number: str | None = None
    phone: str | None = None
    town: str | None = None
    postal_code: str | None = None
    country: str | None = None
    nuts_code: str | None = None
    company_size: str | None = None
    extra_fields: dict[str, Any] = Field(default_factory=dict)
    org_ref: str | None = None
