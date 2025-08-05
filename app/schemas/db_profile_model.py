# app/schemas/db_profile_model.py

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# 사용자가 직접 입력해야 하는 정보만 포함합니다.
class DBProfileCreate(BaseModel):
    type: str = Field(..., description="DB 종류")
    host: str | None = Field(None, description="호스트 주소")
    port: int | None = Field(None, description="포트 번호")
    username: str | None = Field(None, description="사용자 이름")
    password: str | None = Field(None, description="비밀번호")
    name: str | None = Field(None, description="데이터베이스 이름")
    driver: str | None = Field(None, description="드라이버 이름")

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
            raise ValueError("DB 종류(type)는 필수 항목입니다.")

        db_type = self.type.lower()
        if db_type not in required_fields_by_type:
            raise ValueError(f"지원하지 않는 DB 종류입니다: {self.type}")

        missing = [
            field_name
            for field_name in required_fields_by_type[db_type]
            if self._is_empty(getattr(self, field_name, None))
        ]

        if missing:
            raise ValueError(f"{self.type} 연결에 필요한 값이 누락되었습니다: {missing}")

    @staticmethod
    def _is_empty(value: Any | None) -> bool:
        """값이 None, 빈 문자열, 공백 문자열인지 검사"""
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        return False


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
