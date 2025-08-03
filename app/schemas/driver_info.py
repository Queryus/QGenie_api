# app/schemas/driver_info.py
from pydantic import BaseModel

from app.core.db_driver_enum import DBTypesEnum


class DriverInfo(BaseModel):
    db_type: str
    is_installed: bool
    driver_name: str | None
    driver_version: str | None
    driver_size_bytes: int | None

    @classmethod
    def from_module(cls, db_type: str, driver_name: str, version: str | None, size: int | None):
        """
        설치된 드라이버의 모든 정보를 바탕으로 DriverInfo 객체를 생성합니다.
        `is_installed`는 항상 True로 설정됩니다.
        """
        return cls(
            db_type=db_type,
            is_installed=True,
            driver_name=driver_name,
            driver_version=version,
            driver_size_bytes=size,
        )

    @classmethod
    def from_driver_info(cls, db_type: str, driver_name: str):
        """
        최소한의 정보(DB 타입, 드라이버 이름)만으로 초기 DriverInfo 객체를 생성합니다.
        `is_installed`는 False로 설정됩니다.
        """
        return cls(
            db_type=db_type,
            is_installed=False,
            driver_name=driver_name,
            driver_version=None,
            driver_size_bytes=None,
        )

    @classmethod
    def from_enum(cls, db_type_enum: DBTypesEnum):
        """
        DBTypesEnum 객체를 인자로 받아, from_driver_info를 호출해 초기 객체를 생성합니다.
        """
        return cls.from_driver_info(db_type=db_type_enum.name, driver_name=db_type_enum.value)
