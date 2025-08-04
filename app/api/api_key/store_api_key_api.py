from fastapi import APIRouter

from app.core.exceptions import APIException
from app.core.response import ResponseMessage
from app.core.status import CommonCode
from app.schemas.llm_api_key import ApiKeyCredentialCreate, ApiKeyCredentialResponse
from app.services.api_key import store_api_key_service

router = APIRouter()


@router.post(
    "/actions",
    response_model=ResponseMessage[ApiKeyCredentialResponse],
    summary="API KEY 저장 (처음 한 번)",
    description="외부 AI 서비스의 API Key를 암호화하여 로컬 데이터베이스에 저장합니다.",
)
def store_api_key(credential: ApiKeyCredentialCreate) -> ResponseMessage:
    """
    - **service_name**: API Key가 사용될 외부 서비스 이름 (예: "OpenAI")
    - **api_key**: 암호화하여 저장할 실제 API Key (예: "sk-***..")
    """

    # 우선은 간단하게 존재 여부와 공백 여부로 검증
    # TODO: 검증 로직 강화
    if not credential.api_key or credential.api_key.isspace():
        raise APIException(CommonCode.INVALID_API_KEY_FORMAT)

    created_credential = store_api_key_service.store_api_key(credential)

    response_data = ApiKeyCredentialResponse(
        id=created_credential.id,
        service_name=created_credential.service_name.value,
        api_key_encrypted=created_credential.api_key,
        created_at=created_credential.created_at,
        updated_at=created_credential.updated_at,
    )

    return ResponseMessage.success(value=response_data, code=CommonCode.CREATED)
