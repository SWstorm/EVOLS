import customtkinter as ctk
from tkinter import messagebox, simpledialog
import os
from crypto import Encryptor
from customtkinter import ThemeManager
from utils.theme_manager import ThemeManager
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

        # Применяем тему к корневому окну
        ThemeManager.setup_theme(self.root)

        # Установка обработчика закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.encryptor = None
        self.db = None

        # Запускаем аутентификацию
        self.authenticate()

    def on_close(self):
        """Корректно закрывает приложение"""
        # Здесь можно добавить логику сохранения данных перед выходом
        self.root.destroy()

    def authenticate(self):
        """Аутентификация пользователя со стилизованными экранами входа."""
        # Настраиваем главное окно для начальных экранов
        self.root.title("Хранилище паролей EVOLS")
        self.root.geometry(f"{ThemeManager.WINDOW_WIDTH}x{ThemeManager.WINDOW_HEIGHT}")

        # Применяем единый стиль
        ThemeManager.setup_theme(self.root)

        # Очищаем окно
        for widget in self.root.winfo_children():
            widget.destroy()

        # Настраиваем адаптивность корневого окна
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Создаем основной контейнер
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Проверяем, существует ли файл базы данных
        if not os.path.exists("passwords.db"):
            # Первый запуск - создаем экран создания мастер-пароля
            self.create_password_screen(main_frame)
        else:
            # Запрашиваем существующий мастер-пароль
            self.login_screen(main_frame)

    def create_password_screen(self, parent_frame):
        """Создает экран с формой создания мастер-пароля."""
        # Создаем контейнер с отступами
        container = ctk.CTkFrame(parent_frame)
        container.grid(row=0, column=0, sticky="nsew", padx=100, pady=100)
        container.grid_columnconfigure(0, weight=1)

        # Заголовок
        ctk.CTkLabel(
            container,
            text="Создание мастер-пароля",
            font=ThemeManager.get_title_font()
        ).grid(row=0, column=0, pady=(0, 30))

        # Поле для ввода пароля
        ctk.CTkLabel(
            container,
            text="Создайте мастер-пароль для вашего хранилища:",
            font=ThemeManager.get_normal_font()
        ).grid(row=1, column=0, sticky="w", pady=(0, 5))

        password_var = ctk.StringVar()
        password_entry = ctk.CTkEntry(
            container,
            textvariable=password_var,
            width=300,
            font=ThemeManager.get_normal_font(),
            show="*"
        )
        password_entry.grid(row=2, column=0, pady=(0, 20))

        # Поле для подтверждения пароля
        ctk.CTkLabel(
            container,
            text="Подтвердите мастер-пароль:",
            font=ThemeManager.get_normal_font()
        ).grid(row=3, column=0, sticky="w", pady=(0, 5))

        confirm_var = ctk.StringVar()
        confirm_entry = ctk.CTkEntry(
            container,
            textvariable=confirm_var,
            width=300,
            font=ThemeManager.get_normal_font(),
            show="*"
        )
        confirm_entry.grid(row=4, column=0, pady=(0, 30))

        # Кнопки
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.grid(row=5, column=0)

        def on_create():
            # Получаем введенные пароли
            master_password = password_var.get()
            confirm_password = confirm_var.get()

            if not master_password:
                messagebox.showerror("Ошибка", "Мастер-пароль обязателен!")
                return

            if master_password != confirm_password:
                messagebox.showerror("Ошибка", "Пароли не совпадают!")
                return

            # Создаем шифровальщик с новой солью
            self.encryptor = Encryptor(master_password)

            # Сохраняем соль для будущей аутентификации
            with open("vault.salt", "wb") as f:
                f.write(self.encryptor.salt)

            self.db = PasswordDatabase("passwords.db", self.encryptor)

            # Создаем директорию для данных и файл с распространенными паролями
            self.create_data_directory()

            # Очищаем экран и создаем основной интерфейс
            for widget in self.root.winfo_children():
                widget.destroy()

            self.main_window = MainWindow(self.root, self.db, self.encryptor)

        def on_exit():
            self.root.destroy()

        ctk.CTkButton(
            button_frame,
            text="Создать",
            command=on_create,
            width=150,
            font=ThemeManager.get_button_font(),
            fg_color=ThemeManager.SUCCESS_COLOR,
            hover_color="#388E3C"
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Выход",
            command=on_exit,
            width=100,
            font=ThemeManager.get_button_font(),
            fg_color="#9E9E9E",
            hover_color="#757575"
        ).grid(row=0, column=1, padx=10)

        # Фокус на первом поле ввода
        password_entry.focus_set()

    def login_screen(self, parent_frame):
        """Создает экран ввода мастер-пароля для входа."""
        # Создаем контейнер с отступами
        container = ctk.CTkFrame(parent_frame)
        container.grid(row=0, column=0, sticky="nsew", padx=100, pady=100)
        container.grid_columnconfigure(0, weight=1)

        # Заголовок
        ctk.CTkLabel(
            container,
            text="Вход в хранилище паролей",
            font=ThemeManager.get_title_font()
        ).grid(row=0, column=0, pady=(0, 30))

        # Поле для ввода пароля
        ctk.CTkLabel(
            container,
            text="Введите мастер-пароль для доступа к хранилищу:",
            font=ThemeManager.get_normal_font()
        ).grid(row=1, column=0, sticky="w", pady=(0, 10))

        password_var = ctk.StringVar()
        password_entry = ctk.CTkEntry(
            container,
            textvariable=password_var,
            width=300,
            font=ThemeManager.get_normal_font(),
            show="*"
        )
        password_entry.grid(row=2, column=0, pady=(0, 30))

        # Кнопки
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.grid(row=3, column=0)

        def on_login():
            master_password = password_var.get()

            if not master_password:
                messagebox.showerror("Ошибка", "Мастер-пароль обязателен!")
                return

            try:
                # Загружаем сохраненную соль
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

                # Если настроена 2FA, показываем экран ввода кода
                if os.path.exists("2fa_secret.key"):
                    self.show_2fa_screen(parent_frame)
                else:
                    # Иначе переходим к основному интерфейсу
                    for widget in self.root.winfo_children():
                        widget.destroy()

                    self.main_window = MainWindow(self.root, self.db, self.encryptor)

            except Exception as e:
                messagebox.showerror("Ошибка аутентификации", f"Неверный мастер-пароль или повреждение данных: {e}")

        def on_exit():
            self.root.destroy()

        ctk.CTkButton(
            button_frame,
            text="Войти",
            command=on_login,
            width=150,
            font=ThemeManager.get_button_font(),
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color="#1565C0"
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Выход",
            command=on_exit,
            width=100,
            font=ThemeManager.get_button_font(),
            fg_color="#9E9E9E",
            hover_color="#757575"
        ).grid(row=0, column=1, padx=10)

        # Фокус на поле ввода
        password_entry.focus_set()

    def show_2fa_screen(self, parent_frame):
        """Показывает экран ввода кода двухфакторной аутентификации."""
        # Очищаем родительский фрейм
        for widget in parent_frame.winfo_children():
            widget.destroy()

        # Создаем контейнер с отступами
        container = ctk.CTkFrame(parent_frame)
        container.grid(row=0, column=0, sticky="nsew", padx=100, pady=100)
        container.grid_columnconfigure(0, weight=1)

        # Заголовок
        ctk.CTkLabel(
            container,
            text="Двухфакторная аутентификация",
            font=ThemeManager.get_title_font()
        ).grid(row=0, column=0, pady=(0, 30))

        # Поле для ввода кода
        ctk.CTkLabel(
            container,
            text="Введите код из приложения аутентификатора:",
            font=ThemeManager.get_normal_font()
        ).grid(row=1, column=0, sticky="w", pady=(0, 5))

        code_var = ctk.StringVar()
        code_entry = ctk.CTkEntry(
            container,
            textvariable=code_var,
            width=200,
            font=ThemeManager.get_normal_font()
        )
        code_entry.grid(row=2, column=0, pady=(0, 30))

        # Кнопки
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.grid(row=3, column=0)

        def on_verify():
            totp_code = code_var.get()

            if not totp_code:
                messagebox.showerror("Ошибка", "Код обязателен для входа!")
                return

            try:
                # Проверяем код
                import pyotp
                with open("2fa_secret.key", "r") as f:
                    secret_key = f.read().strip()

                totp = pyotp.TOTP(secret_key)
                if totp.verify(totp_code):
                    # Если код верный, переходим к основному интерфейсу
                    for widget in self.root.winfo_children():
                        widget.destroy()

                    self.main_window = MainWindow(self.root, self.db, self.encryptor)
                else:
                    messagebox.showerror("Ошибка аутентификации", "Неверный код аутентификации")
            except Exception as e:
                messagebox.showerror("Ошибка аутентификации", f"Ошибка при проверке 2FA: {e}")

        def on_exit():
            self.root.destroy()

        ctk.CTkButton(
            button_frame,
            text="Подтвердить",
            command=on_verify,
            width=150,
            font=ThemeManager.get_button_font(),
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color="#1565C0"
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Выход",
            command=on_exit,
            width=100,
            font=ThemeManager.get_button_font(),
            fg_color="#9E9E9E",
            hover_color="#757575"
        ).grid(row=0, column=1, padx=10)

        # Фокус на поле ввода
        code_entry.focus_set()

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