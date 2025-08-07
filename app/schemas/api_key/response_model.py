from datetime import datetime

from app.schemas.api_key.base_model import APIKeyBase


class APIKeyResponse(APIKeyBase):
    """API 응답용 스키마"""

    id: str
    created_at: datetime
    updated_at: datetime
