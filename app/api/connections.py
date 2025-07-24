from fastapi import APIRouter

from app.services.driver_info_provider import db_driver_info

router = APIRouter()


@router.get("/connections/drivers/{driverId}")
def read_driver_info(driverId: str):
    return db_driver_info(driverId)
