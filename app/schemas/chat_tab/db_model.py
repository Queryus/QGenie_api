from datetime import datetime

from pydantic import Field

from app.schemas.chat_tab.base_model import ChatTabBase


class ChatTabInDB(ChatTabBase):
    """데이터베이스에 저장된 형태의 스키마 (내부용)"""

    id: str
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatMessageInDB(ChatTabBase):
    """데이터베이스에 저장된 형태의 메시지 스키마 (내부용)"""

    id: str = Field(..., description="메시지의 고유 ID (서버에서 생성)")
    chat_tab_id: str = Field(..., description="해당 메시지가 속한 채팅 탭의 ID")
    sender: str = Field(..., description="메시지 발신자 ('AI' 또는 'User')")
    message: str = Field(..., description="메시지 내용")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
