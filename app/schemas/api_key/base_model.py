from pydantic import BaseModel, Field

from app.core.enum.llm_service_info import LLMServiceEnum


class APIKeyBase(BaseModel):
    """API Key 도메인의 모든 스키마가 상속하는 기본 모델"""

    service_name: LLMServiceEnum = Field(..., description="외부 서비스 이름")
