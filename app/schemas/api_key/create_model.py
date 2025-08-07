# app/schemas/api_key/create_model.py
from pydantic import Field, field_validator

from app.schemas.api_key.base_model import APIKeyBase


class APIKeyCreate(APIKeyBase):
    """API Key 생성을 위한 스키마"""

    api_key: str = Field(..., description="암호화하여 저장할 실제 API Key")

    @field_validator("api_key", mode="after")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v or v.isspace():
            raise ValueError("API key cannot be empty or just whitespace.")
        return v
