import sqlite3

from fastapi import Depends

from app.core.exceptions import APIException
from app.core.security import AES256
from app.core.status import CommonCode
from app.core.utils import generate_prefixed_uuid
from app.repository.api_key_repository import APIKeyRepository, api_key_repository
from app.schemas.api_key.create_model import APIKeyCreate
from app.schemas.api_key.db_model import APIKeyInDB

api_key_repository_dependency = Depends(lambda: api_key_repository)


class APIKeyService:
    def store_api_key(
        self, credential_data: APIKeyCreate, repository: APIKeyRepository = api_key_repository
    ) -> APIKeyInDB:
        """API_KEY를 암호화하고 repository를 통해 데이터베이스에 저장합니다."""
        try:
            encrypted_key = AES256.encrypt(credential_data.api_key)
            new_id = generate_prefixed_uuid("QGENIE")

            created_row = repository.create_api_key(
                new_id=new_id,
                service_name=credential_data.service_name.value,
                encrypted_key=encrypted_key,
            )

            if not created_row:
                raise APIException(CommonCode.FAIL_TO_VERIFY_CREATION)

            return created_row

        except sqlite3.IntegrityError as e:
            # UNIQUE 제약 조건 위반 (service_name)
            raise APIException(CommonCode.DUPLICATION) from e
        except sqlite3.Error as e:
            # "database is locked" 오류를 명시적으로 처리
            if "database is locked" in str(e):
                raise APIException(CommonCode.DB_BUSY) from e
            # 기타 모든 sqlite3 오류
            raise APIException(CommonCode.FAIL) from e


api_key_service = APIKeyService()
