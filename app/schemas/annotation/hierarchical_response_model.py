from datetime import datetime

from pydantic import BaseModel, Field


class HierarchicalColumnAnnotation(BaseModel):
    column_name: str = Field(..., description="컬럼 이름")
    description: str | None = Field(None, description="AI가 생성한 컬럼 어노테이션")
    data_type: str | None = Field(None, description="컬럼 데이터 타입")


class HierarchicalTableAnnotation(BaseModel):
    table_name: str = Field(..., description="테이블 이름")
    description: str | None = Field(None, description="AI가 생성한 테이블 어노테이션")
    columns: list[HierarchicalColumnAnnotation] = Field(..., description="테이블에 속한 컬럼 목록")


class HierarchicalRelationshipAnnotation(BaseModel):
    from_table: str = Field(..., description="외래 키 제약조건이 시작되는 테이블")
    from_columns: list[str] = Field(..., description="외래 키에 포함된 컬럼들")
    to_table: str = Field(..., description="외래 키가 참조하는 테이블")
    to_columns: list[str] = Field(..., description="참조되는 테이블의 컬럼들")
    description: str | None = Field(None, description="AI가 생성한 관계 어노테이션")


class HierarchicalDBAnnotation(BaseModel):
    db_name: str = Field(..., description="데이터베이스 이름")
    description: str | None = Field(None, description="AI가 생성한 데이터베이스 어노테이션")
    tables: list[HierarchicalTableAnnotation] = Field(..., description="데이터베이스에 속한 테이블 목록")
    relationships: list[HierarchicalRelationshipAnnotation] = Field(..., description="테이블 간의 관계 목록")


class HierarchicalDBMSAnnotation(BaseModel):
    dbms_type: str = Field(..., description="DBMS 종류 (e.g., postgresql, oracle)")
    databases: list[HierarchicalDBAnnotation] = Field(..., description="DBMS에 속한 데이터베이스 목록")
    annotation_id: str = Field(..., description="최상위 어노테이션 ID")
    db_profile_id: str = Field(..., description="DB 프로필 ID")
    created_at: datetime = Field(..., description="생성 일시")
    updated_at: datetime = Field(..., description="수정 일시")
