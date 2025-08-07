import sqlite3

from app.core.utils import get_db_path
from app.schemas.api_key.db_model import APIKeyInDB


class APIKeyRepository:
    def create_api_key(self, new_id: str, service_name: str, encrypted_key: str) -> APIKeyInDB:
        """
        암호화된 API Key 정보를 받아 데이터베이스에 저장하고,
        저장된 객체를 반환합니다.
        """
        db_path = get_db_path()
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO ai_credential (id, service_name, api_key)
                VALUES (?, ?, ?)
                """,
                (new_id, service_name, encrypted_key),
            )
            conn.commit()

            cursor.execute("SELECT * FROM ai_credential WHERE id = ?", (new_id,))
            created_row = cursor.fetchone()

            if not created_row:
                return None

            return APIKeyInDB.model_validate(dict(created_row))

        finally:
            if conn:
                conn.close()

    def get_all_api_keys(self) -> list[APIKeyInDB]:
        """데이터베이스에 저장된 모든 API Key를 조회합니다."""
        db_path = get_db_path()
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM ai_credential")
            rows = cursor.fetchall()

            return [APIKeyInDB.model_validate(dict(row)) for row in rows]
        finally:
            if conn:
                conn.close()

    def get_api_key_by_service_name(self, service_name: str) -> APIKeyInDB | None:
        """서비스 이름으로 특정 API Key를 조회합니다."""
        db_path = get_db_path()
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM ai_credential WHERE service_name = ?", (service_name,))
            row = cursor.fetchone()

            if not row:
                return None

            return APIKeyInDB.model_validate(dict(row))
        finally:
            if conn:
                conn.close()

    def update_api_key(self, service_name: str, encrypted_key: str) -> APIKeyInDB | None:
        """서비스 이름에 해당하는 API Key를 수정하고, 수정된 객체를 반환합니다."""
        db_path = get_db_path()
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 먼저 해당 서비스의 데이터가 존재하는지 확인
            cursor.execute("SELECT id FROM ai_credential WHERE service_name = ?", (service_name,))
            if not cursor.fetchone():
                return None

            # 데이터 업데이트
            cursor.execute(
                "UPDATE ai_credential SET api_key = ?, updated_at = datetime('now', 'localtime') WHERE service_name = ?",
                (encrypted_key, service_name),
            )
            conn.commit()

            # rowcount가 0이면 업데이트된 행이 없음 (정상적인 경우 발생하기 어려움)
            if cursor.rowcount == 0:
                return None

            cursor.execute("SELECT * FROM ai_credential WHERE service_name = ?", (service_name,))
            updated_row = cursor.fetchone()

            return APIKeyInDB.model_validate(dict(updated_row))
        finally:
            if conn:
                conn.close()


api_key_repository = APIKeyRepository()
