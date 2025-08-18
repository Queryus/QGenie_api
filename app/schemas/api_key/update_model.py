from pydantic import BaseModel, Field

from app.core.exceptions import APIException
from app.core.status import CommonCode


class APIKeyUpdate(BaseModel):
    """API Key 수정을 위한 스키마"""

    api_key: str = Field(..., description="새로운 API Key")

    def validate_with_api_key(self) -> None:
        """API Key의 유효성을 검증합니다."""
        # 기본 형식 검증 (공백 또는 빈 문자열)
        if not self.api_key or self.api_key.isspace():
            raise APIException(CommonCode.INVALID_API_KEY_FORMAT)
