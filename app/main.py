# main.py

import uvicorn
from fastapi import FastAPI

from app.api import health  # 헬스 체크
from app.core.port import get_available_port  # 동적 포트 할당
from app.api.api_router import api_router


from app.core.exceptions import (
    APIException,
    api_exception_handler,
    generic_exception_handler
)

app = FastAPI()

# 전역 예외 처리기 등록
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# 라우터
app.include_router(health.router)
app.include_router(api_router, prefix="/api")

@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI Backend!"}


if __name__ == "__main__":
    # 동적 할당 로직
    port = get_available_port()
    # Uvicorn 서버를 시작합니다.
    uvicorn.run(app, host="0.0.0.0", port=port)
