import sqlite3

from app.core.exceptions import APIException
from app.core.security import AES256
from app.core.status import CommonCode
from app.core.utils import generate_prefixed_uuid, get_db_path
from app.schemas.api_key import APIKeyInDB, APIKeyStore, APIKeyUpdate


def store_api_key(credential_data: APIKeyStore) -> APIKeyInDB:
    """API Key를 암호화하여 데이터베이스에 저장합니다."""
    encrypted_key = AES256.encrypt(credential_data.api_key)
    new_id = generate_prefixed_uuid()

    db_path = get_db_path()
    conn = None
    try:
        # timeout을 10초로 설정하여 BUSY 상태에서 대기하도록 함
        conn = sqlite3.connect(str(db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO ai_credential (id, service_name, api_key)
            VALUES (?, ?, ?)
            """,
            (new_id, credential_data.service_name.value, encrypted_key),
        )
        conn.commit()

        cursor.execute("SELECT * FROM ai_credential WHERE id = ?", (new_id,))
        created_row = cursor.fetchone()

        if not created_row:
            raise APIException(CommonCode.FAIL, "Failed to retrieve the created credential.")

        return APIKeyInDB.model_validate(dict(created_row))

    except sqlite3.IntegrityError as e:
        # UNIQUE 제약 조건 위반 (service_name)
        raise APIException(CommonCode.DUPLICATION) from e
    except sqlite3.Error as e:
        # "database is locked" 오류를 명시적으로 처리
        if "database is locked" in str(e):
            raise APIException(CommonCode.DB_BUSY) from e
        # 기타 모든 sqlite3 오류
        raise APIException(CommonCode.FAIL) from e
    finally:
        if conn:
            conn.close()


def get_all_api_keys() -> list[APIKeyInDB]:
    """데이터베이스에 저장된 모든 API Key를 조회합니다."""
    db_path = get_db_path()
    conn = None
    try:
        conn = sqlite3.connect(str(db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM ai_credential")
        rows = cursor.fetchall()

        # 저장된 API Key가 없으면 그냥 빈 리스트를 반환할지?
        # 아니면 예외처리를 해줄지?
        return [APIKeyInDB.model_validate(dict(row)) for row in rows]

    # TODO: 발생가능한 에러들 전부 테스트 해보며 예외처리 세분화
    except sqlite3.Error as e:
        print(e.__class__)
        raise APIException(CommonCode.FAIL) from e
    finally:
        if conn:
            conn.close()


def get_api_key_by_service_name(service_name: str) -> APIKeyInDB:
    """서비스 이름으로 특정 API Key를 조회합니다."""
    db_path = get_db_path()
    conn = None
    try:
        conn = sqlite3.connect(str(db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM ai_credential WHERE service_name = ?", (service_name,))
        row = cursor.fetchone()

        if not row:
            raise APIException(CommonCode.NO_SEARCH_DATA)

        return APIKeyInDB.model_validate(dict(row))

    # TODO: 발생가능한 에러들 전부 테스트 해보며 예외처리 세분화
    except sqlite3.Error as e:
        raise APIException(CommonCode.FAIL) from e
    finally:
        if conn:
            conn.close()


def update_api_key(service_name: str, key_data: APIKeyUpdate) -> APIKeyInDB:
    """서비스 이름에 해당하는 API Key를 수정합니다."""
    encrypted_key = AES256.encrypt(key_data.api_key)
    db_path = get_db_path()
    conn = None
    try:
        conn = sqlite3.connect(str(db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 먼저 해당 서비스의 데이터가 존재하는지 확인
        cursor.execute("SELECT id FROM ai_credential WHERE service_name = ?", (service_name,))
        if not cursor.fetchone():
            raise APIException(CommonCode.NO_SEARCH_DATA)

        # 데이터 업데이트
        cursor.execute(
            "UPDATE ai_credential SET api_key = ?, updated_at = datetime('now', 'localtime') WHERE service_name = ?",
            (encrypted_key, service_name),
        )
        conn.commit()

        # rowcount가 0이면 업데이트된 행이 없음 (정상적인 경우 발생하기 어려움)
        if cursor.rowcount == 0:
            raise APIException(CommonCode.FAIL)

        # 업데이트된 정보를 다시 조회하여 반환
        cursor.execute("SELECT * FROM ai_credential WHERE service_name = ?", (service_name,))
        updated_row = cursor.fetchone()

        return APIKeyInDB.model_validate(dict(updated_row))

    except sqlite3.Error as e:
        if "database is locked" in str(e):
            raise APIException(CommonCode.DB_BUSY) from e
        raise APIException(CommonCode.FAIL) from e
    finally:
        if conn:
            conn.close()
