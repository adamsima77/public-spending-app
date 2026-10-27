from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class OrganizationDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    cin: Optional[str] = None
    tin: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    street_name: Optional[str] = None
    street_number: Optional[str] = None
    phone: Optional[str] = None
    town: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    nuts_code: Optional[str] = None
    company_size: Optional[str] = None
    extra_fields: Dict[str, Any] = Field(default_factory=dict)
    org_ref: Optional[str] = None