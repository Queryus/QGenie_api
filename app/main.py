# main.py

import uvicorn
from fastapi import FastAPI

from app.api import (
    connect_driver,  # 드라이버 확인
    health,  # 헬스 체크
)
from app.api.api_router import api_router
from app.core.exceptions import APIException, api_exception_handler, generic_exception_handler

app = FastAPI()

# 전역 예외 처리기 등록
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# 라우터
app.include_router(health.router)
app.include_router(api_router, prefix="/api")
app.include_router(connect_driver.router, prefix="/api")


if __name__ == "__main__":
    # Uvicorn 서버를 시작합니다.
    uvicorn.run(app, host="0.0.0.0", port=39722)
