from datetime import datetime

from app.schemas.chat_tab.base_model import AIChatBase


class AIChatInDB(AIChatBase):
    """데이터베이스에 저장된 형태의 스키마 (내부용)"""

    id: str
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
