import email
import imaplib
import logging
import smtplib
from email import policy
from email.message import Message
from email.parser import BytesParser
from typing import List, Optional

logger = logging.getLogger(__name__)


class Inbound:
    def __init__(self, host: str, username: str, password: str, port: int = 993) -> None:
        self._imap_host = host
        self._imap_port = port
        self._imap_username = username
        self._imap_password = password

    def get_pending_messages(self, to_address: Optional[str] = None) -> List[Message]:
        pending_messages = []
        with imaplib.IMAP4_SSL(self._imap_host, self._imap_port) as mailbox:
            mailbox.login(self._imap_username, self._imap_password)
            mailbox.select("Inbox")

            if to_address:
                ret, data = mailbox.search(None, f'(UNSEEN HEADER TO "{to_address}")')
            else:
                ret, data = mailbox.search(None, "(UNSEEN)")
            if ret == "OK":
                for message_number in data[0].split():
                    if not message_number:
                        continue
                    ret, data = mailbox.fetch(message_number, "(RFC822)")
                    if ret == "OK":
                        message = BytesParser(policy=policy.default).parsebytes(data[0][1])
                        pending_messages.append(message)
        return pending_messages


class Outbound:
    def __init__(self, host: str, username: str, password: str, port: int = 465) -> None:
        self._smtp_host = host
        self._smtp_port = port
        self._smtp_username = username
        self._smtp_password = password

    def send_email(self, to: str, body: str, subject: Optional[str] = None, reply_address: Optional[str] = None):
        message = email.message.EmailMessage()
        message["From"] = self._smtp_username
        if reply_address:
            message["Reply-To"] = reply_address
        message["To"] = to
        if subject:
            message["Subject"] = subject
        message.set_content(body)
        self.send_message(message)

    def send_message(self, message: email.message.EmailMessage):
        with smtplib.SMTP_SSL(self._smtp_host, self._smtp_port) as smtp:
            smtp.login(self._smtp_username, self._smtp_password)
            smtp.send_message(message)
