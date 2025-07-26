from unittest import mock

from app.api.connect_driver import DriverEnum
from app.services.driver_info_provider import db_driver_info


# 드라이버 설치 되었을 때
def test_supported_driver_installed():
    driver = DriverEnum.mysql
    result = db_driver_info(driver.value, driver.driver_module)
    print(result)


# 존재하지 않는 DB 타입을 넘겼을 때 (Enum 변환 실패)
def test_invalid_enum_value():
    try:
        DriverEnum("nonexistent-driver")
        assert False  # 실패하지 않으면 오류!
    except ValueError as e:
        print(f"[Enum 변환 실패] {e}")  # 콘솔에 예외 메시지 출력
        assert True


# 빈 값 넘겼을 때 -> 제거: Enum 유효성 검사로 인해 필요성 없음


# importlib 실패 상황 테스트
def test_driver_import_failure_at_api():
    with mock.patch("importlib.import_module", side_effect=ModuleNotFoundError("모듈 없음")):
        driver = DriverEnum.mysql
        result = db_driver_info(driver.value, driver.driver_module)
        print(result)
