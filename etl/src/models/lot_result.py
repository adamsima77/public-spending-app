from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SubmissionStatDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    category_code: Optional[str] = None  
    count: Optional[str] = None         


class LotResultDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    lot_reference: Optional[str] = None      
    award_outcome: Optional[str] = None       
    non_award_reason: Optional[str] = None    
    lowest_offer_value: Optional[str] = None  
    lowest_offer_currency: Optional[str] = None
    highest_offer_value: Optional[str] = None  
    highest_offer_currency: Optional[str] = None
    tender_refs: List[str] = Field(default_factory=list)   
    contract_refs: List[str] = Field(default_factory=list) 
    submission_stats: List[SubmissionStatDto] = Field(default_factory=list)
    extra_fields: Dict[str, Any] = Field(default_factory=dict)