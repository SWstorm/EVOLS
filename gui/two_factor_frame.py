import customtkinter as ctk
from tkinter import messagebox
from utils.design_system import DesignSystem


class TwoFactorFrame(ctk.CTkFrame):
    def __init__(self, parent, on_submit):
        super().__init__(parent)
        self.notes_textbox = None
        self.parent = parent
        self.on_submit = on_submit

        # Применяем тему
        DesignSystem.setup_theme(parent)

        # Настраиваем адаптивность
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_ui()

    def     setup_ui(self, form_frame=None):
        # Основной фрейм с отступами
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=100, pady=100)
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

        for widget in form_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkEntry):
                        child.bind("<Return>", lambda event: self.save_password())
                    elif isinstance(child, ctk.CTkComboBox):
                        child.bind("<Return>", lambda event: self.save_password())

        # Привязка Enter для текстового поля заметок (Ctrl+Enter)
        self.notes_textbox.bind("<Control-Return>", lambda event: self.save_password())

        self.window.bind("<Control-s>", lambda event: self.save_password())  # Ctrl+S для сохранения
        self.window.bind("<Escape>", lambda event: self.window.destroy())  # Escape для отмены


        # Кнопки
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=(10, 0))

        ctk.CTkButton(
            button_frame,
            text="Подтвердить",
            width=150,
            font=DesignSystem.get_button_font(),
            command=self.submit
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Выход",
            width=100,
            font=DesignSystem.get_button_font(),
            fg_color="#9E9E9E",
            hover_color="#757575",
            command=self.exit_app
        ).grid(row=0, column=1, padx=10)

        # Фокус на поле ввода
        self.code_entry.focus_set()

    def submit(self):
        code = self.code_entry.get()

        if not code:
            messagebox.showerror("Ошибка", "Код обязателен для входа!")
            return

        # Вызываем колбэк с результатом
        self.on_submit(code)

    def exit_app(self):
        # Безопасно выходим из приложения
        self.parent.quit()

    def save_password(self):
        pass
