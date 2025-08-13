from pydantic import Field

from app.schemas.annotation.base_model import RequestBase


class AnnotationCreateRequest(RequestBase):
    """어노테이션 생성 요청 스키마"""

    db_profile_id: str = Field(..., description="어노테이션을 생성할 DB 프로필의 고유 ID")

    def validate(self):
        self.validate_required_fields(["db_profile_id"])
