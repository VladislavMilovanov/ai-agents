from dataclasses import dataclass
from typing import Literal


@dataclass
class ChatMessage:
    role: Literal["user", "assistant"]
    content: str

    def to_api_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}
