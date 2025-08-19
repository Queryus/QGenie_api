import sqlite3

from app.core.enum.sender import SenderEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.core.utils import get_db_path
from app.schemas.chat_message.db_model import ChatMessageInDB
from app.schemas.chat_message.response_model import ALLChatMessagesResponseByTab, ChatMessagesResponse


class ChatMessageRepository:
    def create_chat_message(self, new_id: str, sender: str, chat_tab_id: str, message: str) -> ChatMessageInDB:
        """새로운 채팅을 데이터베이스에 저장하고, 저장된 객체를 반환합니다."""

        db_path = get_db_path()
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO chat_message (id, chat_tab_id, sender, message)
                VALUES (?, ?, ?, ?)
                """,
                (
                    new_id,
                    chat_tab_id,
                    sender,
                    message,
                ),
            )
            conn.commit()

            cursor.execute("SELECT * FROM chat_message WHERE id = ?", (new_id,))
            created_row = cursor.fetchone()

            if not created_row:
                return None

            return ChatMessageInDB.model_validate(dict(created_row))

        finally:
            if conn:
                conn.close()

    def get_chat_tab_and_messages_by_id(self, tabId: str) -> ALLChatMessagesResponseByTab:
        """주어진 chat_tab_id에 해당하는 모든 메시지를 가져옵니다."""
        db_path = get_db_path()
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 1. 채팅 탭 정보 조회
            cursor.execute(
                "SELECT id, name, created_at, updated_at FROM chat_tab WHERE id = ?",
                (tabId,),
            )
            tab_row = cursor.fetchone()

            if not tab_row:
                raise APIException(CommonCode.NO_CHAT_TAB_DATA)

            # 2. 해당 탭의 메시지들 조회
            cursor.execute(
                """
                SELECT id, chat_tab_id, sender, message, created_at, updated_at
                FROM chat_message
                WHERE chat_tab_id = ?
                ORDER BY created_at ASC
                """,
                (tabId,),
            )
            message_rows = cursor.fetchall()

            # 3. 메시지들을 ChatMessagesResponse로 변환
            messages = [
                ChatMessagesResponse(
                    id=row["id"],
                    chat_tab_id=row["chat_tab_id"],
                    sender=SenderEnum(row["sender"]),
                    message=row["message"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                for row in message_rows
            ]

            # 4. ALLChatMessagesResponseByTab 객체 생성
            return ALLChatMessagesResponseByTab(
                id=tab_row["id"],
                name=tab_row["name"],
                created_at=tab_row["created_at"],
                updated_at=tab_row["updated_at"],
                messages=messages,
            )
        except sqlite3.Error as e:
            raise e
        finally:
            if conn:
                conn.close()

    def get_chat_tab_by_id(self, tabId: str) -> None:
        """데이터베이스에 저장된 특정 Chat Tab ID를 조회합니다."""
        db_path = get_db_path()
        conn = None
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id FROM chat_tab WHERE id = ?",
                (tabId,),
            )

            return None
        finally:
            if conn:
                conn.close()


chat_message_repository = ChatMessageRepository()
