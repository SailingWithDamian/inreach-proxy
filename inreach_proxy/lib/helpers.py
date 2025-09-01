import math
from email.message import EmailMessage
from typing import Optional, Union


def get_message_plain_text_body(message: EmailMessage) -> Optional[str]:
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            content_disposition = part.get("Content-Disposition", "")
            if content_type == "text/plain" and "attachment" not in content_disposition:
                return part.get_content()
    else:
        if message.get_content_type() == "text/plain":
            return message.get_content()

    return None


def get_grib_attachment(message: EmailMessage) -> Optional[bytes]:
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "application/octet-stream" or "attachment" in part.get(
                "Content-Disposition", ""
            ):
                return part.get_content()
    return None


def dd_mm_ss_to_decimal_degrees(coord: str):
    degrees, minutes = map(float, coord[:-1].split("."))
    decimal = degrees + minutes / 60
    if coord[-1] in ["S", "W"]:
        decimal = -decimal
    return decimal


def decimal_degress_to_dd_mm_ss(decimal_string: Union[str, float], is_latitude: bool):
    orientation = (
        ("S" if str(decimal_string)[0] == "-" else "N")
        if is_latitude
        else ("W" if str(decimal_string)[0] == "-" else "E")
    )
    decimal_degrees = float(str(decimal_string).lstrip("-"))

    degrees = int(decimal_degrees)
    decimal_minutes = abs(decimal_degrees - degrees) * 60
    minutes = int(decimal_minutes)

    return normalise_dd_mm_ss(f"{degrees}.{minutes}{orientation}", is_latitude)


def normalise_dd_mm_ss(text: str, is_latitude: bool) -> str:
    orientation = ""
    if text[-1].upper() in {"N", "S", "E", "W"}:
        orientation = text[-1].upper()
        text = text[0:-1]

    expected_len = 2 if is_latitude else 3
    if "." in text:
        parts = text.split(".")
        return f'{parts[0].rjust(expected_len, "0")[-expected_len:]}.{parts[1]}{orientation}'
    return f'{text.rjust(expected_len, "0")[-expected_len:]}{orientation}'


def calculate_bounding_box(latitude: float, longitude: float, bearing: Optional[float] = None):
    half_box = 120 / 2.0
    delta_latitude = 1.0 / 60.0
    delta_longitude = 1.0 / (60.0 * math.cos(math.radians(latitude)))

    if bearing is not None:
        heading = math.radians(bearing)
        delta_x_nm = half_box * math.sin(heading)
        delta_y_nm = half_box * math.cos(heading)

        forward_x_deg = delta_x_nm * (2 * 0.9) * delta_longitude
        forward_y_deg = delta_y_nm * (2 * 0.9) * delta_latitude
        backward_x_deg = -delta_x_nm * (2 * 0.1) * delta_longitude
        backward_y_deg = -delta_y_nm * (2 * 0.1) * delta_latitude

        latitude_min = latitude + min(backward_y_deg, forward_y_deg)
        latitude_max = latitude + max(backward_y_deg, forward_y_deg)
        longitude_min = longitude + min(backward_x_deg, forward_x_deg)
        longitude_max = longitude + max(backward_x_deg, forward_x_deg)
    else:
        latitude_min = latitude - delta_latitude
        latitude_max = latitude + delta_latitude
        longitude_min = longitude - delta_longitude
        longitude_max = longitude + delta_longitude

    return (
        decimal_degress_to_dd_mm_ss(latitude_min, True),
        decimal_degress_to_dd_mm_ss(latitude_max, True),
        decimal_degress_to_dd_mm_ss(longitude_min, False),
        decimal_degress_to_dd_mm_ss(longitude_max, False),
    )
