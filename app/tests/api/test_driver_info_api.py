from fastapi.testclient import TestClient

from app.main import app  # FastAPI 앱 객체

client = TestClient(app)


def test_api_supported_driver():
    response = client.get("/connections/drivers/mysql")
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "드라이버 정보를 성공적으로 불러왔습니다."
    assert body["data"]["db_type"] == "mysql"
    assert body["data"]["is_installed"] is True


def test_api_unsupported_driver():
    response = client.get("/connections/drivers/unknown-db")
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "지원되지 않는 DB입니다."
    assert body["data"] is None


def test_api_empty_driver():
    response = client.get("/connections/drivers/")
    assert response.status_code in [404, 422]  # 경로 누락이므로 상태코드로 판단
