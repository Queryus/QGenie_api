import importlib
import logging
import os

DRIVER_MAP = {
    "postgresql": ["psycopg2", "pg8000"],
    "mysql": ["pymysql", "mysql.connector"],
    "sqlite": ["sqlite3"],
    "oracle": ["cx_Oracle"],
    "sqlserver": ["pyodbc"],
    "mariadb": ["pymysql", "mysql.connector"],
}


def db_driver_info(driver_id: str) -> dict:
    driver_key = driver_id.lower()
    module_names = DRIVER_MAP.get(driver_key)

    if not module_names:
        # 지원되지 않는 DB 타입
        return {"message": "지원되지 않는 DB입니다.", "data": None}

    for mod_name in module_names:
        try:
            mod = importlib.import_module(mod_name)
            version = getattr(mod, "__version__", None)
            path = getattr(mod.__spec__, "origin", None)
            size = os.path.getsize(path) if path else None

            return {
                "message": "드라이버 정보를 성공적으로 불러왔습니다.",
                "data": {
                    "db_type": driver_id,
                    "is_installed": True,
                    "driver_name": mod_name,
                    "driver_version": version,
                    "driver_size_bytes": size,
                },
            }
        except (ModuleNotFoundError, AttributeError, OSError) as e:
            logging.warning(f"드라이버 '{mod_name}' import 실패: {e}")
            continue

    # import 실패한 경우
    return {"message": "드라이버 정보를 가져오지 못했습니다. 다시 시도해주세요.", "data": None}
