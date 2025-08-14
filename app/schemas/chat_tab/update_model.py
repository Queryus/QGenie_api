from pydantic import Field

from app.schemas.chat_tab.base_model import ChatTabBase


class ChatTabUpdate(ChatTabBase):
    """채팅 탭 이름 수정을 위한 스키마"""

    name: str = Field(None, description="수정할 채팅 탭 이름")
