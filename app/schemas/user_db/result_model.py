# app/schemas/user_db/result_model.py

from pydantic import BaseModel, Field

from app.core.status import CommonCode

# 기본 반환 모델
class BasicResult(BaseModel):
    is_successful: bool = Field(..., description="성공 여부")
    code: CommonCode = Field(None, description="결과 코드")

# 디비 정보 저장
class SaveProfileResult(BasicResult):
    """DB 조회 결과를 위한 확장 모델"""
    view_name: str = Field(..., description="저장된 디비명")
