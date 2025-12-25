import customtkinter as ctk
from tkinter import messagebox
import os
import re

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
        return ("Segoe UI", 32, "bold")

    @staticmethod
    def get_subtitle_font():
        return ("Segoe UI", 16)

    @staticmethod
    def get_body_font():
        return ("Segoe UI", 13)

    @staticmethod
    def get_button_font():
        return ("Segoe UI", 14, "bold")

    @staticmethod
    def get_caption_font():
        return ("Segoe UI", 11)


class PasswordStrengthIndicator:
    """Индикатор надёжности пароля в реальном времени"""

    @staticmethod
    def check_strength(password):
        """Возвращает оценку и цвет"""
        if not password:
            return 0, ModernDesign.TEXT_MUTED, "Введите пароль"

        score = 0
        feedback = []

        # Длина
        if len(password) >= 8:
            score += 25
        else:
            feedback.append("минимум 8 символов")

        if len(password) >= 12:
            score += 15

        # Разнообразие символов
        if re.search(r'[a-z]', password):
            score += 15
        else:
            feedback.append("строчные буквы")

        if re.search(r'[A-Z]', password):
            score += 15
        else:
            feedback.append("заглавные буквы")

        if re.search(r'\d', password):
            score += 15
        else:
            feedback.append("цифры")

        if re.search(r'[!@#$%^&*()_+\-=\[\]{};:\',.<>?]', password):
            score += 15
        else:
            feedback.append("спецсимволы")

        # Определяем уровень
        if score < 40:
            color = ModernDesign.DANGER
            level = "Слабый"
        elif score < 70:
            color = ModernDesign.WARNING
            level = "Средний"
        else:
            color = ModernDesign.SUCCESS
            level = "Сильный"

        hint = f"{level} • Добавьте: {', '.join(feedback[:2])}" if feedback else level

        return score, color, hint


class ToastNotification:
    """Красивые toast-уведомления"""

    @staticmethod
    def show(parent, message, type="info", duration=3000):
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
                toast.destroy()
            except:
                pass

        parent.after(duration, fade_out)


class LoginFrame:
    """Современный экран входа/создания vault"""

    def __init__(self, root, app_instance):
        self.root = root
        self.app = app_instance  # Ссылка на PasswordVaultApp

        # Настройка темы
        ctk.set_appearance_mode("dark")

        self.root.title("EVOLS Password Manager")
        self.root.geometry("1000x700")
        self.root.minsize(900, 650)
        self.root.configure(fg_color=ModernDesign.BG_DARK)

        # Центрируем окно
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Проверяем, существует ли vault
        self.vault_exists = os.path.exists(self.app.get_db_path())

        if self.vault_exists:
            self.show_login_screen()
        else:
            self.show_welcome_screen()

    def clear_frame(self):
        """Очищает окно"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_welcome_screen(self):
        """Экран приветствия для нового пользователя"""
        self.clear_frame()

        # Главный контейнер
        main_container = ctk.CTkFrame(self.root, fg_color=ModernDesign.BG_DARK)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # Центральная карточка
        card = ctk.CTkFrame(
            main_container,
            fg_color=ModernDesign.BG_CARD,
            corner_radius=20,
            border_width=2,
            border_color=ModernDesign.PRIMARY
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(padx=80, pady=60)

        # Логотип
        ctk.CTkLabel(
            content,
            text="🔐",
            font=("Segoe UI", 80)
        ).pack(pady=(0, 20))

        # Заголовок
        ctk.CTkLabel(
            content,
            text="EVOLS",
            font=("Segoe UI", 42, "bold"),
            text_color=ModernDesign.PRIMARY
        ).pack()

        ctk.CTkLabel(
            content,
            text="Password Manager",
            font=("Segoe UI", 18),
            text_color=ModernDesign.TEXT_SECONDARY
        ).pack(pady=(5, 40))

        # Приветственное сообщение
        welcome_text = ctk.CTkFrame(content, fg_color=ModernDesign.BG_HOVER, corner_radius=12)
        welcome_text.pack(fill="x", pady=(0, 40))

        ctk.CTkLabel(
            welcome_text,
            text="👋 Добро пожаловать!",
            font=("Segoe UI", 16, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY
        ).pack(pady=(15, 5), padx=30)

        ctk.CTkLabel(
            welcome_text,
            text="Создайте мастер-пароль для защиты ваших данных",
            font=ModernDesign.get_body_font(),
            text_color=ModernDesign.TEXT_SECONDARY,
            wraplength=400
        ).pack(pady=(0, 15), padx=30)

        # Кнопка создания
        create_btn = ctk.CTkButton(
            content,
            text="🚀 Создать хранилище",
            command=self.show_create_vault_screen,
            font=("Segoe UI", 16, "bold"),
            height=55,
            width=350,
            fg_color=ModernDesign.PRIMARY,
            hover_color=ModernDesign.PRIMARY_DARK,
            corner_radius=12
        )
        create_btn.pack()

        # Дополнительная информация
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(pady=(30, 0))

        features = [
            ("🔒", "AES-256 шифрование"),
            ("⚡", "Быстрый доступ"),
            ("🌙", "Современный интерфейс")
        ]

        for i, (icon, text) in enumerate(features):
            feature_row = ctk.CTkFrame(info_frame, fg_color="transparent")
            feature_row.grid(row=i, column=0, pady=5, sticky="w")

            ctk.CTkLabel(
                feature_row,
                text=icon,
                font=("Segoe UI", 16)
            ).pack(side="left", padx=(0, 10))

            ctk.CTkLabel(
                feature_row,
                text=text,
                font=ModernDesign.get_caption_font(),
                text_color=ModernDesign.TEXT_SECONDARY
            ).pack(side="left")

    def show_create_vault_screen(self):
        """Экран создания нового vault"""
        self.clear_frame()

        # Главный контейнер
        main_container = ctk.CTkFrame(self.root, fg_color=ModernDesign.BG_DARK)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # Скроллируемая область
        scroll_frame = ctk.CTkScrollableFrame(
            main_container,
            fg_color="transparent"
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        scroll_frame.grid_columnconfigure(0, weight=1)

        # Центральная карточка
        card = ctk.CTkFrame(
            scroll_frame,
            fg_color=ModernDesign.BG_CARD,
            corner_radius=20
        )
        card.pack(pady=20, padx=20)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(padx=60, pady=50)
        content.grid_columnconfigure(0, weight=1)

        # Заголовок
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 30))

        ctk.CTkLabel(
            header,
            text="🔐",
            font=("Segoe UI", 48)
        ).pack()

        ctk.CTkLabel(
            header,
            text="Создание хранилища",
            font=("Segoe UI", 28, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            header,
            text="Придумайте надежный мастер-пароль",
            font=ModernDesign.get_subtitle_font(),
            text_color=ModernDesign.TEXT_SECONDARY
        ).pack()

        # Поля ввода
        fields_frame = ctk.CTkFrame(content, fg_color="transparent")
        fields_frame.grid(row=1, column=0, sticky="ew", pady=20)
        fields_frame.grid_columnconfigure(0, weight=1)

        # Переменные
        self.password_var = ctk.StringVar()
        self.confirm_var = ctk.StringVar()

        # Индикатор надежности
        self.strength_label = ctk.CTkLabel(
            fields_frame,
            text="",
            font=ModernDesign.get_caption_font(),
            text_color=ModernDesign.TEXT_MUTED
        )

        self.strength_bar = ctk.CTkProgressBar(
            fields_frame,
            width=400,
            height=8,
            progress_color=ModernDesign.TEXT_MUTED
        )

        # Поле мастер-пароля - ИСПРАВЛЕНО!
        password_section = ctk.CTkFrame(fields_frame, fg_color=ModernDesign.BG_HOVER, corner_radius=12)
        password_section.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        # Используем pack для правильного выравнивания
        inner_frame = ctk.CTkFrame(password_section, fg_color="transparent")
        inner_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            inner_frame,
            text="🔑",
            font=("Segoe UI", 20)
        ).pack(side="left", padx=(0, 15))

        password_entry_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        password_entry_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            password_entry_frame,
            text="Мастер-пароль",
            font=("Segoe UI", 11, "bold"),
            text_color=ModernDesign.TEXT_SECONDARY,
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        password_input = ctk.CTkEntry(
            password_entry_frame,
            textvariable=self.password_var,
            show="●",
            height=45,
            font=("Segoe UI", 14),
            border_width=0,
            fg_color=ModernDesign.BG_DARK,
            placeholder_text="Введите надежный пароль"
        )
        password_input.pack(fill="x")

        # ИСПРАВЛЕННАЯ функция toggle
        show_btn_container = ctk.CTkFrame(inner_frame, fg_color="transparent")
        show_btn_container.pack(side="left")

        def toggle_password():
            if password_input.cget('show') == '●':
                password_input.configure(show='')
                show_btn.configure(text="👁️‍🗨️")
            else:
                password_input.configure(show='●')
                show_btn.configure(text="👁️")

        show_btn = ctk.CTkButton(
            show_btn_container,
            text="👁️",
            command=toggle_password,
            width=45,
            height=45,
            font=("Segoe UI", 18),
            fg_color=ModernDesign.PRIMARY,
            hover_color=ModernDesign.PRIMARY_DARK,
            corner_radius=8
        )
        show_btn.pack()

        # Индикатор надежности
        strength_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        strength_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        strength_frame.grid_columnconfigure(0, weight=1)

        self.strength_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.strength_bar.set(0)

        self.strength_label.grid(row=1, column=0, sticky="w")

        def on_password_change(*args):
            password = self.password_var.get()
            score, color, hint = PasswordStrengthIndicator.check_strength(password)

            self.strength_bar.set(score / 100)
            self.strength_bar.configure(progress_color=color)
            self.strength_label.configure(text=hint, text_color=color)

        self.password_var.trace("w", on_password_change)

        # Поле подтверждения - ИСПРАВЛЕНО!
        confirm_section = ctk.CTkFrame(fields_frame, fg_color=ModernDesign.BG_HOVER, corner_radius=12)
        confirm_section.grid(row=2, column=0, sticky="ew")

        # Используем pack для правильного выравнивания
        confirm_inner = ctk.CTkFrame(confirm_section, fg_color="transparent")
        confirm_inner.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            confirm_inner,
            text="✓",
            font=("Segoe UI", 20)
        ).pack(side="left", padx=(0, 15))

        confirm_entry_frame = ctk.CTkFrame(confirm_inner, fg_color="transparent")
        confirm_entry_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            confirm_entry_frame,
            text="Подтверждение пароля",
            font=("Segoe UI", 11, "bold"),
            text_color=ModernDesign.TEXT_SECONDARY,
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        confirm_input = ctk.CTkEntry(
            confirm_entry_frame,
            textvariable=self.confirm_var,
            show="●",
            height=45,
            font=("Segoe UI", 14),
            border_width=0,
            fg_color=ModernDesign.BG_DARK,
            placeholder_text="Повторите пароль"
        )
        confirm_input.pack(fill="x")

        # Советы
        tips_frame = ctk.CTkFrame(content, fg_color=ModernDesign.BG_HOVER, corner_radius=12)
        tips_frame.grid(row=2, column=0, sticky="ew", pady=(0, 30))

        tips_header = ctk.CTkFrame(tips_frame, fg_color="transparent")
        tips_header.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            tips_header,
            text="💡 Советы для надежного пароля",
            font=("Segoe UI", 13, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY,
            anchor="w"
        ).pack(anchor="w")

        tips = [
            "Используйте минимум 12 символов",
            "Комбинируйте буквы, цифры и символы",
            "Избегайте простых слов и дат",
            "Не используйте один пароль везде"
        ]

        for tip in tips:
            tip_row = ctk.CTkFrame(tips_frame, fg_color="transparent")
            tip_row.pack(fill="x", padx=20, pady=2)

            ctk.CTkLabel(
                tip_row,
                text="•",
                font=ModernDesign.get_body_font(),
                text_color=ModernDesign.PRIMARY
            ).pack(side="left", padx=(0, 10))

            ctk.CTkLabel(
                tip_row,
                text=tip,
                font=ModernDesign.get_body_font(),
                text_color=ModernDesign.TEXT_SECONDARY,
                anchor="w"
            ).pack(side="left")

        ctk.CTkLabel(
            tips_frame,
            text="",
            height=5
        ).pack()

        # Кнопки
        buttons_frame = ctk.CTkFrame(content, fg_color="transparent")
        buttons_frame.grid(row=3, column=0)

        def create_vault():
            password = self.password_var.get()
            confirm = self.confirm_var.get()

            if not password:
                ToastNotification.show(self.root, "Введите мастер-пароль", "error")
                return

            if len(password) < 8:
                ToastNotification.show(self.root, "Пароль должен содержать минимум 8 символов", "error")
                return

            if password != confirm:
                ToastNotification.show(self.root, "Пароли не совпадают", "error")
                return

            score, _, _ = PasswordStrengthIndicator.check_strength(password)
            if score < 40:
                result = messagebox.askyesno(
                    "Слабый пароль",
                    "Ваш пароль недостаточно надежный.\n\nПродолжить всё равно?"
                )
                if not result:
                    return

            # Вызываем метод создания vault из app
            self.app.create_vault_with_password(password)

        create_btn = ctk.CTkButton(
            buttons_frame,
            text="🚀 Создать хранилище",
            command=create_vault,
            font=("Segoe UI", 15, "bold"),
            height=50,
            width=250,
            fg_color=ModernDesign.SUCCESS,
            hover_color="#00C853",
            corner_radius=10
        )
        create_btn.grid(row=0, column=0, padx=10)

        back_btn = ctk.CTkButton(
            buttons_frame,
            text="← Назад",
            command=self.show_welcome_screen,
            font=ModernDesign.get_button_font(),
            height=50,
            width=120,
            fg_color=ModernDesign.BG_HOVER,
            hover_color="#475569",
            corner_radius=10
        )
        back_btn.grid(row=0, column=1, padx=10)

        # Привязка Enter
        confirm_input.bind("<Return>", lambda e: create_vault())

    def show_login_screen(self):
        """Экран входа в существующий vault - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        self.clear_frame()

        # Главный контейнер
        main_container = ctk.CTkFrame(self.root, fg_color=ModernDesign.BG_DARK)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # Центральная карточка
        card = ctk.CTkFrame(
            main_container,
            fg_color=ModernDesign.BG_CARD,
            corner_radius=20,
            border_width=2,
            border_color=ModernDesign.PRIMARY
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(padx=80, pady=60)

        # Логотип
        ctk.CTkLabel(
            content,
            text="🔐",
            font=("Segoe UI", 70)
        ).pack(pady=(0, 15))

        # Заголовок
        ctk.CTkLabel(
            content,
            text="С возвращением!",
            font=("Segoe UI", 32, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY
        ).pack()

        ctk.CTkLabel(
            content,
            text="Введите мастер-пароль для доступа",
            font=ModernDesign.get_subtitle_font(),
            text_color=ModernDesign.TEXT_SECONDARY
        ).pack(pady=(5, 40))

        # Поле пароля - ИСПРАВЛЕНО!
        password_section = ctk.CTkFrame(content, fg_color=ModernDesign.BG_HOVER, corner_radius=12)
        password_section.pack(fill="x", pady=(0, 30))

        # Используем pack вместо grid для лучшего выравнивания
        inner_frame = ctk.CTkFrame(password_section, fg_color="transparent")
        inner_frame.pack(fill="x", padx=20, pady=20)

        # Иконка ключа
        ctk.CTkLabel(
            inner_frame,
            text="🔑",
            font=("Segoe UI", 24)
        ).pack(side="left", padx=(5, 15))

        # Контейнер для поля ввода
        entry_container = ctk.CTkFrame(inner_frame, fg_color="transparent")
        entry_container.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.login_password_var = ctk.StringVar()

        password_input = ctk.CTkEntry(
            entry_container,
            textvariable=self.login_password_var,
            show="●",
            height=50,
            font=("Segoe UI", 15),
            border_width=0,
            fg_color=ModernDesign.BG_DARK,
            placeholder_text="Мастер-пароль"
        )
        password_input.pack(fill="x")

        # ИСПРАВЛЕННАЯ функция toggle - правильная область видимости
        show_btn_container = ctk.CTkFrame(inner_frame, fg_color="transparent")
        show_btn_container.pack(side="left")

        def toggle_login_password():
            if password_input.cget('show') == '●':
                password_input.configure(show='')
                show_btn.configure(text="👁️‍🗨️")
            else:
                password_input.configure(show='●')
                show_btn.configure(text="👁️")

        show_btn = ctk.CTkButton(
            show_btn_container,
            text="👁️",
            command=toggle_login_password,
            width=50,
            height=50,
            font=("Segoe UI", 20),
            fg_color=ModernDesign.PRIMARY,
            hover_color=ModernDesign.PRIMARY_DARK,
            corner_radius=8
        )
        show_btn.pack()

        # Кнопка входа
        def do_login():
            password = self.login_password_var.get()

            if not password:
                ToastNotification.show(self.root, "Введите пароль", "error")
                return

            # Вызываем метод входа из app
            self.app.login_with_password(password)

        login_btn = ctk.CTkButton(
            content,
            text="🚀 Войти",
            command=do_login,
            font=("Segoe UI", 16, "bold"),
            height=55,
            width=400,
            fg_color=ModernDesign.PRIMARY,
            hover_color=ModernDesign.PRIMARY_DARK,
            corner_radius=12
        )
        login_btn.pack()

        # Информация внизу
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(pady=(30, 0))

        ctk.CTkLabel(
            info_frame,
            text="🔒 Ваши данные защищены AES-256 шифрованием",
            font=ModernDesign.get_caption_font(),
            text_color=ModernDesign.TEXT_MUTED
        ).pack()

        # Привязка Enter
        password_input.bind("<Return>", lambda e: do_login())
        password_input.focus_set()