# app/core/security.py

import base64
import os

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

"""
보안 원칙을 적용한 AES-256 암호화 및 복호화 클래스입니다.
- 암호화 시 매번 새로운 랜덤 IV를 생성합니다.
"""


class AES256:
    _key = None

    @classmethod
    def _get_key(cls):
        """키를 한 번만 로드하고 캐싱하여 재사용합니다 (지연 로딩)."""
        if cls._key is None:
            key_from_env = os.getenv("ENV_AES256_KEY")
            if key_from_env is None:
                raise ValueError("환경 변수 'ENV_AES256_KEY'가 설정되지 않았거나 .env 파일 로드에 실패했습니다.")
            cls._key = base64.b64decode(key_from_env)
        return cls._key

    @staticmethod
    def encrypt(text: str) -> str:
        key = AES256._get_key()
        iv = get_random_bytes(AES.block_size)

        cipher = AES.new(key, AES.MODE_CBC, iv)

        data_bytes = text.encode("utf-8")
        padded_bytes = pad(data_bytes, AES.block_size)

        encrypted_bytes = cipher.encrypt(padded_bytes)

        combined_bytes = iv + encrypted_bytes
        return base64.b64encode(combined_bytes).decode("utf-8")

    @staticmethod
    def decrypt(cipher_text: str) -> str:
        """
        AES-256으로 암호화된 텍스트를 복호화합니다.
        """
        key = AES256._get_key()
        combined_bytes = base64.b64decode(cipher_text)

        iv = combined_bytes[: AES.block_size]
        encrypted_bytes = combined_bytes[AES.block_size :]

        cipher = AES.new(key, AES.MODE_CBC, iv)

        decrypted_padded_bytes = cipher.decrypt(encrypted_bytes)
        decrypted_bytes = unpad(decrypted_padded_bytes, AES.block_size)

        return decrypted_bytes.decode("utf-8")
