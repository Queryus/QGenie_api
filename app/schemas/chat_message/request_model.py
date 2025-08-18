from pydantic import Field

from app.schemas.chat_message.base_model import RequestBase


class ChatMessagesReqeust(RequestBase):
    """채팅 메시지 생성 요청 스키마"""

    chat_tab_id: str = Field(..., description="채팅 탭의 고유 ID")
    message: str = Field(..., description="메시지 내용")

    def validate(self):
        self.validate_chat_tab_id()
