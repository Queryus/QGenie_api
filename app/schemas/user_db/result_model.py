# app/schemas/user_db/result_model.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Any

from app.core.status import CommonCode

# 기본 반환 모델
class BasicResult(BaseModel):
    is_successful: bool = Field(..., description="성공 여부")
    code: CommonCode = Field(None, description="결과 코드")

# 디비 정보 후 반환되는 저장 모델
class UpdateOrSaveProfileResult(BasicResult):
    """DB 조회 결과를 위한 확장 모델"""
    view_name: str = Field(..., description="저장된 디비명")

# DB Profile 조회되는 정보를 담는 모델입니다.
class DBProfile(BaseModel):
    id: str
    type: str
    host: str | None
    port: int | None
    name: str | None
    username: str | None
    view_name: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# DB Profile 전체 조회 결과를 담는 새로운 모델
class AllDBProfileResult(BasicResult):
    """DB 프로필 전체 조회 결과를 위한 확장 모델"""
    profiles: List[DBProfile] = Field([], description="DB 프로필 목록")

class ColumnInfo(BaseModel):
    """단일 컬럼의 상세 정보를 담는 모델"""
    name: str = Field(..., description="컬럼 이름")
    type: str = Field(..., description="데이터 타입")
    nullable: bool = Field(..., description="NULL 허용 여부")
    default: Any | None = Field(None, description="기본값")
    comment: str | None = Field(None, description="코멘트")
    is_pk: bool = Field(False, description="기본 키(Primary Key) 여부")

class TableInfo(BaseModel):
    """단일 테이블의 이름과 컬럼 목록을 담는 모델"""
    name: str = Field(..., description="테이블 이름")
    columns: List[ColumnInfo] = Field([], description="컬럼 목록")
    comment: str | None = Field(None, description="테이블 코멘트")

class SchemaInfoResult(BasicResult):
    """DB 스키마 상세 정보 조회 결과를 위한 확장 모델"""
    schema: List[TableInfo] = Field([], description="테이블 및 컬럼 정보 목록")

class SchemaListResult(BasicResult):
    schemas: List[str] = Field([], description="스키마 이름 목록")

class TableListResult(BasicResult):
    tables: List[str] = Field([], description="테이블 이름 목록")

class ColumnListResult(BasicResult):
    columns: List[ColumnInfo] = Field([], description="컬럼 정보 목록")
