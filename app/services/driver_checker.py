import importlib.util
import os

from app.schemas.db_driver_info import DBDriverInfo

DRIVER_MAP = {
    "postgresql": "psycopg2",
    "mysql": "pymysql",
    "sqlite": "sqlite3",
    "oracle": "cx_Oracle",
    "sqlserver": "pyodbc",
}


def check_driver(driver_id: str) -> DBDriverInfo:
    module_name = DRIVER_MAP.get(driver_id.lower())
    if not module_name:
        return DBDriverInfo(
            db_type=driver_id,
            is_installed=False,
            message="지원되지 않는 DB 타입입니다.",
            driver_path=None,
            driver_name=None,
            driver_size_bytes=None,
            driver_version=None,
        )

    # 해당 모듈이 현재 파이썬 환경에 설치되어 있는지 확인(즉, import 가능한지)
    spec = importlib.util.find_spec(module_name)
    # 설치 유무 확인
    is_installed = spec is not None

    return DBDriverInfo(
        db_type=driver_id,
        is_installed=is_installed,
        message="드라이버가 설치되어 있습니다." if is_installed else "드라이버가 설치되어 있지 않습니다.",
        driver_path=spec.origin if is_installed else None,
        driver_name=os.path.basename(spec.origin) if is_installed else None,
        driver_size_bytes=os.path.getsize(spec.origin) if is_installed else None,
        driver_version="N/A",  # 버전 확인 로직은 각 패키지별로 다르게 처리
    )
