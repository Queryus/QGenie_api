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

            db_models = self._transform_ai_response_to_db_models(ai_response, db_profile, request.db_profile_id)
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
        self, ai_response: dict[str, Any], db_profile: AllDBProfileInfo, db_profile_id: str
    ) -> dict[str, Any]:
        now = datetime.now()
        annotation_id = generate_prefixed_uuid(DBSaveIdEnum.database_annotation.value)

        db_anno = DatabaseAnnotationInDB(
            id=annotation_id,
            db_profile_id=db_profile_id,
            database_name=db_profile.name,
            description=ai_response.get("database_annotation"),
            created_at=now,
            updated_at=now,
        )

        table_annos, col_annos, constraint_annos, constraint_col_annos, index_annos, index_col_annos = (
            [],
            [],
            [],
            [],
            [],
            [],
        )

        for tbl_data in ai_response.get("tables", []):
            table_id = generate_prefixed_uuid(DBSaveIdEnum.table_annotation.value)
            table_annos.append(
                TableAnnotationInDB(
                    id=table_id,
                    database_annotation_id=annotation_id,
                    table_name=tbl_data["table_name"],
                    description=tbl_data.get("annotation"),
                    created_at=now,
                    updated_at=now,
                )
            )

            col_map = {
                col["column_name"]: generate_prefixed_uuid(DBSaveIdEnum.column_annotation.value)
                for col in tbl_data.get("columns", [])
            }

            for col_data in tbl_data.get("columns", []):
                col_annos.append(
                    ColumnAnnotationInDB(
                        id=col_map[col_data["column_name"]],
                        table_annotation_id=table_id,
                        column_name=col_data["column_name"],
                        description=col_data.get("annotation"),
                        created_at=now,
                        updated_at=now,
                    )
                )

            for const_data in tbl_data.get("constraints", []):
                const_id = generate_prefixed_uuid(DBSaveIdEnum.table_constraint.value)
                constraint_annos.append(
                    TableConstraintInDB(
                        id=const_id,
                        table_annotation_id=table_id,
                        name=const_data["name"],
                        constraint_type=ConstraintTypeEnum(const_data["type"]),
                        created_at=now,
                        updated_at=now,
                    )
                )
                for col_name in const_data.get("columns", []):
                    constraint_col_annos.append(
                        ConstraintColumnInDB(
                            id=generate_prefixed_uuid(DBSaveIdEnum.constraint_column.value),
                            constraint_id=const_id,
                            column_annotation_id=col_map[col_name],
                            created_at=now,
                            updated_at=now,
                        )
                    )

            for idx_data in tbl_data.get("indexes", []):
                idx_id = generate_prefixed_uuid(DBSaveIdEnum.index_annotation.value)
                index_annos.append(
                    IndexAnnotationInDB(
                        id=idx_id,
                        table_annotation_id=table_id,
                        name=idx_data["name"],
                        is_unique=1 if idx_data.get("is_unique") else 0,
                        created_at=now,
                        updated_at=now,
                    )
                )
                for col_name in idx_data.get("columns", []):
                    index_col_annos.append(
                        IndexColumnInDB(
                            id=generate_prefixed_uuid(DBSaveIdEnum.index_column.value),
                            index_id=idx_id,
                            column_annotation_id=col_map[col_name],
                            created_at=now,
                            updated_at=now,
                        )
                    )

        return {
            "db_annotation": db_anno,
            "table_annotations": table_annos,
            "column_annotations": col_annos,
            "constraint_annotations": constraint_annos,
            "constraint_column_annotations": constraint_col_annos,
            "index_annotations": index_annos,
            "index_column_annotations": index_col_annos,
        }

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
