from fastapi import APIRouter, Depends

from app.core.response import ResponseMessage
from app.core.status import CommonCode
from app.schemas.ai_chat.create_model import AIChatCreate
from app.schemas.ai_chat.response_model import AIChatResponse
from app.services.ai_chat_service import AIChatService, ai_chat_service

ai_chat_service_dependency = Depends(lambda: ai_chat_service)

router = APIRouter()


@router.post(
    "/actions",
    response_model=ResponseMessage[AIChatResponse],
    summary="Chat Tab 생성",
    description="새로운 Chat Tab을 생성하여 로컬 데이터베이스에 저장합니다.",
)
def store_ai_chat(
    chatName: AIChatCreate, service: AIChatService = ai_chat_service_dependency
) -> ResponseMessage[AIChatResponse]:
    """
    - **name**: 새로운 Chat_tab 이름 (예: "채팅 타이틀")
    """
    created_chat = service.store_ai_chat(chatName)

    response_data = AIChatResponse(
        id=created_chat.id,
        name=created_chat.name,
        created_at=created_chat.created_at,
        updated_at=created_chat.updated_at,
    )
    return ResponseMessage.success(value=response_data, code=CommonCode.SUCCESS_AI_CHAT_CREATE)
