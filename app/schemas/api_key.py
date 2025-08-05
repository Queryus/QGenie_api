from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enum.llm_service import LLMServiceEnum


class APIKeyBase(BaseModel):
    """모든 API Key 스키마의 기본 모델"""

    service_name: LLMServiceEnum = Field(..., description="외부 서비스 이름")


class APIKeyStore(APIKeyBase):
    """API Key 저장을 위한 스키마"""

    api_key: str = Field(..., description="암호화하여 저장할 실제 API Key")


class APIKeyInDB(APIKeyBase):
    """데이터베이스에 저장된 형태의 스키마 (내부용)"""

    id: str
    api_key: str  # DB 모델에서는 암호화된 키를 의미
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class APIKeyInfo(APIKeyBase):
    """API 응답용 스키마 (민감 정보 제외)"""

    id: str
    created_at: datetime
    updated_at: datetime
