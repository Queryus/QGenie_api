import importlib
import importlib.util
import logging
import os
import platform
import shutil
import subprocess
import sys

from app.schemas.db_driver_info import DBDriverInfo

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

os_simple_name = platform.system()  # Darwin, Windows, Linux 등 간단 이름
os_full_name = platform.platform()  # Darwin-22.5.0-x86_64, Windows-10-10.0.19045 등 상세 버전 포함

# 주요 DB별 대표적인 파이썬 드라이버들 복수 리스트로 작성
DRIVER_MAP = {
    "postgresql": ["psycopg2", "psycopg2_binary", "pg8000"],
    "mysql": ["mysql.connector", "pymysql", "MySQLdb", "oursql"],
    "sqlite": ["sqlite3"],
    "oracle": ["cx_Oracle", "oracledb"],
    "sqlserver": ["pyodbc", "pymssql"],
    "mariadb": ["mariadb", "mysql.connector", "pymysql", "MySQLdb", "oursql"],
}


# OS 레벨에서 드라이버 설치 확인용 명령어 (간단 체크용)
OS_DRIVER_CHECK_COMMANDS = {
    "postgresql": {
        "macos": ["which", "psql"],
        "windows": ["where", "psql"],
    },
    "mysql": {
        "macos": ["which", "mysql"],
        "windows": ["where", "mysql"],
    },
    "sqlite": {
        "macos": ["which", "sqlite3"],
        "windows": ["where", "sqlite3"],
    },
    "oracle": {
        "macos": ["which", "sqlplus"],
        "windows": ["where", "sqlplus"],
    },
    "sqlserver": {
        "macos": ["which", "sqlcmd"],
        "windows": ["where", "sqlcmd"],
    },
}


def is_python_environment() -> bool:
    """현재 환경이 Python 실행 환경인지 확인"""
    if sys.executable:
        return True
    if shutil.which("python3") or shutil.which("python"):
        return True
    return False


def check_os_driver_installed(driver_id: str) -> bool:
    """Python 환경이 아닐 때 OS 레벨에서 DB 클라이언트 도구 설치 여부 확인"""
    system = platform.system().lower()
    driver_key = driver_id.lower()

    if driver_key not in OS_DRIVER_CHECK_COMMANDS:
        return False  # 지원하지 않는 드라이버

    if system == "darwin":
        cmd = OS_DRIVER_CHECK_COMMANDS[driver_key]["macos"]
    elif system == "windows":
        cmd = OS_DRIVER_CHECK_COMMANDS[driver_key]["windows"]
    else:
        return False  # Linux 등은 필요 시 추가

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return bool(result.stdout.strip())
    except Exception:
        return False


def check_driver(driver_id: str) -> DBDriverInfo:
    driver_key = driver_id.lower()
    module_names = DRIVER_MAP.get(driver_key)

    if not module_names:
        return DBDriverInfo(
            db_type=driver_id,
            is_installed=False,
            message="지원되지 않는 DB 타입입니다.",
            driver_path=None,
            driver_name=None,
            driver_size_bytes=None,
            driver_version=None,
            os_name=os_simple_name,
            os_full_name=os_full_name,
        )

    logger.info(f"[check_driver] 요청된 드라이버: {driver_id} → 모듈명: {module_names}")
    logger.info(f"[check_driver] Python 환경 여부: {is_python_environment()}")

    if not is_python_environment():
        os_installed = check_os_driver_installed(driver_key)
        return DBDriverInfo(
            db_type=driver_id,
            is_installed=os_installed,
            message=(
                "Python 환경이 아니어서 OS 레벨로 설치 여부를 확인했습니다."
                if os_installed
                else "Python 환경이 아니며 OS 레벨에서도 드라이버를 찾을 수 없습니다."
            ),
            driver_path=None,
            driver_name=None,
            driver_size_bytes=None,
            driver_version=None,
            os_name=os_simple_name,
            os_full_name=os_full_name,
        )

    # module_names가 리스트일 때 첫 발견된 드라이버를 찾음
    if isinstance(module_names, str):
        module_names = [module_names]

    installed_module = None

    spec = None

    for mod_name in module_names:
        try:
            mod = importlib.import_module(mod_name)
            installed_module = mod_name
            spec = getattr(mod, "__spec__", None)
            break
        except ModuleNotFoundError:
            continue

    is_installed = installed_module is not None
    logger.info(f"[check_driver] 발견된 모듈명: {installed_module}, spec: {spec}")

    driver_path = None
    driver_name = None
    driver_size_bytes = None
    driver_version = "N/A"

    if is_installed and spec and spec.origin:
        driver_path = spec.origin
        driver_name = os.path.basename(driver_path)
        try:
            driver_size_bytes = os.path.getsize(driver_path)
        except Exception:
            driver_size_bytes = None

        try:
            mod = importlib.import_module(installed_module)
            driver_version = getattr(mod, "__version__", "Unknown")
        except Exception:
            driver_version = "Unknown"

    return DBDriverInfo(
        db_type=driver_id,
        is_installed=is_installed,
        message="드라이버가 설치되어 있습니다." if is_installed else "드라이버가 설치되어 있지 않습니다.",
        driver_path=driver_path,
        driver_name=driver_name,
        driver_size_bytes=driver_size_bytes,
        driver_version=driver_version,
        os_name=os_simple_name,
        os_full_name=os_full_name,
    )
