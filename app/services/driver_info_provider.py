# app/service/driver_info_provider.py

import importlib
import os

from app.schemas.driver_info import DriverInfo, DriverInfoResponse


def db_driver_info(db_type: str, module_name: str) -> DriverInfoResponse:
    try:
        mod = importlib.import_module(module_name)
        version = getattr(mod, "__version__", None)
        path = getattr(mod.__spec__, "origin", None)
        size = os.path.getsize(path) if path else None

        info = DriverInfo(
            db_type=db_type,
            is_installed=True,
            driver_name=module_name,
            driver_version=version,
            driver_size_bytes=size,
        )
        return DriverInfoResponse.success(info)

    except (ModuleNotFoundError, AttributeError, OSError) as e:
        return DriverInfoResponse.error(e)
