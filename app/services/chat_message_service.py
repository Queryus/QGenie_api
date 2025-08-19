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
from app.schemas.chat_message.base_model import validate_chat_tab_id_format
from app.schemas.chat_message.db_model import ChatMessageInDB
from app.schemas.chat_message.request_model import ChatMessagesReqeust
from app.schemas.chat_message.response_model import ALLChatMessagesResponseByTab, ChatMessagesResponse

chat_message_repository_dependency = Depends(lambda: chat_message_repository)

# AI_SERVER_URL = os.getenv("ENV_AI_SERVER_URL")

# if not AI_SERVER_URL:
#     raise APIException(CommonCode.FAIL_AI_SERVER_CONNECTION)
#
# url: str = AI_SERVER_URL


class ChatMessageService:
    def __init__(self, repository: ChatMessageRepository = chat_message_repository):
        self.repository = repository
        self._ai_server_url = None

    def _get_ai_server_url(self) -> str:
        """AI 서버 URL을 한 번만 로드하고 캐싱하여 재사용합니다 (지연 로딩)."""
        if self._ai_server_url is None:
            url = os.getenv("ENV_AI_SERVER_URL")
            if not url:
                raise ValueError("환경 변수 'ENV_AI_SERVER_URL'가 설정되지 않았거나 .env 파일 로드에 실패했습니다.")
            self._ai_server_url = url
        return self._ai_server_url

    def get_chat_tab_and_messages_by_id(self, tab_id: str) -> ALLChatMessagesResponseByTab:
        """
        채팅 탭 정보와 메시지들을 함께 조회
        탭이 존재하지 않으면 예외를 발생시킵니다.
        """
        # chat_tab_id 형식 유효성 검사
        validate_chat_tab_id_format(tab_id)

        # 채팅 탭 정보와 메시지 조회
        try:
            return self.repository.get_chat_tab_and_messages_by_id(tab_id)
        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL) from e

    async def create_chat_message(self, request: ChatMessagesReqeust) -> ChatMessagesResponse:
        # 1. tab_id, message 유효성 검사 및 유무 확인
        request.validate()

        self.repository.get_chat_tab_by_id(request.chat_tab_id)

        # 2. 사용자 질의 저장
        try:
            self._transform_user_request_to_db_models(request)
        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL) from e

        # 3. AI 서버에 요청
        ai_response = await self._request_chat_message_to_ai_server(request)

        # 4. AI 서버 응답 저장
        response = self._transform_ai_response_to_db_models(request, ai_response)

        # DB 모델을 API 응답 모델로 변환
        response_data = ChatMessagesResponse.model_validate(response)

        return response_data

    def get_chat_tab_by_id(self, request: ChatMessagesReqeust) -> ChatMessageInDB:
        """특정 채팅 탭 조회"""

        # 채팅 탭 ID 조회
        try:
            chat_tab = self.repository.get_chat_tab_by_id(request.chat_tab_id)
            if not chat_tab:
                raise APIException(CommonCode.NO_CHAT_TAB_DATA)
            return chat_tab

        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL) from e

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

    async def _request_chat_message_to_ai_server(self, request: ChatMessagesReqeust) -> dict:
        """AI 서버에 사용자 질의를 보내고 답변을 받아옵니다."""
        # 1. DB에서 해당 탭의 모든 메시지 조회
        chat_tab_with_messages = self.repository.get_chat_tab_and_messages_by_id(request.chat_tab_id)
        messages: list[ChatMessagesResponse] = chat_tab_with_messages.messages

        if not messages:
            history = []
            latest_message = request.message  # DB에 없으면 요청 메시지 그대로
        else:
            history = [{"role": m.sender, "content": m.message} for m in messages[:-1]]
            latest_message = messages[-1].message

        # 3. AI 서버에 보내는 DATA
        request_body = {"question": latest_message, "chat_history": history}
        ai_server_url = self._get_ai_server_url()

        # 4. AI 서버에 POST 요청
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(ai_server_url, json=request_body, timeout=60.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise APIException(CommonCode.FAIL_AI_SERVER_PROCESSING) from e
            except httpx.RequestError as e:
                raise APIException(CommonCode.FAIL_AI_SERVER_CONNECTION) from e

    def _transform_ai_response_to_db_models(self, request: ChatMessagesReqeust, ai_response: dict) -> ChatMessageInDB:
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
