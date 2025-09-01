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
    def from_inputs(cls, database_id: Optional[int], inputs: Dict[str, Any]) -> Optional["BaseAction"]:
        return cls(**(inputs | ({"_database_id": database_id} if hasattr(cls, "_database_id") else {})))

    def get_data(self) -> Dict[Any, Any]:
        data = dict(self.__dict__)
        if "_database_id" in data:
            del data["_database_id"]
        return data

    def get_type(self) -> int:
        return 0

    def execute(self) -> str:
        raise NotImplementedError

    def execute_with_email(self, conversation: GarminConversations) -> str:
        raise NotImplementedError
