import logging
from getpass import getpass
from typing import Any

from django.core.management import BaseCommand, CommandParser

from inreach_proxy.models import EmailInbox, GarminConversations

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--name", required=True)
        parser.add_argument("--username")
        parser.add_argument("--imap-host")
        parser.add_argument("--smtp-host")
        parser.add_argument("--selector")

    def handle(self, *args: Any, **options: Any) -> None:
        """Configure an email inbox / converstaion."""
        try:
            inbox = EmailInbox.objects.get(name=options["name"])
        except EmailInbox.DoesNotExist:
            if not all([options["username"], options["imap_host"], options["smtp_host"]]):
                print("Must pass additional arguments for mailbox creation")
                return

            password = getpass("Password: ")

            inbox = EmailInbox.objects.create(
                name=options["name"],
                username=options["username"],
                password=password,
                smtp_host=options["smtp_host"],
                imap_host=options["imap_host"],
            )
            logger.info(f"Created inbox: {inbox}")
        else:
            logger.info(f"Inbox already exists: {inbox}")

        conversation, created = GarminConversations.objects.get_or_create(inbox=inbox, selector=options["selector"])
        if created:
            logger.info(f"Created conversation: {conversation}")
        else:
            logger.info(f"Conversation already exists: {conversation}")
