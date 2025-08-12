from pydantic import Field

from app.schemas.chat_tab.base_model import ChatTabBase
from app.schemas.chat_tab.validation_utils import validate_chat_tab_name


class ChatTabUpdate(ChatTabBase):
    """채팅 탭 이름 수정을 위한 스키마"""
    name: str | None = Field(None, description="수정할 채팅 탭 이름")

    def validate_with_name(self) -> None:
        validate_chat_tab_name(self.name)
