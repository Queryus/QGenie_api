# app/api/driver_api.py

from fastapi import APIRouter, Depends

from app.core.enum.db_driver import DBTypesEnum
from app.core.exceptions import APIException
from app.core.response import ResponseMessage
from app.core.status import CommonCode
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
    try:
        db_type_enum = DBTypesEnum[driver_id.lower()]
        driver_info_data = DriverInfo.from_enum(db_type_enum)
        return ResponseMessage.success(value=service.read_driver_info(driver_info_data))
    except KeyError:
        raise APIException(CommonCode.INVALID_ENUM_VALUE) from KeyError
