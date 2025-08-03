from fastapi import APIRouter

from app.core.response import ResponseMessage
from app.core.exceptions import APIException
from app.core.status import CommonCode

router = APIRouter()

@router.get("", response_model=ResponseMessage, summary="타입 변환을 이용한 성공/실패/버그 테스트")
def simple_test(mode: str):
    """
    curl 테스트 시 아래 명령어 사용
    curl -i -X GET "http://localhost:<port>/api/test?mode=1"
    curl -i -X GET "http://localhost:8000/api/test?mode=1"

    쿼리 파라미터 'mode' 값에 따라 다른 응답을 반환합니다.

    - **mode=1**: 성공 응답 (200 OK)
    - **mode=2**: 커스텀 성공 응답 (200 OK)
    - **mode=기타 숫자**: 예상된 실패 (404 Not Found)
    - **mode=문자열**: 예상치 못한 서버 버그 (500 Internal Server Error)
    """
    try:
        # 1. 입력받은 mode를 정수(int)로 변환 시도
        mode_int = int(mode)

        # 2. 정수로 변환 성공 시, 값에 따라 분기
        if mode_int == 1:
            # 기본 성공 코드(SUCCESS)로 응답
            return ResponseMessage.success(
                value={"detail": "기본 성공 테스트입니다."}
            )
        elif mode_int == 2:
            # 커스텀 성공 코드(CREATED)로 응답
            return ResponseMessage.success(
                value={"detail": "커스텀 성공 코드(CREATED) 테스트입니다."},
                code=CommonCode.CREATED
            )
        else:
            # 그 외 숫자는 '데이터 없음' 오류로 처리
            raise APIException(CommonCode.NO_SEARCH_DATA)

    except ValueError:
        # 3. 정수로 변환 실패 시 (문자열이 들어온 경우)
        # 예상치 못한 버그를 강제로 발생시킵니다.
        # 이 에러는 generic_exception_handler가 처리하게 됩니다.
        raise TypeError("의도적으로 발생시킨 타입 에러입니다.")

