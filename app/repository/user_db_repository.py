from typing import Any

import oracledb
import sqlite3

from app.core.status import CommonCode
from app.schemas.user_db.result_model import BasicResult, SaveProfileResult
from app.schemas.user_db.db_profile_model import SaveDBProfile
from app.core.utils import get_db_path

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

user_db_repository = UserDbRepository()
