# app/api/connect_driver.py

from fastapi import APIRouter

from app.schemas.driver_info import DriverEnum, DriverInfoResponse
from app.services.driver_info_provider import db_driver_info

router = APIRouter(tags=["Driver"])


@router.get(
    "/connections/drivers/{driver_id}",
    summary="DB 드라이버 정보 조회 API",
    response_model=DriverInfoResponse,
)
def read_driver_info(driver_id: DriverEnum):
    module = driver_id.driver_module
    db_type = driver_id.value
    return db_driver_info(db_type, module)
