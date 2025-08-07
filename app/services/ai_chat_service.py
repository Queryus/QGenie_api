import sqlite3

from fastapi import Depends

from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.core.utils import generate_prefixed_uuid
from app.repository.ai_chat_repository import AIChatRepository, ai_chat_repository
from app.schemas.ai_chat.create_model import AIChatCreate
from app.schemas.ai_chat.db_model import AIChatInDB

ai_chat_repository_dependency = Depends(lambda: ai_chat_repository)


class AIChatService:
    def __init__(self, repository: AIChatRepository = ai_chat_repository):
        self.repository = repository

    def store_ai_chat(self, chatName: AIChatCreate) -> AIChatInDB:
        """새로운 AI 채팅을 데이터베이스에 저장합니다."""
        chatName.validate_with_name()

        new_id = generate_prefixed_uuid("CHAT_TAB")

        try:
            created_row = self.repository.create_ai_chat(
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


ai_chat_service = AIChatService()
