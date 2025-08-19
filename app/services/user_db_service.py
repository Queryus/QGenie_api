# app/service/driver_service.py

import importlib
import logging
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
    DBDetail,
    SchemaDetail,
    SchemaInfoResult,
    TableInfo,
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
            result = repository.connection_test(driver_module, **connect_kwargs)
            if not result.is_successful:
                raise APIException(result.code)
            return result
        except APIException:
            raise
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
            sql, data = self._get_create_query_and_data(create_db_info)
            return repository.create_profile(sql, data, create_db_info)
        except APIException:
            raise
        except Exception as e:
            raise APIException(CommonCode.FAIL_SAVE_PROFILE) from e

    def update_profile(
        self, update_db_info: UpdateOrCreateDBProfile, repository: UserDbRepository = user_db_repository
    ) -> ChangeProfileResult:
        """
        DB 연결 정보를 업데이트 후 결과를 반환합니다.
        """
        try:
            sql, data = self._get_update_query_and_data(update_db_info)
            return repository.update_profile(sql, data, update_db_info)
        except APIException:
            raise
        except Exception as e:
            raise APIException(CommonCode.FAIL_UPDATE_PROFILE) from e

    def delete_profile(self, profile_id: str, repository: UserDbRepository = user_db_repository) -> ChangeProfileResult:
        """
        DB 연결 정보를 삭제 후 결과를 반환합니다.
        """
        try:
            sql, data = self._get_delete_query_and_data(profile_id)
            return repository.delete_profile(sql, data, profile_id)
        except APIException:
            raise
        except Exception as e:
            raise APIException(CommonCode.FAIL_DELETE_PROFILE) from e

    def find_all_profile(self, repository: UserDbRepository = user_db_repository) -> AllDBProfileResult:
        """
        모든 DB 연결 정보를 반환합니다.
        """
        try:
            sql = self._get_find_all_query()
            result = repository.find_all_profile(sql)
            if not result.is_successful:
                raise APIException(result.code)
            return result
        except APIException:
            raise
        except Exception as e:
            raise APIException(CommonCode.FAIL_FIND_PROFILE) from e

    def find_profile(self, profile_id, repository: UserDbRepository = user_db_repository) -> AllDBProfileInfo:
        """
        특정 DB 연결 정보를 반환합니다.
        """
        try:
            # [수정] 쿼리와 데이터를 서비스에서 생성하여 레포지토리로 전달합니다.
            sql, data = self._get_find_one_query_and_data(profile_id)
            return repository.find_profile(sql, data)
        except APIException:
            raise
        except Exception as e:
            raise APIException(CommonCode.FAIL_FIND_PROFILE) from e

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

    def get_full_schema_info(
        self, db_info: AllDBProfileInfo, repository: UserDbRepository = user_db_repository
    ) -> list[TableInfo]:
        """
        DB 프로필 정보를 받아 해당 데이터베이스의 전체 스키마 정보
        (테이블, 컬럼, 제약조건, 인덱스)를 조회하여 반환합니다.
        """
        logging.info(f"Starting schema scan for db_profile: {db_info.id}")
        try:
            driver_module = self._get_driver_module(db_info.type)
            connect_kwargs = self._prepare_connection_args(db_info)
            schemas_to_scan = self._get_schemas_to_scan(db_info, repository, driver_module, connect_kwargs)

            full_schema_info = []
            for schema_name in schemas_to_scan:
                tables_result = repository.find_tables(
                    driver_module, self._get_table_query(db_info.type), schema_name, **connect_kwargs
                )
                logging.info(
                    f"Found {len(tables_result.tables)} tables in schema '{schema_name}': {tables_result.tables}"
                )

                if not tables_result.is_successful:
                    logging.warning(f"Failed to find tables for schema '{schema_name}'. Skipping.")
                    continue

                for table_name in tables_result.tables:
                    table_info = self._get_table_details(
                        driver_module, db_info, schema_name, table_name, connect_kwargs, repository
                    )
                    full_schema_info.append(table_info)

            logging.info(
                f"Finished schema scan. Total tables found: {len(full_schema_info)}. "
                f"Table names: {[t.name for t in full_schema_info]}"
            )
            return full_schema_info
        except APIException:
            raise
        except Exception as e:
            logging.error("An unexpected error occurred in get_full_schema_info", exc_info=True)
            raise APIException(CommonCode.FAIL) from e

    def get_hierarchical_schema_info(
        self, db_info: AllDBProfileInfo, repository: UserDbRepository = user_db_repository
    ) -> list[DBDetail]:
        """
        DB 프로필 정보를 받아 해당 DBMS의 전체 데이터베이스 및 스키마 정보를
        계층적인 구조 (DB -> 스키마 -> 테이블 -> 컬럼 등)로 조회하여 반환합니다.
        """
        logging.info(f"Starting hierarchical schema scan for db_profile: {db_info.id}")
        try:
            driver_module = self._get_driver_module(db_info.type)
            db_type = db_info.type.lower()

            initial_connect_kwargs = self._prepare_connection_args(db_info, ignore_db_name=(db_type == "postgresql"))
            db_query = self._get_database_query(db_type)
            databases_result = repository.find_databases(driver_module, db_type, db_query, **initial_connect_kwargs)

            if not databases_result.is_successful:
                raise APIException(CommonCode.FAIL_FIND_DATABASES)

            all_db_details = []
            for db_name in sorted(databases_result.databases):
                db_detail = self._get_db_schema_details(db_name, db_info, driver_module, repository)
                if db_detail:
                    all_db_details.append(db_detail)

            logging.info(f"Finished hierarchical schema scan. Total databases found: {len(all_db_details)}.")
            return all_db_details
        except APIException:
            raise
        except Exception as e:
            logging.error("An unexpected error occurred in get_hierarchical_schema_info", exc_info=True)
            raise APIException(CommonCode.FAIL) from e

    def _get_db_schema_details(
        self,
        db_name: str,
        db_info: AllDBProfileInfo,
        driver_module: Any,
        repository: UserDbRepository,
    ) -> DBDetail | None:
        """특정 데이터베이스의 모든 스키마와 테이블 정보를 조회하여 DBDetail 모델을 반환합니다."""
        db_type = db_info.type.lower()
        if db_type == "sqlite":
            current_db_info = db_info
            connect_kwargs = self._prepare_connection_args(db_info)
        else:
            current_db_info = db_info.model_copy(update={"name": db_name})
            connect_kwargs = self._prepare_connection_args(current_db_info)

        schema_query = self._get_schema_query(db_type, db_name)
        schemas_result = repository.find_schemas(driver_module, schema_query, **connect_kwargs)

        if not schemas_result.is_successful:
            logging.warning(f"Failed to find schemas for database '{db_name}'. Skipping.")
            return None

        schemas_to_scan = schemas_result.schemas
        if db_type == "sqlite" and not schemas_to_scan:
            schemas_to_scan = ["main"]

        schema_details = []
        for schema_name in sorted(schemas_to_scan):
            effective_schema_name = schema_name.upper() if db_type == "oracle" else schema_name
            table_query = self._get_table_query(db_type)
            tables_result = repository.find_tables(driver_module, table_query, effective_schema_name, **connect_kwargs)

            if not tables_result.is_successful:
                logging.warning(f"Failed to find tables for schema '{effective_schema_name}'. Skipping.")
                continue

            table_details = [
                self._get_table_details(
                    driver_module,
                    current_db_info,
                    effective_schema_name,
                    table_name,
                    connect_kwargs,
                    repository,
                )
                for table_name in tables_result.tables
            ]

            if table_details:
                schema_details.append(SchemaDetail(schema_name=schema_name, tables=table_details))

        if schema_details:
            return DBDetail(db_name=db_name, db_type=db_info.type, schemas=schema_details)

        return None

    def _get_schemas_to_scan(
        self,
        db_info: AllDBProfileInfo,
        repository: UserDbRepository,
        driver_module: Any,
        connect_kwargs: dict[str, Any],
    ) -> set[str]:
        """어노테이션을 위해 스캔할 스키마 목록을 결정합니다."""
        schemas_to_scan = set()
        if db_info.type.lower() == "oracle":
            if not db_info.username:
                logging.error("Oracle profile is missing a username, cannot determine schema.")
                raise APIException(CommonCode.FAIL_FIND_SCHEMAS)
            schemas_to_scan.add(db_info.username)
            logging.info(f"Oracle DB detected. Limiting schema scan to user: {db_info.username}")
        else:
            logging.info(f"'{db_info.type}' DB detected. Fetching all available schemas.")
            schemas_result = repository.find_schemas(
                driver_module, self._get_schema_query(db_info.type), **connect_kwargs
            )
            if schemas_result.is_successful and schemas_result.schemas:
                schemas_to_scan.update(schemas_result.schemas)
            else:
                logging.warning("Could not retrieve schema list. Falling back to username if available.")
            if db_info.username:
                schemas_to_scan.add(db_info.username)
        logging.info(f"Final schemas to scan: {list(schemas_to_scan)}")
        return schemas_to_scan

    def _get_table_details(
        self,
        driver_module: Any,
        db_info: AllDBProfileInfo,
        schema_name: str,
        table_name: str,
        connect_kwargs: dict[str, Any],
        repository: UserDbRepository,
    ) -> TableInfo:
        """단일 테이블의 상세 정보(컬럼, 제약조건, 인덱스)를 조회합니다."""
        logging.info(f"Fetching details for table: {schema_name}.{table_name}")
        columns_result = repository.find_columns(
            driver_module, self._get_column_query(db_info.type), schema_name, db_info.type, table_name, **connect_kwargs
        )
        try:
            constraints = repository.find_constraints(
                driver_module, db_info.type, schema_name, table_name, **connect_kwargs
            )
        except (sqlite3.Error, self._get_driver_module(db_info.type).DatabaseError) as e:
            logging.error(f"Error finding constraints for {schema_name}.{table_name}: {e}", exc_info=True)
            raise APIException(CommonCode.FAIL_FIND_CONSTRAINTS) from e
        try:
            indexes = repository.find_indexes(driver_module, db_info.type, schema_name, table_name, **connect_kwargs)
        except (sqlite3.Error, self._get_driver_module(db_info.type).DatabaseError) as e:
            raise APIException(CommonCode.FAIL_FIND_INDEXES) from e

        table_info = TableInfo(
            name=table_name,
            columns=columns_result.columns if columns_result.is_successful else [],
            constraints=constraints,
            indexes=indexes,
            comment=None,
        )
        logging.info(
            f"Successfully fetched details for {schema_name}.{table_name}. "
            f"Columns: {len(table_info.columns)}, "
            f"Constraints: {len(table_info.constraints)}, "
            f"Indexes: {len(table_info.indexes)}"
        )
        return table_info

    def get_sample_rows(
        self, db_info: AllDBProfileInfo, table_infos: list[TableInfo], repository: UserDbRepository = user_db_repository
    ) -> dict[str, list[dict[str, Any]]]:
        """
        테이블 정보 목록을 받아 각 테이블의 샘플 데이터를 조회하여 반환합니다.
        """
        try:
            if not table_infos:
                return {}

            driver_module = self._get_driver_module(db_info.type)
            connect_kwargs = self._prepare_connection_args(db_info)

            schema_name = ""
            if db_info.type == "oracle":
                schema_name = db_info.username  # Oracle은 사용자 이름이 스키마
            elif db_info.type != "sqlite":
                # TODO: PostgreSQL 등 다른 DB는 여러 스키마를 가질 수 있어 리팩토링 필요
                schema_name = db_info.name

            table_names = [table.name for table in table_infos]

            return repository.find_sample_rows(driver_module, db_info.type, schema_name, table_names, **connect_kwargs)
        except Exception as e:
            raise APIException(CommonCode.FAIL_FIND_SAMPLE_ROWS) from e

    def _get_driver_module(self, db_type: str):
        """
        DB 타입에 따라 동적으로 드라이버 모듈을 로드합니다.
        """
        driver_name = DBTypesEnum[db_type.lower()].value
        if driver_name == "sqlite3":
            return sqlite3
        return importlib.import_module(driver_name)

    def _prepare_connection_args(self, db_info: DBProfileInfo, ignore_db_name: bool = False) -> dict[str, Any]:
        """
        DB 타입에 따라 연결에 필요한 매개변수를 딕셔너리로 구성합니다.
        `ignore_db_name` 플래그 추가: 초기 연결 시 특정 DB에 종속되지 않기 위함.
        """
        db_type = db_info.type.lower()

        if db_type == "sqlite":
            return {"database": db_info.name}

        if db_type == "mssql":
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={db_info.host},{db_info.port};"
                f"UID={db_info.username};"
                f"PWD={db_info.password};"
            )
            if db_info.name and not ignore_db_name:
                connection_string += f"DATABASE={db_info.name};"
            return {"connection_string": connection_string}

        kwargs = {"host": db_info.host, "port": db_info.port, "user": db_info.username, "password": db_info.password}

        if db_info.name and not ignore_db_name:
            if db_type == "postgresql":
                kwargs["dbname"] = db_info.name
            elif db_type in ["mysql", "mariadb"]:
                kwargs["database"] = db_info.name
            elif db_type == "oracle":
                kwargs["service_name"] = db_info.name

        return kwargs

    def _get_database_query(self, db_type: str) -> str | None:
        db_type = db_type.lower()
        if db_type == "postgresql":
            return "SELECT datname FROM pg_database WHERE datistemplate = false;"
        elif db_type in ["mysql", "mariadb"]:
            return "SHOW DATABASES;"
        elif db_type == "oracle":
            return "SELECT global_name FROM global_name"
        return None

    def _get_schema_query(self, db_type: str, db_name: str | None = None) -> str | None:
        db_type = db_type.lower()
        if db_type == "postgresql":
            return """
                SELECT schema_name FROM information_schema.schemata
                WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            """
        elif db_type in ["mysql", "mariadb"]:
            # MySQL/MariaDB에서는 스키마가 데이터베이스와 동일하므로, 현재 데이터베이스의 이름을 스키마로 간주합니다.
            # `information_schema.schemata`를 쿼리하여 명시적으로 확인하는 것이 더 정확합니다.
            return f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{db_name}'"
        elif db_type == "oracle":
            return "SELECT username FROM all_users WHERE ORACLE_MAINTAINED = 'N'"
        elif db_type == "sqlite":
            return None  # SQLite는 단일 파일 데이터베이스로, 스키마 개념이 다릅니다. 'main'을 사용합니다.
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
                    SELECT table_name FROM information_schema.tables
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
                SELECT
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    c.column_default,
                    pgd.description AS comment,
                    (
                        SELECT TRUE
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu
                            ON tc.constraint_name = kcu.constraint_name
                            AND tc.table_schema = kcu.table_schema
                        WHERE tc.constraint_type = 'PRIMARY KEY'
                        AND tc.table_schema = c.table_schema
                        AND tc.table_name = c.table_name
                        AND kcu.column_name = c.column_name
                    ) AS is_pk,
                    c.character_maximum_length,
                    c.numeric_precision,
                    c.numeric_scale
                FROM
                    information_schema.columns c
                LEFT JOIN
                    pg_catalog.pg_stat_all_tables st
                    ON c.table_schema = st.schemaname AND c.table_name = st.relname
                LEFT JOIN
                    pg_catalog.pg_description pgd
                    ON pgd.objoid = st.relid AND pgd.objsubid = c.ordinal_position
                WHERE
                    c.table_schema = %s AND c.table_name = %s
                ORDER BY
                    c.ordinal_position;
            """
        elif db_type in ["mysql", "mariadb"]:
            return """
                SELECT column_name, data_type, is_nullable, column_default, table_name, table_schema
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
            """
        elif db_type == "oracle":
            return "SELECT column_name FROM user_tab_columns WHERE table_name = :table"
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
