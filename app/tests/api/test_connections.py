import subprocess
import sys
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.driver_checker import check_driver

print(f"Python 실행 경로: {sys.executable}")
client = TestClient(app)


def test_check_mysql_driver_installed():
    mock_spec = MagicMock()
    mock_spec.origin = "/usr/lib/python3.11/site-packages/mysql_driver.so"

    with patch("app.services.driver_checker.is_python_environment", return_value=True):
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


def test_check_mysql_driver_not_installed_python_env():
    # Python 환경이지만 드라이버가 설치되어 있지 않은 경우
    with patch("app.services.driver_checker.is_python_environment", return_value=True):
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


def test_check_driver_not_python_environment_driver_installed():
    # Python 환경이 아니고, OS 레벨에서 설치되어 있다고 판단되는 경우
    with patch("app.services.driver_checker.is_python_environment", return_value=False):
        # subprocess.run 결과를 mocking: 설치되어 있다고 판단
        mock_subproc_result = subprocess.CompletedProcess(
            args=["which", "mysql"], returncode=0, stdout=b"/usr/bin/mysql\n"
        )
        with patch("subprocess.run", return_value=mock_subproc_result):
            response = client.get("/connections/drivers/mysql")
            assert response.status_code == 200
            data = response.json()
            print(data)
            assert data["db_type"] == "mysql"
            assert data["is_installed"] is True
            assert "Python 환경이 아니어서 OS 레벨로 설치 여부를 확인했습니다." in data["message"]


def test_check_driver_not_python_environment_driver_not_installed():
    # Python 환경이 아니고, OS 레벨에서 설치 안되어 있다고 판단되는 경우
    with patch("app.services.driver_checker.is_python_environment", return_value=False):
        mock_subproc_result = subprocess.CompletedProcess(args=["which", "mysql"], returncode=1, stdout=b"")
        with patch("subprocess.run", return_value=mock_subproc_result):
            response = client.get("/connections/drivers/mysql")
            assert response.status_code == 200
            data = response.json()
            print(data)
            assert data["db_type"] == "mysql"
            assert data["is_installed"] is False
            assert "Python 환경이 아니며 OS 레벨에서도 드라이버를 찾을 수 없습니다." in data["message"]


def test_check_driver_unsupported_db_direct():
    unsupported_db = "unknown_db"
    response = check_driver(unsupported_db)

    print(response)

    assert response.db_type == unsupported_db
    assert response.is_installed is False
    assert response.message == "지원되지 않는 DB 타입입니다."
    assert response.driver_path is None
    assert response.driver_name is None
    assert response.driver_size_bytes is None
    assert response.driver_version is None
