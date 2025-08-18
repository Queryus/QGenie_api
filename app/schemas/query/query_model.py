# app/schemas/query/query_model.py

from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.core.enum.db_key_prefix_name import DBSaveIdEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.core.utils import generate_prefixed_uuid


def _is_empty(value: Any | None) -> bool:
    """값이 None, 빈 문자열, 공백 문자열인지 검사"""
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


class QueryInfo(BaseModel):
    user_db_id: str = Field(..., description="DB Key")
    database: str | None = Field(None, description="database 명")
    query_text: str | None = Field(None, description="쿼리 내용")

    @model_validator(mode="after")
    def validate_required_fields(self) -> "QueryInfo":
        """QueryInfo 모델에 대한 필수 필드 유효성 검사"""
        if _is_empty(self.user_db_id):
            raise APIException(CommonCode.NO_DB_DRIVER)

        if _is_empty(self.query_text):
            raise APIException(CommonCode.NO_QUERY)

        return self


class RequestExecutionQuery(QueryInfo):
    chat_message_id: str | None = Field(None, description="연결된 메시지 Key")

    @model_validator(mode="after")
    def validate_chat_message_id(self) -> "RequestExecutionQuery":
        """RequestExecutionQuery 모델에만 필요한 추가 필드 유효성 검사"""
        if _is_empty(self.chat_message_id):
            raise APIException(CommonCode.NO_CHAT_KEY)

        return self


class ExecutionQuery(RequestExecutionQuery):
    id: str | None = Field(None, description="Query Key 값")
    type: str | None = Field(None, description="디비 타입")
    is_success: str | None = Field(None, description="성공 여부")
    error_message: str | None = Field(None, description="에러 메시지")

    @classmethod
    def from_query_info(
        cls, query_info: RequestExecutionQuery, type: str, is_success: bool, error_message: str | None = None
    ):
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
