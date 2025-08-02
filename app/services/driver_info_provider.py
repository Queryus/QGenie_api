# app/service/driver_info_provider.py
from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.schemas.driver_info import DriverInfo


def db_driver_info(db_type: str, module_name: str):
    try:
        info = DriverInfo.from_module(db_type, module_name)
        return info

    except (ModuleNotFoundError, AttributeError, OSError):
        raise APIException(CommonCode.FAIL)
