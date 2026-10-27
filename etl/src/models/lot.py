from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class LotDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    lot_reference: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    estimated_value: Optional[str] = None        
    estimated_currency: Optional[str] = None
    framework_max_value: Optional[str] = None    
    framework_max_currency: Optional[str] = None
    main_cpv: Optional[str] = None
    nuts_code: Optional[str] = None
    award_criterion: Optional[str] = None       
    submission_deadline: Optional[str] = None
    document_url: Optional[str] = None
    detail_url: Optional[str] = None
    place_of_performance: Optional[str] = None
    duration_value: Optional[str] = None
    duration_unit: Optional[str] = None
    eu_funded: Optional[str] = None              
    eordering_allowed: Optional[bool] = None     
    epayment_allowed: Optional[bool] = None    
    einvoicing: Optional[str] = None            
    variants_allowed: Optional[str] = None       
    reserved_execution: Optional[str] = None    
    reserved_participation: Optional[str] = None 

    extra_fields: Dict[str, Any] = Field(default_factory=dict)