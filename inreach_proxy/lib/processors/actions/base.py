import dataclasses
from typing import Optional, Dict, Any

from inreach_proxy.models import GarminConversations


@dataclasses.dataclass
class BaseAction:
    @staticmethod
    def matches(text: str) -> bool:
        raise NotImplementedError

    @staticmethod
    def from_text(text: str, settings: Optional[Dict[Any, Any]] = None) -> Optional["BaseAction"]:
        raise NotImplementedError

    @classmethod
    def from_inputs(cls, inputs: Dict[str, Any]) -> Optional["BaseAction"]:
        return cls(**inputs)

    def get_data(self) -> Dict[Any, Any]:
        return self.__dict__

    def get_type(self) -> int:
        return 0

    def execute(self) -> str:
        raise NotImplementedError

    def execute_with_email(self, conversation: GarminConversations) -> str:
        raise NotImplementedError
