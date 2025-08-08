# app/service/driver_service.py

import importlib
import sqlite3
from typing import Any

from fastapi import Depends

from app.core.enum.db_driver import DBTypesEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.repository.user_db_repository import UserDbRepository, user_db_repository
from app.schemas.user_db.result_model import BasicResult, SaveProfileResult
from app.schemas.user_db.db_profile_model import DBProfileInfo, SaveDBProfile
from app.core.utils import generate_prefixed_uuid
from app.core.enum.db_key_prefix_name import DBSaveIdEnum

user_db_repository_dependency = Depends(lambda: user_db_repository)


class UserDbService:
    def connection_test(
        self,
        db_info: DBProfileInfo,
        repository: UserDbRepository = user_db_repository
    ) -> BasicResult:
        """
        DB 연결 정보를 받아 연결 테스트를 수행하고 결과를 객체로 반환합니다.
        """
        try:
            driver_module = self._get_driver_module(db_info.type)
            connect_kwargs = self._prepare_connection_args(db_info)
            return repository.connection_test(driver_module, **connect_kwargs)
        except Exception as e:
            raise APIException(CommonCode.FAIL) from e

    def save_profile(
        self,
        save_db_info: SaveDBProfile,
        repository: UserDbRepository = user_db_repository
    ) -> SaveProfileResult:
        """
        DB 연결 정보를 저장 후 결과를 객체로 반환합니다.
        """
        save_db_info.id = generate_prefixed_uuid(DBSaveIdEnum.user_db.value)
        try:
            return repository.save_profile(save_db_info)
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


user_db_service = UserDbService()
