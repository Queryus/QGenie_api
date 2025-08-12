import sqlite3

from app.core.utils import get_db_path
from app.schemas.chat_tab.db_model import ChatMessageInDB


class ChatMessageRepository:

    def get_chat_messages_by_tabId(self, id: str) -> list[ChatMessageInDB]:
        """주어진 chat_tab_id에 해당하는 모든 메시지를 가져옵니다."""
        db_path = get_db_path()
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # chat_message 테이블에서 chat_tab_id에 해당하는 모든 메시지를 조회합니다.'
            # 메시지가 없을 경우, 빈 리스트를 반환합니다.
            cursor.execute(
                "SELECT * FROM chat_message WHERE chat_tab_id = ? ORDER BY created_at ASC",
                (id,),
            )
            rows = cursor.fetchall()

            # 조회된 모든 행을 ChatMessageInDB 객체 리스트로 변환
            return [ChatMessageInDB.model_validate(dict(row)) for row in rows]

        finally:
            if conn:
                conn.close()


chat_message_repository = ChatMessageRepository()
