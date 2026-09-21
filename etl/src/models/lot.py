from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class LotDto:
    lot_reference: Optional[str] = None
    title: Optional[str] = None
    main_cpv: Optional[str] = None
    award_criterion: Optional[str] = None
    extra_fields: Dict[str, Any] = field(default_factory=dict)