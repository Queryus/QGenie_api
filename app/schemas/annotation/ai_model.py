from typing import Any

from pydantic import BaseModel, Field


class AIColumnInfo(BaseModel):
    """AI 요청을 위한 컬럼 정보 모델"""

    column_name: str = Field(..., description="컬럼 이름")
    data_type: str = Field(..., description="데이터 타입")
    is_pk: bool = Field(False, description="기본 키(Primary Key) 여부")
    is_nullable: bool = Field(..., description="NULL 허용 여부")
    default_value: Any | None = Field(None, description="기본값")


class AIConstraintInfo(BaseModel):
    """AI 요청을 위한 제약 조건 정보 모델 (FK 제외)"""

    name: str | None = Field(None, description="제약 조건 이름")
    type: str = Field(..., description="제약 조건 타입 (PRIMARY KEY, UNIQUE, CHECK)")
    columns: list[str] = Field(..., description="제약 조건에 포함된 컬럼 목록")
    check_expression: str | None = Field(None, description="CHECK 제약 조건 표현식")


class AIIndexInfo(BaseModel):
    """AI 요청을 위한 인덱스 정보 모델"""

    name: str | None = Field(None, description="인덱스 이름")
    columns: list[str] = Field(..., description="인덱스에 포함된 컬럼 목록")
    is_unique: bool = Field(False, description="고유 인덱스 여부")


class AITableInfo(BaseModel):
    """AI 요청을 위한 테이블 정보 모델"""

    table_name: str = Field(..., description="테이블 이름")
    columns: list[AIColumnInfo] = Field(..., description="컬럼 목록")
    constraints: list[AIConstraintInfo] = Field([], description="제약 조건 목록 (FK 제외)")
    indexes: list[AIIndexInfo] = Field([], description="인덱스 목록")
    sample_rows: list[dict[str, Any]] = Field([], description="테이블 샘플 데이터")


class AIRelationship(BaseModel):
    """AI 요청을 위한 관계(FK) 정보 모델"""

    from_table: str = Field(..., description="관계를 시작하는 테이블")
    from_columns: list[str] = Field(..., description="관계를 시작하는 컬럼")
    to_table: str = Field(..., description="관계를 맺는 대상 테이블")
    to_columns: list[str] = Field(..., description="관계를 맺는 대상 컬럼")


class AIDatabaseInfo(BaseModel):
    """AI 요청을 위한 데이터베이스 정보 모델"""

    database_name: str = Field(..., description="데이터베이스 이름")
    tables: list[AITableInfo] = Field(..., description="테이블 목록")
    relationships: list[AIRelationship] = Field([], description="관계(FK) 목록")


class AIAnnotationRequest(BaseModel):
    """AI 어노테이션 생성 요청 최상위 모델"""

    dbms_type: str = Field(..., description="DBMS 종류")
    databases: list[AIDatabaseInfo] = Field(..., description="데이터베이스 목록")
