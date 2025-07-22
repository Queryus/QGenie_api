from pydantic import BaseModel


class DBDriverInfo(BaseModel):
    db_type: str
    is_installed: bool
    message: str
    driver_path: str | None = None
    driver_name: str | None = None
    driver_size_bytes: int | None = None
    driver_version: str | None = None
    os_name: str | None = None
    os_full_name: str | None = None
