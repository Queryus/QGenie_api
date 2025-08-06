from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.core.enum.llm_service import LLMServiceEnum


class ApiKeyCredentialBase(BaseModel):
    service_name: LLMServiceEnum = Field(..., description="외부 서비스 이름")


class ApiKeyCredentialCreate(ApiKeyCredentialBase):
    api_key: str = Field(..., description="암호화하여 저장할 실제 API Key")

    @field_validator("api_key", mode="after")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v or v.isspace():
            raise ValueError("API key cannot be empty or just whitespace.")
        return v


class ApiKeyCredentialInDB(ApiKeyCredentialBase):
    id: str
    api_key: str  # DB 모델에서는 암호화된 키를 의미
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApiKeyCredentialResponse(ApiKeyCredentialBase):
    id: str
    api_key_encrypted: str = Field(..., description="암호화된 API Key")
    created_at: datetime
    updated_at: datetime
