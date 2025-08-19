from datetime import datetime

from pydantic import Field

from app.schemas.chat_tab.base_model import ChatTabBase


class ChatTabResponse(ChatTabBase):
    """AI 채팅 탭 정보 API 응답용 스키마"""

    id: str = Field(..., description="채팅 탭의 고유 ID (서버에서 생성)")
    name: str = Field(..., description="채팅 탭의 이름")
    created_at: datetime
    updated_at: datetime
