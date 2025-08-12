from pydantic import BaseModel, Field


class ChatTabBase(BaseModel):
    """모든 AI Chat Tab 스키마의 기본 모델"""

    name: str = Field(..., description="새로운 채팅 탭 이름")
