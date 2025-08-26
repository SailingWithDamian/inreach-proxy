import logging
from typing import Optional, Tuple
from defusedxml import ElementTree as ET

import requests

logger = logging.getLogger(__name__)


class Garmin:
    def _decimal_degress_to_dd_mm_ss(self, decimal_string: str, is_latitude: bool):
        orientation = (
            ("W" if decimal_string[0] == "-" else "E") if is_latitude else ("S" if decimal_string[0] == "-" else "N")
        )
        decimal_degress = float(decimal_string.lstrip("-"))

        degrees = int(decimal_degress)
        decimal_minutes = abs(decimal_degress - degrees) * 60
        minutes = int(decimal_minutes)
        return f"{degrees}.{minutes}{orientation}"

    def get_latest_position(self, share_key: str) -> Tuple[Optional[str], Optional[str]]:
        r = requests.get(f"https://share.garmin.com/Feed/Share/{share_key}", timeout=10)
        r.raise_for_status()
        root = ET.fromstring(r.text)

        coordinates = root.find(
            ".//kml:Placemark//kml:Point//kml:coordinates", {"kml": "http://www.opengis.net/kml/2.2"}
        )
        if coordinates is not None:
            if "," in coordinates.text:
                parts = coordinates.text.split(",")

                latitude = self._decimal_degress_to_dd_mm_ss(parts[0], True)
                longitude = self._decimal_degress_to_dd_mm_ss(parts[1], False)
                return longitude, latitude

        return None, None
