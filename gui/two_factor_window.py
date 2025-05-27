import customtkinter as ctk
from tkinter import messagebox
from utils.design_system import DesignSystem, UIComponents



class TwoFactorWindow:
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback

        # Создаем окно
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Двухфакторная аутентификация")
        self.window.geometry("450x250")
        self.window.minsize(400, 200)

        # Настройки окна
        self.window.grab_set()  # Модальное окно
        self.window.transient(parent)  # Поверх родительского окна
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)  # Обработка закрытия

        # Настраиваем адаптивность
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # Применяем тему
        DesignSystem.setup_DesignSystem(self.window)

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
        ctk.CTkLabel(
            main_frame,
            text="Двухфакторная аутентификация",
            font=DesignSystem.get_title_font()
        ).grid(row=0, column=0, pady=(0, 20))

        # Инструкция
        ctk.CTkLabel(
            main_frame,
            text="Введите код из приложения аутентификатора:",
            font=DesignSystem.get_normal_font()
        ).grid(row=1, column=0, sticky="w", pady=(0, 10))

        # Поле для ввода кода
        self.code_entry = ctk.CTkEntry(
            main_frame,
            width=150,
            font=DesignSystem.get_normal_font()
        )
        self.code_entry.grid(row=2, column=0, pady=(0, 20))

        # Кнопки
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=(10, 0))

        ctk.CTkButton(
            button_frame,
            text="Подтвердить",
            width=150,
            font=DesignSystem.get_button_font(),
            command=self.on_submit
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Отмена",
            width=100,
            font=DesignSystem.get_button_font(),
            fg_color="#9E9E9E",
            hover_color="#757575",
            command=self.on_close
        ).grid(row=0, column=1, padx=10)

        # Фокус на поле ввода
        self.code_entry.focus_set()

    def on_submit(self):
        code = self.code_entry.get()

        if not code:
            messagebox.showerror("Ошибка", "Код обязателен для входа!")
            return

        # Закрываем окно и вызываем колбэк с результатом
        self.window.destroy()
        self.callback(code)

    def on_close(self):
        # Вместо уничтожения родительского окна просто выходим из приложения
        import sys
        sys.exit(0)

