# main.py
import os
import sys

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from app.api import health_api
from app.api.api_router import api_router
from app.core.all_logging import log_requests_middleware
from app.core.exceptions import (
    APIException,
    api_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
)
from app.db.init_db import initialize_database

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# 실행 파일 내부에서 assets 폴더 경로를 찾는 로직
def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# 애플리케이션 시작 전 .env 파일 로드
env_path = resource_path("assets/.env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print(f".env 파일을 성공적으로 로드했습니다: {env_path}")
else:
    print(f"경고: .env 파일을 찾을 수 없습니다. ({env_path})")

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
