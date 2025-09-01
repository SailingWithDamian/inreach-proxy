import dataclasses
from email.message import EmailMessage
from typing import Dict, Any, List, Optional

from inreach_proxy.lib.email import Outbound
from inreach_proxy.lib.helpers import get_message_plain_text_body, calculate_bounding_box, normalise_dd_mm_ss
from inreach_proxy.lib.integrations.garmin import Garmin
from inreach_proxy.lib.integrations.predict_wind import PredictWind
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
        if model.upper() not in {"GFS", "GFS-WAVE", "HRRR", "ECMWF", "ICON", "NAVGEM", "COAMPS", "RTOFS"}:
            raise ValueError(f"Invalid model: {model}")

        area_parts = parts[1].split(",") if len(parts) >= 2 else "auto"

        if len(parts) < 2 or parts[1].lower() in {"auto", "auto:simple"}:
            if settings:
                bearing = None
                if len(parts) < 2 or parts[1].lower() == "auto":
                    if predict_wind_key := settings.get("predict_wind_key"):
                        bearing = PredictWind().get_average_bearing(predict_wind_key)

                if map_share_key := settings.get("map_share_key"):
                    latitude, longitude = Garmin().get_latest_position(map_share_key)
                    if latitude and longitude:
                        (
                            min_latitude,
                            max_latitude,
                            min_longitude,
                            max_longitude,
                        ) = calculate_bounding_box(latitude, longitude, bearing)
                        area_parts = [min_latitude, max_latitude, min_longitude, max_longitude]

        if not isinstance(area_parts, list) or len(area_parts) != 4:
            area_parts = ["36n", "52n", "026w", "005e"]

        # Normalise area:
        # N/S is 00 - 90
        # E/W is 000 - 180
        area_parts[0] = normalise_dd_mm_ss(area_parts[0], True)
        area_parts[1] = normalise_dd_mm_ss(area_parts[1], True)
        area_parts[2] = normalise_dd_mm_ss(area_parts[2], False)
        area_parts[3] = normalise_dd_mm_ss(area_parts[3], False)

        window = parts[2] if len(parts) >= 3 else None
        if len(parts) < 2 or parts[1].lower() == "auto":
            window = "24"

        parameters = parts[4].split(",") if len(parts) >= 5 else None
        if len(parts) < 2 or parts[1].lower() == "auto":
            parameters = ["WIND"]

        return GribFetchAction(
            model=model,
            area=",".join(area_parts),
            grid=parts[3] if len(parts) >= 4 else "0.25,0.25",
            window=window or "24,48,72,96",
            parameters=sorted(parameters or ["WIND", "PRMSL", "WAVES"]),
        )

    def get_type(self) -> int:
        return 0

    def execute_with_email(self, conversation: GarminConversations):
        request = f'send {self.model}:{self.area}|{self.grid}|{self.window}|{",".join(self.parameters)}\nquit\n'
        out = Outbound(conversation.inbox.smtp_host, conversation.inbox.username, conversation.inbox.password)
        out.send_email("query@saildocs.com", request, reply_address=conversation.address)
