import logging
from typing import Optional, Tuple
from defusedxml import ElementTree as ET

import requests

from inreach_proxy.lib.helpers import decimal_degress_to_dd_mm_ss

logger = logging.getLogger(__name__)


class Garmin:
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

                latitude = decimal_degress_to_dd_mm_ss(parts[0], True)
                longitude = decimal_degress_to_dd_mm_ss(parts[1], False)
                return longitude, latitude

        return None, None
