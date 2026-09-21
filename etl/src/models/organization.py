from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class OrganizationDto:
    name: Optional[str] = None
    cin: Optional[str] = None
    tin: Optional[str] = None
    town: Optional[str] = None
    country: Optional[str] = None
    extra_fields: Dict[str, Any] = field(default_factory=dict)