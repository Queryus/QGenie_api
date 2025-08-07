# app/schemas/api_key/response_model.py
from datetime import datetime

from pydantic import Field

from app.schemas.api_key.base_model import APIKeyBase


class APIKeyResponse(APIKeyBase):
    """API 응답용 스키마"""

    id: str
    api_key_encrypted: str = Field(..., description="암호화된 API Key")
    created_at: datetime
    updated_at: datetime
