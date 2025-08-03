# app/service/driver_service.py
import importlib
import os

from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.schemas.driver_info import DriverInfo


def db_driver_info(driver_info: DriverInfo):
    try:
        mod = importlib.import_module(driver_info.driver_name)
        version = getattr(mod, "__version__", None)
        path = getattr(mod.__spec__, "origin", None)
        size = os.path.getsize(path) if path else None

        return driver_info.update_from_module(version, size)

    except (ModuleNotFoundError, AttributeError, OSError):
        raise APIException(CommonCode.FAIL)
