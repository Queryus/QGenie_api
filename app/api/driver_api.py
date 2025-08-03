# app/api/driver_api.py

from fastapi import APIRouter

from app.core.db_driver_enum import DBTypesEnum
from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.schemas.driver_info import DriverInfo
from app.schemas.response import ResponseMessage
from app.services.driver_service import db_driver_info

router = APIRouter()


@router.get("/drivers/{driverId}", response_model=ResponseMessage[DriverInfo], summary="DB 드라이버 정보 조회 API")
def read_driver_info(driverId: str):
    """DB 드라이버 정보 조회"""
    try:
        # DBTypesEnum에서 driverID에 맞는 객체를 가져옵니다.
        db_type_enum = DBTypesEnum[driverId.lower()]
        return ResponseMessage.success(value=db_driver_info(DriverInfo.from_enum(db_type_enum)))
    # db_type_enum 유효성 검사 실패
    except KeyError:
        raise APIException(CommonCode.INVALID_ENUM_VALUE)
