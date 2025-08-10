import sqlite3

from fastapi import Depends

from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.core.utils import generate_prefixed_uuid
from app.repository.chat_tab_repository import ChatTabRepository, chat_tab_repository
from app.schemas.chat_tab.create_model import ChatTabCreate
from app.schemas.chat_tab.db_model import ChatTabInDB
from app.schemas.chat_tab.validation_utils import validate_chat_tab_name

chat_tab_repository_dependency = Depends(lambda: chat_tab_repository)


class ChatTabService:
    def __init__(self, repository: ChatTabRepository = chat_tab_repository):
        self.repository = repository

    def store_chat_tab(self, chatName: ChatTabCreate) -> ChatTabInDB:
        """새로운 AI 채팅을 데이터베이스에 저장합니다."""
        validate_chat_tab_name(chatName.name)

        new_id = generate_prefixed_uuid("CHAT_TAB")

        try:
            created_row = self.repository.create_chat_tab(
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


chat_tab_service = ChatTabService()
