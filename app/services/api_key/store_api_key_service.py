import sqlite3

from app.core.exceptions import APIException
from app.core.security import AES256
from app.core.status import CommonCode
from app.core.utils import generate_prefixed_uuid, get_db_path
from app.schemas.llm_api_key import ApiKeyCredentialCreate, ApiKeyCredentialInDB


def store_api_key(credential_data: ApiKeyCredentialCreate) -> ApiKeyCredentialInDB:
    """API_KEY를 암호화하여 데이터베이스에 저장합니다."""

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
            (new_id, credential_data.service_name, encrypted_key),
        )
        conn.commit()

        cursor.execute("SELECT * FROM ai_credential WHERE id = ?", (new_id,))
        created_row = cursor.fetchone()

        if not created_row:
            raise APIException(CommonCode.FAIL_TO_VERIFY_CREATION)

        return ApiKeyCredentialInDB.model_validate(dict(created_row))

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
