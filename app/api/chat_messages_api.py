from fastapi import APIRouter, Depends

from app.core.enum.sender import SenderEnum
from app.core.response import ResponseMessage
from app.core.status import CommonCode
from app.schemas.chat_message.request_model import ChatMessagesReqeust
from app.schemas.chat_message.response_model import ChatMessagesResponse
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

    print(ChatMessagesResponse.model_json_schema())

    response_data = ChatMessagesResponse(
        id=new_messages.id,
        chat_tab_id=new_messages.chat_tab_id,
        sender=SenderEnum(new_messages.sender),
        message=new_messages.message,
        created_at=new_messages.created_at,
        updated_at=new_messages.updated_at,
    )

    return ResponseMessage.success(value=response_data, code=CommonCode.SUCCESS_CREATE_CHAT_MESSAGES)
