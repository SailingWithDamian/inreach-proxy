import logging
from typing import Any

from django.core.management import BaseCommand

from inreach_proxy.lib.business import process_response, create_request_for_action
from inreach_proxy.lib.email import Inbound
from inreach_proxy.lib.parsers import parse_message
from inreach_proxy.models import EmailInbox, GarminConversations

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        """Check the inbox for new messages and process them."""
        for inbox in EmailInbox.objects.all():
            inbound = Inbound(inbox.imap_host, inbox.username, inbox.password)
            for conversation in GarminConversations.objects.filter(inbox=inbox).order_by("selector"):
                pending_messages = inbound.get_pending_messages(conversation.address)
                logger.info(f"[{inbox.name}] Found {len(pending_messages)} pending messages for {conversation.user}")

                for message in pending_messages:
                    parsed_message = parse_message(message, inbox.settings)

                    if parsed_message.garmin_reply_url and conversation.reply_url != parsed_message.garmin_reply_url:
                        logger.info(f"[{conversation.user}] Updating reply url to {parsed_message.garmin_reply_url}")
                        conversation.reply_url = parsed_message.garmin_reply_url
                        conversation.save()

                    for action in parsed_message.actions:
                        logger.info(f"[{inbox.name}] Creating action {action}")
                        create_request_for_action(conversation, action)

                    for response in parsed_message.responses:
                        logger.info(f"[{inbox.name}] Handling response {response}")
                        process_response(conversation, response)
