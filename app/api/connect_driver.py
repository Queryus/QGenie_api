# app/api/connect_driver.py

from fastapi import APIRouter

from app.core.driver_enum import DriverEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.schemas.driver_info import DriverInfo
from app.schemas.response import ResponseMessage
from app.services.driver_info_provider import db_driver_info

router = APIRouter()


@router.get("/drivers/{driverId}", response_model=ResponseMessage[DriverInfo], summary="DB 드라이버 정보 조회 API")
def read_driver_info(driverId: str):
    """DB 드라이버 정보 조회"""
    for driver in DriverEnum:
        if driver.db_type == driverId:
            return ResponseMessage.success(value=db_driver_info(driver.db_type, driver.driver_module))

    # db_type 초기 유효성 검사 실패시
    raise APIException(CommonCode.INVALID_ENUM_VALUE)
