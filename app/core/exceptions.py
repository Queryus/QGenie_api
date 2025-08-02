import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.status import CommonCode


class APIException(Exception):
    """
    API 로직 내에서 발생하는 모든 예상된 오류에 사용할 기본 예외 클래스입니다.
    """
    def __init__(self, code: CommonCode, *args):
        self.code_enum = code
        self.message = code.get_message(*args)
        super().__init__(self.message)

async def api_exception_handler(request: Request, exc: APIException):
    """
    APIException이 발생했을 때, 이를 감지하여 표준화된 JSON 오류 응답을 반환합니다.
    """
    return JSONResponse(
        status_code=exc.code_enum.http_status,
        content={
            "code": exc.code_enum.code,
            "message": exc.message,
            "data": None
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """
    처리되지 않은 모든 예외를 잡아, 일관된 500 서버 오류를 반환합니다.
    """
    # 운영 환경에서는 파일 로그나 모니터링 시스템으로 보내야 합니다.
    print("="*20, "UNEXPECTED ERROR", "="*20)
    traceback.print_exc()
    print("="*50)

    # 사용자에게는 간단한 500 에러 메시지만 보여줍니다.
    error_response = {
        "code": CommonCode.FAIL.code,
        "message": CommonCode.FAIL.message,
        "data": None
    }

    return JSONResponse(
        status_code=CommonCode.FAIL.http_status,
        content=error_response,
    )