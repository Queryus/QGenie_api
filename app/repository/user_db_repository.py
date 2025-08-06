from typing import Any

import oracledb

from app.core.status import CommonCode
from app.schemas.user_db.connect_test_result_model import TestConnectionResult


class UserDbRepository:
    def test_db_connection(self, driver_module: Any, **kwargs: Any) -> TestConnectionResult:
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

            return TestConnectionResult(is_successful=True, code=CommonCode.SUCCESS_USER_DB_CONNECT_TEST)

        except Exception:
            return TestConnectionResult(is_successful=False, code=CommonCode.FAIL_CONNECT_DB)
        finally:
            if connection:
                connection.close()


user_db_repository = UserDbRepository()
