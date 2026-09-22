from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field
from models.organization import OrganizationDto


class ProcedureDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    reference: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    procedure_type: Optional[str] = None
    main_cpv: Optional[str] = None
    total_value: Optional[str] = None
    currency: Optional[str] = None
    buyer_ref: Optional[str] = None
    provider_ref: Optional[str] = None
    buyer: Optional[OrganizationDto] = None
    provider: Optional[OrganizationDto] = None
    extra_fields: Dict[str, Any] = Field(default_factory=dict)