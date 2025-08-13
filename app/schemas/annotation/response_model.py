from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.annotation.base_model import AnnotationBase


# 상세 정보 모델 (조회 시 사용)
class ColumnAnnotationDetail(BaseModel):
    id: str
    column_name: str
    description: str | None = None


class ConstraintDetail(BaseModel):
    name: str | None = None
    type: str
    columns: list[str]
    description: str | None = None  # AI가 생성해줄 수 있음


class IndexDetail(BaseModel):
    name: str | None = None
    columns: list[str]
    is_unique: bool
    description: str | None = None  # AI가 생성해줄 수 있음


class TableAnnotationDetail(AnnotationBase):
    table_name: str
    description: str | None = None
    columns: list[ColumnAnnotationDetail]
    constraints: list[ConstraintDetail]
    indexes: list[IndexDetail]


class FullAnnotationResponse(AnnotationBase):
    """전체 어노테이션 상세 정보 응답 스키마"""

    db_profile_id: str = Field(..., description="DB 프로필의 고유 ID")
    database_name: str = Field(..., description="데이터베이스 이름")
    description: str | None = Field(None, description="데이터베이스 전체에 대한 설명")
    tables: list[TableAnnotationDetail] = Field([], description="테이블 어노테이션 목록")


# 간단한 생성/삭제 응답 모델
# 필요할지는 모르겠음
class AnnotationCreationSummary(BaseModel):
    """어노테이션 생성 결과 요약 응답 스키마"""

    id: str = Field(..., description="생성된 어노테이션의 고유 ID")
    db_profile_id: str = Field(..., description="DB 프로필의 고유 ID")
    database_name: str = Field(..., description="데이터베이스 이름")
    created_at: datetime = Field(..., description="어노테이션 생성 시각")


class AnnotationDeleteResponse(BaseModel):
    """어노테이션 삭제 API 응답 스키마"""

    id: str = Field(..., description="삭제된 어노테이션의 고유 ID")
    message: str = Field("성공적으로 삭제되었습니다.", description="삭제 결과 메시지")
