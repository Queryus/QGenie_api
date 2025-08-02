from fastapi import APIRouter

from app.api import test_api
api_router = APIRouter()

# 테스트 라우터
api_router.include_router(test_api.router, prefix="/test", tags=["Test"])

# 라우터
# api_router.include_router(connect_driver.router, prefix="/connections", tags=["Driver"])