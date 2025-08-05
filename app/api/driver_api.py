# app/api/driver_api.py

from fastapi import APIRouter, Depends

from app.core.enum.db_driver import DBTypesEnum
from app.core.exceptions import APIException
from app.core.response import ResponseMessage
from app.core.status import CommonCode
from app.schemas.db_profile_model import DBProfileCreate
from app.schemas.driver_info import DriverInfo
from app.services.driver_service import DriverService, driver_service

driver_service_dependency = Depends(lambda: driver_service)

router = APIRouter()


@router.get(
    "/drivers/{driver_id}",
    response_model=ResponseMessage,
    summary="DB 드라이버 정보 조회",
)
def read_driver_info(
    driver_id: str,
    service: DriverService = driver_service_dependency,
) -> ResponseMessage:
    """경로 파라미터로 받은 driver_id에 해당하는 DB 드라이버의 지원 정보를 조회합니다."""
    db_type_enum = DBTypesEnum[driver_id.lower()]
    driver_info_data = DriverInfo.from_enum(db_type_enum)
    return ResponseMessage.success(value=service.read_driver_info(driver_info_data), code=CommonCode.SUCCESS_DB_INFO)


@router.post(
    "/test/db",
    response_model=ResponseMessage,
    summary="DB 연결 테스트",
)
def test_connection_endpoint(
    db_info: DBProfileCreate,
    service: DriverService = driver_service_dependency,
) -> ResponseMessage:
    """DB 연결 정보를 받아 연결 가능 여부를 테스트합니다."""
    try:
        db_info.validate_required_fields()
    except ValueError as e:
        raise APIException(CommonCode.NO_VALUE, *e.args) from e

    result = service.test_connection(db_info)
    if not result.is_successful:
        raise APIException(result.code)
    return ResponseMessage.success(code=result.code)
