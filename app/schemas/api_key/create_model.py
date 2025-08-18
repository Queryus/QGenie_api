from pydantic import Field

from app.core.enum.llm_service_info import LLMServiceEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.schemas.api_key.base_model import APIKeyBase


class APIKeyCreate(APIKeyBase):
    """API Key 생성을 위한 스키마"""

    api_key: str = Field(..., description="암호화하여 저장할 실제 API Key")

    def validate_with_service(self) -> None:
        """서비스 종류에 따라 API Key의 유효성을 검증합니다."""
        # 1. 기본 형식 검증 (공백 또는 빈 문자열)
        if not self.api_key or self.api_key.isspace():
            raise APIException(CommonCode.INVALID_API_KEY_FORMAT)

        # 2. 서비스별 접두사 검증
        key_prefix_map = {
            LLMServiceEnum.OPENAI: "sk-",
        }
        required_prefix = key_prefix_map.get(self.service_name)

        if required_prefix and not self.api_key.startswith(required_prefix):
            raise APIException(CommonCode.INVALID_API_KEY_PREFIX)
