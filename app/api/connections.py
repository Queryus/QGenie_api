from fastapi import APIRouter

from app.schemas.db_driver_info import DBDriverInfo
from app.services.driver_checker import check_driver, is_python_environment

router = APIRouter()


@router.get("/connections/drivers/{driverId}", response_model=DBDriverInfo)
def get_driver_info(driverId: str):
    return check_driver(driverId)


@router.get("/environment/python")
def check_python_environment():
    return {"is_python_environment": is_python_environment()}
