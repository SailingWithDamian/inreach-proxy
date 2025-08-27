import dataclasses
import logging
from datetime import datetime
from typing import Optional, List, Tuple

from django.db.models import Q

from inreach_proxy.lib.processors.actions import ACTION_TO_DB_ID, SpotForecastAction
from inreach_proxy.lib.processors.responses.base import BaseResponse
from inreach_proxy.models import Request, GarminConversations

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SpotForecast(BaseResponse):
    received_time: datetime
    request_code: str
    text: str

    @staticmethod
    def matches(text: str) -> bool:
        for line in text.splitlines():
            if line.startswith("spot:"):
                return True
        return False

    def _get_lat_long_from_request(self) -> Tuple[Optional[str], Optional[str]]:
        parts = self.request_code.split(":")[1].split(",")
        if len(parts) < 2:
            logger.error(f"Could not parse lat/long: {parts}")
            return None, None

        # Normalise to same as request
        return parts[0].rjust(3, "0").upper(), parts[1].rjust(4, "0").upper()

    def find_request_for_response(self, conversion: GarminConversations) -> List[Request]:
        lat, long = self._get_lat_long_from_request()
        if not lat or not long:
            return []

        request = {"lat": lat, "long": long}

        requests = Request.objects.filter(
            Q(status=1)
            & Q(conversation=conversion)
            & Q(action=ACTION_TO_DB_ID[SpotForecastAction])
            & Q(created__lte=self.received_time)
            & Q(input__latitude=request["lat"])
            & Q(input__longitude=request["long"])
        )
        return [request for request in requests]

    def __str__(self) -> str:
        return f"SpotForecast(received_time={self.received_time}, request_code={self.request_code})"

    def get_messages(self) -> List[str]:
        # Strip the body text down to only the forecast lines
        in_block = False

        interesting_lines = []
        for line in self.text.splitlines():
            if line.startswith("Forecast for "):
                in_block = True
                continue
            if line.startswith("Refer to notice") or line.startswith("====="):
                in_block = False
            if in_block:
                interesting_lines.append(line)

        header_fields = [field for field in interesting_lines[0].split(" ") if len(field.strip()) > 0]

        message_prefix = ""
        lat, long = self._get_lat_long_from_request()
        if lat and long:
            message_prefix = f"{lat} {long}\n"

        messages = []
        for line in interesting_lines[3:]:
            if line.strip() == "":
                continue

            fields = [field for field in line.split(" ") if len(field.strip()) > 0]
            mapped = {header_fields[x]: fields[x] for x, _ in enumerate(header_fields)}

            messages.append(
                f"{message_prefix}"
                f'{mapped["Date"]} {mapped["Time"]}\n'
                f'Wind: {mapped["WIND"]}kts gust {mapped["GUST"]}kts @ {mapped["DIR"]}\n'
                f'Sea: {mapped["HTSGW"]}m interval {mapped["PERPW"]}s @ {mapped["DIRPW"]}\n'
                f'Pressure: {mapped["PRESS"]}mb'
            )

        return messages[0:3]
