import customtkinter as ctk
from tkinter import messagebox, simpledialog
import os
from crypto import Encryptor
from database import PasswordDatabase
from gui.main_window import MainWindow

# Настройка темы
ctk.set_appearance_mode("System")  # Системная тема (автоматически светлая/темная)
ctk.set_default_color_theme("blue")  # Основной цвет акцентов


class PasswordVaultApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Локальное хранилище паролей")
        self.root.geometry("800x600")

        # Можно установить минимальный размер окна
        self.root.minsize(700, 500)

        self.encryptor = None
        self.db = None

        self.authenticate()

    def authenticate(self):
        # Проверяем, существует ли файл базы данных
        if not os.path.exists("passwords.db"):
            # Первый запуск - создаем мастер-пароль
            master_password = simpledialog.askstring("Создание мастер-пароля",
                                                     "Создайте мастер-пароль для вашего хранилища:",
                                                     show='*')
            if not master_password:
                messagebox.showerror("Ошибка", "Мастер-пароль обязателен!")
                self.root.destroy()
                return

            confirm_password = simpledialog.askstring("Подтверждение мастер-пароля",
                                                      "Подтвердите мастер-пароль:",
                                                      show='*')
            if master_password != confirm_password:
                messagebox.showerror("Ошибка", "Пароли не совпадают!")
                self.root.destroy()
                return

            # Создаем шифровальщик с новой солью
            self.encryptor = Encryptor(master_password)

            # Сохраняем соль для будущей аутентификации
            with open("vault.salt", "wb") as f:
                f.write(self.encryptor.salt)

            self.db = PasswordDatabase("passwords.db", self.encryptor)

            # Создаем директорию для данных и файл с распространенными паролями
            self.create_data_directory()

            # Создаем основной интерфейс
            self.main_window = MainWindow(self.root, self.db, self.encryptor)
        else:
            # Запрашиваем существующий мастер-пароль
            master_password = simpledialog.askstring("Введите мастер-пароль",
                                                     "Введите мастер-пароль для доступа к хранилищу:",
                                                     show='*')
            if not master_password:
                messagebox.showerror("Ошибка", "Мастер-пароль обязателен!")
                self.root.destroy()
                return

            # Загружаем сохраненную соль
            try:
                with open("vault.salt", "rb") as f:
                    salt = f.read()

                # Создаем шифровальщик с загруженной солью
                self.encryptor = Encryptor(master_password, salt)

                # Инициализируем базу данных с шифровальщиком
                self.db = PasswordDatabase("passwords.db", self.encryptor)

                # Проверяем, можем ли мы расшифровать какую-нибудь запись
                test = self.db.get_all_passwords()
                if test:
                    _ = self.db.get_password(test[0][0])  # Проверка пароля

                # Если настроена 2FA, запрашиваем код
                if os.path.exists("2fa_secret.key"):
                    try:
                        # Запрашиваем код 2FA
                        totp_code = simpledialog.askstring("Двухфакторная аутентификация",
                                                           "Введите код из приложения аутентификатора:",
                                                           show='*')
                        if not totp_code:
                            messagebox.showerror("Ошибка", "Код обязателен для входа!")
                            self.root.destroy()
                            return

                        # Проверяем код
                        import pyotp
                        with open("2fa_secret.key", "r") as f:
                            secret_key = f.read().strip()

                        totp = pyotp.TOTP(secret_key)
                        if not totp.verify(totp_code):
                            messagebox.showerror("Ошибка аутентификации", "Неверный код аутентификации")
                            self.root.destroy()
                            return

                    except Exception as e:
                        messagebox.showerror("Ошибка аутентификации", f"Ошибка при проверке 2FA: {e}")
                        self.root.destroy()
                        return

                # Если 2FA успешно пройдена или не настроена, создаем основной интерфейс
                self.main_window = MainWindow(self.root, self.db, self.encryptor)

            except Exception as e:
                messagebox.showerror("Ошибка аутентификации", f"Неверный мастер-пароль или повреждение данных: {e}")
                self.root.destroy()
                return

    def create_data_directory(self):
        """Создает директорию для данных и файл с распространенными паролями."""
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(data_dir, exist_ok=True)

        # Создаем простой файл с распространенными паролями
        common_passwords_file = os.path.join(data_dir, "common-passwords.txt")

        if not os.path.exists(common_passwords_file):
            common_passwords = [
                "123456", "password", "12345678", "qwerty", "123456789",
                "12345", "1234", "111111", "1234567", "dragon",
                "123123", "baseball", "abc123", "football", "monkey",
                "letmein", "696969", "shadow", "master", "666666",
                "qwertyuiop", "123321", "mustang", "1234567890", "michael",
                "654321", "superman", "1qaz2wsx", "7777777", "fuckyou",
                "121212", "000000", "qazwsx", "123qwe", "killer",
                "trustno1", "jordan", "jennifer", "zxcvbnm", "asdfgh"
            ]

            with open(common_passwords_file, 'w', encoding='utf-8') as f:
                for password in common_passwords:
                    f.write(f"{password}\n")


if __name__ == "__main__":
    root = ctk.CTk()  # Используем CustomTkinter вместо tk.Tk()
    app = PasswordVaultApp(root)
    root.mainloop()