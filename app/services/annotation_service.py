import sqlite3
from datetime import datetime
from typing import Any

from fastapi import Depends

from app.core.enum.constraint_type import ConstraintTypeEnum
from app.core.enum.db_key_prefix_name import DBSaveIdEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.core.utils import generate_prefixed_uuid, get_db_path
from app.repository.annotation_repository import AnnotationRepository, annotation_repository
from app.schemas.annotation.db_model import (
    ColumnAnnotationInDB,
    ConstraintColumnInDB,
    DatabaseAnnotationInDB,
    IndexAnnotationInDB,
    IndexColumnInDB,
    TableAnnotationInDB,
    TableConstraintInDB,
)
from app.schemas.annotation.request_model import AnnotationCreateRequest
from app.schemas.annotation.response_model import AnnotationDeleteResponse, FullAnnotationResponse
from app.schemas.user_db.db_profile_model import AllDBProfileInfo
from app.schemas.user_db.result_model import TableInfo as UserDBTableInfo
from app.services.user_db_service import UserDbService, user_db_service

annotation_repository_dependency = Depends(lambda: annotation_repository)
user_db_service_dependency = Depends(lambda: user_db_service)

# AI 서버의 주소 (임시)
AI_SERVER_URL = "http://localhost:8001/api/v1/annotate/database"


class AnnotationService:
    def __init__(
        self, repository: AnnotationRepository = annotation_repository, user_db_serv: UserDbService = user_db_service
    ):
        self.repository = repository
        self.user_db_service = user_db_serv

    async def create_annotation(self, request: AnnotationCreateRequest) -> FullAnnotationResponse:
        """
        어노테이션 생성을 위한 전체 프로세스를 관장합니다.
        1. DB 프로필 및 전체 스키마 정보 조회
        2. TODO: AI 서버에 요청 (현재는 Mock 데이터 사용)
        3. 트랜잭션 내에서 전체 어노테이션 정보 저장
        """
        try:
            request.validate()
        except ValueError as e:
            raise APIException(CommonCode.INVALID_ANNOTATION_REQUEST, detail=str(e)) from e

        # 1. DB 프로필 및 전체 스키마 정보 조회
        db_profile = self.user_db_service.find_profile(request.db_profile_id)
        full_schema_info = self.user_db_service.get_full_schema_info(db_profile)

        # 2. AI 서버에 요청 (현재는 Mock 데이터 사용)
        ai_response = await self._request_annotation_to_ai_server(full_schema_info)

        # 3. 트랜잭션 내에서 전체 어노테이션 정보 저장
        db_path = get_db_path()
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            conn.execute("BEGIN")

            db_models = self._transform_ai_response_to_db_models(
                ai_response, db_profile, request.db_profile_id, full_schema_info
            )
            self.repository.create_full_annotation(db_conn=conn, **db_models)

            conn.commit()
            annotation_id = db_models["db_annotation"].id

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise APIException(CommonCode.FAIL_CREATE_ANNOTATION, detail=f"Database transaction failed: {e}") from e
        finally:
            if conn:
                conn.close()

        return self.get_full_annotation(annotation_id)

    def _transform_ai_response_to_db_models(
        self,
        ai_response: dict[str, Any],
        db_profile: AllDBProfileInfo,
        db_profile_id: str,
        full_schema_info: list[UserDBTableInfo],
    ) -> dict[str, Any]:
        now = datetime.now()
        annotation_id = generate_prefixed_uuid(DBSaveIdEnum.database_annotation.value)

        # 원본 스키마 정보를 쉽게 조회할 수 있도록 룩업 테이블 생성
        schema_lookup: dict[str, UserDBTableInfo] = {table.name: table for table in full_schema_info}

        db_anno = DatabaseAnnotationInDB(
            id=annotation_id,
            db_profile_id=db_profile_id,
            database_name=db_profile.name or db_profile.username,
            description=ai_response.get("database_annotation"),
            created_at=now,
            updated_at=now,
        )

        (
            all_table_annos,
            all_col_annos,
            all_constraint_annos,
            all_constraint_col_annos,
            all_index_annos,
            all_index_col_annos,
        ) = (
            [],
            [],
            [],
            [],
            [],
            [],
        )

        for tbl_data in ai_response.get("tables", []):
            original_table = schema_lookup.get(tbl_data["table_name"])
            if not original_table:
                continue

            (
                table_anno,
                col_annos,
                constraint_annos,
                constraint_col_annos,
                index_annos,
                index_col_annos,
            ) = self._create_annotations_for_table(tbl_data, original_table, annotation_id, now)

            all_table_annos.append(table_anno)
            all_col_annos.extend(col_annos)
            all_constraint_annos.extend(constraint_annos)
            all_constraint_col_annos.extend(constraint_col_annos)
            all_index_annos.extend(index_annos)
            all_index_col_annos.extend(index_col_annos)

        return {
            "db_annotation": db_anno,
            "table_annotations": all_table_annos,
            "column_annotations": all_col_annos,
            "constraint_annotations": all_constraint_annos,
            "constraint_column_annotations": all_constraint_col_annos,
            "index_annotations": all_index_annos,
            "index_column_annotations": all_index_col_annos,
        }

    def _create_annotations_for_table(
        self,
        tbl_data: dict[str, Any],
        original_table: UserDBTableInfo,
        database_annotation_id: str,
        now: datetime,
    ) -> tuple:
        table_id = generate_prefixed_uuid(DBSaveIdEnum.table_annotation.value)
        table_anno = TableAnnotationInDB(
            id=table_id,
            database_annotation_id=database_annotation_id,
            table_name=original_table.name,
            description=tbl_data.get("annotation"),
            created_at=now,
            updated_at=now,
        )

        col_map = {
            col.name: generate_prefixed_uuid(DBSaveIdEnum.column_annotation.value) for col in original_table.columns
        }

        col_annos = self._process_columns(tbl_data, original_table, table_id, col_map, now)
        constraint_annos, constraint_col_annos = self._process_constraints(
            tbl_data, original_table, table_id, col_map, now
        )
        index_annos, index_col_annos = self._process_indexes(tbl_data, original_table, table_id, col_map, now)

        return table_anno, col_annos, constraint_annos, constraint_col_annos, index_annos, index_col_annos

    def _process_columns(
        self, tbl_data: dict, original_table: UserDBTableInfo, table_id: str, col_map: dict, now: datetime
    ) -> list[ColumnAnnotationInDB]:
        col_annos = []
        for col_data in tbl_data.get("columns", []):
            original_column = next((c for c in original_table.columns if c.name == col_data["column_name"]), None)
            if not original_column:
                continue
            col_annos.append(
                ColumnAnnotationInDB(
                    id=col_map[original_column.name],
                    table_annotation_id=table_id,
                    column_name=original_column.name,
                    data_type=original_column.type,
                    is_nullable=1 if original_column.nullable else 0,
                    default_value=original_column.default,
                    description=col_data.get("annotation"),
                    # TODO: check_expression, ordinal_position은 현재 original_column에 없음
                    created_at=now,
                    updated_at=now,
                )
            )
        return col_annos

    def _process_constraints(
        self, tbl_data: dict, original_table: UserDBTableInfo, table_id: str, col_map: dict, now: datetime
    ) -> tuple[list[TableConstraintInDB], list[ConstraintColumnInDB]]:
        constraint_annos, constraint_col_annos = [], []
        for const_data in tbl_data.get("constraints", []):
            original_constraint = next((c for c in original_table.constraints if c.name == const_data["name"]), None)
            if not original_constraint:
                continue
            const_id = generate_prefixed_uuid(DBSaveIdEnum.table_constraint.value)
            constraint_annos.append(
                TableConstraintInDB(
                    id=const_id,
                    table_annotation_id=table_id,
                    name=original_constraint.name,
                    constraint_type=ConstraintTypeEnum(original_constraint.type),
                    ref_table=original_constraint.referenced_table,
                    # TODO: on_update/on_delete/expression 등 추가 정보 필요
                    created_at=now,
                    updated_at=now,
                )
            )
            for i, col_name in enumerate(original_constraint.columns):
                if col_name not in col_map:
                    continue
                constraint_col_annos.append(
                    ConstraintColumnInDB(
                        id=generate_prefixed_uuid(DBSaveIdEnum.constraint_column.value),
                        constraint_id=const_id,
                        column_annotation_id=col_map[col_name],
                        position=i + 1,
                        referenced_column_name=(
                            original_constraint.referenced_columns[i]
                            if original_constraint.referenced_columns
                            and i < len(original_constraint.referenced_columns)
                            else None
                        ),
                        created_at=now,
                        updated_at=now,
                    )
                )
        return constraint_annos, constraint_col_annos

    def _process_indexes(
        self, tbl_data: dict, original_table: UserDBTableInfo, table_id: str, col_map: dict, now: datetime
    ) -> tuple[list[IndexAnnotationInDB], list[IndexColumnInDB]]:
        index_annos, index_col_annos = [], []
        for idx_data in tbl_data.get("indexes", []):
            original_index = next((i for i in original_table.indexes if i.name == idx_data["name"]), None)
            if not original_index:
                continue
            idx_id = generate_prefixed_uuid(DBSaveIdEnum.index_annotation.value)
            index_annos.append(
                IndexAnnotationInDB(
                    id=idx_id,
                    table_annotation_id=table_id,
                    name=original_index.name,
                    is_unique=1 if original_index.is_unique else 0,
                    created_at=now,
                    updated_at=now,
                )
            )
            for i, col_name in enumerate(original_index.columns):
                if col_name not in col_map:
                    continue
                index_col_annos.append(
                    IndexColumnInDB(
                        id=generate_prefixed_uuid(DBSaveIdEnum.index_column.value),
                        index_id=idx_id,
                        column_annotation_id=col_map[col_name],
                        position=i + 1,
                        created_at=now,
                        updated_at=now,
                    )
                )
        return index_annos, index_col_annos

    def get_full_annotation(self, annotation_id: str) -> FullAnnotationResponse:
        try:
            annotation = self.repository.find_full_annotation_by_id(annotation_id)
            if not annotation:
                raise APIException(CommonCode.NO_SEARCH_DATA)
            return annotation
        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL_FIND_ANNOTATION) from e

    def delete_annotation(self, annotation_id: str) -> AnnotationDeleteResponse:
        try:
            is_deleted = self.repository.delete_annotation_by_id(annotation_id)
            if not is_deleted:
                raise APIException(CommonCode.NO_SEARCH_DATA)
            return AnnotationDeleteResponse(id=annotation_id)
        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL_DELETE_ANNOTATION) from e

    async def _request_annotation_to_ai_server(self, schema_info: list[UserDBTableInfo]) -> dict:
        """AI 서버에 스키마 정보를 보내고 어노테이션을 받아옵니다."""
        # 우선은 목업 데이터 활용
        return self._get_mock_ai_response(schema_info)

        # Real implementation below
        # request_body = {"database_schema": {"tables": [table.model_dump() for table in schema_info]}}
        # async with httpx.AsyncClient() as client:
        #     try:
        #         response = await client.post(AI_SERVER_URL, json=request_body, timeout=60.0)
        #         response.raise_for_status()
        #         return response.json()
        #     except httpx.HTTPStatusError as e:
        #         raise APIException(CommonCode.FAIL_AI_SERVER_PROCESSING, detail=f"AI server error: {e.response.text}") from e
        #     except httpx.RequestError as e:
        #         raise APIException(CommonCode.FAIL_AI_SERVER_CONNECTION, detail=f"AI server connection failed: {e}") from e

    def _get_mock_ai_response(self, schema_info: list[UserDBTableInfo]) -> dict:
        """테스트를 위한 Mock AI 서버 응답 생성"""
        mock_response = {
            "database_annotation": "Mock: 데이터베이스 전체에 대한 설명입니다.",
            "tables": [],
            "relationships": [],
        }
        for table in schema_info:
            mock_table = {
                "table_name": table.name,
                "annotation": f"Mock: '{table.name}' 테이블에 대한 설명입니다.",
                "columns": [
                    {"column_name": col.name, "annotation": f"Mock: '{col.name}' 컬럼에 대한 설명입니다."}
                    for col in table.columns
                ],
                "constraints": [
                    {
                        "name": c.name,
                        "type": c.type,
                        "columns": c.columns,
                        "annotation": f"Mock: 제약조건 '{c.name}' 설명.",
                    }
                    for c in table.constraints
                ],
                "indexes": [
                    {
                        "name": i.name,
                        "columns": i.columns,
                        "is_unique": i.is_unique,
                        "annotation": f"Mock: 인덱스 '{i.name}' 설명.",
                    }
                    for i in table.indexes
                ],
            }
            mock_response["tables"].append(mock_table)
        return mock_response


annotation_service = AnnotationService()
