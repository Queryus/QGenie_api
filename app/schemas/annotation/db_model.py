from pydantic import Field

from app.core.enum.constraint_type import ConstraintTypeEnum
from app.schemas.annotation.base_model import AnnotationBase


class DatabaseAnnotationInDB(AnnotationBase):
    db_profile_id: str
    database_name: str
    description: str | None = Field(None, description="AI가 생성한 설명")


class TableAnnotationInDB(AnnotationBase):
    database_annotation_id: str
    table_name: str
    description: str | None = Field(None, description="AI가 생성한 설명")


class ColumnAnnotationInDB(AnnotationBase):
    table_annotation_id: str
    column_name: str
    data_type: str | None = None
    is_nullable: int = 1
    default_value: str | None = None
    check_expression: str | None = None
    ordinal_position: int | None = None
    description: str | None = Field(None, description="AI가 생성한 설명")


class TableRelationshipInDB(AnnotationBase):
    database_annotation_id: str
    from_table_id: str
    to_table_id: str
    relationship_type: str
    description: str | None = Field(None, description="AI가 생성한 설명")


class TableConstraintInDB(AnnotationBase):
    table_annotation_id: str
    constraint_type: ConstraintTypeEnum
    name: str | None = None
    expression: str | None = None
    ref_table: str | None = None
    on_update_action: str | None = None
    on_delete_action: str | None = None


class ConstraintColumnInDB(AnnotationBase):
    constraint_id: str
    column_annotation_id: str
    position: int | None = None
    referenced_column_name: str | None = None


class IndexAnnotationInDB(AnnotationBase):
    table_annotation_id: str
    name: str | None = None
    is_unique: int = 0


class IndexColumnInDB(AnnotationBase):
    index_id: str
    column_annotation_id: str
    position: int | None = None
