import os
import sqlite3

import httpx
from fastapi import Depends

from app.core.enum.db_key_prefix_name import DBSaveIdEnum
from app.core.enum.sender import SenderEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.core.utils import generate_prefixed_uuid
from app.repository.chat_message_repository import ChatMessageRepository, chat_message_repository
from app.schemas.chat_message.db_model import ChatMessageInDB
from app.schemas.chat_message.request_model import ChatMessagesReqeust
from app.schemas.chat_message.response_model import ChatMessagesResponse

chat_message_repository_dependency = Depends(lambda: chat_message_repository)

AI_SERVER_URL = os.getenv("ENV_AI_SERVER_URL")


class ChatMessageService:
    def __init__(self, repository: ChatMessageRepository = chat_message_repository):
        self.repository = repository

    def get_chat_messages_by_tabId(self, tabId: str) -> ChatMessageInDB:
        """
        채팅 탭 메타데이터와 메시지 목록을 모두 가져와서 조합합니다.
        탭이 존재하지 않으면 예외를 발생시킵니다.
        """
        try:
            return self.repository.get_chat_messages_by_tabId(tabId)

        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL) from e

    async def create_chat_message(self, request: ChatMessagesReqeust) -> ChatMessagesResponse:
        # 1. tab_id 확인
        chat_tab_id = request.chat_tab_id

        # chat_tab_id 유효성 검사
        try:
            request.validate()
        except ValueError as e:
            raise APIException(CommonCode.INVALID_CHAT_MESSAGE_REQUEST, detail=str(e)) from e

        try:
            # 같은 서비스 메서드 호출
            self.get_chat_messages_by_tabId(chat_tab_id)
        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL) from e

        # 2. 사용자 질의 저장
        try:
            user_request = self._transform_user_request_to_db_models(request)
        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL) from e

        # 3. AI 서버에 요청
        ai_response = await self._request_chat_message_to_ai_server(user_request)

        # 4. AI 서버 응답 저장
        response = self._transform_ai_response_to_db_models(request, ai_response)

        return response

    def _transform_user_request_to_db_models(self, request: ChatMessagesReqeust) -> ChatMessageInDB:
        """사용자 질의를 데이터베이스에 저장합니다."""

        new_id = generate_prefixed_uuid(DBSaveIdEnum.chat_message.value)
        sender = SenderEnum.user

        chat_tab_id = request.chat_tab_id
        message = request.message

        try:
            created_row = self.repository.create_chat_message(
                new_id=new_id,
                sender=sender,
                chat_tab_id=chat_tab_id,
                message=message,
            )
            if not created_row:
                raise APIException(CommonCode.FAIL_TO_VERIFY_CREATION)

            return created_row

        except sqlite3.Error as e:
            if "database is locked" in str(e):
                raise APIException(CommonCode.DB_BUSY) from e
            raise APIException(CommonCode.FAIL) from e

    async def _request_chat_message_to_ai_server(self, user_request: ChatMessagesReqeust) -> dict:
        """AI 서버에 사용자 질의를 보내고 답변을 받아옵니다."""
        # 1. DB에서 해당 탭의 모든 메시지 조회
        messages: list[ChatMessageInDB] = self.repository.get_chat_messages_by_tabId(user_request.chat_tab_id)

        if not messages:
            history = []
            latest_message = user_request.message  # DB에 없으면 요청 메시지 그대로
        else:
            history = [{"role": m.sender, "content": m.message} for m in messages[:-1]]
            latest_message = messages[-1].message

        # 3. AI 서버에 보내는 DATA
        request_body = {"question": latest_message, "chat_history": history}

        # 4. AI 서버에 POST 요청
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(AI_SERVER_URL, json=request_body, timeout=60.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise APIException(CommonCode.FAIL_AI_SERVER_PROCESSING) from e
            except httpx.RequestError as e:
                raise APIException(CommonCode.FAIL_AI_SERVER_CONNECTION) from e

    def _transform_ai_response_to_db_models(self, request: ChatMessagesReqeust, ai_response: str) -> ChatMessageInDB:
        """AI 서버에서 받은 답변을 데이터베이스에 저장합니다."""

        new_id = generate_prefixed_uuid(DBSaveIdEnum.chat_message.value)
        sender = SenderEnum.ai

        chat_tab_id = request.chat_tab_id
        message = ai_response["answer"]

        try:
            created_row = self.repository.create_chat_message(
                new_id=new_id,
                sender=sender,
                chat_tab_id=chat_tab_id,
                message=message,
            )
            if not created_row:
                raise APIException(CommonCode.FAIL_TO_VERIFY_CREATION)

            return created_row

        except sqlite3.Error as e:
            if "database is locked" in str(e):
                raise APIException(CommonCode.DB_BUSY) from e
            raise APIException(CommonCode.FAIL) from e


chat_message_service = ChatMessageService()
