# app/schemas/user_db/result_model.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

from app.core.status import CommonCode

# 기본 반환 모델
class BasicResult(BaseModel):
    is_successful: bool = Field(..., description="성공 여부")
    code: CommonCode = Field(None, description="결과 코드")

# 디비 정보 후 반환되는 저장 모델
class SaveProfileResult(BasicResult):
    """DB 조회 결과를 위한 확장 모델"""
    view_name: str = Field(..., description="저장된 디비명")

# DB Profile 조회되는 정보를 담는 모델입니다.
class DBProfile(BaseModel):
    id: str
    type: str
    host: str
    port: int
    name: str | None
    username: str
    view_name: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# DB Profile 전체 조회 결과를 담는 새로운 모델
class AllDBProfileResult(BasicResult):
    """DB 프로필 전체 조회 결과를 위한 확장 모델"""
    profiles: List[DBProfile] = Field([], description="DB 프로필 목록")