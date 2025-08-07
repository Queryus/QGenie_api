from datetime import datetime

from app.schemas.api_key.base_model import APIKeyBase


class APIKeyInDB(APIKeyBase):
    """데이터베이스에 저장된 형태의 스키마 (내부용)"""

    id: str
    api_key: str  # DB 모델에서는 암호화된 키를 의미
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
