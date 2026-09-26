from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from models.lot import LotDto
from models.organization import OrganizationDto
from models.procedure import ProcedureDto


class NoticeDto(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    notice_id: Optional[str] = None
    notice_version: Optional[str] = None
    notice_type: Optional[str] = None
    form_type: Optional[str] = None
    title: Optional[str] = None
    legal_basis: Optional[str] = None
    issue_date: Optional[str] = None
    published_at: Optional[str] = None  
    contract_conclusion_date: Optional[str] = None
    extra_fields: Dict[str, Any] = Field(default_factory=dict)
    organizations: List[OrganizationDto] = Field(default_factory=list)
    lots: List[LotDto] = Field(default_factory=list)
    procedure: ProcedureDto = Field(default_factory=ProcedureDto)