from enum import Enum

from fastapi import status


class CommonCode(Enum):
    """
    애플리케이션의 모든 상태 코드를 중앙에서 관리합니다.
    각 멤버는 (HTTP 상태 코드, 고유 비즈니스 코드, 기본 메시지) 튜플을 값으로 가집니다.
    상태 코드 참고: https://developer.mozilla.org/ko/docs/Web/HTTP/Status
    """

    # =======================================
    #    성공 (Success) - 2xxx
    # =======================================
    """ 기본 성공 코드 - 20xx """
    SUCCESS = (status.HTTP_200_OK, "2000", "성공적으로 처리되었습니다.")
    CREATED = (status.HTTP_201_CREATED, "2001", "성공적으로 생성되었습니다.")

    """ DRIVER, DB 성공 코드 - 21xx """
    SUCCESS_DRIVER_INFO = (status.HTTP_200_OK, "2100", "드라이버 정보 조회를 성공하였습니다.")
    SUCCESS_USER_DB_CONNECT_TEST = (status.HTTP_200_OK, "2101", "테스트 연결을 성공하였습니다.")
    SUCCESS_FIND_PROFILE = (status.HTTP_200_OK, "2102", "디비 정보 조회를 성공하였습니다.")
    SUCCESS_FIND_SCHEMAS = (status.HTTP_200_OK, "2103", "디비 스키마 정보 조회를 성공하였습니다.")
    SUCCESS_FIND_TABLES = (status.HTTP_200_OK, "2104", "디비 테이블 정보 조회를 성공하였습니다.")
    SUCCESS_FIND_COLUMNS = (status.HTTP_200_OK, "2105", "디비 컬럼 정보 조회를 성공하였습니다.")
    SUCCESS_SAVE_PROFILE = (status.HTTP_200_OK, "2130", "디비 연결 정보를 저장하였습니다.")
    SUCCESS_UPDATE_PROFILE = (status.HTTP_200_OK, "2150", "디비 연결 정보를 업데이트 하였습니다.")
    SUCCESS_DELETE_PROFILE = (status.HTTP_200_OK, "2170", "디비 연결 정보를 삭제 하였습니다.")

    """ KEY 성공 코드 - 22xx """
    SUCCESS_DELETE_API_KEY = (status.HTTP_204_NO_CONTENT, "2200", "API KEY가 성공적으로 삭제되었습니다.")
    SUCCESS_UPDATE_API_KEY = (status.HTTP_200_OK, "2201", "API KEY가 성공적으로 수정되었습니다.")
    SUCCESS_GET_API_KEY = (status.HTTP_200_OK, "2202", "API KEY 정보를 성공적으로 조회했습니다.")

    """ AI CHAT, DB 성공 코드 - 23xx """
    SUCCESS_CHAT_TAB_CREATE = (status.HTTP_200_OK, "2300", "새로운 채팅 탭이 성공적으로 생성하였습니다.")
    SUCCESS_CHAT_TAB_UPDATE = (status.HTTP_200_OK, "2301", "채팅 탭 이름이 성공적으로 수정되었습니다.")
    SUCCESS_CHAT_TAB_DELETE = (status.HTTP_200_OK, "2302", "채팅 탭을 성공적으로 삭제되었습니다.")
    SUCCESS_GET_CHAT_TAB = (status.HTTP_200_OK, "2303", "모든 채팅 탭을 성공적으로 조회하였습니다.")
    SUCCESS_GET_CHAT_MESSAGES = (status.HTTP_200_OK, "2304", "채팅 탭의 모든 메시지를 성공적으로 불러왔습니다.")

    """ ANNOTATION 성공 코드 - 24xx """
    SUCCESS_CREATE_ANNOTATION = (status.HTTP_201_CREATED, "2400", "어노테이션을 성공적으로 생성하였습니다.")
    SUCCESS_FIND_ANNOTATION = (status.HTTP_200_OK, "2401", "어노테이션 정보를 성공적으로 조회하였습니다.")
    SUCCESS_DELETE_ANNOTATION = (status.HTTP_200_OK, "2402", "어노테이션을 성공적으로 삭제하였습니다.")

    """ SQL 성공 코드 - 25xx """
    SUCCESS_EXECUTION = (status.HTTP_201_CREATED, "2400", "쿼리를 성공적으로 수행하였습니다.")
    SUCCESS_FIND_QUERY_HISTORY = (status.HTTP_200_OK, "2102", "쿼리 이력 조회를 성공하였습니다.")
    SUCCESS_EXECUTION_TEST = (status.HTTP_201_CREATED, "2400", "쿼리 TEST를 성공적으로 수행하였습니다.")

    # =======================================
    #    클라이언트 에러 (Client Error) - 4xxx
    # =======================================
    """ 기본 클라이언트 에러 코드 - 40xx """
    NO_VALUE = (status.HTTP_400_BAD_REQUEST, "4000", "필수 값이 존재하지 않습니다.")
    DUPLICATION = (status.HTTP_409_CONFLICT, "4001", "이미 존재하는 데이터입니다.")
    NO_SEARCH_DATA = (status.HTTP_404_NOT_FOUND, "4002", "요청한 데이터를 찾을 수 없습니다.")
    INVALID_PARAMETER = (status.HTTP_422_UNPROCESSABLE_ENTITY, "4003", "필수 값이 누락되었습니다.")

    """ DRIVER, DB 클라이언트 에러 코드 - 41xx """
    INVALID_DB_DRIVER = (status.HTTP_409_CONFLICT, "4100", "지원하지 않는 데이터베이스입니다.")
    NO_DB_DRIVER = (status.HTTP_400_BAD_REQUEST, "4101", "데이터베이스는 필수 값입니다.")
    NO_DB_PROFILE_FOUND = (status.HTTP_404_NOT_FOUND, "4102", "해당 ID의 DB 프로필을 찾을 수 없습니다.")

    """ KEY 클라이언트 에러 코드 - 42xx """
    INVALID_API_KEY_FORMAT = (status.HTTP_400_BAD_REQUEST, "4200", "API 키의 형식이 올바르지 않습니다.")
    INVALID_API_KEY_PREFIX = (
        status.HTTP_400_BAD_REQUEST,
        "4201",
        "API 키가 선택한 서비스의 올바른 형식이 아닙니다. (예: OpenAI는 sk-로 시작)",
    )

    """ AI CHAT TAB 클라이언트 오류 코드 - 43xx """
    INVALID_CHAT_TAB_NAME_FORMAT = (status.HTTP_400_BAD_REQUEST, "4300", "채팅 탭 이름의 형식이 올바르지 않습니다.")
    INVALID_CHAT_TAB_NAME_LENGTH = (
        status.HTTP_400_BAD_REQUEST,
        "4301",
        "채팅 탭 이름의 길이는 128자를 초과할 수 없습니다.",
    )
    INVALID_CHAT_TAB_NAME_CONTENT = (
        status.HTTP_400_BAD_REQUEST,
        "4302",
        "채팅 탭 이름에 SQL 예약어나 허용되지 않는 특수문자가 포함되어 있습니다. "
        "허용되지 않는 특수 문자: 큰따옴표(\"), 작은따옴표('), 세미콜론(;), 꺾쇠괄호(<, >)",
    )
    INVALID_CHAT_TAB_ID_FORMAT = (status.HTTP_400_BAD_REQUEST, "4303", "채팅 탭 ID의 형식이 올바르지 않습니다.")
    NO_CHAT_TAB_DATA = (status.HTTP_404_NOT_FOUND, "4304", "해당 ID를 가진 채팅 탭을 찾을 수 없습니다.")

    """ ANNOTATION 클라이언트 에러 코드 - 44xx """
    INVALID_ANNOTATION_REQUEST = (status.HTTP_400_BAD_REQUEST, "4400", "어노테이션 요청 데이터가 유효하지 않습니다.")
    NO_ANNOTATION_FOR_PROFILE = (status.HTTP_404_NOT_FOUND, "4401", "해당 DB 프로필에 연결된 어노테이션이 없습니다.")

    """ SQL 클라이언트 에러 코드 - 45xx """
    NO_CHAT_KEY = (status.HTTP_400_BAD_REQUEST, "4501", "CHAT 키는 필수 값입니다.")
    NO_QUERY = (status.HTTP_400_BAD_REQUEST, "4500", "쿼리는 필수 값입니다.")

    # ==================================
    #    서버 에러 (Server Error) - 5xx
    # ==================================
    """ 기본 서버 에러 코드 - 50xx """
    FAIL = (status.HTTP_500_INTERNAL_SERVER_ERROR, "5000", "서버 처리 중 에러가 발생했습니다.")
    DB_BUSY = (
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "5001",
        "데이터베이스가 현재 사용 중입니다. 잠시 후 다시 시도해주세요.",
    )
    FAIL_TO_VERIFY_CREATION = (
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "5002",
        "데이터 생성 후 검증 과정에서 에러가 발생했습니다.",
    )

    """ DRIVER, DB 서버 에러 코드 - 51xx """
    FAIL_CONNECT_DB = (status.HTTP_500_INTERNAL_SERVER_ERROR, "5100", "디비 연결 중 에러가 발생했습니다.")
    FAIL_FIND_PROFILE = (status.HTTP_500_INTERNAL_SERVER_ERROR, "5101", "디비 정보 조회 중 에러가 발생했습니다.")
    FAIL_FIND_SCHEMAS = (status.HTTP_500_INTERNAL_SERVER_ERROR, "5102", "디비 스키마 정보 조회 중 에러가 발생했습니다.")
    FAIL_FIND_TABLES = (status.HTTP_500_INTERNAL_SERVER_ERROR, "5103", "디비 테이블 정보 조회 중 에러가 발생했습니다.")
    FAIL_FIND_COLUMNS = (status.HTTP_500_INTERNAL_SERVER_ERROR, "5104", "디비 컬럼 정보 조회 중 에러가 발생했습니다.")
    FAIL_FIND_CONSTRAINTS_OR_INDEXES = (
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "5105",
        "디비 제약조건 또는 인덱스 정보 조회 중 에러가 발생했습니다.",
    )
    FAIL_FIND_SAMPLE_ROWS = (status.HTTP_500_INTERNAL_SERVER_ERROR, "5106", "샘플 데이터 조회 중 에러가 발생했습니다.")
    FAIL_SAVE_PROFILE = (status.HTTP_500_INTERNAL_SERVER_ERROR, "5130", "디비 정보 저장 중 에러가 발생했습니다.")
    FAIL_UPDATE_PROFILE = (status.HTTP_500_INTERNAL_SERVER_ERROR, "5150", "디비 정보 업데이트 중 에러가 발생했습니다.")
    FAIL_DELETE_PROFILE = (status.HTTP_500_INTERNAL_SERVER_ERROR, "5170", "디비 정보 삭제 중 에러가 발생했습니다.")

    """ KEY 서버 에러 코드 - 52xx """

    """ AI CHAT, DB 서버 에러 코드 - 53xx """

    """ ANNOTATION 서버 에러 코드 - 54xx """
    FAIL_CREATE_ANNOTATION = (status.HTTP_500_INTERNAL_SERVER_ERROR, "5400", "어노테이션 생성 중 에러가 발생했습니다.")
    FAIL_FIND_ANNOTATION = (status.HTTP_500_INTERNAL_SERVER_ERROR, "5401", "어노테이션 조회 중 에러가 발생했습니다.")
    FAIL_DELETE_ANNOTATION = (status.HTTP_500_INTERNAL_SERVER_ERROR, "5402", "어노테이션 삭제 중 에러가 발생했습니다.")
    FAIL_AI_SERVER_CONNECTION = (status.HTTP_503_SERVICE_UNAVAILABLE, "5403", "AI 서버 연결에 실패했습니다.")
    FAIL_AI_SERVER_PROCESSING = (
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "5404",
        "AI 서버가 요청을 처리하는 데 실패했습니다.",
    )

    """ SQL 서버 에러 코드 - 55xx """
    FAIL_CREATE_QUERY = (status.HTTP_500_INTERNAL_SERVER_ERROR, "5170", "쿼리 실행 정보 저장 중 에러가 발생했습니다.")

    def __init__(self, http_status: int, code: str, message: str):
        """Enum 멤버가 생성될 때 각 값을 속성으로 할당합니다."""
        self.http_status = http_status
        self.code = code
        self.message = message

    def get_message(self, *args) -> str:
        """
        메시지 포맷팅이 필요한 경우, 인자를 받아 완성된 메시지를 반환합니다.
        """
        try:
            return self.message % args if args else self.message
        except Exception:
            return self.message
