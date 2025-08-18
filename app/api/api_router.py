# app/api/api_router.py

from fastapi import APIRouter

from app.api import annotation_api, api_key_api, chat_tab_api, driver_api, query_api, test_api, user_db_api

api_router = APIRouter()

# 테스트 라우터
api_router.include_router(test_api.router, prefix="/test", tags=["Test"])

# 라우터
api_router.include_router(driver_api.router, prefix="/driver", tags=["Driver"])
api_router.include_router(user_db_api.router, prefix="/user/db", tags=["UserDb"])
api_router.include_router(api_key_api.router, prefix="/keys", tags=["API Key"])
api_router.include_router(chat_tab_api.router, prefix="/chats", tags=["AI Chat"])
api_router.include_router(annotation_api.router, prefix="/annotations", tags=["Annotation"])
api_router.include_router(query_api.router, prefix="/query", tags=["query"])
