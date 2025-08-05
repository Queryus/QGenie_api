# app/service/driver_service.py
import importlib
import os
import sqlite3
from typing import Any

from app.core.enum.db_driver import DBTypesEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.repository.connect_db_repository import test_db_connection
from app.schemas.db_profile_model import DBProfileCreate
from app.schemas.driver_info import DriverInfo
from app.schemas.view.connection_result_model import TestConnectionResult


class DriverService:
    def read_driver_info(self, driver_info: DriverInfo):
        try:
            driver_name = driver_info.driver_name

            if driver_name == "sqlite3":
                version = sqlite3.sqlite_version
                path = sqlite3.__file__

            else:
                mod = importlib.import_module(driver_name)
                version = getattr(mod, "__version__", None)
                path = getattr(mod.__spec__, "origin", None)

            size = os.path.getsize(path) if path else None
            return driver_info.update_from_module(version, size)
        except (ModuleNotFoundError, AttributeError, OSError) as e:
            raise APIException(CommonCode.FAIL) from e

    def test_connection(self, db_info: DBProfileCreate) -> TestConnectionResult:
        """
        DB 연결 정보를 받아 연결 테스트를 수행하고 결과를 객체로 반환합니다.
        """
        try:
            driver_module = self._get_driver_module(db_info.type)
            connect_kwargs = self._prepare_connection_args(db_info)
            return test_db_connection(driver_module, **connect_kwargs)
        except (ValueError, ImportError) as e:
            raise APIException(CommonCode.FAIL) from e

    def _get_driver_module(self, db_type: str):
        """
        DB 타입에 따라 동적으로 드라이버 모듈을 로드합니다.
        """
        try:
            driver_name = DBTypesEnum[db_type.lower()].value
        except KeyError as e:
            raise ValueError(f"지원하지 않는 DB 타입입니다: {db_type}") from e

        if driver_name == "sqlite3":
            return sqlite3

        return importlib.import_module(driver_name)

    def _prepare_connection_args(self, db_info: DBProfileCreate) -> dict[str, Any]:
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


driver_service = DriverService()
