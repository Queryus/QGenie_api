from pydantic import BaseModel, Field


class DecryptedAPIKeyResponse(BaseModel):
    """Decrypted API Key 응답용 스키마"""

    api_key: str = Field(..., description="복호화된 실제 API Key")
