import sqlite3

from fastapi import Depends

from app.core.enum.db_key_prefix_name import DBSaveIdEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.core.utils import generate_prefixed_uuid
from app.repository.chat_message_repository import ChatMessageRepository, chat_message_repository
from app.repository.chat_tab_repository import ChatTabRepository, chat_tab_repository
from app.schemas.chat_tab.create_model import ChatTabCreate
from app.schemas.chat_tab.db_model import ChatMessageInDB, ChatTabInDB
from app.schemas.chat_tab.update_model import ChatTabUpdate
from app.schemas.chat_tab.validation_utils import validate_chat_tab_id, validate_chat_tab_name

chat_tab_repository_dependency = Depends(lambda: chat_tab_repository)
chat_tab_repository_dependency = Depends(lambda: chat_tab_repository)


class ChatTabService:
    def __init__(
        self,
        tab_repository: ChatTabRepository = chat_tab_repository,
        message_repository: ChatMessageRepository = chat_message_repository,
    ):
        self.tab_repository = tab_repository
        self.message_repository = message_repository

    def store_chat_tab(self, chatName: ChatTabCreate) -> ChatTabInDB:
        """새로운 AI 채팅을 데이터베이스에 저장합니다."""
        validate_chat_tab_name(chatName.name)

        new_id = generate_prefixed_uuid(DBSaveIdEnum.chat_tab.value)

        try:
            created_row = self.tab_repository.create_chat_tab(
                new_id=new_id,
                name=chatName.name,
            )
            if not created_row:
                raise APIException(CommonCode.FAIL_TO_VERIFY_CREATION)

            return created_row

        except sqlite3.Error as e:
            # "database is locked" 오류를 명시적으로 처리
            if "database is locked" in str(e):
                raise APIException(CommonCode.DB_BUSY) from e
            # 기타 모든 sqlite3 오류
            raise APIException(CommonCode.FAIL) from e

    def updated_chat_tab(self, chatID: str, chatName: ChatTabUpdate) -> ChatTabInDB:
        """TabID에 해당하는 AIChatTab name을 수정합니다."""
        validate_chat_tab_name(chatName.name)
        try:
            updated_chat_tab = self.tab_repository.updated_chat_tab(chatID, chatName.name)

            if not updated_chat_tab:
                raise APIException(CommonCode.NO_CHAT_TAB_DATA)

            return updated_chat_tab
        except sqlite3.Error as e:
            if "database is locked" in str(e):
                raise APIException(CommonCode.DB_BUSY) from e
            raise APIException(CommonCode.FAIL) from e

    def delete_chat_tab(self, tabId: str) -> None:
        """TabID에 해당하는 AIChatTab을 삭제합니다."""
        try:
            is_deleted = self.tab_repository.delete_chat_tab(tabId)
            if not is_deleted:
                raise APIException(CommonCode.NO_CHAT_TAB_DATA)
        except sqlite3.Error as e:
            if "database is locked" in str(e):
                raise APIException(CommonCode.DB_BUSY) from e
            raise APIException(CommonCode.FAIL) from e

    def get_all_chat_tab(self) -> ChatTabInDB:
        """데이터베이스에 저장된 모든 Chat_tab을 조회합니다."""
        try:
            return self.tab_repository.get_all_chat_tab()
        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL) from e

    def get_chat_tab_by_tabId(self, tabId: str) -> ChatTabInDB:
        """데이터베이스에 저장된 특정 Chat_tab을 조회합니다."""
        validate_chat_tab_id(tabId)

        try:
            chat_tab = self.tab_repository.get_chat_tab_by_id(tabId)

            if not chat_tab:
                raise APIException(CommonCode.NO_CHAT_TAB_DATA)
            return chat_tab

        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL) from e

    def get_chat_messages_by_tabId(self, tabId: str) -> ChatMessageInDB:
        """
        채팅 탭 메타데이터와 메시지 목록을 모두 가져와서 조합합니다.
        탭이 존재하지 않으면 예외를 발생시킵니다.
        """
        try:
            return self.message_repository.get_chat_messages_by_tabId(tabId)

        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL) from e


chat_tab_service = ChatTabService()
