from enum import Enum


class SenderEnum(str, Enum):
    """채팅 메시지 발신자 구분"""

    user = "U"
    ai = "A"
