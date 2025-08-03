# app/service/driver_info_provider.py
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

        return DriverInfo.from_module(driver_info.db_type, driver_info.driver_name, version, size)

    except (ModuleNotFoundError, AttributeError, OSError):
        raise APIException(CommonCode.FAIL)
