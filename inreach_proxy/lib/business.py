import logging
from typing import Optional, List

from inreach_proxy.lib.models import ParsedEmail
from inreach_proxy.lib.processors.actions import VALID_ACTIONS
from inreach_proxy.lib.processors.actions.base import BaseAction
from inreach_proxy.lib.processors.responses.base import BaseResponse
from inreach_proxy.models import Request, EmailInbox, GarminConversations, Response

logger = logging.getLogger(__name__)


def get_conversation_for_message(email_inbox: EmailInbox, parsed_message: ParsedEmail):
    selector = (
        parsed_message.from_address.split(f"{email_inbox.username}+")[1]
        if parsed_message.from_address.startswith(f"{email_inbox.username}+")
        else None
    )

    conversation, created = GarminConversations.objects.get_or_create(inbox=email_inbox, selector=selector)

    if created or (parsed_message.garmin_reply_url and conversation.reply_url != parsed_message.garmin_reply_url):
        conversation.reply_url = parsed_message.garmin_reply_url
        conversation.save()
    return conversation


def create_request_for_action(conversation: GarminConversations, action: BaseAction):
    database_id = None
    for db_id, valid_action in VALID_ACTIONS.items():
        if isinstance(action, valid_action):
            database_id = db_id
            break

    if database_id is None:
        raise ValueError(f"Failed to find database ID for {action}")

    Request.objects.create(
        conversation=conversation,
        status=0,
        action=database_id,
        input=action.get_data(),
    )


def execute_action(conversation: GarminConversations, action: BaseAction):
    create_response(conversation, None, action.execute())


def process_response(conversation: GarminConversations, response: BaseResponse):
    requests = response.find_request_for_response(conversation)
    if not requests:
        logger.error(f"Failed to find request for {response}")
        return

    for request in requests:
        for message in response.get_messages():
            create_response(request.conversation, request, message, response.get_message_type())


def chunk_message(text: str, message_type: str) -> List[str]:
    if len(text) <= 160 and message_type == "txt":
        return [text]

    chunk_size = 160 - len(f"msg:{message_type}:01:99:")

    messages = []
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
    for x, chunk in enumerate(chunks):
        messages.append(f"msg:{message_type}:{x + 1:02d}:{len(chunks):02d}:{chunk}")
    return messages


def create_response(
    conversation: GarminConversations, request: Optional[Request], text: str, message_type: str = "text"
):
    for message in chunk_message(text, message_type):
        Response.objects.create(
            conversation=conversation,
            request=request,
            status=0,
            message=message,
        )
