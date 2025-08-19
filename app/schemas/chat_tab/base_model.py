import re

from pydantic import BaseModel, Field

from app.core.exceptions import APIException
from app.core.status import CommonCode


class ChatTabBase(BaseModel):
    """
    모든 AI Chat Tab 스키마의 기본 모델
    -  새로운 Chat Tab 생성을 위한 스키마
    -  채팅 탭 이름 수정을 위한 스키마
    """

    name: str | None = Field(..., description="새로운 채팅 탭 이름")

    def validate_chat_tab_name(self) -> None:
        """채팅 탭 이름에 대한 유효성 검증 로직을 수행합니다."""
        # 1. 문자열이 None, 문자열 전체가 공백 문자인지 확인
        if not self.name or self.name.isspace():
            raise APIException(CommonCode.INVALID_CHAT_TAB_NAME_FORMAT)

        # 2. 길이 제한
        if len(self.name) > 128:
            raise APIException(CommonCode.INVALID_CHAT_TAB_NAME_LENGTH)

        # 3. 특수문자 및 SQL 예약어 확인
        # SQL 예약어와 위험한 특수문자를 검사합니다.
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "OR", "AND"]
        for keyword in sql_keywords:
            if keyword in self.name.upper():
                raise APIException(CommonCode.INVALID_CHAT_TAB_NAME_CONTENT)

        # 특정 특수문자를 검사하는 예시
        if re.search(r"[;\"'`<>]", self.name):
            raise APIException(CommonCode.INVALID_CHAT_TAB_NAME_CONTENT)
