from enum import Enum

from fastapi import status


class CommonCode(Enum):
    """
    애플리케이션의 모든 상태 코드를 중앙에서 관리합니다.
    각 멤버는 (HTTP 상태 코드, 고유 비즈니스 코드, 기본 메시지) 튜플을 값으로 가집니다.
    상태 코드 참고: https://developer.mozilla.org/ko/docs/Web/HTTP/Status
    """

    # ==================================
    #    성공 (Success) - 2xx
    # ==================================
    SUCCESS = (status.HTTP_200_OK, "2000", "성공적으로 처리되었습니다.")
    CREATED = (status.HTTP_201_CREATED, "2001", "성공적으로 생성되었습니다.")
    SUCCESS_DB_CONNECT = (status.HTTP_200_OK, "2002", "디비 연결을 성공하였습니다.")

    # ==================================
    #    클라이언트 오류 (Client Error) - 4xx
    # ==================================
    NO_VALUE = (status.HTTP_400_BAD_REQUEST, "4000", "필수 값이 존재하지 않습니다.")
    DUPLICATION = (status.HTTP_409_CONFLICT, "4001", "이미 존재하는 데이터입니다.")
    NO_SEARCH_DATA = (status.HTTP_404_NOT_FOUND, "4002", "요청한 데이터를 찾을 수 없습니다.")
    INVALID_PARAMETER = (status.HTTP_422_UNPROCESSABLE_ENTITY, "4003", "필수 값이 누락되었습니다.")
    INVALID_ENUM_VALUE = (status.HTTP_422_UNPROCESSABLE_ENTITY, "4101", "지원하지 않는 데이터베이스 값입니다.")

    # ==================================
    #    서버 오류 (Server Error) - 5xx
    # ==================================
    FAIL = (status.HTTP_500_INTERNAL_SERVER_ERROR, "9999", "서버 처리 중 오류가 발생했습니다.")

    def __init__(self, http_status: int, code: str, message: str):
        """Enum 멤버가 생성될 때 각 값을 속성으로 할당합니다."""
        self.http_status = http_status
        self.code = code
        self.message = message

    def get_message(self, *args) -> str:
        """
        메시지 포맷팅이 필요한 경우, 인자를 받아 완성된 메시지를 반환합니다.
        """
        return self.message % args if args else self.message
