import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class SailDocs:
    def build_grib_request(
        self,
        model: Optional[str] = None,
        area: Optional[str] = None,
        grid: Optional[str] = None,
        window: Optional[str] = None,
        parameters: Optional[List[str]] = None,
    ) -> str:
        if not model:
            model = "GFS"
        if model not in {"GFS", "GFS-wave", "HRRR", "ECMWF", "ICON", "NAVGEM", "COAMPS", "RTOFS"}:
            raise ValueError(f"Invalid model: {model}")
        if not area:
            if model == "COAMPS":
                area = "Euro"
            else:
                area = "36n,52n,026w,005e"
        if not grid:
            grid = "0.25,0.25"
        if not window:
            window = "24,48,72,96"
        if not parameters:
            parameters = ["WIND", "PRMSL", "WAVES"]

        return f'send {model}:{area}|{grid}|{window}|{",".join(parameters)}\nquit\n'
