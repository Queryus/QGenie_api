
from app.schemas.chat_tab.base_model import AIChatBase
from app.schemas.chat_tab.validation_utils import validate_chat_name


class AIChatCreate(AIChatBase):
    """새로운 Chat Tab 생성을 위한 스키마"""

    def validate_with_name(self) -> None:
        validate_chat_name(self.name)
