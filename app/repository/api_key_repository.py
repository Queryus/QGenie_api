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


api_key_repository = APIKeyRepository()
