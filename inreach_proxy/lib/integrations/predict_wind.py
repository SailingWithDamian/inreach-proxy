import logging
from datetime import datetime, timedelta
from typing import Tuple, List

import requests
from numpy import average

logger = logging.getLogger(__name__)


class PredictWind:
    def get_route(self, vessel_key: str) -> List[Tuple[datetime, float, float, float]]:
        r = requests.get(f"https://forecast.predictwind.com/tracking/data/{vessel_key}.json", timeout=10)
        r.raise_for_status()
        return [
            (datetime.fromtimestamp(entry["t"]), entry["p"]["lat"], entry["p"]["lon"], entry["bearing"])
            for entry in r.json()["route"]
        ]

    def get_average_bearing(self, vessel_key: str) -> float:
        route = self.get_route(vessel_key)

        cutoff = datetime.now() - timedelta(hours=24)
        return float(average([bearing for time, _, _, bearing in sorted(route, key=lambda x: x[0]) if time >= cutoff]))
