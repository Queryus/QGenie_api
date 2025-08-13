import sqlite3
from typing import Any

import oracledb

from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.core.utils import get_db_path
from app.schemas.user_db.db_profile_model import AllDBProfileInfo, UpdateOrCreateDBProfile
from app.schemas.user_db.result_model import (
    AllDBProfileResult,
    BasicResult,
    ChangeProfileResult,
    ColumnInfo,
    ColumnListResult,
    ConstraintInfo,
    DBProfile,
    IndexInfo,
    SchemaListResult,
    TableListResult,
)


class UserDbRepository:
    def connection_test(self, driver_module: Any, **kwargs: Any) -> BasicResult:
        """
        DB 드라이버와 연결에 필요한 매개변수들을 받아 연결을 테스트합니다.
        """
        connection = None
        try:
            connection = self._connect(driver_module, **kwargs)
            return BasicResult(is_successful=True, code=CommonCode.SUCCESS_USER_DB_CONNECT_TEST)
        except (AttributeError, driver_module.OperationalError, driver_module.DatabaseError):
            return BasicResult(is_successful=False, code=CommonCode.FAIL_CONNECT_DB)
        except Exception:
            return BasicResult(is_successful=False, code=CommonCode.FAIL)
        finally:
            if connection:
                connection.close()

    def create_profile(self, sql: str, data: tuple, create_db_info: UpdateOrCreateDBProfile) -> ChangeProfileResult:
        """
        DB 드라이버와 연결에 필요한 매개변수들을 받아 저장합니다.
        """
        db_path = get_db_path()
        connection = None
        try:
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute(sql, data)
            connection.commit()
            name = create_db_info.view_name if create_db_info.view_name else create_db_info.type
            return ChangeProfileResult(is_successful=True, code=CommonCode.SUCCESS_SAVE_PROFILE, view_name=name)
        except sqlite3.Error:
            return ChangeProfileResult(is_successful=False, code=CommonCode.FAIL_SAVE_PROFILE)
        except Exception:
            return ChangeProfileResult(is_successful=False, code=CommonCode.FAIL_SAVE_PROFILE)
        finally:
            if connection:
                connection.close()

    def update_profile(self, sql: str, data: tuple, update_db_info: UpdateOrCreateDBProfile) -> ChangeProfileResult:
        """
        DB 드라이버와 연결에 필요한 매개변수들을 받아 업데이트합니다.
        """
        db_path = get_db_path()
        connection = None
        try:
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute(sql, data)
            connection.commit()
            name = update_db_info.view_name if update_db_info.view_name else update_db_info.type
            return ChangeProfileResult(is_successful=True, code=CommonCode.SUCCESS_UPDATE_PROFILE, view_name=name)
        except sqlite3.Error:
            return ChangeProfileResult(is_successful=False, code=CommonCode.FAIL_UPDATE_PROFILE)
        except Exception:
            return ChangeProfileResult(is_successful=False, code=CommonCode.FAIL_UPDATE_PROFILE)
        finally:
            if connection:
                connection.close()

    def delete_profile(
        self,
        sql: str,
        data: tuple,
        profile_id: str,
    ) -> ChangeProfileResult:
        """
        DB 드라이버와 연결에 필요한 매개변수들을 받아 삭제합니다.
        """
        db_path = get_db_path()
        connection = None
        try:
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute(sql, data)
            connection.commit()
            return ChangeProfileResult(is_successful=True, code=CommonCode.SUCCESS_DELETE_PROFILE, view_name=profile_id)
        except sqlite3.Error:
            return ChangeProfileResult(is_successful=False, code=CommonCode.FAIL_DELETE_PROFILE)
        except Exception:
            return ChangeProfileResult(is_successful=False, code=CommonCode.FAIL_DELETE_PROFILE)
        finally:
            if connection:
                connection.close()

    def find_all_profile(self, sql: str) -> AllDBProfileResult:
        """
        전달받은 쿼리를 실행하여 모든 DB 연결 정보를 조회합니다.
        """
        db_path = get_db_path()
        connection = None
        try:
            connection = sqlite3.connect(db_path)
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
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

    def find_profile(self, sql: str, data: tuple) -> AllDBProfileInfo:
        """
        전달받은 쿼리를 실행하여 특정 DB 연결 정보를 조회합니다.
        """
        db_path = get_db_path()
        connection = None
        try:
            connection = sqlite3.connect(db_path)
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(sql, data)
            row = cursor.fetchone()

            if not row:
                raise APIException(CommonCode.NO_SEARCH_DATA)
            return AllDBProfileInfo(**dict(row))
        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL_FIND_PROFILE) from e
        except Exception as e:
            raise APIException(CommonCode.FAIL) from e
        finally:
            if connection:
                connection.close()

    # ─────────────────────────────
    # 스키마 조회
    # ─────────────────────────────
    def find_schemas(self, driver_module: Any, schema_query: str, **kwargs: Any) -> SchemaListResult:
        connection = None
        try:
            connection = self._connect(driver_module, **kwargs)
            cursor = connection.cursor()

            if not schema_query:
                return SchemaListResult(is_successful=True, code=CommonCode.SUCCESS_FIND_SCHEMAS, schemas=["main"])

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
    def find_tables(self, driver_module: Any, table_query: str, schema_name: str, **kwargs: Any) -> TableListResult:
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
        self, driver_module: Any, column_query: str, schema_name: str, db_type, table_name: str, **kwargs: Any
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
                        is_pk=(c[5] == 1),
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
                        try:
                            pos_query = column_query.replace(":owner", ":1").replace(":table", ":2")
                            cursor.execute(pos_query, [owner_bind, table_bind])
                        except Exception as e:
                            raise APIException(CommonCode.FAIL) from e
                else:
                    cursor.execute(column_query)

                columns = [
                    ColumnInfo(
                        name=c[0],
                        type=c[1],
                        nullable=(c[2] in ["YES", "Y", True]),
                        default=c[3],
                        comment=c[4] if len(c) > 4 else None,
                        is_pk=(c[5] in ["PRI", True] if len(c) > 5 else False),
                    )
                    for c in cursor.fetchall()
                ]

            return ColumnListResult(is_successful=True, code=CommonCode.SUCCESS_FIND_COLUMNS, columns=columns)
        except Exception:
            return ColumnListResult(is_successful=False, code=CommonCode.FAIL_FIND_COLUMNS, columns=[])
        finally:
            if connection:
                connection.close()

    def find_constraints(
        self, driver_module: Any, db_type: str, table_name: str, **kwargs: Any
    ) -> list[ConstraintInfo]:
        """
        테이블의 제약 조건 정보를 조회합니다.
        - 현재는 SQLite만 지원합니다.
        - 실패 시 DB 드라이버의 예외를 직접 발생시킵니다.
        """
        connection = None
        try:
            connection = self._connect(driver_module, **kwargs)
            cursor = connection.cursor()
            constraints = []

            if db_type == "sqlite":
                # Foreign Key 제약 조건 조회
                fk_list_sql = f"PRAGMA foreign_key_list('{table_name}')"
                cursor.execute(fk_list_sql)
                fks = cursor.fetchall()

                # Foreign Key 정보를 그룹화
                fk_groups = {}
                for fk in fks:
                    fk_id = fk[0]
                    if fk_id not in fk_groups:
                        fk_groups[fk_id] = {"referenced_table": fk[2], "columns": [], "referenced_columns": []}
                    fk_groups[fk_id]["columns"].append(fk[3])
                    fk_groups[fk_id]["referenced_columns"].append(fk[4])

                for _, group in fk_groups.items():
                    constraints.append(
                        ConstraintInfo(
                            name=f"fk_{table_name}_{'_'.join(group['columns'])}",
                            type="FOREIGN KEY",
                            columns=group["columns"],
                            referenced_table=group["referenced_table"],
                            referenced_columns=group["referenced_columns"],
                        )
                    )

            # 다른 DB 타입에 대한 제약 조건 조회 로직 추가 가능
            # elif db_type == "postgresql": ...

            return constraints
        finally:
            if connection:
                connection.close()

    def find_indexes(self, driver_module: Any, db_type: str, table_name: str, **kwargs: Any) -> list[IndexInfo]:
        """
        테이블의 인덱스 정보를 조회합니다.
        - 현재는 SQLite만 지원합니다.
        - 실패 시 DB 드라이버의 예외를 직접 발생시킵니다.
        """
        connection = None
        try:
            connection = self._connect(driver_module, **kwargs)
            cursor = connection.cursor()
            indexes = []

            if db_type == "sqlite":
                index_list_sql = f"PRAGMA index_list('{table_name}')"
                cursor.execute(index_list_sql)
                raw_indexes = cursor.fetchall()

                for idx in raw_indexes:
                    index_name = idx[1]
                    is_unique = idx[2] == 1

                    # "sqlite_autoindex_"로 시작하는 인덱스는 PK에 의해 자동 생성된 것이므로 제외
                    if index_name.startswith("sqlite_autoindex_"):
                        continue

                    index_info_sql = f"PRAGMA index_info('{index_name}')"
                    cursor.execute(index_info_sql)
                    index_columns = [row[2] for row in cursor.fetchall()]

                    if index_columns:
                        indexes.append(IndexInfo(name=index_name, columns=index_columns, is_unique=is_unique))

            # 다른 DB 타입에 대한 인덱스 조회 로직 추가 가능
            # elif db_type == "postgresql": ...

            return indexes
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
