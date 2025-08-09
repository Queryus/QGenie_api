from datetime import datetime

from pydantic import Field

from app.schemas.chat_tab.base_model import AIChatBase


class AIChatResponse(AIChatBase):
    """AI 채팅 탭 정보 API 응답용 스키마"""

    id: str = Field(..., description="채팅 세션의 고유 ID (서버에서 생성)")
    name: str = Field(..., description="채팅 세션의 이름")
    created_at: datetime
    updated_at: datetime
