from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enum.sender import SenderEnum
from app.schemas.chat_message.base_model import ChatMessagesBase


class ChatMessagesResponse(ChatMessagesBase):
    chat_tab_id: str = Field(..., description="해당 메시지가 속한 채팅 탭의 ID")
    sender: SenderEnum = Field(..., description="메시지 발신자 ('AI' 또는 'User')")
    message: str = Field(..., description="메시지 내용")

    class Config:
        use_enum_values = True


class ALLChatMessagesResponseByTab(BaseModel):
    """채팅 탭의 메타데이터와 전체 메시지 목록을 담는 응답 스키마"""

    id: str = Field(..., description="채팅 탭의 고유 ID")
    name: str = Field(..., description="채팅 탭의 이름")
    created_at: datetime = Field(..., description="생성 시각")
    updated_at: datetime = Field(..., description="마지막 수정 시각")
    messages: list[ChatMessagesResponse] = Field(
        default_factory=list, description="해당 채팅 탭에 속한 모든 메시지 목록"
    )
