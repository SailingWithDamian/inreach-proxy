from email.message import EmailMessage
from typing import Optional


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
