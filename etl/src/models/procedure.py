from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from models.organization import OrganizationDto


@dataclass
class ProcedureDto:
    reference: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    main_cpv: Optional[str] = None
    buyer_ref: Optional[str] = None
    provider_ref: Optional[str] = None
    buyer: Optional[OrganizationDto] = None
    provider: Optional[OrganizationDto] = None
    extra_fields: Dict[str, Any] = field(default_factory=dict)