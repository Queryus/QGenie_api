from fastapi import APIRouter, Depends, Path

from app.core.response import ResponseMessage
from app.core.status import CommonCode
from app.schemas.chat_tab.base_model import ChatTabBase
from app.schemas.chat_tab.response_model import ChatMessagesResponse, ChatTabResponse
from app.schemas.chat_tab.update_model import ChatTabUpdate
from app.services.chat_tab_service import ChatTabService, chat_tab_service

chat_tab_service_dependency = Depends(lambda: chat_tab_service)

router = APIRouter()


@router.post(
    "/create",
    response_model=ResponseMessage[ChatTabResponse],
    summary="새로운 Chat Tab 생성",
    description="새로운 Chat Tab을 생성하여 로컬 데이터베이스에 저장합니다.",
)
def create_chat_tab(
    chatName: ChatTabBase, service: ChatTabService = chat_tab_service_dependency
) -> ResponseMessage[ChatTabResponse]:
    """
    - **name**: 새로운 Chat_tab 이름 (예: "채팅 타이틀")
    """
    created_chat_tab = service.create_chat_tab(chatName)

    response_data = ChatTabResponse(
        id=created_chat_tab.id,
        name=created_chat_tab.name,
        created_at=created_chat_tab.created_at,
        updated_at=created_chat_tab.updated_at,
    )
    return ResponseMessage.success(value=response_data, code=CommonCode.SUCCESS_CHAT_TAB_CREATE)


@router.get(
    "/find",
    response_model=ResponseMessage[list[ChatTabResponse]],
    summary="저장된 모든 Chat_tab 정보 조회",
    description="""
    chat_tab 테이블에 저장된 모든 chat tab들을 확인합니다.
    """,
)
def get_all_chat_tab(
    service: ChatTabService = chat_tab_service_dependency,
) -> ResponseMessage[list[ChatTabResponse]]:
    """저장된 모든 chat_tab의 메타데이터를 조회하여 등록 여부를 확인합니다."""
    chat_tabs_in_db = service.get_all_chat_tab()

    response_data = [
        ChatTabResponse(
            id=chat_tab.id,
            name=chat_tab.name,
            created_at=chat_tab.created_at,
            updated_at=chat_tab.updated_at,
        )
        for chat_tab in chat_tabs_in_db
    ]
    return ResponseMessage.success(value=response_data, code=CommonCode.SUCCESS_GET_CHAT_TAB)


@router.get(
    "/find/{tabId}",
    response_model=ResponseMessage[ChatMessagesResponse],
    summary="특정 탭의 메시지 전체 조회",
)
def get_chat_messages_by_tabId(
    tabId: str = Path(..., description="채팅 탭 고유 ID"), service: ChatTabService = chat_tab_service_dependency
) -> ResponseMessage[list[ChatMessagesResponse]]:
    """tabId를 기준으로 해당 chat_tab의 전체 메시지를 가져옵니다."""
    chat_tab = service.get_chat_tab_by_tabId(tabId)

    chat_messages = service.get_chat_messages_by_tabId(tabId)

    response_data = ChatMessagesResponse(
        id=chat_tab.id,
        name=chat_tab.name,
        created_at=chat_tab.created_at,
        updated_at=chat_tab.updated_at,
        messages=chat_messages,
    )

    return ResponseMessage.success(value=response_data, code=CommonCode.SUCCESS_GET_CHAT_MESSAGES)


@router.put(
    "/modify/{tabId}",
    response_model=ResponseMessage[ChatTabResponse],
    summary="특정 Chat Tab Name 수정",
)
def updated_chat_tab(
    chatName: ChatTabUpdate,
    tabId: str = Path(..., description="수정할 채팅 탭의 고유 ID"),
    service: ChatTabService = chat_tab_service_dependency,
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


@router.delete(
    "/remove/{tabId}",
    response_model=ResponseMessage,
    summary="특정 Chat Tab 삭제",
)
def delete_chat_tab(
    tabId: str = Path(..., description="수정할 채팅 탭의 고유 ID"),
    service: ChatTabService = chat_tab_service_dependency,
) -> ResponseMessage:
    """
    채팅 탭 ID를 기준으로 채팅 탭을 삭제합니다.
    - **id**: 삭제할 채팅 탭 ID
    """
    service.delete_chat_tab(tabId)
    return ResponseMessage.success(code=CommonCode.SUCCESS_CHAT_TAB_DELETE)
