# app/schemas/driver_info.py
from pydantic import BaseModel


class DriverInfo(BaseModel):
    db_type: str
    is_installed: bool
    driver_name: str | None
    driver_version: str | None
    driver_size_bytes: int | None

    @classmethod
    def from_module(
        cls, db_type: str, driver_name: str, version: str | None, size: int | None
    ):  # 자기 자신의 인스턴스를 생성하여 반환
        return cls(
            db_type=db_type,
            is_installed=True,
            driver_name=driver_name,
            driver_version=version,
            driver_size_bytes=size,
        )

    @classmethod
    def from_driver_info(cls, db_type: str, driver_name: str):
        # 최소한의 정보로 객체를 생성할 때 사용
        return cls(
            db_type=db_type,
            is_installed=False,
            driver_name=driver_name,
            driver_version=None,
            driver_size_bytes=None,
        )
