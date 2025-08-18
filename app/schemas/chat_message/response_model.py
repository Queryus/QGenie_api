from pydantic import Field

from app.core.enum.sender import SenderEnum
from app.schemas.chat_message.base_model import ChatMessagesBase


class ChatMessagesResponse(ChatMessagesBase):
    chat_tab_id: str = Field(..., description="해당 메시지가 속한 채팅 탭의 ID")
    sender: SenderEnum = Field(..., description="메시지 발신자 ('AI' 또는 'User')")
    message: str = Field(..., description="메시지 내용")

    class Config:
        use_enum_values = True
