import uuid
from pathlib import Path

# 앱 데이터를 저장할 폴더 이름
APP_DATA_DIR_NAME = ".qgenie"


def get_db_path() -> Path:
    """
    사용자 홈 디렉터리 내에 앱 데이터 폴더를 만들고,
    SQLite DB 파일의 전체 경로를 반환합니다.
    """
    home_dir = Path.home()
    app_data_dir = home_dir / APP_DATA_DIR_NAME
    app_data_dir.mkdir(exist_ok=True)
    db_path = app_data_dir / "local_storage.sqlite"
    return db_path


def generate_uuid() -> str:
    return uuid.uuid4().hex.upper()


def generate_prefixed_uuid(prefix: str) -> str:
    return f"{prefix.upper()}-{uuid.uuid4().hex.upper()}"
