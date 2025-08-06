# app/service/driver_service.py
import importlib
import os
import sqlite3

from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.schemas.driver.driver_info_model import DriverInfo


class DriverService:
    def read_driver_info(self, driver_info: DriverInfo):
        try:
            driver_name = driver_info.driver_name

            if driver_name == "sqlite3":
                version = sqlite3.sqlite_version
                path = sqlite3.__file__

            else:
                mod = importlib.import_module(driver_name)
                version = getattr(mod, "__version__", None)
                path = getattr(mod.__spec__, "origin", None)

            size = os.path.getsize(path) if path else None
            return driver_info.update_from_module(version, size)
        except (ModuleNotFoundError, AttributeError, OSError) as e:
            raise APIException(CommonCode.FAIL) from e


driver_service = DriverService()
