import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import os
import sys
from crypto import Encryptor
from database import PasswordDatabase
from gui.main_window import MainWindow
from utils.design_system import DesignSystem, ThemeManager, UIComponents

class PasswordVaultApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Локальное хранилище паролей")
        self.root.geometry("800x600")

        # Применяем тему к корневому окну
        DesignSystem.setup_theme(self.root)

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
        self.root.geometry(f"{DesignSystem.WINDOW_WIDTH}x{DesignSystem.WINDOW_HEIGHT}")

        # Применяем единый стиль
        DesignSystem.setup_theme(self.root)

        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        if not os.path.exists("passwords.db"):
            self.create_password_screen(main_frame)
        else:
            # Запрашиваем существующий мастер-пароль
            self.login_screen(main_frame)

    def shake_widget(self, widget):
        """Анимация тряски для виджета при ошибке"""
        try:
            original_fg = widget.cget("border_color")
        except:
            original_fg = None

        # Меняем цвет границы на красный
        try:
            widget.configure(border_color=DesignSystem.DANGER, border_width=2)
        except:
            pass

        def restore_color():
            try:
                if original_fg:
                    widget.configure(border_color=original_fg, border_width=0)
                else:
                    widget.configure(border_width=0)
            except:
                pass

        # Восстанавливаем цвет через 2 секунды
        try:
            widget.after(2000, restore_color)
        except:
            pass

    def show_error_tooltip(self, widget, message):
        """Показывает тултип с ошибкой"""
        try:
            # Создаем временную метку с ошибкой
            tooltip = ctk.CTkLabel(
                widget.master,
                text=message,
                font=DesignSystem.get_caption_font(),
                text_color=DesignSystem.DANGER
            )

            # Размещаем под полем ввода
            widget_info = widget.grid_info()
            if widget_info:  # Проверяем, что виджет размещен в grid
                tooltip.grid(
                    row=widget_info['row'] + 1,
                    column=widget_info['column'],
                    sticky="w",
                    pady=(DesignSystem.SPACE_1, 0)
                )

                # Удаляем тултип через 3 секунды
                def remove_tooltip():
                    try:
                        tooltip.destroy()
                    except:
                        pass

                tooltip.after(3000, remove_tooltip)
        except Exception as e:
            # Если не получилось показать тултип, просто показываем сообщение
            print(f"Ошибка показа тултипа: {e}")
            messagebox.showerror("Ошибка", message)

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
            font=DesignSystem.get_title_font()
        ).grid(row=0, column=0, pady=(0, 30))

        # Поле для ввода пароля
        ctk.CTkLabel(
            container,
            text="Создайте мастер-пароль для вашего хранилища:",
            font=DesignSystem.get_body_font()
        ).grid(row=1, column=0, sticky="w", pady=(0, 5))

        password_var = ctk.StringVar()
        password_entry = ctk.CTkEntry(
            container,
            textvariable=password_var,
            width=300,
            font=DesignSystem.get_body_font(),
            show="*"
        )
        password_entry.grid(row=2, column=0, pady=(0, 20))

        # Поле для подтверждения пароля
        ctk.CTkLabel(
            container,
            text="Подтвердите мастер-пароль:",
            font=DesignSystem.get_body_font()
        ).grid(row=3, column=0, sticky="w", pady=(0, 5))

        confirm_var = ctk.StringVar()
        confirm_entry = ctk.CTkEntry(
            container,
            textvariable=confirm_var,
            width=300,
            font=DesignSystem.get_body_font(),
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
            font=DesignSystem.get_button_font(),
            fg_color=DesignSystem.SUCCESS,
            hover_color="#388E3C"
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Выход",
            command=on_exit,
            width=100,
            font=DesignSystem.get_button_font(),
            fg_color="#9E9E9E",
            hover_color="#757575"
        ).grid(row=0, column=1, padx=10)

        # Фокус на первом поле ввода
        password_entry.focus_set()

    def login_screen(self, parent_frame):
        """Создает профессиональный экран входа."""
        # Очищаем родительский фрейм
        for widget in parent_frame.winfo_children():
            widget.destroy()

        # Применяем дизайн-систему
        DesignSystem.setup_theme(self.root)

        # Основной контейнер с правильными отступами
        main_container = ctk.CTkFrame(parent_frame, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # Центральная карточка входа
        login_card = UIComponents.create_card(main_container)
        login_card.grid(row=0, column=0, padx=DesignSystem.SPACE_20, pady=DesignSystem.SPACE_20)
        login_card.grid_columnconfigure(0, weight=1)

        # Внутренний контейнер с отступами
        inner_container = ctk.CTkFrame(login_card, fg_color="transparent")
        inner_container.grid(row=0, column=0, sticky="ew", padx=DesignSystem.SPACE_12, pady=DesignSystem.SPACE_12)
        inner_container.grid_columnconfigure(0, weight=1)

        # Логотип/иконка приложения
        logo_frame = ctk.CTkFrame(inner_container, fg_color="transparent")
        logo_frame.grid(row=0, column=0, pady=(0, DesignSystem.SPACE_8))

        logo_icon = ctk.CTkLabel(
            logo_frame,
            text="🔐",
            font=("Arial", 48)  # Используем простой кортеж вместо CTkFont
        )
        logo_icon.grid(row=0, column=0)

        # Заголовок приложения
        app_title = UIComponents.create_section_title(inner_container, "EVOLS")
        app_title.grid(row=1, column=0, pady=(0, DesignSystem.SPACE_2))

        # Подзаголовок
        subtitle = UIComponents.create_subtitle(inner_container, "Хранилище паролей")
        subtitle.grid(row=2, column=0, pady=(0, DesignSystem.SPACE_10))

        # Описание действия
        description = UIComponents.create_body_text(
            inner_container,
            "Введите мастер-пароль для доступа"
        )
        description.grid(row=3, column=0, pady=(0, DesignSystem.SPACE_6))

        # Поле ввода пароля
        password_var = ctk.StringVar()
        password_entry = UIComponents.create_input_field(
            inner_container,
            placeholder="Мастер-пароль",
            width=350,
            show="*"
        )
        password_entry.configure(textvariable=password_var)
        password_entry.grid(row=4, column=0, pady=(0, DesignSystem.SPACE_8))

        # Контейнер для кнопок
        button_container = ctk.CTkFrame(inner_container, fg_color="transparent")
        button_container.grid(row=5, column=0, pady=(DesignSystem.SPACE_4, 0))
        button_container.grid_columnconfigure((0, 1), weight=1)

        def on_login():
            master_password = password_var.get()

            if not master_password:
                # Анимация тряски поля
                self.shake_widget(password_entry)
                self.show_error_tooltip(password_entry, "Поле не может быть пустым")
                return

            try:
                # Логика входа
                with open("vault.salt", "rb") as f:
                    salt = f.read()

                self.encryptor = Encryptor(master_password, salt)
                self.db = PasswordDatabase("passwords.db", self.encryptor)

                test = self.db.get_all_passwords()
                if test:
                    _ = self.db.get_password(test[0][0])

                if os.path.exists("2fa_secret.key"):
                    self.show_2fa_screen(parent_frame)
                else:
                    for widget in self.root.winfo_children():
                        widget.destroy()
                    self.main_window = MainWindow(self.root, self.db, self.encryptor)

            except Exception as e:
                self.shake_widget(password_entry)
                password_entry.delete(0, "end")
                self.show_error_tooltip(password_entry, "Неверный мастер-пароль")

        def on_exit():
            self.root.destroy()

        # Кнопка входа (основная)
        login_button = UIComponents.create_primary_button(
            button_container,
            "Войти",
            command=on_login,
            width=160
        )
        login_button.grid(row=0, column=0, padx=(0, DesignSystem.SPACE_3), sticky="ew")

        # Кнопка выхода (вторичная)
        exit_button = UIComponents.create_secondary_button(
            button_container,
            "Выход",
            command=on_exit,
            width=100
        )
        exit_button.grid(row=0, column=1, padx=(DesignSystem.SPACE_3, 0), sticky="ew")

        # Подсказка внизу
        hint_text = UIComponents.create_caption(
            inner_container,
            "Приложение автоматически блокируется при бездействии"
        )
        hint_text.grid(row=6, column=0, pady=(DesignSystem.SPACE_8, 0))

        # Привязка Enter к кнопке входа
        password_entry.bind("<Return>", lambda event: on_login())
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
            font=DesignSystem.get_title_font()
        ).grid(row=0, column=0, pady=(0, 30))

        # Поле для ввода кода
        ctk.CTkLabel(
            container,
            text="Введите код из приложения аутентификатора:",
            font=DesignSystem.get_body_font()
        ).grid(row=1, column=0, sticky="w", pady=(0, 5))

        code_var = ctk.StringVar()
        code_entry = ctk.CTkEntry(
            container,
            textvariable=code_var,
            width=200,
            font=DesignSystem.get_body_font()
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
            font=DesignSystem.get_button_font(),
            fg_color=DesignSystem.PRIMARY,
            hover_color="#1565C0"
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Выход",
            command=on_exit,
            width=100,
            font=DesignSystem.get_button_font(),
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
