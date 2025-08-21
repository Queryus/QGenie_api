from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enum.db_key_prefix_name import DBSaveIdEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode


def validate_chat_tab_id_format(tab_id: str) -> None:
    """채팅 탭 ID 형식 유효성 검사"""
    required_prefix = DBSaveIdEnum.chat_tab.value + "-"
    if not tab_id.startswith(required_prefix):
        raise APIException(CommonCode.INVALID_CHAT_TAB_ID_FORMAT)


class ChatMessagesBase(BaseModel):
    id: str = Field(..., description="고유 ID")
    created_at: datetime = Field(..., description="생성 시각")
    updated_at: datetime = Field(..., description="마지막 수정 시각")


class RequestBase(BaseModel):
    """요청 스키마의 기본 모델"""

    def validate_chat_tab_id(self, field_value: str) -> None:
        validate_chat_tab_id_format(field_value)

    def validate_message(self, field_value: str) -> None:
        """메시지 유효성 검사"""
        if not field_value or field_value.strip() == "":
            raise APIException(CommonCode.INVALID_CHAT_MESSAGE_REQUEST)
