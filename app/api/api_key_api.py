from fastapi import APIRouter, Depends

from app.core.response import ResponseMessage
from app.core.status import CommonCode
from app.schemas.api_key.create_model import APIKeyCreate
from app.schemas.api_key.response_model import APIKeyResponse
from app.services.api_key_service import APIKeyService, api_key_service

api_key_service_dependency = Depends(lambda: api_key_service)

router = APIRouter()


@router.post(
    "/actions",
    response_model=ResponseMessage[APIKeyResponse],
    summary="API KEY 저장 (처음 한 번)",
    description="외부 AI 서비스의 API Key를 암호화하여 로컬 데이터베이스에 저장합니다.",
)
def store_api_key(
    credential: APIKeyCreate, service: APIKeyService = api_key_service_dependency
) -> ResponseMessage[APIKeyResponse]:
    """
    - **service_name**: API Key가 사용될 외부 서비스 이름 (예: "OpenAI")
    - **api_key**: 암호화하여 저장할 실제 API Key (예: "sk-***..")
    """
    created_credential = service.store_api_key(credential)

    response_data = APIKeyResponse(
        id=created_credential.id,
        service_name=created_credential.service_name.value,
        api_key_encrypted=created_credential.api_key,
        created_at=created_credential.created_at,
        updated_at=created_credential.updated_at,
    )

    return ResponseMessage.success(value=response_data, code=CommonCode.CREATED)
