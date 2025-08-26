import logging
from typing import Any

from django.core.management import BaseCommand
from django.core.management import call_command

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def _execute_command(self, command):
        try:
            call_command(command)
        except Exception as e:
            logger.warning(f"Executing {command} failed: {e}")

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute a full run."""
        # Handle emails
        self._execute_command("process_incoming")

        # Process things in the request queue (from messages)
        self._execute_command("process_requests")

        # Process things in the response queue (from requests)
        self._execute_command("process_responses")
