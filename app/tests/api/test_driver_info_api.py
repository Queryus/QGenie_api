from fastapi.testclient import TestClient

from app.main import app  # FastAPI 앱 객체

client = TestClient(app)


def test_api_supported_driver():
    response = client.get("api/connections/drivers/mysql")
    assert response.status_code == 200

    body = response.json()
    assert body["message"] == "드라이버 정보를 성공적으로 불러왔습니다."
    assert body["data"]["db_type"] == "mysql"
    assert body["data"]["is_installed"] is True
    assert body["data"]["driver_name"] == "mysql.connector"
    assert isinstance(body["data"]["driver_size_bytes"], int)


def test_api_unsupported_driver():
    response = client.get("api/connections/drivers/unknown-db")
    assert response.status_code == 422  # ❗ Enum validation이 터짐

    body = response.json()
    assert body["detail"][0]["msg"].startswith("Input should be")
    assert body["detail"][0]["loc"] == ["path", "driver_id"]


def test_api_empty_driver():
    response = client.get("api/connections/drivers/")  # 누락된 경로
    assert response.status_code in [404, 422]
