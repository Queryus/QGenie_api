from datetime import datetime

from pydantic import Field

from app.schemas.chat_tab.base_model import ChatTabBase
from app.schemas.chat_tab.db_model import ChatMessageInDB


class ChatTabResponse(ChatTabBase):
    """AI 채팅 탭 정보 API 응답용 스키마"""

    id: str = Field(..., description="채팅 탭의 고유 ID (서버에서 생성)")
    name: str = Field(..., description="채팅 탭의 이름")
    created_at: datetime
    updated_at: datetime


class ChatMessagesResponse(ChatTabResponse):
    """AI 채팅 탭의 메타데이터와 전체 메시지 목록을 담는 API 응답 스키마"""

    # 해당 탭의 모든 메시지를 리스트로 담습니다.
    messages: list[ChatMessageInDB] = Field(..., description="해당 채팅 탭에 속한 모든 메시지 목록")
