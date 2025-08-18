from fastapi import APIRouter, Depends

from app.core.enum.llm_service_info import LLMServiceEnum
from app.core.response import ResponseMessage
from app.core.status import CommonCode
from app.schemas.api_key.create_model import APIKeyCreate
from app.schemas.api_key.decrypted_response_model import DecryptedAPIKeyResponse
from app.schemas.api_key.response_model import APIKeyResponse
from app.schemas.api_key.update_model import APIKeyUpdate
from app.services.api_key_service import APIKeyService, api_key_service

api_key_service_dependency = Depends(lambda: api_key_service)

router = APIRouter()


@router.post(
    "/create",
    response_model=ResponseMessage[APIKeyResponse],
    summary="API KEY 저장 (처음 한 번)",
    description="외부 AI 서비스의 API Key를 암호화하여 로컬 데이터베이스에 저장합니다.",
)
def store_api_key(
    api_key_data: APIKeyCreate, service: APIKeyService = api_key_service_dependency
) -> ResponseMessage[APIKeyResponse]:
    """
    - **service_name**: API Key가 사용될 외부 서비스 이름 (예: "OpenAI")
    - **api_key**: 암호화하여 저장할 실제 API Key (예: "sk-***..")
    """
    created_api_key = service.store_api_key(api_key_data)

    response_data = APIKeyResponse(
        id=created_api_key.id,
        service_name=created_api_key.service_name.value,
        created_at=created_api_key.created_at,
        updated_at=created_api_key.updated_at,
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
    api_keys_in_db = service.get_all_api_keys()

    response_data = [
        APIKeyResponse(
            id=api_key.id,
            service_name=api_key.service_name,
            created_at=api_key.created_at,
            updated_at=api_key.updated_at,
        )
        for api_key in api_keys_in_db
    ]
    return ResponseMessage.success(value=response_data, code=CommonCode.SUCCESS_GET_API_KEY)


@router.get(
    "/result/{serviceName}",
    response_model=ResponseMessage[APIKeyResponse],
    summary="특정 서비스의 API KEY 정보 조회",
)
def get_api_key_by_service_name(
    serviceName: LLMServiceEnum, service: APIKeyService = api_key_service_dependency
) -> ResponseMessage[APIKeyResponse]:
    """서비스 이름을 기준으로 특정 API Key의 메타데이터를 조회합니다."""
    api_key_in_db = service.get_api_key_by_service_name(serviceName)

    response_data = APIKeyResponse(
        id=api_key_in_db.id,
        service_name=api_key_in_db.service_name,
        created_at=api_key_in_db.created_at,
        updated_at=api_key_in_db.updated_at,
    )
    return ResponseMessage.success(value=response_data, code=CommonCode.SUCCESS_GET_API_KEY)


@router.get(
    "/internal/decrypted/{serviceName}",
    response_model=ResponseMessage[DecryptedAPIKeyResponse],
    summary="[내부용] 복호화된 API KEY 조회",
    description="내부 AI 서버와 같이, 신뢰된 서비스가 복호화된 API 키를 요청할 때 사용합니다. (외부 노출 금지)",
    # include_in_schema=False,  # Swagger 문서에 포함하지 않음
)
def get_decrypted_api_key(
    serviceName: LLMServiceEnum, service: APIKeyService = api_key_service_dependency
) -> ResponseMessage[DecryptedAPIKeyResponse]:
    """서비스 이름을 기준으로 API Key를 복호화하여 반환합니다."""
    decrypted_key = service.get_decrypted_api_key(serviceName.value)
    return ResponseMessage.success(
        value=DecryptedAPIKeyResponse(api_key=decrypted_key), code=CommonCode.SUCCESS_GET_API_KEY
    )


@router.put(
    "/modify/{serviceName}",
    response_model=ResponseMessage[APIKeyResponse],
    summary="특정 서비스의 API KEY 수정",
)
def update_api_key(
    serviceName: LLMServiceEnum,
    key_data: APIKeyUpdate,
    service: APIKeyService = api_key_service_dependency,
) -> ResponseMessage[APIKeyResponse]:
    """
    서비스 이름을 기준으로 특정 API Key를 새로운 값으로 수정합니다.
    - **service_name**: 수정할 서비스의 이름
    - **api_key**: 새로운 API Key
    """
    updated_api_key = service.update_api_key(serviceName.value, key_data)

    response_data = APIKeyResponse(
        id=updated_api_key.id,
        service_name=updated_api_key.service_name,
        created_at=updated_api_key.created_at,
        updated_at=updated_api_key.updated_at,
    )

    return ResponseMessage.success(value=response_data, code=CommonCode.SUCCESS_UPDATE_API_KEY)


@router.delete(
    "/remove/{serviceName}",
    response_model=ResponseMessage,
    summary="특정 서비스의 API KEY 삭제",
)
def delete_api_key(serviceName: LLMServiceEnum, service: APIKeyService = api_key_service_dependency) -> ResponseMessage:
    """
    서비스 이름을 기준으로 특정 API Key를 삭제합니다.
    - **service_name**: 삭제할 서비스의 이름
    """
    service.delete_api_key(serviceName.value)
    return ResponseMessage.success(code=CommonCode.SUCCESS_DELETE_API_KEY)
