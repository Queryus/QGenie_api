from datetime import datetime

from pydantic import BaseModel, Field

from app.core.enum.db_key_prefix_name import DBSaveIdEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode


class ChatMessagesBase(BaseModel):
    id: str = Field(..., description="고유 ID")
    created_at: datetime = Field(..., description="생성 시각")
    updated_at: datetime = Field(..., description="마지막 수정 시각")


class RequestBase(BaseModel):
    """요청 스키마의 기본 모델"""

    def validate_chat_tab_id(self) -> None:
        """채팅 탭 ID에 대한 유효성 검증 로직을 수행합니다."""

        required_prefix = DBSaveIdEnum.chat_tab.value + "-"
        if not self.chat_tab_id.startswith(required_prefix):
            raise APIException(CommonCode.INVALID_CHAT_TAB_ID_FORMAT)
