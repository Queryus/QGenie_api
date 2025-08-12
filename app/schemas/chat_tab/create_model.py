from app.schemas.chat_tab.base_model import ChatTabBase
from app.schemas.chat_tab.validation_utils import validate_chat_tab_name


class ChatTabCreate(ChatTabBase):
    """새로운 Chat Tab 생성을 위한 스키마"""

    def validate_with_name(self) -> None:
        validate_chat_tab_name(self.name)
