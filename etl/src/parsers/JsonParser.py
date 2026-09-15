import aiofiles
import ijson
from typing import AsyncIterator, Iterator, Dict, Any, List, Optional, Tuple

class JsonParser:
    def __init__(self, target_bt_codes: Optional[List[str]] = None):    
        self.target_bt_codes = set(target_bt_codes or [])

    