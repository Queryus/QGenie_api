# app/api/user_db_api.py

from fastapi import APIRouter, Depends
from typing import List

from app.core.exceptions import APIException
from app.core.response import ResponseMessage
from app.schemas.user_db.db_profile_model import DBProfileInfo, SaveDBProfile
from app.services.user_db_service import UserDbService, user_db_service
from app.schemas.user_db.result_model import DBProfile

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
    save_db_info.validate_required_fields()
    result = service.save_profile(save_db_info)

    if not result.is_successful:
        raise APIException(result.code)
    return ResponseMessage.success(value=result.view_name, code=result.code)

@router.get(
    "/find/all",
    response_model=ResponseMessage[List[DBProfile]],
    summary="DB 프로필 전체 조회",
)
def find_all_profile(
    service: UserDbService = user_db_service_dependency,
) -> ResponseMessage[List[DBProfile]]:
    result = service.find_all_profile()

    if not result.is_successful:
        raise APIException(result.code)
    return ResponseMessage.success(value=result.profiles, code=result.code)
