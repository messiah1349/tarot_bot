from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

@dataclass
class AgentChat:
    chat: Any
    last_call_date: Optional[datetime]
    last_call_status: bool # True means success
