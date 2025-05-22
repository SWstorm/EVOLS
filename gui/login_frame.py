import customtkinter as ctk
from tkinter import messagebox
import os
from utils.theme_manager import ThemeManager


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, on_submit, is_first_run=False):
        super().__init__(parent)
        self.parent = parent
        self.on_submit = on_submit
        self.is_first_run = is_first_run

        # Применяем тему
        ThemeManager.setup_theme(parent)

        # Настраиваем адаптивность
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_ui()

    def setup_ui(self):
        # Основной фрейм с отступами
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=100, pady=100)
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
            command=self.submit
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Выход",
            width=100,
            font=ThemeManager.get_button_font(),
            fg_color="#9E9E9E",
            hover_color="#757575",
            command=self.exit_app
        ).grid(row=0, column=1, padx=10)

        # Фокус на поле ввода
        self.password_entry.focus_set()

    def submit(self):
        master_password = self.password_entry.get()

        if not master_password:
            messagebox.showerror("Ошибка", "Мастер-пароль обязателен!")
            return

        if self.is_first_run:
            confirm_password = self.confirm_entry.get()
            if master_password != confirm_password:
                messagebox.showerror("Ошибка", "Пароли не совпадают!")
                return

        # Вызываем колбэк с результатом
        self.on_submit(master_password)

    def exit_app(self):
        # Безопасно выходим из приложения
        self.parent.quit()
