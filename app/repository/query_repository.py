import sqlite3
from typing import Any

import oracledb

from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.core.utils import get_db_path
from app.schemas.query.result_model import (
    BasicResult,
    ExecutionResult,
    ExecutionSelectResult,
    InsertLocalDBResult,
    QueryTestResult,
    SelectQueryHistoryResult,
)


class QueryRepository:
    def execution(
        self,
        query: str,
        driver_module: Any,
        **kwargs: Any,
    ) -> ExecutionSelectResult | ExecutionResult | BasicResult:
        """
        쿼리 수행합니다.
        """
        connection = None
        try:
            connection = self._connect(driver_module, **kwargs)
            cursor = connection.cursor()

            cursor.execute(query)

            if self._is_select_query(query):
                rows = cursor.fetchall()

                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    data = [dict(zip(columns, row, strict=False)) for row in rows]
                else:
                    columns = []
                    data = []
                result = {"columns": columns, "data": data}

                return ExecutionSelectResult(is_successful=True, code=CommonCode.SUCCESS_EXECUTION, data=result)

            connection.commit()
            return ExecutionResult(is_successful=True, code=CommonCode.SUCCESS_EXECUTION, data=cursor.rowcount)
        except (AttributeError, driver_module.OperationalError, driver_module.DatabaseError):
            return BasicResult(is_successful=False, code=CommonCode.FAIL_CONNECT_DB)
        except Exception:
            return BasicResult(is_successful=False, code=CommonCode.FAIL)
        finally:
            if connection:
                connection.close()

    def execution_test(
        self,
        query: str,
        driver_module: Any,
        **kwargs: Any,
    ) -> QueryTestResult:
        """
        쿼리가 문법적으로 유효한지 테스트합니다.
        실제 데이터는 변경되지 않습니다. (모든 작업은 롤백됩니다).
        """
        connection = None
        try:
            connection = self._connect(driver_module, **kwargs)
            cursor = connection.cursor()
            cursor.execute(query)

            if not self._is_select_query(query):
                return QueryTestResult(is_successful=True, code=CommonCode.SUCCESS_EXECUTION_TEST, data=True)

            rows = cursor.fetchall()
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                data = [dict(zip(columns, row, strict=False)) for row in rows]
            else:
                columns = []
                data = []

            result = {"columns": columns, "data": data}
            return QueryTestResult(is_successful=True, code=CommonCode.SUCCESS_EXECUTION, data=result)
        except (AttributeError, driver_module.OperationalError, driver_module.DatabaseError) as e:
            return QueryTestResult(is_successful=False, code=CommonCode.FAIL_CONNECT_DB, data=str(e))
        except Exception as e:
            return QueryTestResult(is_successful=False, code=CommonCode.FAIL, data=str(e))
        finally:
            if connection:
                connection.rollback()
                connection.close()

    def create_query_history(
        self,
        sql: str,
        data: tuple,
        query: str,
    ) -> InsertLocalDBResult:
        """
        쿼리 실행 결과를 저장합니다.
        """
        db_path = get_db_path()
        connection = None
        try:
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute(sql, data)
            connection.commit()

            return ExecutionResult(is_successful=True, code=CommonCode.SUCCESS_EXECUTION, data=query)
        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL_CONNECT_DB) from e
        except Exception as e:
            raise APIException(CommonCode.FAIL_CREATE_QUERY) from e
        finally:
            if connection:
                connection.close()

    def find_query_history(self, chat_tab_id: int) -> SelectQueryHistoryResult:
        """
        전달받은 쿼리를 실행하여 모든 DB 연결 정보를 조회합니다.
        """
        db_path = get_db_path()
        connection = None
        try:
            connection = sqlite3.connect(db_path)
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()

            sql = """
                SELECT qh.*
                FROM query_history AS qh
                LEFT JOIN chat_message AS cm ON qh.chat_message_id = cm.id
                WHERE cm.chat_tab_id = ?
                ORDER BY qh.created_at DESC
                LIMIT 5;
            """
            data = (chat_tab_id,)

            cursor.execute(sql, data)
            rows = cursor.fetchall()

            columns = [desc[0] for desc in cursor.description]
            data = [dict(zip(columns, row, strict=False)) for row in rows]
            result = {"columns": columns, "data": data}

            return SelectQueryHistoryResult(is_successful=True, code=CommonCode.SUCCESS_FIND_QUERY_HISTORY, data=result)
        except sqlite3.Error:
            return SelectQueryHistoryResult(is_successful=False, code=CommonCode.FAIL_CONNECT_DB)
        except Exception:
            return SelectQueryHistoryResult(is_successful=False, code=CommonCode.FAIL)
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

    def _is_select_query(self, query_text: str) -> bool:
        for stmt in query_text.split(";"):
            cleaned_stmt = stmt.strip().lower()
            if cleaned_stmt and not cleaned_stmt.startswith("--") and cleaned_stmt.startswith("select"):
                return True
        return False


query_repository = QueryRepository()
