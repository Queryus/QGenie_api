# app/schemas/query/query_model.py

from typing import Any

from pydantic import BaseModel, Field

from app.core.enum.db_key_prefix_name import DBSaveIdEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.core.utils import generate_prefixed_uuid


# 사용자가 직접 입력해야 하는 정보만 포함합니다.
class QueryInfo(BaseModel):
    user_db_id: str = Field(..., description="DB Key")
    chat_message_id: str | None = Field(None, description="연결된 메시지 Key")
    database: str | None = Field(None, description="database 명")
    query_text: str | None = Field(None, description="쿼리 내용")

    def validate_required_fields(self) -> None:
        """DB 종류별 필수 필드 유효성 검사"""
        if self._is_empty(self.user_db_id):
            raise APIException(CommonCode.NO_DB_DRIVER)

        if self._is_empty(self.chat_message_id):
            raise APIException(CommonCode.NO_CHAT_KEY)

        if self._is_empty(self.query_text):
            raise APIException(CommonCode.NO_QUERY)

    @staticmethod
    def _is_empty(value: Any | None) -> bool:
        """값이 None, 빈 문자열, 공백 문자열인지 검사"""
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        return False


class ExecutionQuery(QueryInfo):
    id: str | None = Field(None, description="Query Key 값")
    type: str | None = Field(None, description="디비 타입")
    is_success: str | None = Field(None, description="성공 여부")
    error_message: str | None = Field(None, description="에러 메시지")

    @classmethod
    def from_query_info(cls, query_info: QueryInfo, type: str, is_success: bool, error_message: str | None = None):
        return cls(
            id=generate_prefixed_uuid(DBSaveIdEnum.query.value),
            user_db_id=query_info.user_db_id,
            chat_message_id=query_info.chat_message_id,
            database=query_info.database,
            query_text=query_info.query_text,
            type=type,
            is_success="Y" if is_success else "N",
            error_message=error_message,
        )
