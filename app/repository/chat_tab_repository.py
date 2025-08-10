import sqlite3

from app.core.utils import get_db_path
from app.schemas.chat_tab.db_model import AIChatInDB


class AIChatRepository:

    def create_ai_chat(self, new_id: str, name: str) -> AIChatInDB:
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
                INSERT INTO chat_tab (id, name)
                VALUES (?, ?)
                """,
                (
                    new_id,
                    name,
                ),
            )
            conn.commit()

            cursor.execute("SELECT * FROM chat_tab WHERE id = ?", (new_id,))
            created_row = cursor.fetchone()

            if not created_row:
                raise None

            return AIChatInDB.model_validate(dict(created_row))

        finally:
            if conn:
                conn.close()


ai_chat_repository = AIChatRepository()
