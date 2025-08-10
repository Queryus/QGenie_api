from typing import Any

import oracledb
import sqlite3

from app.core.status import CommonCode
from app.core.utils import get_db_path
from app.core.exceptions import APIException
from app.schemas.user_db.result_model import (
    DBProfile,
    BasicResult,
    SaveProfileResult,
    AllDBProfileResult,
    SchemaListResult,
    TableListResult,
    ColumnListResult,
    ColumnInfo
)
from app.schemas.user_db.db_profile_model import (
    SaveDBProfile,
    AllDBProfileInfo
)

class UserDbRepository:
    def connection_test(
        self,
        driver_module: Any,
        **kwargs: Any
    ) -> BasicResult:
        """
        DB 드라이버와 연결에 필요한 매개변수들을 받아 연결을 테스트합니다.
        """
        connection = None
        try:
            if driver_module is oracledb:
                if kwargs.get("user").lower() == "sys":
                    kwargs["mode"] = oracledb.AUTH_MODE_SYSDBA
                connection = driver_module.connect(**kwargs)
            # MSSQL과 같이 전체 연결 문자열이 제공된 경우
            elif "connection_string" in kwargs:
                connection = driver_module.connect(kwargs["connection_string"])
            # SQLite와 같이 파일 이름만 필요한 경우
            elif "db_name" in kwargs:
                connection = driver_module.connect(kwargs["db_name"])
            # 그 외 (MySQL, PostgreSQL, Oracle 등) 일반적인 키워드 인자 방식 연결
            else:
                connection = driver_module.connect(**kwargs)

            return BasicResult(is_successful=True, code=CommonCode.SUCCESS_USER_DB_CONNECT_TEST)
        except (AttributeError, driver_module.OperationalError, driver_module.DatabaseError) as e:
            return BasicResult(is_successful=False, code=CommonCode.FAIL_CONNECT_DB)
        except Exception as e:
            return BasicResult(is_successful=False, code=CommonCode.FAIL)
        finally:
            if connection:
                connection.close()

    def save_profile(
        self,
        save_db_info: SaveDBProfile
    ) -> SaveProfileResult:
        """
        DB 드라이버와 연결에 필요한 매개변수들을 받아 연결을 테스트합니다.
        """
        db_path = get_db_path()
        connection = None
        try:
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            profile_dict = save_db_info.model_dump()

            columns_to_insert = {
                key: value for key, value in profile_dict.items() if value is not None
            }

            columns = ", ".join(columns_to_insert.keys())
            placeholders = ", ".join(["?"] * len(columns_to_insert))

            sql = f"INSERT INTO db_profile ({columns}) VALUES ({placeholders})"
            data_to_insert = tuple(columns_to_insert.values())

            cursor.execute(sql, data_to_insert)
            connection.commit()
            name = save_db_info.view_name if save_db_info.view_name else save_db_info.type

            return SaveProfileResult(is_successful=True, code=CommonCode.SUCCESS_SAVE_DB_PROFILE, view_name=name)
        except sqlite3.Error:
            return SaveProfileResult(is_successful=False, code=CommonCode.FAIL_SAVE_PROFILE)
        except Exception:
            return SaveProfileResult(is_successful=False, code=CommonCode.FAIL_SAVE_PROFILE)
        finally:
            if connection:
                connection.close()

    def find_all_profile(
        self
    ) -> AllDBProfileResult:
        """
        모든 DB 연결 정보를 조회합니다.
        """
        db_path = get_db_path()
        connection = None
        try:
            connection = sqlite3.connect(db_path)
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()

            sql = """
            SELECT
                id,
                type,
                host,
                port,
                name,
                username,
                view_name,
                created_at,
                updated_at 
            FROM db_profile
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            profiles = [DBProfile(**row) for row in rows]

            return AllDBProfileResult(is_successful=True, code=CommonCode.SUCCESS_FIND_PROFILE, profiles=profiles)
        except sqlite3.Error:
            return AllDBProfileResult(is_successful=False, code=CommonCode.FAIL_FIND_PROFILE)
        except Exception:
            return AllDBProfileResult(is_successful=False, code=CommonCode.FAIL_FIND_PROFILE)
        finally:
            if connection:
                connection.close()

    def find_profile(
        self,
        profile_id
    ) -> AllDBProfileInfo:
        """
        특정 DB 연결 정보를 조회합니다.
        """
        db_path = get_db_path()
        connection = None
        try:
            connection = sqlite3.connect(db_path)
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()

            sql = """
            SELECT
                id,
                type,
                host,
                port,
                name,
                username,
                password,
                view_name,
                created_at,
                updated_at 
            FROM db_profile
            WHERE id = ?
            """
            cursor.execute(sql, (profile_id,))
            row = cursor.fetchone()

            return AllDBProfileInfo(**dict(row))
        except sqlite3.Error:
            raise APIException(CommonCode.FAIL_FIND_PROFILE)
        except Exception:
            raise APIException(CommonCode.FAIL)
        finally:
            if connection:
                connection.close()

    # ─────────────────────────────
    # 스키마 조회
    # ─────────────────────────────
    def find_schemas(
            self,
            driver_module: Any,
            schema_query: str,
            **kwargs: Any
    ) -> SchemaListResult:
        connection = None
        try:
            connection = self._connect(driver_module, **kwargs)
            cursor = connection.cursor()

            if not schema_query:
                return SchemaListResult(
                    is_successful=True,
                    code=CommonCode.SUCCESS_FIND_SCHEMAS,
                    schemas=["main"]
                )

            cursor.execute(schema_query)
            schemas = [row[0] for row in cursor.fetchall()]

            return SchemaListResult(is_successful=True, code=CommonCode.SUCCESS_FIND_SCHEMAS, schemas=schemas)
        except Exception:
            return SchemaListResult(is_successful=False, code=CommonCode.FAIL_FIND_SCHEMAS, schemas=[])
        finally:
            if connection:
                connection.close()

    # ─────────────────────────────
    # 테이블 조회
    # ─────────────────────────────
    def find_tables(
        self,
        driver_module: Any,
        table_query: str,
        schema_name: str,
        **kwargs: Any
    ) -> TableListResult:
        connection = None
        try:
            connection = self._connect(driver_module, **kwargs)
            cursor = connection.cursor()

            if "%s" in table_query or "?" in table_query:
                cursor.execute(table_query, (schema_name,))
            elif ":owner" in table_query:
                cursor.execute(table_query, {"owner": schema_name})
            else:
                cursor.execute(table_query)

            tables = [row[0] for row in cursor.fetchall()]

            return TableListResult(is_successful=True, code=CommonCode.SUCCESS_FIND_TABLES, tables=tables)
        except Exception:
            return TableListResult(is_successful=False, code=CommonCode.FAIL_FIND_TABLES, tables=[])
        finally:
            if connection:
                connection.close()

    # ─────────────────────────────
    # 컬럼 조회
    # ─────────────────────────────
    def find_columns(
        self,
        driver_module: Any,
        column_query: str,
        schema_name: str,
        db_type,
        table_name: str,
        **kwargs: Any
    ) -> ColumnListResult:
        connection = None
        try:
            connection = self._connect(driver_module, **kwargs)
            cursor = connection.cursor()

            if db_type == "sqlite":
                # SQLite는 PRAGMA를 직접 실행
                pragma_sql = f"PRAGMA table_info('{table_name}')"
                cursor.execute(pragma_sql)
                columns_raw = cursor.fetchall()
                columns = [
                    ColumnInfo(
                        name=c[1],
                        type=c[2],
                        nullable=(c[3] == 0),  # notnull == 0 means nullable
                        default=c[4],
                        comment=None,
                        is_pk=(c[5] == 1)
                    )
                    for c in columns_raw
                ]
            else:
                if "%s" in column_query or "?" in column_query:
                    cursor.execute(column_query, (schema_name, table_name))
                elif ":owner" in column_query and ":table" in column_query:
                    owner_bind = schema_name.upper() if schema_name else schema_name
                    table_bind = table_name.upper() if table_name else table_name
                    try:
                        cursor.execute(column_query, {"owner": owner_bind, "table": table_bind})
                    except Exception:
                        # fallback: try positional binds (:1, :2) if named binds fail
                        try:
                            pos_query = column_query.replace(":owner", ":1").replace(":table", ":2")
                            cursor.execute(pos_query, [owner_bind, table_bind])
                        except Exception:
                            # re-raise to be handled by outer exception handler
                            raise
                else:
                    cursor.execute(column_query)

                columns = [
                    ColumnInfo(
                        name=c[0],
                        type=c[1],
                        nullable=(c[2] in ["YES", "Y", True]),
                        default=c[3],
                        comment=c[4] if len(c) > 4 else None,
                        is_pk=(c[5] in ["PRI", True] if len(c) > 5 else False)
                    )
                    for c in cursor.fetchall()
                ]

            return ColumnListResult(is_successful=True, code=CommonCode.SUCCESS_FIND_COLUMNS, columns=columns)
        except Exception:
            return ColumnListResult(is_successful=False, code=CommonCode.FAIL_FIND_COLUMNS, columns=[])
        finally:
            if connection:
                connection.close()

    # ─────────────────────────────
    # DB 연결 메서드
    # ─────────────────────────────
    def _connect(self, driver_module: Any, **kwargs):
        if driver_module is oracledb:
            if kwargs.get("user", "").lower() == "sys":
                kwargs["mode"] = oracledb.AUTH_MODE_SYSDBA
            return driver_module.connect(**kwargs)
        elif "connection_string" in kwargs:
            return driver_module.connect(kwargs["connection_string"])
        elif "db_name" in kwargs:
            return driver_module.connect(kwargs["db_name"])
        else:
            return driver_module.connect(**kwargs)

user_db_repository = UserDbRepository()
