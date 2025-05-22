import customtkinter as ctk
from tkinter import messagebox
import os
from utils.theme_manager import ThemeManager


class LoginWindow:
    def __init__(self, parent, callback, is_first_run=False):
        self.parent = parent
        self.callback = callback
        self.is_first_run = is_first_run

        # Создаем окно
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Вход в хранилище паролей" if not is_first_run else "Создание мастер-пароля")
        self.window.geometry("450x300")
        self.window.minsize(400, 250)

        # Настройки окна
        self.window.grab_set()  # Модальное окно
        self.window.transient(parent)  # Поверх родительского окна
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)  # Обработка закрытия

        # Настраиваем адаптивность
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # Применяем тему
        ThemeManager.setup_theme(self.window)

        self.setup_ui()

        # Центрируем окно
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        # Основной фрейм
        main_frame = ctk.CTkFrame(self.window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        # Заголовок
        title = "Создание мастер-пароля" if self.is_first_run else "Вход в хранилище паролей"
        ctk.CTkLabel(
            main_frame,
            text=title,
            font=ThemeManager.get_title_font()
        ).grid(row=0, column=0, pady=(0, 20))

        # Поле для мастер-пароля
        ctk.CTkLabel(
            main_frame,
            text="Мастер-пароль:",
            font=ThemeManager.get_normal_font()
        ).grid(row=1, column=0, sticky="w", pady=(0, 5))

        self.password_entry = ctk.CTkEntry(
            main_frame,
            width=300,
            show="*",
            font=ThemeManager.get_normal_font()
        )
        self.password_entry.grid(row=2, column=0, pady=(0, 20))

        # Поле для подтверждения пароля (только при первом запуске)
        if self.is_first_run:
            ctk.CTkLabel(
                main_frame,
                text="Подтвердите мастер-пароль:",
                font=ThemeManager.get_normal_font()
            ).grid(row=3, column=0, sticky="w", pady=(0, 5))

            self.confirm_entry = ctk.CTkEntry(
                main_frame,
                width=300,
                show="*",
                font=ThemeManager.get_normal_font()
            )
            self.confirm_entry.grid(row=4, column=0, pady=(0, 20))

        # Кнопки
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, pady=(10, 0))

        ctk.CTkButton(
            button_frame,
            text="Войти" if not self.is_first_run else "Создать",
            width=150,
            font=ThemeManager.get_button_font(),
            command=self.on_submit
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Отмена",
            width=100,
            font=ThemeManager.get_button_font(),
            fg_color="#9E9E9E",
            hover_color="#757575",
            command=self.on_close
        ).grid(row=0, column=1, padx=10)

        # Фокус на поле ввода
        self.password_entry.focus_set()

    def on_submit(self):
        master_password = self.password_entry.get()

        if not master_password:
            messagebox.showerror("Ошибка", "Мастер-пароль обязателен!")
            return

        if self.is_first_run:
            confirm_password = self.confirm_entry.get()
            if master_password != confirm_password:
                messagebox.showerror("Ошибка", "Пароли не совпадают!")
                return

        # Закрываем окно и вызываем колбэк с результатом
        self.window.destroy()
        self.callback(master_password)

    def on_close(self):
        # Вместо уничтожения родительского окна просто выходим из приложения
        import sys
        sys.exit(0)

