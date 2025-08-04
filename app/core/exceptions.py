import traceback
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.status import CommonCode


def _create_error_response(code: CommonCode, data: Any | None = None, *message_args) -> JSONResponse:
    """
    모든 에러 응답에 사용될 표준 JSONResponse 객체를 생성하는 헬퍼 함수.
    """
    error_content = {
        "code": code.code,
        "message": code.get_message(*message_args),
        "data": data,
    }
    return JSONResponse(
        status_code=code.http_status,
        content=error_content,
    )


class APIException(Exception):
    """
    API 로직 내에서 발생하는 모든 예상된 오류에 사용할 기본 예외 클래스입니다.
    """

    def __init__(self, code: CommonCode, *args):
        self.code_enum = code
        self.message = code.get_message(*args)
        super().__init__(self.message)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Pydantic 모델의 유효성 검사 실패(RequestValidationError)를 감지하여
    표준화된 JSON 오류 응답을 반환합니다.
    """
    error_details = []
    for error in exc.errors():
        field_name = ".".join(map(str, error["loc"][1:]))
        error_details.append({"field": field_name, "message": error["msg"]})

    return _create_error_response(code=CommonCode.INVALID_PARAMETER, data={"details": error_details})


async def api_exception_handler(request: Request, exc: APIException):
    """
    APIException이 발생했을 때, 이를 감지하여 표준화된 JSON 오류 응답을 반환합니다.
    """
    return _create_error_response(
        code=exc.code_enum.http_status, data={"code": exc.code_enum.code, "message": exc.message, "data": None}
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    처리되지 않은 모든 예외를 잡아, 일관된 500 서버 오류를 반환합니다.
    """
    error_traceback = traceback.format_exc()

    print("=" * 20, "UNEXPECTED ERROR", "=" * 20)
    print(error_traceback)
    print("=" * 50)

    return _create_error_response(code=CommonCode.FAIL, data={"traceback": error_traceback})
