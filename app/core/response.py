from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from app.core.status import CommonCode

T = TypeVar("T")


class ResponseMessage(BaseModel, Generic[T]):
    """
    모든 API 응답에 사용될 공용 스키마입니다.
    """

    code: str = Field(..., description="응답을 나타내는 고유 상태 코드")
    message: str = Field(..., description="응답 메시지")
    data: T | None = Field(None, description="반환될 실제 데이터")

    @classmethod
    def success(cls, value: T | None = None, code: CommonCode = CommonCode.SUCCESS, *args) -> "ResponseMessage[T]":
        """
        성공 응답을 생성하는 팩토리 메서드입니다.
        """
        return cls(code=code.code, message=code.get_message(*args), data=value)
