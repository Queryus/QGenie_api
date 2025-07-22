from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_check_python_environment_api():
    response = client.get("/environment/python")
    assert response.status_code == 200
    data = response.json()
    print("[python env result]", data)

    assert "is_python_environment" in data
    assert isinstance(data["is_python_environment"], bool)
