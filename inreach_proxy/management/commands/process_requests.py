import logging
import time
from typing import Any

from django.core.management import BaseCommand
from django.db.models import Q

from inreach_proxy.lib.business import create_response
from inreach_proxy.lib.processors.actions import VALID_ACTIONS
from inreach_proxy.models import Request, EmailInbox, GarminConversations

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def _handle_request(self, request: Request):
        try:
            action = VALID_ACTIONS[request.action].from_inputs(request.id, request.input)
        except TypeError as e:
            logger.error(f"Failed to construct action from request {request}: {e}")
            request.status = 3
            request.save()
            return

        if action.get_type() == 1:
            # Sync execution
            logger.info(f"Executing sync {action} for {request}")
            output = action.execute()
            create_response(request.conversation, request, output)
            request.status = 2
            request.save()
        else:
            # Async execution
            logger.info(f"Executing async {action} for {request}")
            action.execute_with_email(request.conversation)
            # Update the data in case the action changed it i.e. resolved a position
            request.input = action.get_data()
            request.status = 1
            request.save()

    def handle(self, *args: Any, **options: Any) -> None:
        """Check the database for pending requests and execute them."""
        processed_requests = 0
        for inbox in EmailInbox.objects.all():
            for conversation in GarminConversations.objects.filter(inbox=inbox).order_by("selector"):
                logger.info(f"[{inbox.name}] Processing {conversation.user}:")

                for request in Request.objects.filter(Q(conversation=conversation) & Q(status=0)).prefetch_related(
                    "conversation"
                ):

                    try:
                        self._handle_request(request)
                    except Exception as e:
                        logger.exception(f"Failed to process {request}: {e}")

                    processed_requests += 1
                    if processed_requests > 1:
                        time.sleep(1)
