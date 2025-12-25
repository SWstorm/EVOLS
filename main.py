import os
import customtkinter as ctk
from tkinter import messagebox

import paths
from main.encryption import Encryptor, InvalidToken
from main.database import PasswordDatabase
from gui.main_window import MainWindow
from gui.login_frame import LoginFrame


class PasswordVaultApp:
    """Главный класс приложения - только логика, без UI"""

    def __init__(self, root):
        self.root = root
        self.root.title("EVOLS Password Manager")
        self.root.geometry("1000x700")
        self.root.minsize(900, 650)

        # Настройка темы
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.encryptor = None
        self.db = None

        # Таймер автоблокировки
        self.idle_timeout_ms = 10 * 60 * 1000
        self.idle_after_id = None
        self.is_locked = True

        # Показываем экран входа/создания
        self.show_login_frame()

    # === ПУТИ К ФАЙЛАМ ===

    def get_data_dir(self):
        return paths.get_data_dir()

    def get_db_path(self):
        return paths.db_path()

    def get_salt_path(self):
        return paths.salt_path()

    def get_2fa_path(self):
        return paths.twofa_path()

    def get_verification_path(self):
        """Путь к файлу контрольного токена для проверки пароля."""
        return os.path.join(self.get_data_dir(), "verify.token")

    # === ЭКРАН ВХОДА/СОЗДАНИЯ ===

    def show_login_frame(self):
        """Показывает экран входа/создания vault"""
        # Очищаем окно
        for widget in self.root.winfo_children():
            widget.destroy()

        # Создаём LoginFrame
        self.login_frame = LoginFrame(self.root, self)

    # === СОЗДАНИЕ VAULT ===

    def create_vault_with_password(self, master_password):
        """
        Создаёт новое хранилище с мастер-паролем
        Вызывается из LoginFrame
        """
        try:
            # Создаём encryptor
            self.encryptor = Encryptor(master_password)

            # Сохраняем соль
            with open(self.get_salt_path(), "wb") as f:
                f.write(self.encryptor.salt)

            # 🔒 БЕЗОПАСНОСТЬ: Сохраняем контрольный токен для проверки пароля
            verification_token = self.encryptor.encrypt("EVOLS_VERIFICATION_TOKEN_2024")
            with open(self.get_verification_path(), "w", encoding="utf-8") as f:
                f.write(verification_token)

            # Создаём базу данных
            self.db = PasswordDatabase(self.get_db_path(), self.encryptor)

            # Разблокируем приложение
            self.is_locked = False
            self.setup_idle_timer()

            # Показываем главное окно
            self.show_main_window()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать хранилище: {e}")

    # === ВХОД В VAULT ===

    def login_with_password(self, master_password):
        """
        Вход в существующее хранилище
        Вызывается из LoginFrame
        """
        try:
            # Загружаем соль
            with open(self.get_salt_path(), "rb") as f:
                salt = f.read()

            # Создаём encryptor
            self.encryptor = Encryptor(master_password, salt)

            # 🔒 БЕЗОПАСНОСТЬ: ОБЯЗАТЕЛЬНАЯ проверка пароля через контрольный токен
            # Работает даже если база данных пустая!
            with open(self.get_verification_path(), "r", encoding="utf-8") as f:
                verification_token = f.read()

            # Попытка расшифровать контрольный токен
            # Если пароль неверный - будет InvalidToken
            decrypted = self.encryptor.decrypt(verification_token)
            if decrypted != "EVOLS_VERIFICATION_TOKEN_2024":
                raise InvalidToken()

            # Открываем базу данных
            self.db = PasswordDatabase(self.get_db_path(), self.encryptor)

            # Разблокируем приложение
            self.is_locked = False
            self.setup_idle_timer()

            # Показываем главное окно
            self.show_main_window()

        except InvalidToken:
            messagebox.showerror("Ошибка", "Неверный мастер-пароль")
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл проверки не найден. Возможно база повреждена.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при входе: {e}")

    # === ГЛАВНОЕ ОКНО ===

    def show_main_window(self):
        """Показывает главное окно после успешного входа"""
        # Очищаем окно
        for widget in self.root.winfo_children():
            widget.destroy()

        # Создаём главное окно
        self.main_window = MainWindow(self.root, self.db, self.encryptor)

    # === АВТОБЛОКИРОВКА ===

    def setup_idle_timer(self):
        """Настраивает таймер автоблокировки"""
        self.root.bind_all("<Any-KeyPress>", self.reset_idle_timer)
        self.root.bind_all("<Any-Button>", self.reset_idle_timer)
        self.reset_idle_timer()

    def reset_idle_timer(self, event=None):
        """Сбрасывает таймер при активности"""
        if self.is_locked:
            return
        if self.idle_after_id:
            self.root.after_cancel(self.idle_after_id)
        self.idle_after_id = self.root.after(self.idle_timeout_ms, self.lock_app)

    def lock_app(self):
        """Блокирует приложение при бездействии"""
        if self.is_locked:
            return

        # Закрываем БД
        if self.db:
            try:
                self.db.close()
            except:
                pass
            self.db = None

        # Очищаем encryptor
        if self.encryptor:
            try:
                self.encryptor.clear()
            except:
                pass
            self.encryptor = None

        self.is_locked = True

        # Показываем экран разблокировки
        from gui.unlock_window import UnlockWindow

        def on_unlock_success():
            self.is_locked = False
            self.setup_idle_timer()
            self.show_main_window()

        def on_unlock_cancel():
            self.on_close()

        UnlockWindow(
            self.root,
            on_success_callback=on_unlock_success,
            on_cancel_callback=on_unlock_cancel
        )

    # === ЗАКРЫТИЕ ПРИЛОЖЕНИЯ ===

    def on_close(self):
        """Обрабатывает закрытие приложения"""
        if self.db:
            try:
                self.db.close()
            except Exception as e:
                print(f"Ошибка при закрытии БД: {e}")

        if self.encryptor:
            try:
                self.encryptor.clear()
            except:
                pass

        if self.idle_after_id:
            self.root.after_cancel(self.idle_after_id)

        self.root.destroy()


def main():
    """Точка входа в приложение"""
    # Настройка темы
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Создаём главное окно
    root = ctk.CTk()

    # Запускаем приложение
    PasswordVaultApp(root)

    # Главный цикл
    root.mainloop()


if __name__ == "__main__":
    main()