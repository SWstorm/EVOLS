from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os


class Encryptor:
    def __init__(self, master_password, salt=None):
        # Инициализация...
        if salt is None:
            salt = os.urandom(16)
        self.salt = salt
        self.master_password = master_password
        self._generate_cipher()

    def _generate_cipher(self):
        # Генерация ключа...
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
        self.cipher = Fernet(key)

    def set_salt(self, salt):
        self.salt = salt
        self._generate_cipher()

    def encrypt(self, data):
        # Шифрование данных...
        if data is None or data == "":
            return ""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data):
        # Расшифровка данных...
        if not encrypted_data:
            return ""

        try:
            if isinstance(encrypted_data, str):
                encrypted_bytes = encrypted_data.encode()
            else:
                encrypted_bytes = encrypted_data

            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            # Для отладки можно раскомментировать следующие строки
            # import traceback
            # print(f"Ошибка расшифровки: {e}")
            # print(traceback.format_exc())
            return "[Ошибка расшифровки]"
