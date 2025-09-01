from typing import List

from inreach_proxy.models import Request, GarminConversations


class BaseResponse:
    @staticmethod
    def matches(text: str) -> bool:
        raise NotImplementedError

    def find_request_for_response(self, conversation: GarminConversations) -> List[Request]:
        raise NotImplementedError

    def get_message_type(self) -> "str":
        return "txt"

    def get_messages(self) -> List[str]:
        raise NotImplementedError

    def execute(self) -> str:
        raise NotImplementedError
