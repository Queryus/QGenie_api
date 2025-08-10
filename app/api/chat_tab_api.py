from fastapi import APIRouter, Depends

from app.core.response import ResponseMessage
from app.core.status import CommonCode
from app.schemas.chat_tab.create_model import ChatTabCreate
from app.schemas.chat_tab.response_model import ChatTabResponse
from app.services.chat_tab_service import ChatTabService, chat_tab_service

chat_tab_service_dependency = Depends(lambda: chat_tab_service)

router = APIRouter()


@router.post(
    "/actions",
    response_model=ResponseMessage[ChatTabResponse],
    summary="Chat Tab 생성",
    description="새로운 Chat Tab을 생성하여 로컬 데이터베이스에 저장합니다.",
)
def store_chat_tab(
    chatName: ChatTabCreate, service: ChatTabService = chat_tab_service_dependency
) -> ResponseMessage[ChatTabResponse]:
    """
    - **name**: 새로운 Chat_tab 이름 (예: "채팅 타이틀")
    """
    created_chat = service.store_chat_tab(chatName)

    response_data = ChatTabResponse(
        id=created_chat.id,
        name=created_chat.name,
        created_at=created_chat.created_at,
        updated_at=created_chat.updated_at,
    )
    return ResponseMessage.success(value=response_data, code=CommonCode.SUCCESS_CHAT_TAB_CREATE)
