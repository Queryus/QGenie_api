# app/api/connect_driver.py

from fastapi import APIRouter

from app.core.db_driver_enum import DBTypesEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.schemas.driver_info import DriverInfo
from app.schemas.response import ResponseMessage
from app.services.driver_info_provider import db_driver_info

router = APIRouter()


@router.get("/drivers/{driverId}", response_model=ResponseMessage[DriverInfo], summary="DB 드라이버 정보 조회 API")
def read_driver_info(driverId: str):
    """DB 드라이버 정보 조회"""
    try:
        # DBTypesEnum 객체를 한 줄로 가져옵니다.
        db_type_enum = DBTypesEnum[driverId.lower()]

        return ResponseMessage.success(
            value=db_driver_info(DriverInfo.from_driver_info(db_type=db_type_enum.name, driver_name=db_type_enum.value))
        )
    # db_type 유효성 검사 실패시
    except KeyError:
        raise APIException(CommonCode.INVALID_ENUM_VALUE)
