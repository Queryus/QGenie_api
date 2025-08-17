# app/service/query_service.py

import importlib
import sqlite3
from typing import Any

from fastapi import Depends

from app.core.enum.db_driver import DBTypesEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.repository.query_repository import QueryRepository, query_repository
from app.schemas.query.query_model import ExecutionQuery, QueryInfo, RequestExecutionQuery
from app.schemas.query.result_model import (
    BasicResult,
    ExecutionResult,
    ExecutionSelectResult,
    QueryTestResult,
    SelectQueryHistoryResult,
)
from app.schemas.user_db.db_profile_model import AllDBProfileInfo, DBProfileInfo

query_repository_dependency = Depends(lambda: query_repository)


class QueryService:
    def execution(
        self,
        query_info: RequestExecutionQuery,
        db_info: AllDBProfileInfo,
        repository: QueryRepository = query_repository,
    ) -> ExecutionSelectResult | ExecutionResult | BasicResult:
        """
        쿼리 수행 후 결과를 저장합니다.
        """
        driver_module = self._get_driver_module(db_info.type)
        connect_kwargs = self._prepare_connection_args(db_info, query_info.database)
        result = repository.execution(query_info.query_text, driver_module, **connect_kwargs)
        try:
            query_history_info = ExecutionQuery.from_query_info(query_info, db_info.type, result.is_successful, None)
            sql, data = self._get_create_query_and_data(query_history_info)
            repository.create_query_history(sql, data, query_history_info.query_text)
        except Exception as e:
            raise APIException(CommonCode.FAIL) from e
        return result

    def execution_test(
        self, query_info: QueryInfo, db_info: AllDBProfileInfo, repository: QueryRepository = query_repository
    ) -> QueryTestResult:
        """
        쿼리 수행 후 결과를 저장합니다.
        """
        driver_module = self._get_driver_module(db_info.type)
        connect_kwargs = self._prepare_connection_args(db_info, query_info.database)
        return repository.execution_test(query_info.query_text, driver_module, **connect_kwargs)

    def find_query_history(
        self, chat_tab_id: int, repository: QueryRepository = query_repository
    ) -> SelectQueryHistoryResult:
        """
        쿼리 기록을 조회합니다.
        """
        try:
            return repository.find_query_history(chat_tab_id)
        except Exception as e:
            raise APIException(CommonCode.FAIL) from e

    def _get_driver_module(self, db_type: str):
        """
        DB 타입에 따라 동적으로 드라이버 모듈을 로드합니다.
        """
        driver_name = DBTypesEnum[db_type.lower()].value
        if driver_name == "sqlite3":
            return sqlite3
        return importlib.import_module(driver_name)

    def _prepare_connection_args(self, db_info: DBProfileInfo, database_name: str) -> dict[str, Any]:
        """
        DB 타입에 따라 연결에 필요한 매개변수를 딕셔너리로 구성합니다.
        """
        # SQLite는 별도 처리
        if db_info.type == "sqlite":
            return {"db_name": db_info.name}

        # 그 외 DB들은 공통 파라미터로 시작
        kwargs = {"host": db_info.host, "port": db_info.port, "user": db_info.username, "password": db_info.password}

        # DB 이름이 없을 경우, 기본 파라미터만 반환
        if not db_info.name and not database_name:
            return kwargs

        # DB 이름이 있다면, 타입에 따라 적절한 파라미터를 추가합니다.
        final_db = database_name if database_name else db_info.name
        if db_info.type == "postgresql":
            kwargs["dbname"] = final_db
        elif db_info.type in ["mysql", "mariadb"]:
            kwargs["database"] = final_db
        elif db_info.type == "oracle":
            kwargs["dsn"] = f"{db_info.host}:{db_info.port}/{final_db}"

        return kwargs

    # ─────────────────────────────
    # 프로필 CRUD 쿼리 생성 메서드
    # ─────────────────────────────
    def _get_create_query_and_data(self, query_info: ExecutionQuery) -> tuple[str, tuple]:
        profile_dict = query_info.model_dump()
        columns_to_insert = {k: v for k, v in profile_dict.items() if v is not None}
        columns = ", ".join(columns_to_insert.keys())
        placeholders = ", ".join(["?"] * len(columns_to_insert))
        sql = f"INSERT INTO query_history ({columns}) VALUES ({placeholders})"
        data = tuple(columns_to_insert.values())
        return sql, data


query_service = QueryService()
