from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field
from models.organization import OrganizationDto


class ProcedureDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    reference: Optional[str] = None
    identifier: Optional[str] = None  
    source_order_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    procedure_type: Optional[str] = None
    contract_type: Optional[str] = None
    main_cpv: Optional[str] = None
    estimated_value: Optional[str] = None
    currency: Optional[str] = None
    nuts_code: Optional[str] = None
    buyer_profile_url: Optional[str] = None
    performance_note: Optional[str] = None
    buyer_ref: Optional[str] = None
    provider_ref: Optional[str] = None
    buyer: Optional[OrganizationDto] = None
    provider: Optional[OrganizationDto] = None
    place_of_performance: Optional[str] = None
    extra_fields: Dict[str, Any] = Field(default_factory=dict)