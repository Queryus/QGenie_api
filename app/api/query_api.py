# app/api/query_api.py


from typing import Any

from fastapi import APIRouter, Depends

from app.core.exceptions import APIException
from app.core.response import ResponseMessage
from app.schemas.query.query_model import QueryInfo, RequestExecutionQuery
from app.services.query_service import QueryService, query_service
from app.services.user_db_service import UserDbService, user_db_service

query_service_dependency = Depends(lambda: query_service)
user_db_service_dependency = Depends(lambda: user_db_service)

router = APIRouter()


@router.post(
    "/execute",
    response_model=ResponseMessage[dict | str | None],
    summary="쿼리 실행",
)
def execution(
    query_info: RequestExecutionQuery,
    service: QueryService = query_service_dependency,
    userDbservice: UserDbService = user_db_service_dependency,
) -> ResponseMessage[dict | str | None]:

    db_info = userDbservice.find_profile(query_info.user_db_id)
    result = service.execution(query_info, db_info)

    if not result.is_successful:
        raise APIException(result.code)
    return ResponseMessage.success(value=result.data, code=result.code)


@router.post(
    "/execute/test",
    response_model=ResponseMessage[Any],
    summary="쿼리 실행",
)
def execution_test(
    query_info: QueryInfo,
    service: QueryService = query_service_dependency,
    userDbservice: UserDbService = user_db_service_dependency,
) -> ResponseMessage[Any]:

    db_info = userDbservice.find_profile(query_info.user_db_id)
    result = service.execution_test(query_info, db_info)

    return ResponseMessage.success(value=result.data, code=result.code)


@router.get(
    "/find/{chat_tab_id}",
    response_model=ResponseMessage[dict],
    summary="쿼리 실행 내역 조회",
)
def find_query_history(
    chat_tab_id: str,
    service: QueryService = query_service_dependency,
) -> ResponseMessage[dict]:

    result = service.find_query_history(chat_tab_id)

    if not result.is_successful:
        raise APIException(result.code)
    return ResponseMessage.success(value=result.data, code=result.code)
