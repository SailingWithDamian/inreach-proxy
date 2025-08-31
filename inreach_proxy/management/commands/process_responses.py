import logging
import time
from typing import Any

from django.core.management import BaseCommand
from django.db.models import Q

from inreach_proxy.lib.garmin import GarminThread
from inreach_proxy.models import Response, EmailInbox, GarminConversations

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def _handle_response(self, response: Response):
        if GarminThread(response.conversation).send(response.message):
            response.status = 1
            response.save()
        else:
            response.status = 2
            response.save()

    def handle(self, *args: Any, **options: Any) -> None:
        """Check the database for pending responses and send them."""
        processed_responses = 0
        for inbox in EmailInbox.objects.all():
            for conversation in GarminConversations.objects.filter(inbox=inbox).order_by("selector"):
                logger.info(f"[{inbox.name}] Processing {conversation.user}:")

                for response in Response.objects.filter(Q(conversation=conversation) & Q(status=0)).prefetch_related(
                    "conversation"
                ):
                    try:
                        self._handle_response(response)
                    except Exception as e:
                        logger.exception(f"Failed to process {response}: {e}")

                    processed_responses += 1
                    if processed_responses > 1:
                        time.sleep(1)
