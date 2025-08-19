# app/schemas/user_db/result_model.py

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.core.status import CommonCode


# 기본 반환 모델
class BasicResult(BaseModel):
    is_successful: bool = Field(..., description="성공 여부")
    code: CommonCode = Field(None, description="결과 코드")


# 디비 정보 후 반환되는 저장 모델
class ChangeProfileResult(BasicResult):
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
    annotation_id: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# DB Profile 전체 조회 결과를 담는 새로운 모델
class AllDBProfileResult(BasicResult):
    """DB 프로필 전체 조회 결과를 위한 확장 모델"""

    profiles: list[DBProfile] = Field([], description="DB 프로필 목록")


class ColumnInfo(BaseModel):
    """단일 컬럼의 상세 정보를 담는 모델"""

    name: str = Field(..., description="컬럼 이름")
    type: str = Field(..., description="데이터 타입")
    nullable: bool = Field(..., description="NULL 허용 여부")
    default: Any | None = Field(None, description="기본값")
    comment: str | None = Field(None, description="코멘트")
    is_pk: bool = Field(False, description="기본 키(Primary Key) 여부")
    ordinal_position: int | None = Field(None, description="컬럼 순서")


class ConstraintInfo(BaseModel):
    """테이블 제약 조건 정보를 담는 모델"""

    name: str | None = Field(None, description="제약 조건 이름")
    type: str = Field(..., description="제약 조건 타입 (PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK)")
    columns: list[str] = Field(..., description="제약 조건에 포함된 컬럼 목록")
    # FOREIGN KEY 관련 필드
    referenced_table: str | None = Field(None, description="참조하는 테이블 (FK)")
    referenced_columns: list[str] | None = Field(None, description="참조하는 테이블의 컬럼 (FK)")
    on_update: str | None = Field(None, description="UPDATE 시 동작 (FK)")
    on_delete: str | None = Field(None, description="DELETE 시 동작 (FK)")
    # CHECK 관련 필드
    check_expression: str | None = Field(None, description="CHECK 제약 조건 표현식")


class IndexInfo(BaseModel):
    """테이블 인덱스 정보를 담는 모델"""

    name: str | None = Field(None, description="인덱스 이름")
    columns: list[str] = Field(..., description="인덱스에 포함된 컬럼 목록")
    is_unique: bool = Field(False, description="고유 인덱스 여부")


class TableInfo(BaseModel):
    """단일 테이블의 이름과 상세 정보를 담는 모델"""

    name: str = Field(..., description="테이블 이름")
    columns: list[ColumnInfo] = Field([], description="컬럼 목록")
    constraints: list[ConstraintInfo] = Field([], description="제약 조건 목록")
    indexes: list[IndexInfo] = Field([], description="인덱스 목록")
    comment: str | None = Field(None, description="테이블 코멘트")


class SchemaInfoResult(BasicResult):
    """DB 스키마 상세 정보 조회 결과를 위한 확장 모델"""

    schema: list[TableInfo] = Field([], description="테이블 및 컬럼 정보 목록")


class SchemaListResult(BasicResult):
    schemas: list[str] = Field([], description="스키마 이름 목록")


class TableListResult(BasicResult):
    tables: list[str] = Field([], description="테이블 이름 목록")


class ColumnListResult(BasicResult):
    columns: list[ColumnInfo] = Field([], description="컬럼 정보 목록")


# ─────────────────────────────
# 계층적 스키마 조회를 위한 모델
# ─────────────────────────────


class SchemaDetail(BaseModel):
    """계층적 조회에서 스키마 정보를 담는 모델 (테이블 포함)"""

    schema_name: str = Field(..., description="스키마 이름")
    tables: list[TableInfo] = Field([], description="테이블 목록")
