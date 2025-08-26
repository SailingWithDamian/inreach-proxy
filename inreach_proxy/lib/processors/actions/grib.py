import dataclasses
from email.message import EmailMessage
from typing import Dict, Any, List, Optional

from inreach_proxy.lib.email import Outbound
from inreach_proxy.lib.helpers import get_message_plain_text_body
from inreach_proxy.lib.processors.actions.base import BaseAction
from inreach_proxy.models import GarminConversations


@dataclasses.dataclass
class GribFetchAction(BaseAction):
    model: str
    area: str
    window: str
    grid: str
    parameters: List[str]

    @staticmethod
    def matches(text: str) -> bool:
        for line in text.splitlines():
            if line.strip() == "grib" or line.startswith("grib "):
                return True
        return False

    @staticmethod
    def from_email(message: EmailMessage, settings: Optional[Dict[Any, Any]] = None) -> "GribFetchAction":
        for line in get_message_plain_text_body(message).splitlines():
            if line.strip() == "grib" or line.startswith("grib "):
                return GribFetchAction.from_text(line, settings)

    @staticmethod
    def from_text(text: str, settings: Optional[Dict[Any, Any]] = None) -> "GribFetchAction":
        parts = text.split(" ")[1].strip().split("|") if " " in text else []

        model = parts[0].strip() if len(parts) >= 1 else "GFS"
        if model not in {"GFS", "GFS-wave", "HRRR", "ECMWF", "ICON", "NAVGEM", "COAMPS", "RTOFS"}:
            raise ValueError(f"Invalid model: {model}")

        default_area = ["36n", "52n", "026w", "005e"]
        area_parts = parts[1].split(",") if len(parts) >= 2 else default_area
        if len(area_parts) != 4:
            area_parts = default_area

        # Normalise area:
        # N/S is 00 - 90
        # E/W is 000 - 180
        area_parts[0] = area_parts[0].rjust(3, "0")
        area_parts[1] = area_parts[1].rjust(3, "0")
        area_parts[2] = area_parts[2].rjust(4, "0")
        area_parts[3] = area_parts[3].rjust(4, "0")

        return GribFetchAction(
            model=model,
            area=",".join(area_parts).lower(),
            grid=parts[3] if len(parts) >= 4 else "0.25,0.25",
            window=parts[2] if len(parts) >= 3 else "24,48,72,96",
            parameters=sorted(parts[4].split(",") if len(parts) >= 5 else ["WIND", "PRMSL", "WAVES"]),
        )

    def get_type(self) -> int:
        return 0

    def execute_with_email(self, conversation: GarminConversations):
        request = f'send {self.model}:{self.area}|{self.grid}|{self.window}|{",".join(self.parameters)}\nquit\n'
        out = Outbound(conversation.inbox.smtp_host, conversation.inbox.username, conversation.inbox.password)
        out.send_email("query@saildocs.com", request, reply_address=conversation.address)
