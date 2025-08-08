# app/core/all_logging.py

import logging
from fastapi import Request

# 로깅 기본 설정 (애플리케이션 시작 시 한 번만 구성)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s", # [수정] 로그 레벨(INFO, ERROR)을 포함
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def log_requests_middleware(request: Request, call_next):
    """
    모든 API 요청과 에러에 대한 로그를 남기는 미들웨어입니다.
    """
    endpoint = f"{request.method} {request.url.path}"

    # 일반 요청 로그를 남깁니다.
    logging.info(f"엔드포인트: {endpoint}")

    try:
        # 다음 미들웨어 또는 실제 엔드포인트를 호출합니다.
        response = await call_next(request)
        return response
    except Exception as e:
        # [수정] 에러 발생 시, exc_info=True를 추가하여 전체 트레이스백을 함께 기록합니다.
        # 메시지 형식도 "ERROR 엔드포인트:"로 변경합니다.
        logging.error(f"ERROR 엔드포인트: {endpoint}", exc_info=True)
        # 예외를 다시 발생시켜 FastAPI의 전역 예외 처리기가 최종 응답을 만들도록 합니다.
        raise e

