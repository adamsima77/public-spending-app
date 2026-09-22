from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class LotDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    lot_reference: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    value: Optional[str] = None
    currency: Optional[str] = None
    main_cpv: Optional[str] = None
    nuts_code: Optional[str] = None
    award_criterion: Optional[str] = None
    extra_fields: Dict[str, Any] = Field(default_factory=dict)