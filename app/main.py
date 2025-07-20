# main.py
import os
import socket  # 소켓 모듈 임포트

import uvicorn
from fastapi import FastAPI

from app.api import health  # 헬스체크

app = FastAPI()

# 헬스 체크 라우터
app.include_router(health.router)


@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI Backend!"}


# 이 부분이 추가된 동적 포트 할당 로직입니다.
if __name__ == "__main__":
    # 1. 환경 변수 'PORT'가 있으면 해당 포트를 사용합니다.
    # 2. 없으면 사용 가능한 임시 포트를 찾습니다.
    port_from_env = os.getenv("PORT")

    if port_from_env:
        port = int(port_from_env)
        print(f"Using port from environment variable: {port}")
    else:
        # 시스템에서 사용 가능한 임시 포트를 찾습니다.
        # 포트 0을 바인딩하면 운영체제가 사용 가능한 포트를 할당해 줍니다.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", 0))  # 0.0.0.0에 포트 0을 바인딩
            port = s.getsockname()[1]  # 할당된 포트 번호 가져오기
            print(f"Dynamically assigned port: {port}")

    # Uvicorn 서버를 시작합니다.
    uvicorn.run(app, host="0.0.0.0", port=port)
