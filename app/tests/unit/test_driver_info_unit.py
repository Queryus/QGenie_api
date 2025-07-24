import pytest

from app.services.driver_info_provider import db_driver_info


# 설치된 DB 드라이버 중 하나를 테스트 (환경에 따라 달라질 수 있음)
def test_supported_driver_installed():
    result = db_driver_info("mysql")
    assert result["message"] == "드라이버 정보를 성공적으로 불러왔습니다."
    assert result["data"] is not None
    assert result["data"]["db_type"] == "mysql"
    assert result["data"]["is_installed"] is True
    assert result["data"]["driver_name"] in ["pymysql", "mysql.connector"]


# 존재하지 않는 DB 타입을 넘겼을 때
def test_unsupported_driver():
    result = db_driver_info("unknown-db")
    assert result["message"] == "지원되지 않는 DB입니다."
    assert result["data"] is None


# 빈 값 넘겼을 때
def test_empty_input():
    result = db_driver_info("")
    assert result["message"] == "지원되지 않는 DB입니다."
    assert result["data"] is None


# 지원은 하지만 환경에 설치되지 않은 드라이버를 일부러 테스트
@pytest.mark.skip(reason="환경에 따라 설치 여부가 다르므로 건너뜀")
def test_supported_but_not_installed():
    result = db_driver_info("oracle")
    assert result["message"] in [
        "드라이버 정보를 성공적으로 불러왔습니다.",
        "드라이버 정보를 가져오지 못했습니다. 다시 시도해주세요.",
    ]


# 함수 강제 실패 테스트
def test_import_fails_and_fallback_message():
    from unittest import mock

    with mock.patch("importlib.import_module", side_effect=ModuleNotFoundError("모듈 없음")):
        result = db_driver_info("mysql")
        assert result["message"] == "드라이버 정보를 가져오지 못했습니다. 다시 시도해주세요."
        assert result["data"] is None
