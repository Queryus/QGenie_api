from fastapi import APIRouter, Depends

from app.core.enum.llm_service_info import LLMServiceEnum
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


@router.get(
    "/result",
    response_model=ResponseMessage[list[APIKeyResponse]],
    summary="저장된 모든 API KEY 정보 조회",
    description="""
    ai_credential 테이블에 저장된 모든 서비스 이름을 확인합니다.
    이를 통해 프론트엔드에서는 비워둘 필드, 임의의 마스킹된 값을 채워둘 필드를 구분합니다.
    """,
)
def get_all_api_keys(
    service: APIKeyService = api_key_service_dependency,
) -> ResponseMessage[list[APIKeyResponse]]:
    """저장된 모든 API Key의 메타데이터를 조회하여 등록 여부를 확인합니다."""
    db_credentials = service.get_all_api_keys()

    response_data = [
        APIKeyResponse(
            id=cred.id,
            service_name=cred.service_name,
            created_at=cred.created_at,
            updated_at=cred.updated_at,
        )
        for cred in db_credentials
    ]
    return ResponseMessage.success(value=response_data)


@router.get(
    "/result/{serviceName}",
    response_model=ResponseMessage[APIKeyResponse],
    summary="특정 서비스의 API KEY 정보 조회",
)
def get_api_key_by_service_name(
    serviceName: LLMServiceEnum, service: APIKeyService = api_key_service_dependency
) -> ResponseMessage[APIKeyResponse]:
    """서비스 이름을 기준으로 특정 API Key의 메타데이터를 조회합니다."""
    db_credential = service.get_api_key_by_service_name(serviceName)

    response_data = APIKeyResponse(
        id=db_credential.id,
        service_name=db_credential.service_name,
        created_at=db_credential.created_at,
        updated_at=db_credential.updated_at,
    )
    return ResponseMessage.success(value=response_data)
