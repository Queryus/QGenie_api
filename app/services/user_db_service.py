# app/service/driver_service.py

import importlib
import sqlite3
from typing import Any

from fastapi import Depends

from app.core.enum.db_driver import DBTypesEnum
from app.core.enum.db_key_prefix_name import DBSaveIdEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.core.utils import generate_prefixed_uuid
from app.repository.user_db_repository import UserDbRepository, user_db_repository
from app.schemas.user_db.db_profile_model import AllDBProfileInfo, DBProfileInfo, UpdateOrCreateDBProfile
from app.schemas.user_db.result_model import (
    AllDBProfileResult,
    BasicResult,
    ChangeProfileResult,
    ColumnListResult,
    SchemaInfoResult,
    TableListResult,
)

user_db_repository_dependency = Depends(lambda: user_db_repository)


class UserDbService:
    def connection_test(self, db_info: DBProfileInfo, repository: UserDbRepository = user_db_repository) -> BasicResult:
        """
        DB 연결 정보를 받아 연결 테스트를 수행 후 결과를 반환합니다.
        """
        try:
            driver_module = self._get_driver_module(db_info.type)
            connect_kwargs = self._prepare_connection_args(db_info)
            return repository.connection_test(driver_module, **connect_kwargs)
        except Exception as e:
            raise APIException(CommonCode.FAIL) from e

    def create_profile(
        self, create_db_info: UpdateOrCreateDBProfile, repository: UserDbRepository = user_db_repository
    ) -> ChangeProfileResult:
        """
        DB 연결 정보를 저장 후 결과를 반환합니다.
        """
        create_db_info.id = generate_prefixed_uuid(DBSaveIdEnum.user_db.value)
        try:
            # [수정] 쿼리와 데이터를 서비스에서 생성하여 레포지토리로 전달합니다.
            sql, data = self._get_create_query_and_data(create_db_info)
            return repository.create_profile(sql, data, create_db_info)
        except Exception as e:
            raise APIException(CommonCode.FAIL) from e

    def update_profile(
        self, update_db_info: UpdateOrCreateDBProfile, repository: UserDbRepository = user_db_repository
    ) -> ChangeProfileResult:
        """
        DB 연결 정보를 업데이트 후 결과를 반환합니다.
        """
        try:
            # [수정] 쿼리와 데이터를 서비스에서 생성하여 레포지토리로 전달합니다.
            sql, data = self._get_update_query_and_data(update_db_info)
            return repository.update_profile(sql, data, update_db_info)
        except Exception as e:
            raise APIException(CommonCode.FAIL) from e

    def delete_profile(self, profile_id: str, repository: UserDbRepository = user_db_repository) -> ChangeProfileResult:
        """
        DB 연결 정보를 삭제 후 결과를 반환합니다.
        """
        try:
            # [수정] 쿼리와 데이터를 서비스에서 생성하여 레포지토리로 전달합니다.
            sql, data = self._get_delete_query_and_data(profile_id)
            return repository.delete_profile(sql, data, profile_id)
        except Exception as e:
            raise APIException(CommonCode.FAIL) from e

    def find_all_profile(self, repository: UserDbRepository = user_db_repository) -> AllDBProfileResult:
        """
        모든 DB 연결 정보를 반환합니다.
        """
        try:
            # [수정] 쿼리를 서비스에서 생성하여 레포지토리로 전달합니다.
            sql = self._get_find_all_query()
            return repository.find_all_profile(sql)
        except Exception as e:
            raise APIException(CommonCode.FAIL) from e

    def find_profile(self, profile_id, repository: UserDbRepository = user_db_repository) -> AllDBProfileInfo:
        """
        특정 DB 연결 정보를 반환합니다.
        """
        try:
            # [수정] 쿼리와 데이터를 서비스에서 생성하여 레포지토리로 전달합니다.
            sql, data = self._get_find_one_query_and_data(profile_id)
            return repository.find_profile(sql, data)
        except Exception as e:
            raise APIException(CommonCode.FAIL) from e

    def find_schemas(
        self, db_info: AllDBProfileInfo, repository: UserDbRepository = user_db_repository
    ) -> SchemaInfoResult:
        """
        DB 스키마 정보를 조회를 수행합니다.
        """
        try:
            driver_module = self._get_driver_module(db_info.type)
            connect_kwargs = self._prepare_connection_args(db_info)
            schema_query = self._get_schema_query(db_info.type)

            return repository.find_schemas(driver_module, schema_query, **connect_kwargs)
        except Exception as e:
            raise APIException(CommonCode.FAIL) from e

    def find_tables(
        self, db_info: AllDBProfileInfo, schema_name: str, repository: UserDbRepository = user_db_repository
    ) -> TableListResult:
        """
        특정 스키마 내의 테이블 정보를 조회합니다.
        """
        try:
            driver_module = self._get_driver_module(db_info.type)
            connect_kwargs = self._prepare_connection_args(db_info)
            table_query = self._get_table_query(db_info.type, for_all_schemas=False)

            return repository.find_tables(driver_module, table_query, schema_name, **connect_kwargs)
        except Exception as e:
            raise APIException(CommonCode.FAIL) from e

    def find_columns(
        self,
        db_info: AllDBProfileInfo,
        schema_name: str,
        table_name: str,
        repository: UserDbRepository = user_db_repository,
    ) -> ColumnListResult:
        """
        특정 컬럼 정보를 조회합니다.
        """
        try:
            driver_module = self._get_driver_module(db_info.type)
            connect_kwargs = self._prepare_connection_args(db_info)
            column_query = self._get_column_query(db_info.type)
            db_type = db_info.type

            return repository.find_columns(
                driver_module, column_query, schema_name, db_type, table_name, **connect_kwargs
            )
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

    def _prepare_connection_args(self, db_info: DBProfileInfo) -> dict[str, Any]:
        """
        DB 타입에 따라 연결에 필요한 매개변수를 딕셔너리로 구성합니다.
        """
        # SQLite는 별도 처리
        if db_info.type == "sqlite":
            return {"db_name": db_info.name}

        # MSSQL은 연결 문자열을 별도로 구성
        if db_info.type == "mssql":
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={db_info.host},{db_info.port};"
                f"UID={db_info.username};"
                f"PWD={db_info.password};"
            )
            if db_info.name:
                connection_string += f"DATABASE={db_info.name};"
            return {"connection_string": connection_string}

        # 그 외 DB들은 공통 파라미터로 시작
        kwargs = {"host": db_info.host, "port": db_info.port, "user": db_info.username, "password": db_info.password}

        # DB 이름이 없을 경우, 기본 파라미터만 반환
        if not db_info.name:
            return kwargs

        # DB 이름이 있다면, 타입에 따라 적절한 파라미터를 추가합니다.
        if db_info.type == "postgresql":
            kwargs["dbname"] = db_info.name
        elif db_info.type in ["mysql", "mariadb"]:
            kwargs["database"] = db_info.name
        elif db_info.type == "oracle":
            kwargs["dsn"] = f"{db_info.host}:{db_info.port}/{db_info.name}"

        return kwargs

    def _get_schema_query(self, db_type: str) -> str | None:
        db_type = db_type.lower()
        if db_type == "postgresql":
            return """
                SELECT schema_name FROM information_schema.schemata
                WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
            """
        elif db_type in ["mysql", "mariadb"]:
            return "SELECT schema_name FROM information_schema.schemata"
        elif db_type == "oracle":
            return "SELECT username FROM all_users"
        elif db_type == "sqlite":
            return None
        return None

    def _get_table_query(self, db_type: str, for_all_schemas: bool = False) -> str | None:  # 수정됨
        db_type = db_type.lower()
        if db_type == "postgresql":
            if for_all_schemas:
                return """
                    SELECT table_name, table_schema FROM information_schema.tables
                    WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema')
                """
            else:
                return """
                    SELECT table_name, table_schema FROM information_schema.tables
                    WHERE table_type = 'BASE TABLE' AND table_schema = %s
                """
        elif db_type in ["mysql", "mariadb"]:
            if for_all_schemas:
                return """
                    SELECT table_name, table_schema FROM information_schema.tables
                    WHERE table_type = 'BASE TABLE'
                """
            else:
                return """
                    SELECT table_name, table_schema FROM information_schema.tables
                    WHERE table_type = 'BASE TABLE' AND table_schema = %s
                """
        elif db_type == "oracle":
            return "SELECT table_name FROM all_tables WHERE owner = :owner"
        elif db_type == "sqlite":
            return "SELECT name FROM sqlite_master WHERE type='table'"
        return None

    def _get_column_query(self, db_type: str) -> str | None:
        db_type = db_type.lower()
        if db_type == "postgresql":
            return """
                SELECT column_name, data_type, is_nullable, column_default, table_name, table_schema
                FROM information_schema.columns
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                AND table_schema = %s
                AND table_name = %s
            """
        elif db_type in ["mysql", "mariadb"]:
            return """
                SELECT column_name, data_type, is_nullable, column_default, table_name, table_schema
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
            """
        elif db_type == "oracle":
            return """
                SELECT column_name, data_type, nullable, data_default, table_name
                FROM all_tab_columns
                WHERE owner = :owner AND table_name = :table
            """
        elif db_type == "sqlite":
            return None
        return None

    # ─────────────────────────────
    # 프로필 CRUD 쿼리 생성 메서드
    # ─────────────────────────────
    def _get_create_query_and_data(self, db_info: UpdateOrCreateDBProfile) -> tuple[str, tuple]:
        profile_dict = db_info.model_dump()
        columns_to_insert = {k: v for k, v in profile_dict.items() if v is not None}
        columns = ", ".join(columns_to_insert.keys())
        placeholders = ", ".join(["?"] * len(columns_to_insert))
        sql = f"INSERT INTO db_profile ({columns}) VALUES ({placeholders})"
        data = tuple(columns_to_insert.values())
        return sql, data

    def _get_update_query_and_data(self, db_info: UpdateOrCreateDBProfile) -> tuple[str, tuple]:
        profile_dict = db_info.model_dump()
        columns_to_update = {k: v for k, v in profile_dict.items() if v is not None and k != "id"}
        set_clause = ", ".join([f"{key} = ?" for key in columns_to_update.keys()])
        sql = f"UPDATE db_profile SET {set_clause} WHERE id = ?"
        data = tuple(columns_to_update.values()) + (db_info.id,)
        return sql, data

    def _get_delete_query_and_data(self, profile_id: str) -> tuple[str, tuple]:
        sql = "DELETE FROM db_profile WHERE id = ?"
        data = (profile_id,)
        return sql, data

    def _get_find_all_query(self) -> str:
        return "SELECT id, type, host, port, name, username, view_name, created_at, updated_at FROM db_profile"

    def _get_find_one_query_and_data(self, profile_id: str) -> tuple[str, tuple]:
        sql = "SELECT * FROM db_profile WHERE id = ?"
        data = (profile_id,)
        return sql, data


user_db_service = UserDbService()
