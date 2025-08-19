import logging
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
from app.schemas.annotation.ai_model import (
    AnnotationRequest,
    AnnotationResponse,
    AnnotatedTable,
    Column,
    Database,
    Relationship,
    Table,
)
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

user_db_service_dependency = Depends(lambda: user_db_service)

# AI 서버의 주소 (임시)
AI_SERVER_URL = "http://localhost:35816/api/v1/annotator"


class AnnotationService:
    def __init__(
        self, repository: AnnotationRepository = annotation_repository, user_db_serv: UserDbService = user_db_service
    ):
        """
        AnnotationService를 초기화합니다.

        Args:
            repository (AnnotationRepository): 어노테이션 레포지토리 의존성 주입.
            user_db_serv (UserDbService): 사용자 DB 서비스 의존성 주입.
        """
        self.repository = repository
        self.user_db_service = user_db_serv

    async def create_annotation(self, request: AnnotationCreateRequest) -> FullAnnotationResponse:
        """
        어노테이션 생성을 위한 전체 프로세스를 관장합니다.
        1. DB 프로필, 전체 스키마 정보, 샘플 데이터 조회
        2. AI 서버에 요청할 데이터 모델 생성
        3. TODO: AI 서버에 요청 (현재는 Mock 데이터 사용)
        4. 트랜잭션 내에서 전체 어노테이션 정보 저장 및 DB 프로필 업데이트
        """
        logging.info(f"Starting annotation creation for db_profile_id: {request.db_profile_id}")
        try:
            request.validate()
        except ValueError as e:
            raise APIException(CommonCode.INVALID_ANNOTATION_REQUEST, detail=str(e)) from e

        # 1. DB 프로필, 전체 스키마 정보, 샘플 데이터 조회
        db_profile = self.user_db_service.find_profile(request.db_profile_id)
        logging.info("Successfully fetched DB profile.")

        full_schema_info = self.user_db_service.get_full_schema_info(db_profile)
        logging.info(f"Successfully fetched full schema info with {len(full_schema_info)} tables.")

        sample_rows = self.user_db_service.get_sample_rows(db_profile, full_schema_info)
        logging.info(f"Successfully fetched sample rows for {len(sample_rows)} tables.")

        # 2. AI 서버에 요청할 데이터 모델 생성
        ai_request_body = self._prepare_ai_request_body(db_profile, full_schema_info, sample_rows)
        logging.info("Prepared AI request body.")
        logging.debug(f"AI Request Body: {ai_request_body.model_dump_json(indent=2)}")

        # 3. AI 서버에 요청 (현재는 Mock 데이터 사용)
        ai_response = await self._request_annotation_to_ai_server(ai_request_body)
        logging.info("Received AI response.")
        logging.debug(f"AI Response: {ai_response}")

        # 4. 트랜잭션 내에서 전체 어노테이션 정보 저장 및 DB 프로필 업데이트
        db_path = get_db_path()
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            conn.execute("BEGIN")

            db_models = self._transform_ai_response_to_db_models(
                ai_response, db_profile, request.db_profile_id, full_schema_info
            )
            logging.info("Transformed AI response to DB models.")
            self.repository.create_full_annotation(db_conn=conn, **db_models)
            logging.info("Successfully saved full annotation to the database.")

            annotation_id = db_models["db_annotation"].id
            self.repository.update_db_profile_annotation_id(
                db_conn=conn, db_profile_id=request.db_profile_id, annotation_id=annotation_id
            )
            logging.info(f"Updated db_profile with new annotation_id: {annotation_id}")

            conn.commit()
            logging.info("Database transaction committed.")

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logging.error("Database transaction failed and rolled back.", exc_info=True)
            raise APIException(CommonCode.FAIL_CREATE_ANNOTATION, detail=f"Database transaction failed: {e}") from e
        finally:
            if conn:
                conn.close()

        logging.info(f"Annotation creation process completed for annotation_id: {annotation_id}")
        return self.get_full_annotation(annotation_id)

    def get_annotation_by_db_profile_id(self, db_profile_id: str) -> FullAnnotationResponse:
        """
        db_profile_id를 기반으로 완전한 어노테이션 정보를 조회합니다.
        """
        db_profile = self.user_db_service.find_profile(db_profile_id)
        if not db_profile.annotation_id:
            raise APIException(CommonCode.NO_ANNOTATION_FOR_PROFILE)

        return self.get_full_annotation(db_profile.annotation_id)

    def _prepare_ai_request_body(
        self,
        db_profile: AllDBProfileInfo,
        full_schema_info: list[UserDBTableInfo],
        sample_rows: dict[str, list[dict[str, Any]]],
    ) -> AnnotationRequest:
        """
        AI 서버에 보낼 요청 본문을 Pydantic 모델로 생성합니다.
        """
        tables = []
        relationships = []

        for table_info in full_schema_info:
            # FK 제약조건을 분리하여 relationships 목록 생성
            for const in table_info.constraints:
                if const.type == "FOREIGN KEY" and const.referenced_table and const.referenced_columns:
                    relationships.append(
                        Relationship(
                            from_table=table_info.name,
                            from_columns=const.columns,
                            to_table=const.referenced_table,
                            to_columns=const.referenced_columns,
                        )
                    )

            # 간소화된 테이블 모델 생성 (컬럼명과 데이터 타입만)
            table = Table(
                table_name=table_info.name,
                columns=[
                    Column(
                        column_name=col.name,
                        data_type=col.type,
                    )
                    for col in table_info.columns
                ],
                sample_rows=sample_rows.get(table_info.name, []),
            )
            tables.append(table)

        database = Database(
            database_name=db_profile.name or db_profile.username, 
            tables=tables, 
            relationships=relationships
        )

        return AnnotationRequest(dbms_type=db_profile.type, databases=[database])

    def _transform_ai_response_to_db_models(
        self,
        ai_response: dict[str, Any],
        db_profile: AllDBProfileInfo,
        db_profile_id: str,
        full_schema_info: list[UserDBTableInfo],
    ) -> dict[str, Any]:
        """
        AI 서버의 응답을 받아서 DB에 저장할 수 있는 모델 딕셔너리로 변환합니다.
        """
        now = datetime.now()
        annotation_id = generate_prefixed_uuid(DBSaveIdEnum.database_annotation.value)

        # AI 서버 응답을 Pydantic 모델로 파싱
        annotation_response = AnnotationResponse(**ai_response)
        
        # 여러 데이터베이스를 처리할 수 있도록 수정
        if not annotation_response.databases:
            raise APIException(CommonCode.FAIL_CREATE_ANNOTATION, detail="AI 서버 응답에 데이터베이스 정보가 없습니다.")
        
        # 현재는 하나의 DB 프로필에 대해 하나의 어노테이션만 생성하므로 첫 번째 데이터베이스 사용
        # 향후 여러 데이터베이스를 지원하려면 각 데이터베이스별로 별도 어노테이션을 생성해야 함
        annotated_db = annotation_response.databases[0]
        
        # 여러 데이터베이스가 있는 경우 로그로 알림
        if len(annotation_response.databases) > 1:
            logging.warning(f"AI 서버 응답에 {len(annotation_response.databases)}개의 데이터베이스가 있지만, 현재는 첫 번째 데이터베이스만 처리합니다.")
            logging.info(f"처리할 데이터베이스: {annotated_db.database_name}")
            logging.info(f"무시될 데이터베이스들: {[db.database_name for db in annotation_response.databases[1:]]}")
        
        # 원본 스키마 정보를 쉽게 조회할 수 있도록 룩업 테이블 생성
        schema_lookup: dict[str, UserDBTableInfo] = {table.name: table for table in full_schema_info}

        db_anno = DatabaseAnnotationInDB(
            id=annotation_id,
            db_profile_id=db_profile_id,
            database_name=annotated_db.database_name,
            description=annotated_db.description,
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

        for annotated_table in annotated_db.tables:
            original_table = schema_lookup.get(annotated_table.table_name)
            if not original_table:
                logging.warning(
                    f"Table '{annotated_table.table_name}' from AI response not found in original schema. Skipping."
                )
                continue

            (
                table_anno,
                col_annos,
                constraint_annos,
                constraint_col_annos,
                index_annos,
                index_col_annos,
            ) = self._create_annotations_for_table(annotated_table, original_table, annotation_id, now)

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
        annotated_table: AnnotatedTable,
        original_table: UserDBTableInfo,
        database_annotation_id: str,
        now: datetime,
    ) -> tuple:
        """
        단일 테이블에 대한 모든 하위 어노테이션(컬럼, 제약조건, 인덱스)을 생성합니다.
        """
        table_id = generate_prefixed_uuid(DBSaveIdEnum.table_annotation.value)
        table_anno = TableAnnotationInDB(
            id=table_id,
            database_annotation_id=database_annotation_id,
            table_name=original_table.name,
            description=annotated_table.description,
            created_at=now,
            updated_at=now,
        )

        col_map = {
            col.name: generate_prefixed_uuid(DBSaveIdEnum.column_annotation.value) for col in original_table.columns
        }

        col_annos = self._process_columns(annotated_table, original_table, table_id, col_map, now)
        constraint_annos, constraint_col_annos = self._process_constraints(
            annotated_table, original_table, table_id, col_map, now
        )
        index_annos, index_col_annos = self._process_indexes(annotated_table, original_table, table_id, col_map, now)

        return table_anno, col_annos, constraint_annos, constraint_col_annos, index_annos, index_col_annos

    def _process_columns(
        self, annotated_table: AnnotatedTable, original_table: UserDBTableInfo, table_id: str, col_map: dict, now: datetime
    ) -> list[ColumnAnnotationInDB]:
        """
        테이블의 컬럼 어노테이션 모델 리스트를 생성합니다.
        """
        col_annos = []
        for annotated_column in annotated_table.columns:
            original_column = next((c for c in original_table.columns if c.name == annotated_column.column_name), None)
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
                    description=annotated_column.description,
                    ordinal_position=original_column.ordinal_position,
                    created_at=now,
                    updated_at=now,
                )
            )
        return col_annos

    def _process_constraints(
        self, annotated_table: AnnotatedTable, original_table: UserDBTableInfo, table_id: str, col_map: dict, now: datetime
    ) -> tuple[list[TableConstraintInDB], list[ConstraintColumnInDB]]:
        """
        테이블의 제약조건 및 제약조건 컬럼 어노테이션 모델 리스트를 생성합니다.
        간소화된 모델에는 constraints가 없으므로 빈 리스트를 반환합니다.
        """
        # 간소화된 모델에는 constraints가 없으므로 빈 리스트 반환
        return [], []

    def _process_indexes(
        self, annotated_table: AnnotatedTable, original_table: UserDBTableInfo, table_id: str, col_map: dict, now: datetime
    ) -> tuple[list[IndexAnnotationInDB], list[IndexColumnInDB]]:
        """
        테이블의 인덱스 및 인덱스 컬럼 어노테이션 모델 리스트를 생성합니다.
        간소화된 모델에는 indexes가 없으므로 빈 리스트를 반환합니다.
        """
        # 간소화된 모델에는 indexes가 없으므로 빈 리스트 반환
        return [], []

    def get_full_annotation(self, annotation_id: str) -> FullAnnotationResponse:
        """
        ID를 기반으로 완전한 어노테이션 정보를 조회합니다.
        """
        try:
            annotation = self.repository.find_full_annotation_by_id(annotation_id)
            if not annotation:
                raise APIException(CommonCode.NO_SEARCH_DATA)
            return annotation
        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL_FIND_ANNOTATION) from e

    def delete_annotation(self, annotation_id: str) -> AnnotationDeleteResponse:
        """
        ID를 기반으로 어노테이션 및 관련 하위 데이터를 모두 삭제합니다.
        """
        try:
            is_deleted = self.repository.delete_annotation_by_id(annotation_id)
            if not is_deleted:
                raise APIException(CommonCode.NO_SEARCH_DATA)
            return AnnotationDeleteResponse(id=annotation_id)
        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL_DELETE_ANNOTATION) from e

    async def _request_annotation_to_ai_server(self, ai_request: AnnotationRequest) -> dict:
        """AI 서버에 스키마 정보를 보내고 어노테이션을 받아옵니다."""
        import httpx
        
        # 실제 AI 서버 호출 시도
        request_body = ai_request.model_dump()
        async with httpx.AsyncClient() as client:
            try:
                logging.info(f"AI 서버로 요청 전송: {AI_SERVER_URL}")
                response = await client.post(AI_SERVER_URL, json=request_body, timeout=60.0)
                response.raise_for_status()
                logging.info("AI 서버로부터 응답 수신 성공")
                return response.json()
            except httpx.HTTPStatusError as e:
                logging.error(f"AI 서버 HTTP 에러: {e.response.status_code} - {e.response.text}")
                # AI 서버 에러 시 Mock 데이터로 폴백
                logging.info("AI 서버 에러로 인해 Mock 데이터 사용")
                return self._get_mock_ai_response(ai_request)
            except httpx.RequestError as e:
                logging.error(f"AI 서버 연결 에러: {e}")
                # AI 서버 연결 실패 시 Mock 데이터로 폴백
                logging.info("AI 서버 연결 실패로 인해 Mock 데이터 사용")
                return self._get_mock_ai_response(ai_request)

    def _get_mock_ai_response(self, ai_request: AnnotationRequest) -> dict:
        """테스트를 위한 Mock AI 서버 응답 생성"""
        # 요청 데이터를 기반으로 동적으로 Mock 응답을 생성하도록 수정
        # 여러 데이터베이스를 지원하도록 수정
        mock_response = {
            "dbms_type": "sqlite",
            "databases": []
        }
        
        for db_info in ai_request.databases:
            mock_db = {
                "database_name": db_info.database_name,
                "description": f"Mock: '{db_info.database_name}' 데이터베이스 전체에 대한 설명입니다.",
                "tables": [
                    {
                        "table_name": table.table_name,
                        "description": f"Mock: '{table.table_name}' 테이블에 대한 설명입니다.",
                        "columns": [
                            {
                                "column_name": col.column_name,
                                "description": f"Mock: '{col.column_name}' 컬럼에 대한 설명입니다."
                            }
                            for col in table.columns
                        ]
                    }
                    for table in db_info.tables
                ],
                "relationships": [
                    {
                        "from_table": rel.from_table,
                        "from_columns": rel.from_columns,
                        "to_table": rel.to_table,
                        "to_columns": rel.to_columns,
                        "description": f"Mock: '{rel.from_table}'과 '{rel.to_table}'의 관계 설명."
                    }
                    for rel in db_info.relationships
                ]
            }
            mock_response["databases"].append(mock_db)
        
        return mock_response


annotation_service = AnnotationService()
