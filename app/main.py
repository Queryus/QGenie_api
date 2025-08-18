# main.py

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api import health_api
from app.api.api_router import api_router
from app.core.exceptions import (
    APIException,
    api_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
)
from app.db.init_db import initialize_database

from starlette.middleware.base import BaseHTTPMiddleware
from app.core.all_logging import log_requests_middleware

app = FastAPI()

# 전체 로그 찍는 부분
app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests_middleware)

# 전역 예외 처리기 등록
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 라우터
app.include_router(health_api.router)
app.include_router(api_router, prefix="/api")

# initialize_database 함수가 호출되어 테이블이 생성되거나 이미 존재함을 확인합니다.
initialize_database()

if __name__ == "__main__":
    # Uvicorn 서버를 시작합니다.
    uvicorn.run(app, host="0.0.0.0", port=39722)
