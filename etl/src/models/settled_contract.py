from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SettledContractDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    contract_ref: Optional[str] = None     
    contract_number: Optional[str] = None  
    conclusion_date: Optional[str] = None  
    title: Optional[str] = None            
    contract_url: Optional[str] = None     
    tender_refs: List[str] = Field(default_factory=list) 
    extra_fields: Dict[str, Any] = Field(default_factory=dict)