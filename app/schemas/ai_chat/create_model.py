import re

from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.schemas.ai_chat.base_model import AIChatBase


class AIChatCreate(AIChatBase):
    """새로운 Chat Tab 생성을 위한 스키마"""

    def validate_with_name(self) -> None:
        """채팅 탭 이름에 대한 유효성 검증 로직을 수행합니다."""
        # 1. 문자열 전체가 공백 문자인지 확인
        if not self.name or self.name.isspace():
            raise APIException(CommonCode.INVALID_CHAT_NAME_FORMAT)

        # 2. 길이 제한
        if len(self.name) > 255:
            raise APIException(CommonCode.INVALID_CHAT_NAME_LENGTH)

        # 3. 특수문자 및 SQL 예약어 확인
        # SQL 예약어와 위험한 특수문자를 검사합니다.
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "OR", "AND"]
        for keyword in sql_keywords:
            if keyword in self.name.upper():
                raise APIException(CommonCode.INVALID_CHAT_NAME_CONTENT)

        # 특정 특수문자를 검사하는 예시
        if re.search(r"[;\"'`<>]", self.name):
            raise APIException(CommonCode.INVALID_CHAT_NAME_CONTENT)
