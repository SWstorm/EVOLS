import customtkinter as ctk
from tkinter import messagebox
import os
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


class UnlockWindow:
    """Окно разблокировки хранилища"""

    def __init__(self, parent, on_success_callback, on_cancel_callback=None):
        """
        Создает окно разблокировки приложения.

        Args:
            parent: Родительское окно
            on_success_callback: Функция при успешной разблокировке
            on_cancel_callback: Функция при отмене (необязательно)
        """
        self.parent = parent
        self.on_success = on_success_callback
        self.on_cancel = on_cancel_callback or self.default_cancel

        # Счётчик попыток
        self.attempts = 0
        self.max_attempts = 5

        # Создаем окно
        self.window = ctk.CTkToplevel(parent)
        self.window.title("🔒 Разблокировка хранилища")
        self.window.geometry("550x550")
        self.window.minsize(500, 500)
        self.window.configure(fg_color=ModernDesign.BG_DARK)

        # Настройки окна
        self.window.grab_set()  # Модальное окно
        self.window.transient(parent)  # Поверх родительского окна
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.resizable(False, False)

        # Настраиваем адаптивность
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # Центрируем окно
        self.center_window()

        # Создаем интерфейс
        self.setup_ui()

        # Фокус на поле ввода
        self.password_entry.focus_set()

    def center_window(self):
        """Центрирует окно относительно родительского окна или экрана"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()

        try:
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()

            x = parent_x + (parent_width // 2) - (width // 2)
            y = parent_y + (parent_height // 2) - (height // 2)
        except:
            x = (self.window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.window.winfo_screenheight() // 2) - (height // 2)

        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """Создает современный интерфейс окна разблокировки"""
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
            text="🔒",
            font=("Segoe UI", 64)
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            header_content,
            text="Хранилище заблокировано",
            font=("Segoe UI", 22, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY
        ).pack()

        ctk.CTkLabel(
            header_content,
            text="Введите мастер-пароль для разблокировки",
            font=("Segoe UI", 12),
            text_color=ModernDesign.TEXT_SECONDARY
        ).pack(pady=(5, 0))

        # === ПОЛЕ ПАРОЛЯ ===
        password_card = ctk.CTkFrame(main_container, fg_color=ModernDesign.BG_CARD, corner_radius=12)
        password_card.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        password_content = ctk.CTkFrame(password_card, fg_color="transparent")
        password_content.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            password_content,
            text="🔑 Мастер-пароль",
            font=("Segoe UI", 12, "bold"),
            text_color=ModernDesign.TEXT_SECONDARY,
            anchor="w"
        ).pack(anchor="w", pady=(0, 10))

        # Контейнер для поля и кнопки показать
        entry_container = ctk.CTkFrame(password_content, fg_color="transparent")
        entry_container.pack(fill="x")
        entry_container.grid_columnconfigure(0, weight=1)

        self.password_entry = ctk.CTkEntry(
            entry_container,
            placeholder_text="Введите мастер-пароль",
            show="●",
            height=50,
            font=("Segoe UI", 13),
            border_width=0,
            fg_color=ModernDesign.BG_HOVER,
            corner_radius=10
        )
        self.password_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        # Кнопка показать пароль
        def toggle_password():
            if self.password_entry.cget('show') == '●':
                self.password_entry.configure(show='')
            else:
                self.password_entry.configure(show='●')

        show_btn = ctk.CTkButton(
            entry_container,
            text="👁️",
            command=toggle_password,
            width=50,
            height=50,
            font=("Segoe UI", 18),
            fg_color=ModernDesign.PRIMARY,
            hover_color=ModernDesign.PRIMARY_DARK,
            corner_radius=10
        )
        show_btn.grid(row=0, column=1)

        # Привязка Enter
        self.password_entry.bind("<Return>", lambda e: self.unlock())

        # === ИНДИКАТОР ПОПЫТОК ===
        self.attempts_frame = ctk.CTkFrame(main_container, fg_color=ModernDesign.BG_HOVER, corner_radius=10)
        self.attempts_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))

        self.attempts_label = ctk.CTkLabel(
            self.attempts_frame,
            text=f"ℹ️ Попыток осталось: {self.max_attempts - self.attempts}",
            font=ModernDesign.get_caption_font(),
            text_color=ModernDesign.TEXT_SECONDARY
        )
        self.attempts_label.pack(padx=15, pady=12)

        # === ИНФОРМАЦИЯ ===
        info_frame = ctk.CTkFrame(main_container, fg_color=ModernDesign.BG_HOVER, corner_radius=10)
        info_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(
            info_frame,
            text="⚠️ Приложение было заблокировано из-за бездействия",
            font=ModernDesign.get_caption_font(),
            text_color=ModernDesign.TEXT_SECONDARY
        ).pack(padx=15, pady=12)

        # === КНОПКИ ===
        buttons_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        buttons_frame.grid(row=4, column=0, sticky="ew")
        buttons_frame.grid_columnconfigure((0, 1), weight=1)

        unlock_btn = ctk.CTkButton(
            buttons_frame,
            text="🔓 Разблокировать",
            command=self.unlock,
            font=("Segoe UI", 14, "bold"),
            height=50,
            fg_color=ModernDesign.SUCCESS,
            hover_color="#00C853",
            corner_radius=10
        )
        unlock_btn.grid(row=0, column=0, padx=5, sticky="ew")

        exit_btn = ctk.CTkButton(
            buttons_frame,
            text="✕ Выход",
            command=self.on_close,
            font=("Segoe UI", 14, "bold"),
            height=50,
            fg_color=ModernDesign.DANGER,
            hover_color="#C62828",
            corner_radius=10
        )
        exit_btn.grid(row=0, column=1, padx=5, sticky="ew")

    def unlock(self):
        """Обрабатывает попытку разблокировки"""
        password = self.password_entry.get()

        if not password:
            self.shake_widget(self.password_entry)
            ToastNotification.show(self.window, "Введите мастер-пароль!", "error")
            return

        # Проверяем количество попыток
        if self.attempts >= self.max_attempts:
            ToastNotification.show(self.window, "Превышен лимит попыток!", "error")
            self.window.after(1500, lambda: sys.exit(0))
            return

        # Проверяем пароль
        try:
            from crypto import Encryptor

            # Загружаем соль
            with open("vault.salt", "rb") as f:
                salt = f.read()

            # Проверяем пароль
            test_encryptor = Encryptor(password, salt)

            # Проверяем 2FA если настроена
            if os.path.exists("2fa_secret.key"):
                self.check_2fa(password)
            else:
                # Если 2FA не настроена, сразу разблокируем
                ToastNotification.show(self.window, "Разблокировка...", "success")
                self.window.after(500, self.success_unlock)

        except Exception as e:
            # Увеличиваем счётчик попыток
            self.attempts += 1
            remaining = self.max_attempts - self.attempts

            # Обновляем индикатор
            if remaining > 0:
                self.attempts_label.configure(
                    text=f"⚠️ Попыток осталось: {remaining}",
                    text_color=ModernDesign.WARNING if remaining <= 2 else ModernDesign.TEXT_SECONDARY
                )
            else:
                self.attempts_label.configure(
                    text="❌ Лимит попыток исчерпан!",
                    text_color=ModernDesign.DANGER
                )

            # Анимация тряски
            self.shake_widget(self.password_entry)
            self.password_entry.delete(0, "end")
            ToastNotification.show(self.window, f"Неверный пароль! Осталось: {remaining}", "error")

            # Если попытки закончились
            if remaining == 0:
                self.window.after(2000, lambda: sys.exit(0))

    def check_2fa(self, master_password):
        """Запрашивает код двухфакторной аутентификации"""
        def on_2fa_submit(code):
            try:
                import pyotp

                # Читаем секретный ключ
                with open("2fa_secret.key", "r") as f:
                    secret_key = f.read().strip()

                # Проверяем код
                totp = pyotp.TOTP(secret_key)
                if totp.verify(code):
                    ToastNotification.show(self.window, "Разблокировка...", "success")
                    self.window.after(500, self.success_unlock)
                else:
                    ToastNotification.show(self.window, "Неверный код 2FA!", "error")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при проверке 2FA: {e}")

        # Открываем окно 2FA
        from gui.two_factor_window import TwoFactorWindow
        TwoFactorWindow(self.window, on_2fa_submit)

    def success_unlock(self):
        """Вызывается при успешной разблокировке"""
        self.window.destroy()
        self.on_success()

    def shake_widget(self, widget):
        """Создает эффект тряски для виджета при ошибке"""
        original_x = widget.winfo_x()

        def shake_step(step):
            if step < 10:
                offset = 8 if step % 2 == 0 else -8
                try:
                    widget.place(x=original_x + offset, y=widget.winfo_y())
                    self.window.after(40, lambda: shake_step(step + 1))
                except:
                    pass
            else:
                try:
                    widget.place(x=original_x, y=widget.winfo_y())
                    widget.place_forget()
                except:
                    pass

        shake_step(0)

    def default_cancel(self):
        """Стандартное действие при отмене - выход из приложения"""
        self.parent.quit()
        self.parent.destroy()

    def on_close(self):
        """Обрабатывает закрытие окна"""
        result = messagebox.askyesno(
            "Выход",
            "Выйти из приложения?\n\nВсе данные в безопасности."
        )

        if result:
            self.window.destroy()
            self.on_cancel()