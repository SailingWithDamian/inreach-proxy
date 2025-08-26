import dataclasses
from typing import List, Optional

from inreach_proxy.lib.processors.actions.base import BaseAction
from inreach_proxy.lib.processors.responses.base import BaseResponse


@dataclasses.dataclass
class ParsedEmail:
    from_address: str
    garmin_reply_url: Optional[str] = None
    actions: List[BaseAction] = dataclasses.field(default_factory=list)
    responses: List[BaseResponse] = dataclasses.field(default_factory=list)
