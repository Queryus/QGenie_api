from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_check_mysql_driver_installed():
    # 드라이버 설치 되어있을 경우
    mock_spec = MagicMock()
    mock_spec.origin = "/usr/lib/python3.11/site-packages/mysql_driver.so"

    with patch("importlib.util.find_spec", return_value=mock_spec):
        with patch("os.path.getsize", return_value=123456):
            response = client.get("/connections/drivers/mysql")
            assert response.status_code == 200
            data = response.json()
            print(data)
            assert data["db_type"] == "mysql"
            assert data["is_installed"] is True
            assert data["driver_path"] == mock_spec.origin
            assert data["driver_name"] == "mysql_driver.so"
            assert data["driver_size_bytes"] == 123456


def test_check_mysql_driver_not_installed():
    # 드라이버 설치 안되어있을 경우
    with patch("importlib.util.find_spec", return_value=None):
        response = client.get("/connections/drivers/mysql")
        assert response.status_code == 200
        data = response.json()
        print(data)
        assert data["db_type"] == "mysql"
        assert data["is_installed"] is False
        assert data["driver_path"] is None
        assert data["driver_name"] is None
        assert data["driver_size_bytes"] is None
        assert "설치되어 있지 않습니다" in data["message"]


from app.services.driver_checker import check_driver


def test_check_driver_unsupported_db_direct():
    # 지원되지 않는 DB 타입을 넣었을 때
    unsupported_db = "unknown_db"
    response = check_driver(unsupported_db)

    # response는 DBDriverInfo 객체라 바로 속성 접근
    print(response)

    assert response.db_type == unsupported_db
    assert response.is_installed is False
    assert response.message == "지원되지 않는 DB 타입입니다."
    assert response.driver_path is None
    assert response.driver_name is None
    assert response.driver_size_bytes is None
    assert response.driver_version is None
