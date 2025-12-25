import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import shutil
import json

# Условный импорт для 2FA
try:
    import pyotp
    import qrcode
    from PIL import Image
    import io
    HAS_2FA_SUPPORT = True
except ImportError:
    HAS_2FA_SUPPORT = False


# === СОВРЕМЕННАЯ СИСТЕМА ДИЗАЙНА ===
class ModernDesign:
    """Единая система дизайна"""

    PRIMARY = "#2962FF"
    PRIMARY_DARK = "#0039CB"
    SECONDARY = "#00E5FF"
    SUCCESS = "#00E676"
    DANGER = "#FF1744"
    WARNING = "#FFD600"

    BG_DARK = "#0F172A"
    BG_CARD = "#1E293B"
    BG_HOVER = "#334155"
    SIDEBAR_BG = "#1A1F36"

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
    """Toast уведомления"""

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

        icons = {"info": "ℹ️", "success": "✓", "error": "✕", "warning": "⚠️"}

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

        parent.after(duration, lambda: toast.destroy() if toast.winfo_exists() else None)


class SettingsWindow:
    """Окно настроек"""

    def __init__(self, parent, db, encryptor, main_window):
        self.parent = parent
        self.db = db
        self.encryptor = encryptor
        self.main_window = main_window

        # Переменные настроек
        self.auto_lock_var = ctk.StringVar(value="5")
        self.backup_dir_var = ctk.StringVar(value=os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups"))
        self.auto_backup_var = ctk.BooleanVar(value=True)

        # Загрузка текущих настроек
        self.load_current_settings()

        # Создание окна
        self.window = ctk.CTkToplevel(parent)
        self.window.title("⚙️ Настройки")
        self.window.geometry("700x650")
        self.window.minsize(650, 600)
        self.window.configure(fg_color=ModernDesign.BG_DARK)

        # Настройка окна
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.transient(parent)
        self.window.grab_set()

        self.center_window()
        self.setup_ui()

    def center_window(self):
        """Центрирует окно"""
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

    def load_current_settings(self):
        """Загружает текущие настройки"""
        try:
            if os.path.exists("app_settings.json"):
                with open("app_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    self.auto_lock_var.set(str(settings.get("auto_lock_time", 5)))
                    self.backup_dir_var.set(settings.get("backup_directory", self.backup_dir_var.get()))
                    self.auto_backup_var.set(settings.get("auto_backup", True))
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")

    def setup_ui(self):
        """Создает интерфейс"""
        # Главный контейнер
        main_container = ctk.CTkFrame(self.window, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)

        # === ЗАГОЛОВОК ===
        header_frame = ctk.CTkFrame(main_container, fg_color=ModernDesign.BG_CARD, corner_radius=15)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(padx=25, pady=20)

        ctk.CTkLabel(
            header_content,
            text="⚙️",
            font=("Segoe UI", 48)
        ).pack(side="left", padx=(0, 15))

        title_text = ctk.CTkFrame(header_content, fg_color="transparent")
        title_text.pack(side="left")

        ctk.CTkLabel(
            title_text,
            text="Настройки",
            font=("Segoe UI", 24, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY,
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_text,
            text="Управление безопасностью и параметрами приложения",
            font=("Segoe UI", 11),
            text_color=ModernDesign.TEXT_SECONDARY,
            anchor="w"
        ).pack(anchor="w", pady=(3, 0))

        # === ВКЛАДКИ ===
        self.tabview = ctk.CTkTabview(main_container, fg_color=ModernDesign.BG_CARD, corner_radius=12)
        self.tabview.grid(row=1, column=0, sticky="nsew", pady=(0, 15))

        # Добавляем вкладки
        tab_general = self.tabview.add("⏱️ Общие")
        tab_security = self.tabview.add("🔐 Безопасность")
        tab_backup = self.tabview.add("💾 Резервные копии")

        # Настраиваем вкладки
        for tab in [tab_general, tab_security, tab_backup]:
            tab.grid_columnconfigure(0, weight=1)

        self.setup_general_tab(tab_general)
        self.setup_security_tab(tab_security)
        self.setup_backup_tab(tab_backup)

        # === КНОПКИ ===
        buttons_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, sticky="ew")
        buttons_frame.grid_columnconfigure((0, 1), weight=1)

        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Сохранить",
            command=self.save_settings,
            font=("Segoe UI", 14, "bold"),
            height=50,
            fg_color=ModernDesign.SUCCESS,
            hover_color="#00C853",
            corner_radius=10
        )
        save_btn.grid(row=0, column=0, padx=5, sticky="ew")

        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="✕ Отмена",
            command=self.window.destroy,
            font=("Segoe UI", 14, "bold"),
            height=50,
            fg_color=ModernDesign.BG_HOVER,
            hover_color="#475569",
            corner_radius=10
        )
        cancel_btn.grid(row=0, column=1, padx=5, sticky="ew")

    def setup_general_tab(self, tab):
        """Настраивает вкладку общих настроек"""
        # Автоблокировка
        lock_card = ctk.CTkFrame(tab, fg_color=ModernDesign.BG_HOVER, corner_radius=12)
        lock_card.grid(row=0, column=0, sticky="ew", padx=15, pady=15)

        lock_content = ctk.CTkFrame(lock_card, fg_color="transparent")
        lock_content.pack(fill="x", padx=20, pady=20)
        lock_content.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            lock_content,
            text="⏱️ Автоматическая блокировка",
            font=("Segoe UI", 14, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY,
            anchor="w"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        ctk.CTkLabel(
            lock_content,
            text="Блокировать через:",
            font=ModernDesign.get_body_font(),
            text_color=ModernDesign.TEXT_SECONDARY
        ).grid(row=1, column=0, sticky="w", padx=(0, 10))

        vcmd = (self.window.register(lambda P: P.isdigit() or P == ""), '%P')

        lock_entry = ctk.CTkEntry(
            lock_content,
            textvariable=self.auto_lock_var,
            width=80,
            height=40,
            font=("Segoe UI", 13),
            justify="center",
            validate='key',
            validatecommand=vcmd,
            border_width=0,
            fg_color=ModernDesign.BG_CARD,
            corner_radius=8
        )
        lock_entry.grid(row=1, column=1, padx=10)

        ctk.CTkLabel(
            lock_content,
            text="минут бездействия",
            font=ModernDesign.get_body_font(),
            text_color=ModernDesign.TEXT_SECONDARY
        ).grid(row=1, column=2, sticky="w")

    def setup_security_tab(self, tab):
        """Настраивает вкладку безопасности"""
        # Смена мастер-пароля
        password_card = self._create_action_card(
            tab, 0,
            "🔑 Изменить мастер-пароль",
            "Установите новый мастер-пароль для защиты хранилища",
            "Изменить пароль",
            self.change_master_password,
            ModernDesign.PRIMARY
        )

        # 2FA
        if os.path.exists("2fa_secret.key"):
            twofa_card = self._create_action_card(
                tab, 1,
                "🔐 Двухфакторная аутентификация",
                "2FA включена. Вы можете отключить её для упрощения входа",
                "Отключить 2FA",
                self.disable_2fa,
                ModernDesign.DANGER
            )
        else:
            if HAS_2FA_SUPPORT:
                twofa_card = self._create_action_card(
                    tab, 1,
                    "🔐 Двухфакторная аутентификация",
                    "Добавьте дополнительный уровень защиты с помощью кодов",
                    "Настроить 2FA",
                    self.setup_2fa,
                    ModernDesign.SUCCESS
                )
            else:
                info_card = ctk.CTkFrame(tab, fg_color=ModernDesign.BG_HOVER, corner_radius=12)
                info_card.grid(row=1, column=0, sticky="ew", padx=15, pady=15)

                ctk.CTkLabel(
                    info_card,
                    text="⚠️ 2FA недоступна\n\nУстановите: pip install pyotp qrcode pillow",
                    font=ModernDesign.get_body_font(),
                    text_color=ModernDesign.TEXT_SECONDARY,
                    justify="center"
                ).pack(padx=20, pady=20)

        # Проверка паролей
        check_card = self._create_action_card(
            tab, 2,
            "🔍 Проверка надёжности",
            "Проанализируйте силу всех сохранённых паролей",
            "Проверить все пароли",
            self.check_all_passwords,
            ModernDesign.WARNING
        )

    def setup_backup_tab(self, tab):
        """Настраивает вкладку резервного копирования"""
        # Директория
        dir_card = ctk.CTkFrame(tab, fg_color=ModernDesign.BG_HOVER, corner_radius=12)
        dir_card.grid(row=0, column=0, sticky="ew", padx=15, pady=15)

        dir_content = ctk.CTkFrame(dir_card, fg_color="transparent")
        dir_content.pack(fill="x", padx=20, pady=20)
        dir_content.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            dir_content,
            text="💾 Директория для резервных копий",
            font=("Segoe UI", 14, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY,
            anchor="w"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        entry_container = ctk.CTkFrame(dir_content, fg_color="transparent")
        entry_container.grid(row=1, column=0, columnspan=2, sticky="ew")
        entry_container.grid_columnconfigure(0, weight=1)

        dir_entry = ctk.CTkEntry(
            entry_container,
            textvariable=self.backup_dir_var,
            height=45,
            font=("Segoe UI", 11),
            border_width=0,
            fg_color=ModernDesign.BG_CARD,
            corner_radius=8
        )
        dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        def select_backup_dir():
            dir_path = filedialog.askdirectory()
            if dir_path:
                self.backup_dir_var.set(dir_path)
                ToastNotification.show(self.window, "Директория выбрана", "success")

        select_btn = ctk.CTkButton(
            entry_container,
            text="📁 Выбрать",
            command=select_backup_dir,
            font=("Segoe UI", 12, "bold"),
            width=110,
            height=45,
            fg_color=ModernDesign.PRIMARY,
            hover_color=ModernDesign.PRIMARY_DARK,
            corner_radius=8
        )
        select_btn.grid(row=0, column=1)

        # Автобэкап
        auto_backup_frame = ctk.CTkFrame(dir_content, fg_color="transparent")
        auto_backup_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=(15, 0))

        ctk.CTkCheckBox(
            auto_backup_frame,
            text="Автоматически создавать резервную копию при выходе",
            variable=self.auto_backup_var,
            font=ModernDesign.get_body_font(),
            text_color=ModernDesign.TEXT_SECONDARY,
            checkbox_width=24,
            checkbox_height=24,
            corner_radius=6
        ).pack()

    def _create_action_card(self, parent, row, title, description, button_text, command, color):
        """Создаёт карточку с действием"""
        card = ctk.CTkFrame(parent, fg_color=ModernDesign.BG_HOVER, corner_radius=12)
        card.grid(row=row, column=0, sticky="ew", padx=15, pady=15)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=20)
        content.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            content,
            text=title,
            font=("Segoe UI", 14, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY,
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        ctk.CTkLabel(
            content,
            text=description,
            font=ModernDesign.get_caption_font(),
            text_color=ModernDesign.TEXT_SECONDARY,
            anchor="w",
            wraplength=500
        ).grid(row=1, column=0, sticky="w", pady=(0, 12))

        ctk.CTkButton(
            content,
            text=button_text,
            command=command,
            font=("Segoe UI", 12, "bold"),
            height=40,
            width=200,
            fg_color=color,
            hover_color=color if color == ModernDesign.DANGER else ModernDesign.PRIMARY_DARK,
            corner_radius=8
        ).grid(row=2, column=0, sticky="w")

        return card

    def save_settings(self):
        """Сохраняет настройки"""
        try:
            auto_lock_value = self.auto_lock_var.get().strip()
            if not auto_lock_value:
                auto_lock_value = "5"

            try:
                auto_lock_time = int(auto_lock_value)
                if auto_lock_time < 1:
                    auto_lock_time = 1
            except ValueError:
                auto_lock_time = 5
                ToastNotification.show(self.window, "Установлено значение по умолчанию: 5 минут", "warning")

            settings_data = {
                "auto_lock_time": auto_lock_time,
                "backup_directory": self.backup_dir_var.get(),
                "auto_backup": self.auto_backup_var.get()
            }

            backup_dir = settings_data["backup_directory"]
            if backup_dir and not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)

            with open("app_settings.json", "w", encoding="utf-8") as f:
                json.dump(settings_data, f, indent=4, ensure_ascii=False)

            ToastNotification.show(self.window, "Настройки сохранены!", "success")
            self.window.after(800, self.window.destroy)

        except Exception as e:
            ToastNotification.show(self.window, f"Ошибка: {e}", "error")

    def change_master_password(self):
        """Изменение мастер-пароля"""
        # TODO: Реализовать в стиле add_password
        ToastNotification.show(self.window, "Функция в разработке", "info")

    def setup_2fa(self):
        """Настройка 2FA"""
        # TODO: Реализовать в стиле add_password
        ToastNotification.show(self.window, "Функция в разработке", "info")

    def disable_2fa(self):
        """Отключение 2FA"""
        result = messagebox.askyesno(
            "Подтверждение",
            "Отключить двухфакторную аутентификацию?\n\nЭто снизит безопасность."
        )

        if result:
            try:
                if os.path.exists("2fa_secret.key"):
                    os.remove("2fa_secret.key")
                ToastNotification.show(self.window, "2FA отключена", "success")
                self.window.after(500, lambda: self.setup_ui())
            except Exception as e:
                ToastNotification.show(self.window, f"Ошибка: {e}", "error")

    def check_all_passwords(self):
        """Проверяет надёжность всех паролей"""
        passwords = self.db.get_all_passwords()

        if not passwords:
            ToastNotification.show(self.window, "В базе нет паролей для проверки", "warning")
            return

        # Создаем окно результатов
        results_window = ctk.CTkToplevel(self.window)
        results_window.title("🔍 Анализ надёжности паролей")
        results_window.geometry("750x650")
        results_window.minsize(700, 600)
        results_window.configure(fg_color=ModernDesign.BG_DARK)

        results_window.grid_columnconfigure(0, weight=1)
        results_window.grid_rowconfigure(0, weight=1)
        results_window.transient(self.window)
        results_window.grab_set()

        # Центрируем окно
        results_window.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() // 2) - (results_window.winfo_width() // 2)
        y = self.window.winfo_y() + (self.window.winfo_height() // 2) - (results_window.winfo_height() // 2)
        results_window.geometry(f"+{x}+{y}")

        # Главный контейнер
        main_container = ctk.CTkFrame(results_window, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)

        # === ЗАГОЛОВОК ===
        header_frame = ctk.CTkFrame(main_container, fg_color=ModernDesign.BG_CARD, corner_radius=15)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(padx=25, pady=20)

        ctk.CTkLabel(
            header_content,
            text="🔍",
            font=("Segoe UI", 48)
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            header_content,
            text="Анализ надёжности паролей",
            font=("Segoe UI", 22, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY
        ).pack()

        ctk.CTkLabel(
            header_content,
            text=f"Проверено записей: {len(passwords)}",
            font=("Segoe UI", 12),
            text_color=ModernDesign.TEXT_SECONDARY
        ).pack(pady=(5, 0))

        # === СТАТИСТИКА ===
        weak_count = 0
        medium_count = 0
        strong_count = 0

        # Собираем статистику
        password_results = []

        for password_id, title, category in passwords:
            try:
                password_data = self.db.get_password(password_id)
                password = password_data['password']

                # Оценка надёжности
                score = 0
                feedback = []

                if len(password) >= 8:
                    score += 25
                else:
                    feedback.append("минимум 8 символов")

                if len(password) >= 12:
                    score += 15

                if any(c.islower() for c in password):
                    score += 15
                else:
                    feedback.append("строчные буквы")

                if any(c.isupper() for c in password):
                    score += 15
                else:
                    feedback.append("заглавные буквы")

                if any(c.isdigit() for c in password):
                    score += 15
                else:
                    feedback.append("цифры")

                if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
                    score += 15
                else:
                    feedback.append("спецсимволы")

                # Определяем уровень
                if score >= 80:
                    level = "Отличный"
                    color = ModernDesign.SUCCESS
                    icon = "✓"
                    strong_count += 1
                elif score >= 60:
                    level = "Хороший"
                    color = ModernDesign.PRIMARY
                    icon = "○"
                    strong_count += 1
                elif score >= 40:
                    level = "Средний"
                    color = ModernDesign.WARNING
                    icon = "⚠"
                    medium_count += 1
                else:
                    level = "Слабый"
                    color = ModernDesign.DANGER
                    icon = "✕"
                    weak_count += 1

                password_results.append({
                    'title': title,
                    'category': category,
                    'score': score,
                    'level': level,
                    'color': color,
                    'icon': icon,
                    'feedback': feedback
                })

            except Exception as e:
                print(f"Ошибка анализа пароля {title}: {e}")

        # Карточка статистики
        stats_card = ctk.CTkFrame(main_container, fg_color=ModernDesign.BG_CARD, corner_radius=12)
        stats_card.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        stats_content = ctk.CTkFrame(stats_card, fg_color="transparent")
        stats_content.pack(fill="x", padx=20, pady=15)
        stats_content.grid_columnconfigure((0, 1, 2), weight=1)

        # Сильные
        strong_frame = ctk.CTkFrame(stats_content, fg_color=ModernDesign.BG_HOVER, corner_radius=10)
        strong_frame.grid(row=0, column=0, sticky="ew", padx=5)

        ctk.CTkLabel(
            strong_frame,
            text="✓",
            font=("Segoe UI", 32),
            text_color=ModernDesign.SUCCESS
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            strong_frame,
            text=str(strong_count),
            font=("Segoe UI", 24, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY
        ).pack()

        ctk.CTkLabel(
            strong_frame,
            text="Сильные",
            font=ModernDesign.get_caption_font(),
            text_color=ModernDesign.TEXT_SECONDARY
        ).pack(pady=(0, 10))

        # Средние
        medium_frame = ctk.CTkFrame(stats_content, fg_color=ModernDesign.BG_HOVER, corner_radius=10)
        medium_frame.grid(row=0, column=1, sticky="ew", padx=5)

        ctk.CTkLabel(
            medium_frame,
            text="⚠",
            font=("Segoe UI", 32),
            text_color=ModernDesign.WARNING
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            medium_frame,
            text=str(medium_count),
            font=("Segoe UI", 24, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY
        ).pack()

        ctk.CTkLabel(
            medium_frame,
            text="Средние",
            font=ModernDesign.get_caption_font(),
            text_color=ModernDesign.TEXT_SECONDARY
        ).pack(pady=(0, 10))

        # Слабые
        weak_frame = ctk.CTkFrame(stats_content, fg_color=ModernDesign.BG_HOVER, corner_radius=10)
        weak_frame.grid(row=0, column=2, sticky="ew", padx=5)

        ctk.CTkLabel(
            weak_frame,
            text="✕",
            font=("Segoe UI", 32),
            text_color=ModernDesign.DANGER
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            weak_frame,
            text=str(weak_count),
            font=("Segoe UI", 24, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY
        ).pack()

        ctk.CTkLabel(
            weak_frame,
            text="Слабые",
            font=ModernDesign.get_caption_font(),
            text_color=ModernDesign.TEXT_SECONDARY
        ).pack(pady=(0, 10))

        scroll_frame = ctk.CTkScrollableFrame(
            main_container,
            fg_color="transparent"
        )
        scroll_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 15))
        scroll_frame.grid_columnconfigure(0, weight=1)

        # Сортируем: сначала слабые, потом средние, потом сильные
        password_results.sort(key=lambda x: x['score'])

        for i, result in enumerate(password_results):
            card = ctk.CTkFrame(scroll_frame, fg_color=ModernDesign.BG_CARD, corner_radius=12,
                               border_width=2, border_color=result['color'])
            card.grid(row=i, column=0, sticky="ew", pady=5)
            card.grid_columnconfigure(1, weight=1)

            # Иконка
            ctk.CTkLabel(
                card,
                text=result['icon'],
                font=("Segoe UI", 24),
                text_color=result['color'],
                width=40
            ).grid(row=0, column=0, rowspan=2, padx=(15, 10), pady=15)

            # Информация
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=15)
            info_frame.grid_columnconfigure(0, weight=1)

            # Название
            title_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            title_frame.grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                title_frame,
                text=result['title'],
                font=("Segoe UI", 13, "bold"),
                text_color=ModernDesign.TEXT_PRIMARY,
                anchor="w"
            ).pack(side="left")

            if result['category']:
                ctk.CTkLabel(
                    title_frame,
                    text=f" • {result['category']}",
                    font=("Segoe UI", 11),
                    text_color=ModernDesign.TEXT_MUTED,
                    anchor="w"
                ).pack(side="left", padx=(5, 0))

            # Оценка
            score_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            score_frame.grid(row=1, column=0, sticky="w", pady=(5, 0))

            ctk.CTkLabel(
                score_frame,
                text=f"{result['level']}",
                font=("Segoe UI", 11, "bold"),
                text_color=result['color']
            ).pack(side="left")

            ctk.CTkLabel(
                score_frame,
                text=f" ({result['score']}/100)",
                font=("Segoe UI", 10),
                text_color=ModernDesign.TEXT_SECONDARY
            ).pack(side="left")


            if result['feedback']:
                hint_text = "Добавьте: " + ", ".join(result['feedback'][:2])
                ctk.CTkLabel(
                    info_frame,
                    text=hint_text,
                    font=("Segoe UI", 10),
                    text_color=ModernDesign.TEXT_MUTED,
                    anchor="w"
                ).grid(row=2, column=0, sticky="w", pady=(3, 0))

        if weak_count > 0 or medium_count > 0:
            recommend_frame = ctk.CTkFrame(main_container, fg_color=ModernDesign.BG_HOVER, corner_radius=10)
            recommend_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15))

            ctk.CTkLabel(
                recommend_frame,
                text=f"💡 Рекомендуется обновить {weak_count + medium_count} пароль(ей) для повышения безопасности",
                font=ModernDesign.get_caption_font(),
                text_color=ModernDesign.TEXT_SECONDARY,
                wraplength=650
            ).pack(padx=15, pady=12)

        close_btn = ctk.CTkButton(
            main_container,
            text="✓ Закрыть",
            command=results_window.destroy,
            font=("Segoe UI", 14, "bold"),
            height=50,
            fg_color=ModernDesign.PRIMARY,
            hover_color=ModernDesign.PRIMARY_DARK,
            corner_radius=10
        )
        close_btn.grid(row=4, column=0, sticky="ew")