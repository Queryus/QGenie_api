from fastapi import APIRouter

from app.api import driver_api, test_api

api_router = APIRouter()

# 테스트 라우터
api_router.include_router(test_api.router, prefix="/test", tags=["Test"])

# 라우터
api_router.include_router(driver_api.router, prefix="/driver", tags=["Driver"])
# api_router.include_router(user_db_api.router, prefix="/user/db", tags=["UserDb"])
