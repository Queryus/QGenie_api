import logging
import sqlite3
from typing import Any

import oracledb

from app.core.enum.db_driver import DBTypesEnum
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
                raise APIException(CommonCode.NO_DB_PROFILE_FOUND)
            return AllDBProfileInfo(**dict(row))
        except APIException:
            raise
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
                cursor.execute(table_query, {"owner": schema_name.upper()})
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

            columns = []
            db_type_lower = db_type.lower()

            if db_type_lower == DBTypesEnum.sqlite.name:
                columns = self._find_columns_for_sqlite(cursor, table_name)
            elif db_type_lower == DBTypesEnum.postgresql.name:
                columns = self._find_columns_for_postgresql(cursor, schema_name, table_name)
            elif db_type_lower == DBTypesEnum.oracle.name:
                columns = self._find_columns_for_oracle(cursor, schema_name, table_name)
            elif db_type_lower == DBTypesEnum.mysql.name:
                pass
            elif db_type_lower == DBTypesEnum.mariadb.name:
                pass

            else:
                columns = self._find_columns_for_general(cursor, column_query, schema_name, table_name)

            return ColumnListResult(is_successful=True, code=CommonCode.SUCCESS_FIND_COLUMNS, columns=columns)
        except Exception as e:
            logging.error(f"Exception in find_columns for {schema_name}.{table_name}: {e}", exc_info=True)
            return ColumnListResult(is_successful=False, code=CommonCode.FAIL_FIND_COLUMNS, columns=[])
        finally:
            if connection:
                connection.close()

    def _find_columns_for_sqlite(self, cursor: Any, table_name: str) -> list[ColumnInfo]:
        pragma_sql = f"PRAGMA table_info('{table_name}')"
        cursor.execute(pragma_sql)
        columns_raw = cursor.fetchall()
        # SQLite는 pragma에서 순서(cid)를 반환하지만, ordinal_position은 1부터 시작하는 표준이므로 +1
        return [
            ColumnInfo(
                name=c[1],
                type=c[2],
                nullable=(c[3] == 0),
                default=c[4],
                comment=None,
                is_pk=(c[5] == 1),
                ordinal_position=c[0] + 1,
            )
            for c in columns_raw
        ]

    def _find_columns_for_postgresql(self, cursor: Any, schema_name: str, table_name: str) -> list[ColumnInfo]:
        sql = """
            SELECT
                c.column_name,
                c.udt_name,
                c.is_nullable,
                c.column_default,
                c.ordinal_position,
                (SELECT pg_catalog.col_description(cls.oid, c.dtd_identifier::int)
                 FROM pg_catalog.pg_class cls
                 JOIN pg_catalog.pg_namespace n ON n.oid = cls.relnamespace
                 WHERE cls.relname = c.table_name AND n.nspname = c.table_schema) as comment,
                CASE WHEN kcu.column_name IS NOT NULL THEN TRUE ELSE FALSE END as is_pk
            FROM
                information_schema.columns c
            LEFT JOIN information_schema.key_column_usage kcu
                ON c.table_schema = kcu.table_schema
                AND c.table_name = kcu.table_name
                AND c.column_name = kcu.column_name
                AND kcu.constraint_name IN (
                    SELECT constraint_name
                    FROM information_schema.table_constraints
                    WHERE table_schema = %s
                      AND table_name = %s
                      AND constraint_type = 'PRIMARY KEY'
                )
            WHERE
                c.table_schema = %s AND c.table_name = %s
            ORDER BY
                c.ordinal_position;
        """
        cursor.execute(sql, (schema_name, table_name, schema_name, table_name))
        columns_raw = cursor.fetchall()
        return [
            ColumnInfo(
                name=c[0],
                type=c[1],
                nullable=(c[2] == "YES"),
                default=c[3],
                ordinal_position=c[4],
                comment=c[5],
                is_pk=c[6],
            )
            for c in columns_raw
        ]

    def _find_columns_for_oracle(self, cursor: Any, schema_name: str, table_name: str) -> list[ColumnInfo]:
        sql = """
            SELECT
                c.column_name,
                c.data_type,
                c.nullable,
                c.data_default,
                cc.comments,
                CASE WHEN cons.constraint_type = 'P' THEN 1 ELSE 0 END AS is_pk,
                c.data_length,
                c.data_precision,
                c.data_scale,
                c.column_id as ordinal_position
            FROM
                all_tab_columns c
            LEFT JOIN
                all_col_comments cc ON c.owner = cc.owner AND c.table_name = cc.table_name AND c.column_name = cc.column_name
            LEFT JOIN
                (
                    SELECT
                        acc.owner,
                        acc.table_name,
                        acc.column_name,
                        ac.constraint_type
                    FROM
                        all_constraints ac
                    JOIN
                        all_cons_columns acc ON ac.owner = acc.owner AND ac.constraint_name = acc.constraint_name
                    WHERE
                        ac.constraint_type = 'P'
                ) cons ON c.owner = cons.owner AND c.table_name = cons.table_name AND c.column_name = cons.column_name
            WHERE
                c.owner = :owner AND c.table_name = :table_name
            ORDER BY
                c.column_id
        """
        try:
            logging.info(f"Executing find_columns_for_oracle for table: {schema_name.upper()}.{table_name.upper()}")
            cursor.execute(sql, {"owner": schema_name.upper(), "table_name": table_name.upper()})
            columns_raw = cursor.fetchall()
            logging.info(f"Found {len(columns_raw)} raw columns for table: {table_name.upper()}")

            columns = []
            for c in columns_raw:
                (
                    name,
                    data_type,
                    nullable,
                    default,
                    comment,
                    is_pk,
                    length,
                    precision,
                    scale,
                    ordinal_position,
                ) = c

                if data_type in ["VARCHAR2", "NVARCHAR2", "CHAR", "RAW"]:
                    full_type = f"{data_type}({length})"
                elif data_type == "NUMBER":
                    if precision is not None and scale is not None:
                        if precision == 38 and scale == 0:
                            full_type = "NUMBER"
                        else:
                            full_type = f"NUMBER({precision}, {scale})"
                    elif precision is not None:
                        full_type = f"NUMBER({precision})"
                    else:
                        full_type = "NUMBER"
                else:
                    full_type = data_type

                columns.append(
                    ColumnInfo(
                        name=name,
                        type=full_type,
                        nullable=(nullable == "Y"),
                        default=str(default).strip() if default is not None else None,
                        comment=comment,
                        is_pk=bool(is_pk),
                        ordinal_position=ordinal_position,
                    )
                )
            return columns
        except Exception as e:
            logging.error(f"Error in _find_columns_for_oracle for table {table_name}: {e}", exc_info=True)
            return []

    def _find_columns_for_general(
        self, cursor: Any, column_query: str, schema_name: str, table_name: str
    ) -> list[ColumnInfo]:
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

        columns = []
        for c in cursor.fetchall():
            data_type = c[1]
            if c[6] is not None:
                data_type = f"{data_type}({c[6]})"
            elif c[7] is not None and c[8] is not None:
                data_type = f"{data_type}({c[7]}, {c[8]})"

            columns.append(
                ColumnInfo(
                    name=c[0],
                    type=data_type,
                    nullable=(c[2] in ["YES", "Y", True]),
                    default=c[3],
                    comment=c[4] if len(c) > 4 else None,
                    is_pk=(c[5] in ["PRI", True] if len(c) > 5 else False),
                )
            )
        return columns

    def find_constraints(
        self, driver_module: Any, db_type: str, schema_name: str, table_name: str, **kwargs: Any
    ) -> list[ConstraintInfo]:
        """
        테이블의 제약 조건 정보를 조회합니다.
        - SQLite, PostgreSQL, Oracle을 지원합니다.
        - 실패 시 DB 드라이버의 예외를 직접 발생시킵니다.
        """
        connection = None
        try:
            connection = self._connect(driver_module, **kwargs)
            cursor = connection.cursor()
            db_type_lower = db_type.lower()

            if db_type_lower == DBTypesEnum.sqlite.name:
                return self._find_constraints_for_sqlite(cursor, table_name)
            elif db_type_lower == DBTypesEnum.postgresql.name:
                return self._find_constraints_for_postgresql(cursor, schema_name, table_name)
            elif db_type_lower == DBTypesEnum.oracle.name:
                return self._find_constraints_for_oracle(cursor, schema_name, table_name)
            return []
        finally:
            if connection:
                connection.close()

    def _find_constraints_for_sqlite(self, cursor: Any, table_name: str) -> list[ConstraintInfo]:
        constraints = []
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
        return constraints

    def _find_constraints_for_postgresql(self, cursor: Any, schema_name: str, table_name: str) -> list[ConstraintInfo]:
        sql = """
            SELECT
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name,
                rc.update_rule,
                rc.delete_rule,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                chk.check_clause
            FROM
                information_schema.table_constraints tc
            LEFT JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema AND tc.table_name = kcu.table_name
            LEFT JOIN information_schema.referential_constraints rc
                ON tc.constraint_name = rc.constraint_name AND tc.table_schema = rc.constraint_schema
            LEFT JOIN information_schema.constraint_column_usage ccu
                ON rc.unique_constraint_name = ccu.constraint_name AND rc.unique_constraint_schema = ccu.table_schema
            LEFT JOIN information_schema.check_constraints chk
                ON tc.constraint_name = chk.constraint_name AND tc.table_schema = chk.constraint_schema
            WHERE
                tc.table_schema = %s AND tc.table_name = %s;
        """
        cursor.execute(sql, (schema_name, table_name))
        raw_constraints = cursor.fetchall()

        constraint_map = {}
        for row in raw_constraints:
            # Filter out 'NOT NULL' constraints which are handled by `is_nullable` in column info
            const_type = row[1]
            check_clause = row[7]
            if const_type == "CHECK" and check_clause and "IS NOT NULL" in check_clause.upper():
                continue

            (name, _, column, on_update, on_delete, ref_table, ref_column, check_expr) = row
            if name not in constraint_map:
                constraint_map[name] = {
                    "type": const_type,
                    "columns": [],
                    "referenced_table": ref_table,
                    "referenced_columns": [],
                    "check_expression": check_expr,
                    "on_update": on_update,
                    "on_delete": on_delete,
                }
            if column and column not in constraint_map[name]["columns"]:
                constraint_map[name]["columns"].append(column)
            if ref_column and ref_column not in constraint_map[name]["referenced_columns"]:
                constraint_map[name]["referenced_columns"].append(ref_column)

        return [
            ConstraintInfo(
                name=name,
                type=data["type"],
                columns=data["columns"],
                referenced_table=data["referenced_table"],
                referenced_columns=data["referenced_columns"] if data["referenced_columns"] else None,
                check_expression=data["check_expression"],
                on_update=data["on_update"],
                on_delete=data["on_delete"],
            )
            for name, data in constraint_map.items()
        ]

    def _find_constraints_for_oracle(self, cursor: Any, schema_name: str, table_name: str) -> list[ConstraintInfo]:
        sql = """
            SELECT
                ac.constraint_name,
                ac.constraint_type,
                acc.column_name,
                ac.search_condition,
                r_ac.table_name AS referenced_table,
                r_acc.column_name AS referenced_column,
                ac.delete_rule
            FROM
                all_constraints ac
            JOIN
                all_cons_columns acc ON ac.owner = acc.owner AND ac.constraint_name = acc.constraint_name AND ac.table_name = acc.table_name
            LEFT JOIN
                all_constraints r_ac ON ac.r_owner = r_ac.owner AND ac.r_constraint_name = r_ac.constraint_name
            LEFT JOIN
                all_cons_columns r_acc ON ac.r_owner = r_acc.owner AND ac.r_constraint_name = r_acc.constraint_name AND acc.position = r_acc.position
            WHERE
                ac.owner = :owner AND ac.table_name = :table_name
            ORDER BY
                ac.constraint_name, acc.position
        """
        try:
            logging.info(f"Executing find_constraints_for_oracle for table: {schema_name.upper()}.{table_name.upper()}")
            cursor.execute(sql, {"owner": schema_name.upper(), "table_name": table_name.upper()})
            raw_constraints = cursor.fetchall()
            logging.info(f"Found {len(raw_constraints)} raw constraints for table: {table_name.upper()}")

            constraint_map = {}
            for row in raw_constraints:
                name, const_type_char, column, check_expr, ref_table, ref_column, on_delete = row

                const_type_map = {"P": "PRIMARY KEY", "R": "FOREIGN KEY", "U": "UNIQUE", "C": "CHECK"}
                const_type = const_type_map.get(const_type_char)

                if not const_type:
                    continue

                if const_type == "CHECK":
                    check_expr_str = (str(check_expr) if check_expr else "").upper()
                    # "COL" IS NOT NULL 또는 COL IS NOT NULL 형식 모두 처리
                    if (
                        f'"{column.upper()}" IS NOT NULL' in check_expr_str
                        or f"{column.upper()} IS NOT NULL" in check_expr_str
                    ):
                        continue

                if name not in constraint_map:
                    constraint_map[name] = {
                        "type": const_type,
                        "columns": [],
                        "referenced_table": ref_table,
                        "referenced_columns": [],
                        "check_expression": check_expr if const_type == "CHECK" else None,
                        "on_delete": on_delete if const_type == "FOREIGN KEY" else None,
                    }

                if column and column not in constraint_map[name]["columns"]:
                    constraint_map[name]["columns"].append(column)
                if ref_column and ref_column not in constraint_map[name]["referenced_columns"]:
                    constraint_map[name]["referenced_columns"].append(ref_column)

            return [
                ConstraintInfo(
                    name=name,
                    type=data["type"],
                    columns=data["columns"],
                    referenced_table=data["referenced_table"],
                    referenced_columns=data["referenced_columns"] if data["referenced_columns"] else None,
                    check_expression=data["check_expression"],
                    on_delete=data["on_delete"],
                )
                for name, data in constraint_map.items()
            ]
        except Exception as e:
            logging.error(f"Error in _find_constraints_for_oracle for table {table_name}: {e}", exc_info=True)
            return []

    def find_indexes(
        self, driver_module: Any, db_type: str, schema_name: str, table_name: str, **kwargs: Any
    ) -> list[IndexInfo]:
        """
        테이블의 인덱스 정보를 조회합니다.
        - 실패 시 DB 드라이버의 예외를 직접 발생시킵니다.
        """
        connection = None
        try:
            connection = self._connect(driver_module, **kwargs)
            cursor = connection.cursor()
            db_type_lower = db_type.lower()

            if db_type_lower == DBTypesEnum.sqlite.name:
                return self._find_indexes_for_sqlite(cursor, table_name)
            elif db_type_lower == DBTypesEnum.postgresql.name:
                return self._find_indexes_for_postgresql(cursor, schema_name, table_name)
            elif db_type_lower == DBTypesEnum.oracle.name:
                return self._find_indexes_for_oracle(cursor, schema_name, table_name)
            return []
        finally:
            if connection:
                connection.close()

    def _find_indexes_for_sqlite(self, cursor: Any, table_name: str) -> list[IndexInfo]:
        indexes = []
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
        return indexes

    def _find_indexes_for_postgresql(self, cursor: Any, schema_name: str, table_name: str) -> list[IndexInfo]:
        sql = """
            SELECT
                i.relname as index_name,
                a.attname as column_name,
                ix.indisunique as is_unique,
                ix.indisprimary as is_primary
            FROM
                pg_class t,
                pg_class i,
                pg_index ix,
                pg_attribute a,
                pg_namespace n
            WHERE
                t.oid = ix.indrelid
                and i.oid = ix.indexrelid
                and a.attrelid = t.oid
                and a.attnum = ANY(ix.indkey)
                and t.relkind = 'r'
                and n.oid = t.relnamespace
                and n.nspname = %s
                and t.relname = %s
            ORDER BY
                i.relname, a.attnum;
        """
        cursor.execute(sql, (schema_name, table_name))
        raw_indexes = cursor.fetchall()

        index_map = {}
        for row in raw_indexes:
            index_name, column_name, is_unique, is_primary = row
            if is_primary:  # Exclude indexes created for PRIMARY KEY constraints
                continue
            if index_name not in index_map:
                index_map[index_name] = {"columns": [], "is_unique": is_unique}
            index_map[index_name]["columns"].append(column_name)

        return [
            IndexInfo(name=name, columns=data["columns"], is_unique=data["is_unique"])
            for name, data in index_map.items()
        ]

    def _find_indexes_for_oracle(self, cursor: Any, schema_name: str, table_name: str) -> list[IndexInfo]:
        sql = """
            SELECT
                i.index_name,
                i.uniqueness,
                ic.column_name
            FROM
                all_indexes i
            JOIN
                all_ind_columns ic ON i.owner = ic.index_owner AND i.index_name = ic.index_name
            LEFT JOIN
                all_constraints ac ON i.owner = ac.owner AND i.index_name = ac.constraint_name AND ac.constraint_type = 'P'
            WHERE
                i.owner = :owner AND i.table_name = :table_name
                AND ac.constraint_name IS NULL
            ORDER BY
                i.index_name, ic.column_position
        """
        try:
            logging.info(f"Executing find_indexes_for_oracle for table: {schema_name.upper()}.{table_name.upper()}")
            cursor.execute(sql, {"owner": schema_name.upper(), "table_name": table_name.upper()})
            raw_indexes = cursor.fetchall()
            logging.info(f"Found {len(raw_indexes)} raw indexes for table: {table_name.upper()}")

            index_map = {}
            for row in raw_indexes:
                index_name, uniqueness, column_name = row
                if index_name not in index_map:
                    index_map[index_name] = {"columns": [], "is_unique": uniqueness == "UNIQUE"}
                index_map[index_name]["columns"].append(column_name)

            return [
                IndexInfo(name=name, columns=data["columns"], is_unique=data["is_unique"])
                for name, data in index_map.items()
            ]
        except Exception:
            # logging.error(f"Error in _find_indexes_for_oracle for table {table_name}: {e}", exc_info=True)
            return []

    def find_sample_rows(
        self, driver_module: Any, db_type: str, schema_name: str, table_names: list[str], **kwargs: Any
    ) -> dict[str, list[dict[str, Any]]]:
        """
        주어진 테이블 목록에 대해 상위 3개의 샘플 행을 조회합니다.
        - 실패 시 DB 드라이버의 예외를 직접 발생시킵니다.
        """
        connection = None
        try:
            connection = self._connect(driver_module, **kwargs)
            cursor = connection.cursor()

            if db_type == DBTypesEnum.sqlite.name:
                return self._find_sample_rows_for_sqlite(cursor, table_names)
            elif db_type == DBTypesEnum.postgresql.name:
                return self._find_sample_rows_for_postgresql(cursor, schema_name, table_names)
            elif db_type == DBTypesEnum.oracle.name:
                return self._find_sample_rows_for_oracle(cursor, schema_name, table_names)
            return {table_name: [] for table_name in table_names}
        finally:
            if connection:
                connection.close()

    def _find_sample_rows_for_sqlite(self, cursor: Any, table_names: list[str]) -> dict[str, list[dict[str, Any]]]:
        sample_rows_map = {}
        for table_name in table_names:
            try:
                # 컬럼명 조회를 위해 PRAGMA 사용
                cursor.execute(f"PRAGMA table_info('{table_name}')")
                columns = [row[1] for row in cursor.fetchall()]

                # 데이터 조회
                cursor.execute(f'SELECT * FROM "{table_name}" LIMIT 3')
                rows = cursor.fetchall()
                sample_rows_map[table_name] = [dict(zip(columns, row, strict=False)) for row in rows]
            except Exception:
                sample_rows_map[table_name] = []  # 오류 발생 시 빈 리스트 할당
        return sample_rows_map

    def _find_sample_rows_for_postgresql(
        self, cursor: Any, schema_name: str, table_names: list[str]
    ) -> dict[str, list[dict[str, Any]]]:
        sample_rows_map = {}
        for table_name in table_names:
            try:
                # PostgreSQL은 cursor.description을 통해 컬럼명을 바로 얻을 수 있음
                cursor.execute(f'SELECT * FROM "{schema_name}"."{table_name}" LIMIT 3')
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                sample_rows_map[table_name] = [dict(zip(columns, row, strict=False)) for row in rows]
            except Exception:
                sample_rows_map[table_name] = []
        return sample_rows_map

    def _find_sample_rows_for_oracle(
        self, cursor: Any, schema_name: str, table_names: list[str]
    ) -> dict[str, list[dict[str, Any]]]:
        sample_rows_map = {}
        for table_name in table_names:
            try:
                query = f'SELECT * FROM "{schema_name.upper()}"."{table_name.upper()}" FETCH FIRST 3 ROWS ONLY'
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                sample_rows_map[table_name] = [dict(zip(columns, row, strict=False)) for row in rows]
            except Exception:
                sample_rows_map[table_name] = []
        return sample_rows_map

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
