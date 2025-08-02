# app/schemas/driver_info.py
import importlib
import os

from pydantic import BaseModel


class DriverInfo(BaseModel):
    db_type: str
    is_installed: bool
    driver_name: str | None
    driver_version: str | None
    driver_size_bytes: int | None

    @classmethod
    def from_module(cls, db_type: str, module_name: str):
        """모듈 이름으로부터 DriverInfo 객체를 생성하는 팩토리 메서드"""
        # 서비스에 있던 로직을 이곳으로 이동
        mod = importlib.import_module(module_name)
        version = getattr(mod, "__version__", None)
        path = getattr(mod.__spec__, "origin", None)
        size = os.path.getsize(path) if path else None

        # 자기 자신의 인스턴스를 생성하여 반환
        return cls(
            db_type=db_type,
            is_installed=True,
            driver_name=module_name,
            driver_version=version,
            driver_size_bytes=size,
        )
