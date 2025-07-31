import os
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

"""
보안 원칙을 적용한 AES-256 암호화 및 복호화 클래스입니다.
- 암호화 시 매번 새로운 랜덤 IV를 생성합니다.
"""
class AES256:
    _key = "Y1dkbGJtbGxMbUZsY3pJMU5pNXJaWGs9".encode('utf-8')

    @staticmethod
    def encrypt(text: str) -> str:
        iv = get_random_bytes(AES.block_size)

        cipher = AES.new(AES256._key, AES.MODE_CBC, iv)

        data_bytes = text.encode('utf-8')
        padded_bytes = pad(data_bytes, AES.block_size)

        encrypted_bytes = cipher.encrypt(padded_bytes)

        combined_bytes = iv + encrypted_bytes
        return base64.b64encode(combined_bytes).decode('utf-8')

    @staticmethod
    def decrypt(cipher_text: str) -> str:
        """
        AES-256으로 암호화된 텍스트를 복호화합니다.
        """
        combined_bytes = base64.b64decode(cipher_text)

        iv = combined_bytes[:AES.block_size]
        encrypted_bytes = combined_bytes[AES.block_size:]

        cipher = AES.new(AES256._key, AES.MODE_CBC, iv)

        decrypted_padded_bytes = cipher.decrypt(encrypted_bytes)
        decrypted_bytes = unpad(decrypted_padded_bytes, AES.block_size)

        return decrypted_bytes.decode('utf-8')

