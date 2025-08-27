import dataclasses
from typing import Optional, Dict, Any

from inreach_proxy.models import GarminConversations


@dataclasses.dataclass
class BaseAction:
    _database_id: Optional[int] = None

    @staticmethod
    def matches(text: str) -> bool:
        raise NotImplementedError

    @staticmethod
    def from_text(text: str, settings: Optional[Dict[Any, Any]] = None) -> Optional["BaseAction"]:
        raise NotImplementedError

    @classmethod
    def from_inputs(cls, database_id: Optional[int], inputs: Dict[str, Any]) -> Optional["BaseAction"]:
        return cls(**inputs | {"_database_id": database_id})

    def get_data(self) -> Dict[Any, Any]:
        return self.__dict__

    def get_type(self) -> int:
        return 0

    def execute(self) -> str:
        raise NotImplementedError

    def execute_with_email(self, conversation: GarminConversations) -> str:
        raise NotImplementedError
