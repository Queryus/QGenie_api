# app/api/user_db_api.py


from fastapi import APIRouter, Depends

from app.core.exceptions import APIException
from app.core.response import ResponseMessage
from app.core.status import CommonCode
from app.schemas.user_db.db_profile_model import DBProfileInfo, UpdateOrCreateDBProfile
from app.schemas.user_db.result_model import ColumnInfo, DBProfile, TableInfo
from app.services.user_db_service import UserDbService, user_db_service

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
    "/create/profile",
    response_model=ResponseMessage[str],
    summary="DB 프로필 저장",
)
def create_profile(
    create_db_info: UpdateOrCreateDBProfile,
    service: UserDbService = user_db_service_dependency,
) -> ResponseMessage[str]:
    create_db_info.validate_required_fields()
    result = service.create_profile(create_db_info)

    if not result.is_successful:
        raise APIException(result.code)
    return ResponseMessage.success(value=result.view_name, code=result.code)


@router.put(
    "/modify/profile",
    response_model=ResponseMessage[str],
    summary="DB 프로필 업데이트",
)
def update_profile(
    update_db_info: UpdateOrCreateDBProfile,
    service: UserDbService = user_db_service_dependency,
) -> ResponseMessage[str]:
    update_db_info.validate_required_fields()
    result = service.update_profile(update_db_info)

    if not result.is_successful:
        raise APIException(result.code)
    return ResponseMessage.success(value=result.view_name, code=result.code)


@router.delete(
    "/remove/{profile_id}",
    response_model=ResponseMessage[str],
    summary="DB 프로필 삭제",
)
def delete_profile(
    profile_id: str,
    service: UserDbService = user_db_service_dependency,
) -> ResponseMessage[str]:
    result = service.delete_profile(profile_id)

    if not result.is_successful:
        raise APIException(result.code)
    return ResponseMessage.success(value=result.view_name, code=result.code)


@router.get(
    "/find/all",
    response_model=ResponseMessage[list[DBProfile]],
    summary="DB 프로필 전체 조회",
)
def find_all_profile(
    service: UserDbService = user_db_service_dependency,
) -> ResponseMessage[list[DBProfile]]:

    result = service.find_all_profile()

    if not result.is_successful:
        raise APIException(result.code)
    return ResponseMessage.success(value=result.profiles, code=result.code)


@router.get(
    "/find/schemas/{profile_id}",
    response_model=ResponseMessage[list[str]],
    summary="특정 DB의 전체 스키마 조회",
)
def find_schemas(profile_id: str, service: UserDbService = user_db_service_dependency) -> ResponseMessage[list[str]]:

    db_info = service.find_profile(profile_id)
    result = service.find_schemas(db_info)

    if not result.is_successful:
        raise APIException(result.code)
    return ResponseMessage.success(value=result.schemas, code=result.code)


@router.get(
    "/find/tables/{profile_id}/{schema_name}",
    response_model=ResponseMessage[list[str]],
    summary="특정 스키마의 전체 테이블 조회",
)
def find_tables(
    profile_id: str, schema_name: str, service: UserDbService = user_db_service_dependency
) -> ResponseMessage[list[str]]:

    db_info = service.find_profile(profile_id)
    result = service.find_tables(db_info, schema_name)

    if not result.is_successful:
        raise APIException(result.code)
    return ResponseMessage.success(value=result.tables, code=result.code)


@router.get(
    "/find/columns/{profile_id}/{schema_name}/{table_name}",
    response_model=ResponseMessage[list[ColumnInfo]],
    summary="특정 테이블의 전체 컬럼 조회",
)
def find_columns(
    profile_id: str, schema_name: str, table_name: str, service: UserDbService = user_db_service_dependency
) -> ResponseMessage[list[ColumnInfo]]:

    db_info = service.find_profile(profile_id)
    result = service.find_columns(db_info, schema_name, table_name)

    if not result.is_successful:
        raise APIException(result.code)
    return ResponseMessage.success(value=result.columns, code=result.code)


@router.get(
    "/find/all-schemas/{profile_id}",
    response_model=ResponseMessage[list[TableInfo]],
    summary="특정 DB의 전체 스키마의 상세 정보 조회",
    description="테이블, 컬럼, 제약조건, 인덱스를 포함한 모든 스키마 정보를 반환합니다.",
)
def find_all_schema_info(
    profile_id: str, service: UserDbService = user_db_service_dependency
) -> ResponseMessage[list[TableInfo]]:

    db_info = service.find_profile(profile_id)
    full_schema_info = service.get_full_schema_info(db_info)

    return ResponseMessage.success(value=full_schema_info, code=CommonCode.SUCCESS)
