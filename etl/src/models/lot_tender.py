from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class LotTenderDto(BaseModel):

    model_config = ConfigDict(validate_assignment=True)

    lot_reference: Optional[str] = None        
    tender_ref: Optional[str] = None          
    tender_value: Optional[str] = None         
    tender_currency: Optional[str] = None
    tendering_party_ref: Optional[str] = None  
    rank: Optional[str] = None                 
    subcontracting: Optional[str] = None       

    extra_fields: Dict[str, Any] = Field(default_factory=dict)


class TenderingPartyDto(BaseModel):

    model_config = ConfigDict(validate_assignment=True)

    party_ref: Optional[str] = None
    tenderer_org_refs: list[str] = Field(default_factory=list)