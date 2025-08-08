# app/api/user_db_api.py

from fastapi import APIRouter, Depends

from app.core.exceptions import APIException
from app.core.response import ResponseMessage
from app.schemas.user_db.db_profile_model import DBProfileInfo, SaveDBProfile
from app.services.user_db_service import UserDbService, user_db_service
from app.schemas.user_db.result_model import SaveProfileResult

user_db_service_dependency = Depends(lambda: user_db_service)

router = APIRouter()


@router.post(
    "/connect/test",
    response_model=ResponseMessage[bool],
    summary="DB 연결 테스트",
)
def connection_test(
    db_info: DBProfileInfo,
    service: UserDbService = user_db_service_dependency,
) -> ResponseMessage[bool]:
    """DB 연결 정보를 받아 연결 가능 여부를 테스트합니다."""
    db_info.validate_required_fields()
    result = service.connection_test(db_info)

    if not result.is_successful:
        raise APIException(result.code)
    return ResponseMessage.success(value=result.is_successful, code=result.code)

@router.post(
    "/save/profile",
    response_model=ResponseMessage[str],
    summary="DB 프로필 저장",
)
def save_profile(
    save_db_info: SaveDBProfile,
    service: UserDbService = user_db_service_dependency,
) -> ResponseMessage[str]:
    """DB 연결 정보를 저장합니다."""
    save_db_info.validate_required_fields()
    result = service.save_profile(save_db_info)

    if not result.is_successful:
        raise APIException(result.code)
    return ResponseMessage.success(value=result.view_name, code=result.code)
