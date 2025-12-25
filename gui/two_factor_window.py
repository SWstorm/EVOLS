import customtkinter as ctk
from tkinter import messagebox
import sys


# === СОВРЕМЕННАЯ СИСТЕМА ДИЗАЙНА (единая с main_window) ===
class ModernDesign:
    """Крутая система дизайна"""

    # Цвета
    PRIMARY = "#2962FF"
    PRIMARY_DARK = "#0039CB"
    SECONDARY = "#00E5FF"
    SUCCESS = "#00E676"
    DANGER = "#FF1744"
    WARNING = "#FFD600"

    # Фон
    BG_DARK = "#0F172A"
    BG_CARD = "#1E293B"
    BG_HOVER = "#334155"
    SIDEBAR_BG = "#1A1F36"

    # Текст
    TEXT_PRIMARY = "#F8FAFC"
    TEXT_SECONDARY = "#94A3B8"
    TEXT_MUTED = "#64748B"

    @staticmethod
    def get_title_font():
        return ("Segoe UI", 28, "bold")

    @staticmethod
    def get_subtitle_font():
        return ("Segoe UI", 16)

    @staticmethod
    def get_body_font():
        return ("Segoe UI", 12)

    @staticmethod
    def get_button_font():
        return ("Segoe UI", 13, "bold")

    @staticmethod
    def get_caption_font():
        return ("Segoe UI", 11)


class ToastNotification:
    """Красивые toast-уведомления"""

    @staticmethod
    def show(parent, message, type="info", duration=3000):
        try:
            if not parent.winfo_exists():
                return
        except:
            return

        toast = ctk.CTkFrame(
            parent,
            fg_color=ModernDesign.BG_CARD,
            corner_radius=12,
            border_width=2
        )

        border_colors = {
            "info": ModernDesign.PRIMARY,
            "success": ModernDesign.SUCCESS,
            "error": ModernDesign.DANGER,
            "warning": ModernDesign.WARNING
        }
        toast.configure(border_color=border_colors.get(type, ModernDesign.PRIMARY))

        icons = {
            "info": "ℹ️",
            "success": "✓",
            "error": "✕",
            "warning": "⚠️"
        }

        content_frame = ctk.CTkFrame(toast, fg_color="transparent")
        content_frame.pack(padx=20, pady=15, fill="both", expand=True)

        ctk.CTkLabel(
            content_frame,
            text=icons.get(type, "ℹ️"),
            font=("Segoe UI", 20),
            text_color=border_colors.get(type, ModernDesign.PRIMARY)
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            content_frame,
            text=message,
            font=ModernDesign.get_body_font(),
            text_color=ModernDesign.TEXT_PRIMARY,
            wraplength=300
        ).pack(side="left", fill="both", expand=True)

        toast.place(relx=0.5, rely=0.1, anchor="n")
        toast.lift()

        def fade_out():
            try:
                if toast.winfo_exists():
                    toast.destroy()
            except:
                pass

        parent.after(duration, fade_out)


class TwoFactorWindow:
    """Окно двухфакторной аутентификации"""

    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback

        # Создаем окно
        self.window = ctk.CTkToplevel(parent)
        self.window.title("🔐 Двухфакторная аутентификация")
        self.window.geometry("500x400")
        self.window.minsize(450, 350)
        self.window.configure(fg_color=ModernDesign.BG_DARK)

        # Настройки окна
        self.window.grab_set()  # Модальное окно
        self.window.transient(parent)  # Поверх родительского окна
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Настраиваем адаптивность
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.setup_ui()
        self.center_window()

    def center_window(self):
        """Центрирует окно на экране"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """Создает современный интерфейс"""
        # Главный контейнер
        main_container = ctk.CTkFrame(self.window, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        main_container.grid_columnconfigure(0, weight=1)

        # === ЗАГОЛОВОК ===
        header_frame = ctk.CTkFrame(main_container, fg_color=ModernDesign.BG_CARD, corner_radius=15)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(padx=25, pady=25)

        ctk.CTkLabel(
            header_content,
            text="🔐",
            font=("Segoe UI", 56)
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            header_content,
            text="Двухфакторная аутентификация",
            font=("Segoe UI", 20, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY
        ).pack()

        ctk.CTkLabel(
            header_content,
            text="Введите код из приложения аутентификатора",
            font=("Segoe UI", 12),
            text_color=ModernDesign.TEXT_SECONDARY
        ).pack(pady=(5, 0))

        # === ПОЛЕ ВВОДА КОДА ===
        code_card = ctk.CTkFrame(main_container, fg_color=ModernDesign.BG_CARD, corner_radius=12)
        code_card.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        code_content = ctk.CTkFrame(code_card, fg_color="transparent")
        code_content.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            code_content,
            text="🔢 Код подтверждения",
            font=("Segoe UI", 12, "bold"),
            text_color=ModernDesign.TEXT_SECONDARY,
            anchor="w"
        ).pack(anchor="w", pady=(0, 10))

        self.code_entry = ctk.CTkEntry(
            code_content,
            placeholder_text="Введите 6-значный код",
            height=50,
            font=("Segoe UI", 16, "bold"),
            border_width=0,
            fg_color=ModernDesign.BG_HOVER,
            corner_radius=10,
            justify="center"
        )
        self.code_entry.pack(fill="x")

        # Привязка Enter
        self.code_entry.bind("<Return>", lambda e: self.on_submit())

        # === ИНФОРМАЦИЯ ===
        info_frame = ctk.CTkFrame(main_container, fg_color=ModernDesign.BG_HOVER, corner_radius=10)
        info_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(
            info_frame,
            text="ℹ️ Откройте приложение аутентификатора (Google Authenticator, Authy)",
            font=ModernDesign.get_caption_font(),
            text_color=ModernDesign.TEXT_SECONDARY,
            wraplength=400
        ).pack(padx=15, pady=12)

        # === КНОПКИ ===
        buttons_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        buttons_frame.grid(row=3, column=0, sticky="ew")
        buttons_frame.grid_columnconfigure((0, 1), weight=1)

        submit_btn = ctk.CTkButton(
            buttons_frame,
            text="✓ Подтвердить",
            command=self.on_submit,
            font=("Segoe UI", 14, "bold"),
            height=50,
            fg_color=ModernDesign.SUCCESS,
            hover_color="#00C853",
            corner_radius=10
        )
        submit_btn.grid(row=0, column=0, padx=5, sticky="ew")

        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="✕ Выход",
            command=self.on_close,
            font=("Segoe UI", 14, "bold"),
            height=50,
            fg_color=ModernDesign.DANGER,
            hover_color="#C62828",
            corner_radius=10
        )
        cancel_btn.grid(row=0, column=1, padx=5, sticky="ew")

        # Фокус на поле ввода
        self.code_entry.focus_set()

    def on_submit(self):
        """Обработка отправки кода"""
        code = self.code_entry.get().strip()

        # Валидация
        if not code:
            ToastNotification.show(self.window, "Введите код подтверждения!", "error")
            return

        # Проверка формата (6 цифр)
        if not code.isdigit():
            ToastNotification.show(self.window, "Код должен состоять только из цифр!", "error")
            return

        if len(code) != 6:
            ToastNotification.show(self.window, "Код должен содержать 6 цифр!", "error")
            return

        # Закрываем окно и вызываем callback
        self.window.destroy()
        self.callback(code)

    def on_close(self):
        """Обработка закрытия окна"""
        result = messagebox.askyesno(
            "Выход",
            "Вы уверены что хотите выйти?\n\nБез подтверждения 2FA доступ будет закрыт."
        )

        if result:
            sys.exit(0)