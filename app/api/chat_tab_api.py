from fastapi import APIRouter, Depends, Path

from app.core.response import ResponseMessage
from app.core.status import CommonCode
from app.schemas.chat_tab.create_model import ChatTabCreate
from app.schemas.chat_tab.response_model import ChatTabResponse
from app.schemas.chat_tab.update_model import ChatTabUpdate
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
    created_chat_tab = service.store_chat_tab(chatName)

    response_data = ChatTabResponse(
        id=created_chat_tab.id,
        name=created_chat_tab.name,
        created_at=created_chat_tab.created_at,
        updated_at=created_chat_tab.updated_at,
    )
    return ResponseMessage.success(value=response_data, code=CommonCode.SUCCESS_CHAT_TAB_CREATE)

@router.put(
    "/modify/{tabId}",
    response_model=ResponseMessage[ChatTabResponse],
    summary="특정 Chat Tab Name 수정",
)
def updated_chat_tab(
    chatName: ChatTabUpdate,
    tabId: str = Path(..., description="수정할 채팅 탭의 고유 ID"),
    service: ChatTabService = chat_tab_service_dependency
) -> ResponseMessage[ChatTabResponse]:
    """
    채팅 탭 ID를 기준으로 채팅 탭의 이름을 새로운 값으로 수정합니다.
    - **id**: 수정할 채팅 탭 ID
    - **name**: 새로운 채팅 탭의 이름
    """
    updated_chat_tab = service.updated_chat_tab(tabId, chatName)

    response_data = ChatTabResponse(
        id=updated_chat_tab.id,
        name=updated_chat_tab.name,
        created_at=updated_chat_tab.created_at,
        updated_at=updated_chat_tab.updated_at,
    )

    return ResponseMessage.success(value=response_data, code=CommonCode.SUCCESS_CHAT_TAB_UPDATE)
