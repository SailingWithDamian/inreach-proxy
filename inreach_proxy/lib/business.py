import logging
from typing import Optional

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


def process_response(conversion: GarminConversations, response: BaseResponse):
    requests = response.find_request_for_response(conversion)
    if not requests:
        logger.error(f"Failed to find request for {response}")
        return

    for request in requests:
        for message in response.get_messages():
            create_response(request.conversation, request, message)


def create_response(conversation: GarminConversations, request: Optional[Request], text: str):
    if len(text) < 160:
        Response.objects.create(
            conversation=conversation,
            request=request,
            status=0,
            message=text,
        )
    else:
        chunks = [text[i : i + 140] for i in range(0, len(text), 140)]
        for x, chunk in enumerate(chunks):
            Response.objects.create(
                conversation=conversation,
                request=request,
                status=0,
                message=f"msg: {x}/{len(chunks)}\n{chunk}\nZZZZZZZZZZ\n",
            )
