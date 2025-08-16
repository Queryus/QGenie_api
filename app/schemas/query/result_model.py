# app/schemas/user_db/result_model.py

from pydantic import BaseModel, Field

from app.core.status import CommonCode


# 기본 반환 모델
class BasicResult(BaseModel):
    is_successful: bool = Field(..., description="성공 여부")
    code: CommonCode = Field(None, description="결과 코드")


class ExecutionSelectResult(BasicResult):
    """DB 조회 결과를 위한 확장 모델"""

    data: dict = Field(..., description="쿼리 조회 후 결과 - 데이터")


class ExecutionResult(BasicResult):
    """DB 결과를 위한 확장 모델"""

    data: str = Field(..., description="쿼리 수행 후 결과")


class InsertLocalDBResult(BasicResult):
    """DB 결과를 위한 확장 모델"""

    data: str = Field(..., description="쿼리 수행 후 결과")


class SelectQueryHistoryResult(BasicResult):
    """DB 결과를 위한 확장 모델"""

    data: dict = Field(..., description="쿼리 이력 조회")
