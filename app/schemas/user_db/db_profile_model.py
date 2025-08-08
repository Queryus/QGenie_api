# app/schemas/user_db/db_profile_model.py

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.core.exceptions import APIException
from app.core.status import CommonCode


# 사용자가 직접 입력해야 하는 정보만 포함합니다.
class DBProfileInfo(BaseModel):
    type: str = Field(..., description="DB 종류")
    host: str | None = Field(None, description="호스트 주소")
    port: int | None = Field(None, description="포트 번호")
    name: str | None = Field(None, description="연결할 데이터베이스명")
    username: str | None = Field(None, description="사용자 이름")
    password: str | None = Field(None, description="비밀번호")

    def validate_required_fields(self) -> None:
        """DB 종류별 필수 필드 유효성 검사"""
        required_fields_by_type = {
            "sqlite": ["name"],
            "mysql": ["host", "port", "username", "password"],
            "mariadb": ["host", "port", "username", "password"],
            "postgresql": ["host", "port", "username", "password"],
            "oracle": ["host", "port", "username", "password", "name"],
        }

        if not self.type:
            raise APIException(CommonCode.NO_DB_DRIVER)

        db_type = self.type.lower()
        if db_type not in required_fields_by_type:
            raise APIException(CommonCode.INVALID_DB_DRIVER)

        missing = [
            field_name
            for field_name in required_fields_by_type[db_type]
            if self._is_empty(getattr(self, field_name, None))
        ]

        if missing:
            raise APIException(CommonCode.NO_VALUE)

    @staticmethod
    def _is_empty(value: Any | None) -> bool:
        """값이 None, 빈 문자열, 공백 문자열인지 검사"""
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        return False

class SaveDBProfile(DBProfileInfo):
    id: str | None = Field(None, description="DB Key 값")
    view_name: str | None = Field(None, description="DB 노출명")

# DB에서 조회되는 모든 정보를 담는 클래스입니다.
class DBProfile(BaseModel):
    id: str
    type: str
    host: str
    port: int
    name: str | None
    username: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
