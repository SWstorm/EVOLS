import os
import base64
from cryptography.fernet import Fernet, InvalidToken as FernetInvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# Экспортируем InvalidToken из cryptography.fernet
InvalidToken = FernetInvalidToken


class EncryptionError(Exception):
    """Исключение при ошибке шифрования"""
    pass


class DecryptionError(Exception):
    """Исключение при ошибке дешифрования"""
    pass


class Encryptor:
    """
    Класс для шифрования и дешифрования данных с использованием Fernet.
    Использует PBKDF2HMAC для генерации ключа из пароля.
    """
    
    def __init__(self, password: str, salt: bytes = None):
        if salt is None:
            self.salt = os.urandom(16)
        else:
            self.salt = salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=480000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
        self.fernet = Fernet(key)
        self._password = password
    
    def encrypt(self, data: str) -> str:
        try:
            encrypted_bytes = self.fernet.encrypt(data.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            raise EncryptionError(f"Ошибка при шифровании: {e}")
    
    def decrypt(self, encrypted_data: str) -> str:
        try:
            decrypted_bytes = self.fernet.decrypt(encrypted_data.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except FernetInvalidToken:
            raise
        except Exception as e:
            raise DecryptionError(f"Ошибка при дешифровании: {e}")
    
    def encrypt_bytes(self, data: bytes) -> bytes:
        try:
            return self.fernet.encrypt(data)
        except Exception as e:
            raise EncryptionError(f"Ошибка при шифровании байтов: {e}")
    
    def decrypt_bytes(self, encrypted_data: bytes) -> bytes:
        try:
            return self.fernet.decrypt(encrypted_data)
        except FernetInvalidToken:
            raise
        except Exception as e:
            raise DecryptionError(f"Ошибка при дешифровании байтов: {e}")
    
    def clear(self):
        if hasattr(self, '_password'):
            self._password = None
        if hasattr(self, 'fernet'):
            self.fernet = None