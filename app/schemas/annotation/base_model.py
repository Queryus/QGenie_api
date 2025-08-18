from datetime import datetime

from pydantic import BaseModel, Field

from app.core.exceptions import APIException
from app.core.status import CommonCode


class AnnotationBase(BaseModel):
    """어노테이션 스키마의 기본 모델"""

    id: str = Field(..., description="고유 ID")
    created_at: datetime = Field(..., description="생성 시각")
    updated_at: datetime = Field(..., description="마지막 수정 시각")


class RequestBase(BaseModel):
    """요청 스키마의 기본 모델"""

    def validate_required_fields(self, fields: list[str]):
        """필수 필드가 비어있는지 검사하는 공통 유효성 검사 메서드"""
        for field_name in fields:
            value = getattr(self, field_name, None)
            if not value or (isinstance(value, str) and not value.strip()):
                raise APIException(CommonCode.INVALID_PARAMETER, detail=f"'{field_name}' 필드는 비워둘 수 없습니다.")
