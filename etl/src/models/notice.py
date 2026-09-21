from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from models.procedure import ProcedureDto
from models.lot import LotDto
from models.organization import OrganizationDto


@dataclass
class NoticeDto:
    notice_id: Optional[str] = None
    notice_version: Optional[str] = None
    notice_type: Optional[str] = None
    form_type: Optional[str] = None
    title: Optional[str] = None
    extra_fields: Dict[str, Any] = field(default_factory=dict)
    organizations: List[OrganizationDto] = field(default_factory=list)
    lots: List[LotDto] = field(default_factory=list)
    procedure: ProcedureDto = field(default_factory=ProcedureDto)