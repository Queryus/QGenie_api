import sqlite3

from app.core.utils import get_db_path
from app.schemas.chat_tab.db_model import ChatTabInDB


class ChatTabRepository:
    def create_chat_tab(self, new_id: str, name: str) -> ChatTabInDB:
        """
        새로운 채팅 탭 이름을 데이터베이스에 저장하고, 저장된 객체를 반환합니다.
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
                return None

            return ChatTabInDB.model_validate(dict(created_row))

        finally:
            if conn:
                conn.close()

    def updated_chat_tab(self, id: str, new_name: str | None) -> ChatTabInDB | None:
        """채팅 탭ID에 해당하는 ChatName를 수정하고, 수정된 객체를 반환합니다."""
        db_path = get_db_path()
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 먼저 해당 서비스의 데이터가 존재하는지 확인
            cursor.execute("SELECT id FROM chat_tab WHERE id = ?", (id,))
            if not cursor.fetchone():
                return None

            # 데이터 업데이트
            cursor.execute(
                "UPDATE chat_tab SET name = ?, updated_at = datetime('now', 'localtime') WHERE id = ?",
                (new_name, id),
            )
            conn.commit()

            # rowcount가 0이면 업데이트된 행이 없음 (정상적인 경우 발생하기 어려움)
            if cursor.rowcount == 0:
                return None

            cursor.execute("SELECT * FROM chat_tab WHERE id = ?", (id,))
            updated_row = cursor.fetchone()

            return ChatTabInDB.model_validate(dict(updated_row))
        finally:
            if conn:
                conn.close()

    def delete_chat_tab(self, id: str) -> bool:
        """채팅 탭ID에 해당하는 ChatTab을 삭제하고, 성공 여부를 반환합니다."""
        db_path = get_db_path()
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            cursor = conn.cursor()

            # 먼저 해당 서비스의 데이터가 존재하는지 확인
            cursor.execute("SELECT id FROM chat_tab WHERE id = ?", (id,))
            if not cursor.fetchone():
                return False

            # 데이터 삭제
            cursor.execute("DELETE FROM chat_tab WHERE id = ?", (id,))
            conn.commit()

            # rowcount가 0이면 삭제된 행이 없음 (정상적인 경우 발생하기 어려움)
            if cursor.rowcount == 0:
                return False

            return cursor.rowcount > 0
        finally:
            if conn:
                conn.close()

    def get_all_chat_tab(self) -> list[ChatTabInDB]:
        """데이터베이스에 저장된 모든 Chat Tab ID를 조회합니다."""
        db_path = get_db_path()
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM chat_tab")
            rows = cursor.fetchall()

            return [ChatTabInDB.model_validate(dict(row)) for row in rows]
        finally:
            if conn:
                conn.close()


chat_tab_repository = ChatTabRepository()
