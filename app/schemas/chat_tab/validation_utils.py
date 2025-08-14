from app.core.enum.db_key_prefix_name import DBSaveIdEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode


# 리팩토링 예정
def validate_chat_tab_id(id: str | None) -> None:
    """채팅 탭 ID에 대한 유효성 검증 로직을 수행합니다."""

    # 1. 'CHAT-TAB-' 접두사 검증
    required_prefix = DBSaveIdEnum.chat_tab.value + "-"
    if not id.startswith(required_prefix):
        raise APIException(CommonCode.INVALID_CHAT_TAB_ID_FORMAT)
