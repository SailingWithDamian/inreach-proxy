import base64
import dataclasses
import zlib
from datetime import datetime
from typing import List

from django.db.models import Q

from inreach_proxy.lib.helpers import normalise_dd_mm_ss
from inreach_proxy.lib.processors.actions import GribFetchAction, ACTION_TO_DB_ID
from inreach_proxy.lib.processors.responses.base import BaseResponse
from inreach_proxy.models import Request, GarminConversations


@dataclasses.dataclass
class Grib(BaseResponse):
    received_time: datetime
    request_code: str
    grib: bytes

    @staticmethod
    def matches(text: str) -> bool:
        for line in text.splitlines():
            if any(
                {
                    line.upper().startswith(f"{model}:")
                    for model in {"GFS", "GFS-WAVE", "HRRR", "ECMWF", "ICON", "NAVGEM", "COAMPS", "RTOFS"}
                }
            ):
                return True
        return False

    def find_request_for_response(self, conversation: GarminConversations) -> List[Request]:
        model = self.request_code.split(":")[0]
        parts = self.request_code.split(":")[1].split("|")

        # Normalise area (same as request):
        # N/S is 00 - 90
        # E/W is 000 - 180
        area_parts = parts[0].split(",")
        if len(area_parts) == 4:
            area_parts[0] = normalise_dd_mm_ss(area_parts[0], True)
            area_parts[1] = normalise_dd_mm_ss(area_parts[1], True)
            area_parts[2] = normalise_dd_mm_ss(area_parts[2], False)
            area_parts[3] = normalise_dd_mm_ss(area_parts[3], False)
            parts[0] = ",".join(area_parts)

        request = {
            "model": model,
            "area": parts[0],
            "grid": parts[1],
            "window": parts[2],
            "parameters": sorted(parts[3].split(",")),
        }

        requests = Request.objects.filter(
            Q(status=1)
            & Q(conversation=conversation)
            & Q(action=ACTION_TO_DB_ID[GribFetchAction])
            & Q(created__lte=self.received_time)
            & Q(input__model=request["model"])
            & Q(input__area=request["area"])
            & Q(input__grid=request["grid"])
            & Q(input__window=request["window"])
            & Q(input__parameters=request["parameters"])
        )
        return [request for request in requests]

    def __str__(self) -> str:
        return f"Grib(received_time={self.received_time}, request_code={self.request_code})"

    def get_message_type(self) -> "str":
        return "grib"

    def get_messages(self) -> List[str]:
        return [base64.b64encode(zlib.compress(self.grib)).decode()]
