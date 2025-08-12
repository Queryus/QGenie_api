import re

from app.core.enum.db_key_prefix_name import DBSaveIdEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode


# Util 폴더안 or base_model.py 안으로 이동 리팩토링 진행 예정
def validate_chat_tab_name(name: str | None) -> None:
    """채팅 탭 이름에 대한 유효성 검증 로직을 수행합니다."""
    # 1. 문자열이 None, 문자열 전체가 공백 문자인지 확인
    if not name or name.isspace():
        raise APIException(CommonCode.INVALID_CHAT_TAB_NAME_FORMAT)

    # 2. 길이 제한
    if len(name) > 128:
        raise APIException(CommonCode.INVALID_CHAT_TAB_NAME_LENGTH)

    # 3. 특수문자 및 SQL 예약어 확인
    # SQL 예약어와 위험한 특수문자를 검사합니다.
    sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "OR", "AND"]
    for keyword in sql_keywords:
        if keyword in name.upper():
            raise APIException(CommonCode.INVALID_CHAT_TAB_NAME_CONTENT)

    # 특정 특수문자를 검사하는 예시
    if re.search(r"[;\"'`<>]", name):
        raise APIException(CommonCode.INVALID_CHAT_TAB_NAME_CONTENT)


def validate_chat_tab_id(id: str | None) -> None:
    """채팅 탭 ID에 대한 유효성 검증 로직을 수행합니다."""

    # 1. 'CHAT-TAB-' 접두사 검증
    required_prefix = DBSaveIdEnum.chat_tab.value + "-"
    if not id.startswith(required_prefix):
        raise APIException(CommonCode.INVALID_CHAT_TAB_ID_FORMAT)
