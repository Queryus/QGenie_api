import importlib.util
import os
import shutil
import sys

from app.schemas.db_driver_info import DBDriverInfo

DRIVER_MAP = {
    "postgresql": "psycopg2",
    "mysql": "pymysql",
    "sqlite": "sqlite3",
    "oracle": "cx_Oracle",
    "sqlserver": "pyodbc",
}


def is_python_environment() -> bool:
    """현재 환경이 Python 실행 환경인지 확인"""
    # 1) sys.executable 존재 여부 확인 (현재 파이썬 인터프리터 경로)
    if sys.executable:
        return True
    # 2) 시스템 경로에 python3 또는 python 명령어 존재 여부 확인
    if shutil.which("python3") or shutil.which("python"):
        return True
    return False


def check_driver(driver_id: str) -> DBDriverInfo:
    """
    주어진 DB 드라이버 ID에 대해
    - 현재 Python 환경에서 설치 여부 확인
    - 설치되어 있으면 드라이버 정보 반환
    - 설치 안되어 있거나 미지원 타입일 경우 상태 반환
    """
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

    # Python 환경이 아니면 설치 여부 확인 불가 (필요하면 OS 레벨 체크로 확장 가능)
    if not is_python_environment():
        return DBDriverInfo(
            db_type=driver_id,
            is_installed=False,
            message="Python 환경이 아니어서 설치 여부를 확인할 수 없습니다.",
            driver_path=None,
            driver_name=None,
            driver_size_bytes=None,
            driver_version=None,
        )

    # import 가능한지 확인해서 설치 여부 판단
    spec = importlib.util.find_spec(module_name)
    is_installed = spec is not None

    return DBDriverInfo(
        db_type=driver_id,
        is_installed=is_installed,
        message="드라이버가 설치되어 있습니다." if is_installed else "드라이버가 설치되어 있지 않습니다.",
        driver_path=spec.origin if is_installed else None,
        driver_name=os.path.basename(spec.origin) if is_installed else None,
        driver_size_bytes=os.path.getsize(spec.origin) if is_installed else None,
        driver_version="N/A",  # 추후 각 드라이버별 버전 확인 로직 추가 가능
    )
