from email.message import EmailMessage
from typing import Optional, Tuple, Union


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
        ("W" if str(decimal_string)[0] == "-" else "E")
        if is_latitude
        else ("S" if str(decimal_string)[0] == "-" else "N")
    )
    decimal_degress = float(str(decimal_string).lstrip("-"))

    degrees = int(decimal_degress)
    decimal_minutes = abs(decimal_degress - degrees) * 60
    minutes = int(decimal_minutes)
    return f"{degrees}.{minutes}{orientation}"


def calculate_bounding_box(latitude: str, longitude: str) -> Tuple[str, str, str, str]:
    latitude = dd_mm_ss_to_decimal_degrees(latitude)
    longitude = dd_mm_ss_to_decimal_degrees(longitude)
    return (
        decimal_degress_to_dd_mm_ss(latitude - 1, False),
        decimal_degress_to_dd_mm_ss(latitude + 1, False),
        decimal_degress_to_dd_mm_ss(longitude - 1, True),
        decimal_degress_to_dd_mm_ss(longitude + 1, True),
    )
