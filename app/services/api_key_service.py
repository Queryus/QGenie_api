import sqlite3

from fastapi import Depends

from app.core.exceptions import APIException
from app.core.security import AES256
from app.core.status import CommonCode
from app.core.utils import generate_prefixed_uuid
from app.repository.api_key_repository import APIKeyRepository, api_key_repository
from app.schemas.api_key.create_model import APIKeyCreate
from app.schemas.api_key.db_model import APIKeyInDB
from app.schemas.api_key.update_model import APIKeyUpdate

api_key_repository_dependency = Depends(lambda: api_key_repository)


class APIKeyService:
    def __init__(self, repository: APIKeyRepository = api_key_repository):
        self.repository = repository

    def store_api_key(self, api_key_data: APIKeyCreate) -> APIKeyInDB:
        """API_KEY를 암호화하고 repository를 통해 데이터베이스에 저장합니다."""
        api_key_data.validate_with_service()
        try:
            encrypted_key = AES256.encrypt(api_key_data.api_key)
            new_id = generate_prefixed_uuid("QGENIE")

            created_row = self.repository.create_api_key(
                new_id=new_id,
                service_name=api_key_data.service_name.value,
                encrypted_key=encrypted_key,
            )

            if not created_row:
                raise APIException(CommonCode.FAIL_TO_VERIFY_CREATION)

            return created_row

        except sqlite3.IntegrityError as e:
            raise APIException(CommonCode.DUPLICATION) from e
        except sqlite3.Error as e:
            if "database is locked" in str(e):
                raise APIException(CommonCode.DB_BUSY) from e
            raise APIException(CommonCode.FAIL) from e

    def get_all_api_keys(self) -> list[APIKeyInDB]:
        """데이터베이스에 저장된 모든 API Key를 조회합니다."""
        try:
            return self.repository.get_all_api_keys()
        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL) from e

    def get_api_key_by_service_name(self, service_name: str) -> APIKeyInDB:
        """서비스 이름으로 특정 API Key를 조회합니다."""
        try:
            api_key = self.repository.get_api_key_by_service_name(service_name)
            if not api_key:
                raise APIException(CommonCode.NO_SEARCH_DATA)
            return api_key
        except sqlite3.Error as e:
            raise APIException(CommonCode.FAIL) from e

    def update_api_key(self, service_name: str, key_data: APIKeyUpdate) -> APIKeyInDB:
        """서비스 이름에 해당하는 API Key를 수정합니다."""
        key_data.validate_with_api_key()
        try:
            encrypted_key = AES256.encrypt(key_data.api_key)
            updated_api_key = self.repository.update_api_key(service_name, encrypted_key)

            if not updated_api_key:
                raise APIException(CommonCode.NO_SEARCH_DATA)

            return updated_api_key
        except sqlite3.Error as e:
            if "database is locked" in str(e):
                raise APIException(CommonCode.DB_BUSY) from e
            raise APIException(CommonCode.FAIL) from e

    def delete_api_key(self, service_name: str) -> None:
        """서비스 이름에 해당하는 API Key를 삭제합니다."""
        try:
            is_deleted = self.repository.delete_api_key(service_name)
            if not is_deleted:
                raise APIException(CommonCode.NO_SEARCH_DATA)
        except sqlite3.Error as e:
            if "database is locked" in str(e):
                raise APIException(CommonCode.DB_BUSY) from e
            raise APIException(CommonCode.FAIL) from e


api_key_service = APIKeyService()
