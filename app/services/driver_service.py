# app/service/driver_service.py
import importlib
import logging
import os
import sqlite3

from app.core.exceptions import APIException
from app.core.status import CommonCode
from app.schemas.driver.driver_info_model import DriverInfo

logger = logging.getLogger(__name__)


class DriverService:
    def read_driver_info(self, driver_info: DriverInfo):
        try:
            driver_name = driver_info.driver_name

            if driver_name == "sqlite3":
                version = sqlite3.sqlite_version
                try:
                    path = sqlite3.__file__
                    size = os.path.getsize(path) if path else None
                except (TypeError, OSError) as e:
                    logger.exception(f"Driver import failed: {driver_info.driver_name}")
                    logger.exception(f"error: {e}")
                    path, size = None, None
            else:
                mod = importlib.import_module(driver_name)
                version = getattr(mod, "__version__", None)
                spec = getattr(mod, "__spec__", None)
                path = getattr(spec, "origin", None) if spec else None
                try:
                    size = os.path.getsize(path) if path and os.path.exists(path) else None
                except OSError as e:
                    logger.exception(f"Driver import failed: {driver_info.driver_name}")
                    logger.exception(f"error: {e}")
                    size = None

            return driver_info.update_from_module(version, size)
        except (ModuleNotFoundError, AttributeError, OSError) as e:
            logger.exception(f"Driver import failed: {driver_info.driver_name}")
            logger.exception(f"error: {e}")
            raise APIException(CommonCode.FAIL) from e


driver_service = DriverService()
