# app/schemas/user_db/connect_test_result_model.py

from pydantic import BaseModel, Field

from app.core.status import CommonCode


class TestConnectionResult(BaseModel):
    is_successful: bool = Field(..., description="성공 여부")
    code: CommonCode = Field(None, description="결과 코드")
