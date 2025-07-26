# app/schemas/driver_schemas.py
from enum import Enum

from pydantic import BaseModel


class DriverEnum(str, Enum):
    postgresql = ("postgresql", "psycopg2")
    mysql = ("mysql", "mysql.connector")
    sqlite = ("sqlite", "sqlite3")
    oracle = ("oracle", "cx_Oracle")
    sqlserver = ("sqlserver", "pyodbc")
    mariadb = ("mariadb", "pymysql")

    def __new__(cls, db_type, module):
        obj = str.__new__(cls, db_type)
        obj._value_ = db_type  # 초기 유효성 검사 값
        obj.driver_module = module  # db_type에 맞는 드라이버
        return obj


class DriverInfo(BaseModel):
    db_type: str
    is_installed: bool
    driver_name: str | None
    driver_version: str | None
    driver_size_bytes: int | None


class DriverInfoResponse(BaseModel):
    message: str
    data: DriverInfo | None = None

    @classmethod
    def success(cls, value: DriverInfo):
        return cls(message="드라이버 정보를 성공적으로 불러왔습니다.", data=value)

    @classmethod
    def error(cls, e: Exception | None = None):
        if e:
            print(f"[ERROR] {type(e).__name__}: {e}")  # 로그
        return cls(message="드라이버 정보를 가져오지 못했습니다. 다시 시도해주세요.", data=None)
