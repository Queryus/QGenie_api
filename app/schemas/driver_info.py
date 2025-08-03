# app/schemas/driver_info.py
from pydantic import BaseModel

from app.core.enum.db_driver import DBTypesEnum


class DriverInfo(BaseModel):
    db_type: str
    is_installed: bool
    driver_name: str | None
    driver_version: str | None
    driver_size_bytes: int | None

    def update_from_module(self, version: str | None, size: int | None):
        """
        객체 자신의 속성을 직접 업데이트하여 설치된 드라이버 정보를 채웁니다.
        """
        self.is_installed = True
        self.driver_version = version
        self.driver_size_bytes = size

        return self

    @classmethod
    def from_enum(cls, db_type_enum: DBTypesEnum):
        """
        DBTypesEnum 객체를 인자로 받아, db_type, driver_name만으로 driverInfo 객체를 생성합니다.
        `is_installed`는 False로 설정됩니다.
        """
        db_type = db_type_enum.name
        driver_name = db_type_enum.value
        return cls(
            db_type=db_type,
            is_installed=False,
            driver_name=driver_name,
            driver_version=None,
            driver_size_bytes=None,
        )
