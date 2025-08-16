# app/api/query_api.py


from fastapi import APIRouter, Depends

from app.core.exceptions import APIException
from app.core.response import ResponseMessage
from app.schemas.query.query_model import QueryInfo
from app.services.query_service import QueryService, query_service
from app.services.user_db_service import UserDbService, user_db_service

query_service_dependency = Depends(lambda: query_service)
user_db_service_dependency = Depends(lambda: user_db_service)

router = APIRouter()


@router.post(
    "/execution",
    response_model=ResponseMessage[dict | str | None],
    summary="쿼리 실행",
)
def execution(
    query_info: QueryInfo,
    service: QueryService = query_service_dependency,
    userDbservice: UserDbService = user_db_service_dependency,
) -> ResponseMessage[dict | str | None]:

    query_info.validate_required_fields()
    db_info = userDbservice.find_profile(query_info.user_db_id)
    result = service.execution(query_info, db_info)

    if not result.is_successful:
        raise APIException(result.code)
    return ResponseMessage.success(value=result.data, code=result.code)
