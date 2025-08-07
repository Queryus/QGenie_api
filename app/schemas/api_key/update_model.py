from pydantic import BaseModel, Field, field_validator


class APIKeyUpdate(BaseModel):
    """API Key 수정을 위한 스키마"""

    api_key: str = Field(..., description="새로운 API Key")

    @field_validator("api_key", mode="after")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v or v.isspace():
            raise ValueError("API key cannot be empty or just whitespace.")
        return v
