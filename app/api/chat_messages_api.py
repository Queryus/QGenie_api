from fastapi import APIRouter, Depends, Path

from app.core.enum.sender import SenderEnum
from app.core.response import ResponseMessage
from app.core.status import CommonCode
from app.schemas.chat_message.request_model import ChatMessagesReqeust
from app.schemas.chat_message.response_model import ALLChatMessagesResponseByTab, ChatMessagesResponse
from app.services.chat_message_service import ChatMessageService, chat_message_service

chat_message_service_dependency = Depends(lambda: chat_message_service)

router = APIRouter()


@router.post(
    "/create",
    response_model=ResponseMessage[ChatMessagesResponse],
    summary="새로운 사용자 질의 생성",
)
async def create_chat_message(
    request: ChatMessagesReqeust, service: ChatMessageService = chat_message_service_dependency
) -> ResponseMessage[ChatMessagesResponse]:
    """
    `tabId`, `message`를 받아 DB에 저장하고 AI를 통해 사용자 질의를 분석하고 답변을 생성하여 반환합니다.
    """
    new_messages = await service.create_chat_message(request)

    response_data = ChatMessagesResponse(
        id=new_messages.id,
        chat_tab_id=new_messages.chat_tab_id,
        sender=SenderEnum(new_messages.sender),
        message=new_messages.message,
        created_at=new_messages.created_at,
        updated_at=new_messages.updated_at,
    )

    return ResponseMessage.success(value=response_data, code=CommonCode.SUCCESS_CREATE_CHAT_MESSAGES)


@router.get(
    "/find/{tabId}",
    response_model=ResponseMessage[ALLChatMessagesResponseByTab],
    summary="특정 탭의 메시지 전체 조회",
)
def get_chat_messages_by_tabId(
    tabId: str = Path(..., description="채팅 탭 고유 ID"),
    service: ChatMessageService = chat_message_service_dependency,
) -> ResponseMessage[ALLChatMessagesResponseByTab]:
    """tabId를 기준으로 해당 chat_tab의 전체 메시지를 가져옵니다."""

    # 탭 정보와 메시지를 함께 조회
    response_data = service.get_chat_tab_and_messages_by_id(tabId)

    return ResponseMessage.success(value=response_data, code=CommonCode.SUCCESS_GET_CHAT_MESSAGES)
