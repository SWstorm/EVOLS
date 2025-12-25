import customtkinter as ctk
from tkinter import messagebox, simpledialog, filedialog
import os
import tkinter as tk
from functools import partial
from utils.design_system import DesignSystem, ThemeManager


class ModernDesign:
    """Крутая система дизайна для главного окна"""

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

    # Категории (цветные индикаторы)
    CATEGORY_COLORS = {
        "Работа": "#FF6B6B",
        "Личное": "#4ECDC4",
        "Финансы": "#FFE66D",
        "Соцсети": "#9B59B6",
        "Email": "#3498DB",
        "Другое": "#95A5A6"
    }

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
    """Красивые toast-уведомления БЕЗ утечек памяти"""

    _active_toasts = []

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

        ToastNotification._active_toasts.append(toast)

        def fade_out():
            try:
                if toast.winfo_exists():
                    toast.destroy()
                    if toast in ToastNotification._active_toasts:
                        ToastNotification._active_toasts.remove(toast)
            except:
                pass

        timer_id = parent.after(duration, fade_out)
        toast.timer_id = timer_id

    @staticmethod
    def cleanup_all():
        """Очищает все активные уведомления"""
        for toast in ToastNotification._active_toasts[:]:
            try:
                if hasattr(toast, 'timer_id'):
                    toast.master.after_cancel(toast.timer_id)
                toast.destroy()
            except:
                pass
        ToastNotification._active_toasts.clear()


class MainWindow:
    def __init__(self, root, db, encryptor):
        self.root = root
        self.db = db
        self.encryptor = encryptor

        self.add_password_window = None
        self.settings_window = None

        self.idle_timer_id = None
        self.idle_timeout = 5 * 60 * 1000

        # ✅ Debounce для поиска
        self.search_debounce_timer = None

        # ✅ Кеш паролей для оптимизации
        self.passwords_cache = []
        self.cache_valid = False

        # ✅ Виртуализация списка
        self.visible_passwords_count = 20
        self.current_passwords = []  # Текущий отфильтрованный список

        # Переменные для поиска
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.on_search_change_debounced)

        # ✅ Список для отслеживания bind событий
        self.bound_events = []

        # Применяем темную тему
        ctk.set_appearance_mode("dark")

        self.root.title("EVOLS Password Manager")
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)
        self.root.configure(fg_color=ModernDesign.BG_DARK)

        self.load_settings()
        self.setup_ui()
        self.setup_idle_timer()

        self.root.bind("<Key>", self.reset_idle_timer)
        self.root.bind("<Motion>", self.reset_idle_timer)
        self.root.bind("<Button>", self.reset_idle_timer)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Правильная очистка перед закрытием"""
        if self.idle_timer_id:
            self.root.after_cancel(self.idle_timer_id)
        if self.search_debounce_timer:
            self.root.after_cancel(self.search_debounce_timer)

        self.cleanup_bound_events()
        ToastNotification.cleanup_all()

        if self.add_password_window:
            try:
                self.add_password_window.destroy()
            except:
                pass
        if self.settings_window:
            try:
                self.settings_window.destroy()
            except:
                pass

        self.root.destroy()

    def load_settings(self):
        try:
            import json
            if os.path.exists("app_settings.json"):
                with open("app_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    auto_lock_time = settings.get("auto_lock_time", 5)

                    if isinstance(auto_lock_time, str):
                        try:
                            auto_lock_time = int(auto_lock_time) if auto_lock_time.isdigit() else 5
                        except (ValueError, AttributeError):
                            auto_lock_time = 5
                    elif not isinstance(auto_lock_time, (int, float)):
                        auto_lock_time = 5

                    self.idle_timeout = auto_lock_time * 60 * 1000
            else:
                self.idle_timeout = 5 * 60 * 1000
        except Exception as e:
            print(f"Ошибка при загрузке настроек: {e}")
            self.idle_timeout = 5 * 60 * 1000

    def setup_idle_timer(self):
        if self.idle_timeout > 0:
            if self.idle_timer_id:
                self.root.after_cancel(self.idle_timer_id)
            self.idle_timer_id = self.root.after(self.idle_timeout, self.lock_application)

    def reset_idle_timer(self, event=None):
        self.setup_idle_timer()

    def lock_application(self):
        self.root.withdraw()

        def on_unlock_success():
            self.root.deiconify()
            self.setup_idle_timer()

        def on_unlock_cancel():
            self.on_closing()

        from gui.unlock_window import UnlockWindow
        unlock_window = UnlockWindow(
            parent=self.root,
            on_success_callback=on_unlock_success,
            on_cancel_callback=on_unlock_cancel
        )

    def setup_ui(self):
        self.cleanup_bound_events()

        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Главный контейнер
        main_container = ctk.CTkFrame(self.root, fg_color=ModernDesign.BG_DARK)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=0)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # === КРУТОЙ САЙДБАР ===
        self.sidebar = ctk.CTkFrame(
            main_container,
            width=260,
            corner_radius=0,
            fg_color=ModernDesign.SIDEBAR_BG
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Логотип и название
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, pady=(30, 30), sticky="ew")
        logo_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            logo_frame,
            text="🔐",
            font=("Segoe UI", 48)
        ).grid(row=0, column=0, pady=(0, 5))

        ctk.CTkLabel(
            logo_frame,
            text="EVOLS",
            font=("Segoe UI", 24, "bold"),
            text_color=ModernDesign.PRIMARY
        ).grid(row=1, column=0)

        ctk.CTkLabel(
            logo_frame,
            text="Password Manager",
            font=("Segoe UI", 11),
            text_color=ModernDesign.TEXT_SECONDARY
        ).grid(row=2, column=0, pady=(0, 0))

        # Разделитель
        ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color=ModernDesign.BG_HOVER
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

        # Кнопки меню с иконками
        menu_buttons = [
            {"icon": "➕", "text": "Добавить пароль", "command": self.show_add_password, "color": ModernDesign.SUCCESS},
            {"icon": "🎲", "text": "Генератор", "command": self.show_password_generator, "color": ModernDesign.PRIMARY},
            {"icon": "🔍", "text": "Проверить надёжность", "command": self.check_password_strength, "color": ModernDesign.WARNING},
            {"icon": "💾", "text": "Резервная копия", "command": self.backup_data, "color": ModernDesign.SECONDARY},
            {"icon": "⚙️", "text": "Настройки", "command": self.show_settings, "color": ModernDesign.TEXT_MUTED}
        ]

        for i, btn_data in enumerate(menu_buttons):
            btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            btn_frame.grid(row=i + 2, column=0, pady=3, padx=15, sticky="ew")
            btn_frame.grid_columnconfigure(1, weight=1)

            # Иконка
            ctk.CTkLabel(
                btn_frame,
                text=btn_data["icon"],
                font=("Segoe UI", 18),
                width=40
            ).grid(row=0, column=0, padx=(10, 5))

            # Кнопка
            btn = ctk.CTkButton(
                btn_frame,
                text=btn_data["text"],
                command=btn_data["command"],
                font=ModernDesign.get_body_font(),
                height=45,
                fg_color="transparent",
                hover_color=ModernDesign.BG_HOVER,
                anchor="w",
                border_width=0
            )
            btn.grid(row=0, column=1, sticky="ew")

        # === ГЛАВНАЯ ПАНЕЛЬ ===
        main_panel = ctk.CTkFrame(main_container, fg_color=ModernDesign.BG_DARK)
        main_panel.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_panel.grid_columnconfigure(0, weight=1)
        main_panel.grid_rowconfigure(2, weight=1)

        # Заголовок и статистика
        self.header_frame = ctk.CTkFrame(main_panel, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.update_header_stats()

        # Поиск
        search_frame = ctk.CTkFrame(main_panel, fg_color=ModernDesign.BG_CARD, corner_radius=12)
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=("Segoe UI", 20)
        ).grid(row=0, column=0, padx=(15, 5), pady=12)

        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Поиск паролей...",
            font=ModernDesign.get_body_font(),
            height=40,
            border_width=0,
            fg_color="transparent"
        )
        search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=12)

        # Список паролей (скроллируемый)
        self.password_container = ctk.CTkScrollableFrame(
            main_panel,
            fg_color="transparent"
        )
        self.password_container.grid(row=2, column=0, sticky="nsew")
        self.password_container.grid_columnconfigure(0, weight=1)

        self.load_passwords()

    def update_header_stats(self):
        """Обновляет статистику в заголовке"""
        for widget in self.header_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.header_frame,
            text="Ваши пароли",
            font=ModernDesign.get_title_font(),
            text_color=ModernDesign.TEXT_PRIMARY,
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        # ✅ ОПТИМИЗАЦИЯ: Используем кеш
        if not self.cache_valid:
            self.passwords_cache = self.db.get_all_passwords()
            self.cache_valid = True

        password_count = len(self.passwords_cache)

        stats_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="w", pady=(10, 0))

        stats = [
            {"icon": "📊", "value": str(password_count), "label": "Всего паролей"},
            {"icon": "🔒", "value": str(password_count), "label": "Защищено"},
            {"icon": "⚡", "value": "256-bit", "label": "AES шифрование"}
        ]

        for i, stat in enumerate(stats):
            stat_card = ctk.CTkFrame(stats_frame, fg_color=ModernDesign.BG_CARD, corner_radius=10)
            stat_card.grid(row=0, column=i, padx=(0, 10), sticky="w")

            stat_content = ctk.CTkFrame(stat_card, fg_color="transparent")
            stat_content.pack(padx=15, pady=10)

            ctk.CTkLabel(
                stat_content,
                text=stat["icon"],
                font=("Segoe UI", 20)
            ).pack(side="left", padx=(0, 10))

            stat_text = ctk.CTkFrame(stat_content, fg_color="transparent")
            stat_text.pack(side="left")

            ctk.CTkLabel(
                stat_text,
                text=stat["value"],
                font=("Segoe UI", 16, "bold"),
                text_color=ModernDesign.TEXT_PRIMARY
            ).pack(anchor="w")

            ctk.CTkLabel(
                stat_text,
                text=stat["label"],
                font=("Segoe UI", 10),
                text_color=ModernDesign.TEXT_SECONDARY
            ).pack(anchor="w")

    def on_search_change_debounced(self, *args):
        """✅ Отложенная фильтрация (debounce 300ms)"""
        if self.search_debounce_timer:
            self.root.after_cancel(self.search_debounce_timer)

        self.search_debounce_timer = self.root.after(300, self.load_passwords)

    def cleanup_bound_events(self):
        """✅ Очищает все bind события"""
        for widget, event_type in self.bound_events:
            try:
                if widget.winfo_exists():
                    widget.unbind(event_type)
            except:
                pass
        self.bound_events.clear()

    def invalidate_cache(self):
        """Сбрасывает кеш паролей"""
        self.cache_valid = False
        self.visible_passwords_count = 20

    def load_passwords(self):
        """✅ ОПТИМИЗИРОВАННАЯ загрузка с виртуализацией"""
        # Показываем индикатор
        self.show_loading_indicator()

        # Откладываем загрузку на 10ms чтобы UI успел отрисоваться
        self.root.after(10, self._load_passwords_async)

    def show_loading_indicator(self):
        """Показывает спиннер загрузки"""
        self.cleanup_bound_events()

        for widget in self.password_container.winfo_children():
            widget.destroy()

        loading_frame = ctk.CTkFrame(
            self.password_container,
            fg_color="transparent"
        )
        loading_frame.grid(row=0, column=0, sticky="ew", pady=100)

        ctk.CTkLabel(
            loading_frame,
            text="⏳",
            font=("Segoe UI", 48)
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            loading_frame,
            text="Загрузка паролей...",
            font=("Segoe UI", 14),
            text_color=ModernDesign.TEXT_SECONDARY
        ).pack()

        self.root.update_idletasks()

    def _load_passwords_async(self):
        """✅ Асинхронная загрузка"""
        try:
            self.cleanup_bound_events()

            # ✅ Загружаем из кеша
            if not self.cache_valid:
                self.passwords_cache = self.db.get_all_passwords()
                self.cache_valid = True

            passwords = self.passwords_cache[:]

            # Фильтрация
            search_term = self.search_var.get().lower()
            if search_term:
                passwords = [p for p in passwords if search_term in p[1].lower() or 
                            (p[2] and search_term in p[2].lower())]

            self.current_passwords = passwords

            for widget in self.password_container.winfo_children():
                widget.destroy()

            if not passwords:
                self._show_empty_state(search_term)
                return

            # ✅ Виртуализация: показываем только первые 20
            visible_passwords = passwords[:self.visible_passwords_count]

            self.password_ids = []

            # ✅ Прогрессивная отрисовка
            self._create_password_cards_progressive(visible_passwords, 0)

            # Кнопка "Загрузить ещё"
            if len(passwords) > self.visible_passwords_count:
                self._show_load_more_button(len(passwords) - self.visible_passwords_count)

        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            ToastNotification.show(self.root, f"Ошибка: {e}", "error")

    def _create_password_cards_progressive(self, passwords, index):
        """✅ Создаёт карточки постепенно (по 5 штук)"""
        if index >= len(passwords):
            return

        batch_size = 5
        end_index = min(index + batch_size, len(passwords))

        for i in range(index, end_index):
            id, title, category = passwords[i]
            self._create_password_card(i, id, title, category)

        if end_index < len(passwords):
            self.root.after(10, lambda: self._create_password_cards_progressive(passwords, end_index))

    def _create_password_card(self, row_index, id, title, category):
        """Создаёт одну карточку пароля"""
        card = ctk.CTkFrame(
            self.password_container,
            fg_color=ModernDesign.BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=ModernDesign.BG_HOVER
        )
        card.grid(row=row_index, column=0, sticky="ew", pady=5)
        card.grid_columnconfigure(1, weight=1)
        card.password_id = id
        self.password_ids.append(id)

        category_color = ModernDesign.CATEGORY_COLORS.get(category, ModernDesign.TEXT_MUTED)
        indicator = ctk.CTkFrame(
            card,
            width=4,
            fg_color=category_color,
            corner_radius=0
        )
        indicator.grid(row=0, column=0, sticky="ns", rowspan=2)

        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.grid(row=0, column=1, sticky="ew", padx=20, pady=15)
        content_frame.grid_columnconfigure(0, weight=1)

        title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w")

        category_icons = {
            "Работа": "💼",
            "Личное": "👤",
            "Финансы": "💳",
            "Соцсети": "📱",
            "Email": "📧",
            "Другое": "🔑"
        }
        icon = category_icons.get(category, "🔑")

        ctk.CTkLabel(
            title_frame,
            text=icon,
            font=("Segoe UI", 20)
        ).pack(side="left", padx=(0, 10))

        title_text = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_text.pack(side="left")

        ctk.CTkLabel(
            title_text,
            text=title,
            font=("Segoe UI", 14, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY,
            anchor="w"
        ).pack(anchor="w")

        if category:
            ctk.CTkLabel(
                title_text,
                text=f"• {category}",
                font=("Segoe UI", 10),
                text_color=category_color,
                anchor="w"
            ).pack(anchor="w")

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=2, padx=15, pady=15)

        view_btn = ctk.CTkButton(
            btn_frame,
            text="👁️ Просмотр",
            command=partial(self.view_password_by_id, id),
            font=("Segoe UI", 11, "bold"),
            width=110,
            height=35,
            fg_color=ModernDesign.PRIMARY,
            hover_color=ModernDesign.PRIMARY_DARK,
            corner_radius=8
        )
        view_btn.pack(side="left", padx=2)

        copy_btn = ctk.CTkButton(
            btn_frame,
            text="📋",
            command=partial(self.quick_copy_password, id),
            font=("Segoe UI", 14),
            width=35,
            height=35,
            fg_color=ModernDesign.SUCCESS,
            hover_color="#00C853",
            corner_radius=8
        )
        copy_btn.pack(side="left", padx=2)

        on_enter = partial(self._card_hover, card, ModernDesign.PRIMARY)
        on_leave = partial(self._card_hover, card, ModernDesign.BG_HOVER)

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        self.bound_events.append((card, "<Enter>"))
        self.bound_events.append((card, "<Leave>"))

    def _show_empty_state(self, search_term):
        """Показывает пустое состояние"""
        empty_frame = ctk.CTkFrame(
            self.password_container,
            fg_color=ModernDesign.BG_CARD,
            corner_radius=15
        )
        empty_frame.grid(row=0, column=0, sticky="ew", pady=50)

        empty_content = ctk.CTkFrame(empty_frame, fg_color="transparent")
        empty_content.pack(padx=40, pady=60)

        ctk.CTkLabel(
            empty_content,
            text="🔐",
            font=("Segoe UI", 60)
        ).pack(pady=(0, 15))

        ctk.CTkLabel(
            empty_content,
            text="У вас пока нет сохраненных паролей" if not search_term else "Ничего не найдено",
            font=("Segoe UI", 16),
            text_color=ModernDesign.TEXT_SECONDARY
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            empty_content,
            text="Нажмите '➕ Добавить пароль' чтобы начать" if not search_term else "Попробуйте другой запрос",
            font=ModernDesign.get_caption_font(),
            text_color=ModernDesign.TEXT_MUTED
        ).pack(pady=(0, 20))

        if not search_term:
            ctk.CTkButton(
                empty_content,
                text="Добавить первый пароль",
                command=self.show_add_password,
                font=ModernDesign.get_button_font(),
                height=45,
                fg_color=ModernDesign.SUCCESS,
                hover_color="#00C853",
                corner_radius=10
            ).pack()

    def _show_load_more_button(self, remaining_count):
        """Показывает кнопку 'Загрузить ещё'"""
        load_more_frame = ctk.CTkFrame(
            self.password_container,
            fg_color="transparent"
        )
        load_more_frame.grid(row=999, column=0, sticky="ew", pady=20)

        ctk.CTkButton(
            load_more_frame,
            text=f"⬇️ Загрузить ещё ({remaining_count})",
            command=self._load_more_passwords,
            font=ModernDesign.get_button_font(),
            height=45,
            fg_color=ModernDesign.PRIMARY,
            hover_color=ModernDesign.PRIMARY_DARK,
            corner_radius=10
        ).pack()

    def _load_more_passwords(self):
        """Загружает ещё пароли"""
        self.visible_passwords_count += 20
        self.load_passwords()

    def _card_hover(self, card, color, event=None):
        """Вспомогательная функция для hover эффекта"""
        try:
            if card.winfo_exists():
                card.configure(border_color=color)
        except:
            pass

    def quick_copy_password(self, password_id):
        """Быстрое копирование пароля"""
        try:
            password_data = self.db.get_password(password_id)
            self.root.clipboard_clear()
            self.root.clipboard_append(password_data['password'])
            ToastNotification.show(self.root, f"Пароль '{password_data['title']}' скопирован!", "success")
        except Exception as e:
            ToastNotification.show(self.root, f"Ошибка: {e}", "error")

    def view_password_by_id(self, password_id):
        """Открывает окно просмотра пароля"""
        # ✅ Открываем через after()
        self.root.after(50, lambda: self._open_view_window(password_id))

    def _open_view_window(self, password_id):
        """Внутренний метод открытия окна просмотра"""
        try:
            password_data = self.db.get_password(password_id)
            self.view_password_details_direct(password_id, password_data)
        except Exception as e:
            ToastNotification.show(self.root, f"Ошибка: {e}", "error")

    def view_password_details_direct(self, password_id, password_data):
        """Показывает детали пароля"""
        view_window = ctk.CTkToplevel(self.root)
        view_window.title(f"{password_data['title']}")
        view_window.geometry("550x650")
        view_window.minsize(500, 600)
        view_window.configure(fg_color=ModernDesign.BG_DARK)

        view_window.grid_columnconfigure(0, weight=1)
        view_window.grid_rowconfigure(0, weight=1)
        view_window.transient(self.root)
        view_window.grab_set()

        scroll_frame = ctk.CTkScrollableFrame(view_window, fg_color="transparent")
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        scroll_frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(scroll_frame, fg_color=ModernDesign.BG_CARD, corner_radius=15)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(padx=25, pady=20)

        ctk.CTkLabel(
            header_content,
            text="🔐",
            font=("Segoe UI", 48)
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            header_content,
            text=password_data['title'],
            font=("Segoe UI", 22, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY
        ).pack()

        if password_data['category']:
            category_color = ModernDesign.CATEGORY_COLORS.get(password_data['category'], ModernDesign.TEXT_MUTED)
            ctk.CTkLabel(
                header_content,
                text=f"• {password_data['category']}",
                font=("Segoe UI", 12),
                text_color=category_color
            ).pack(pady=(5, 0))

        fields = [
            {"label": "👤 Логин", "value": password_data['username'], "copy": True},
            {"label": "🔑 Пароль", "value": password_data['password'], "copy": True, "password": True},
            {"label": "🌐 URL", "value": password_data['url'], "copy": False},
            {"label": "📝 Заметки", "value": password_data['notes'], "copy": False, "multiline": True}
        ]

        for field in fields:
            if not field["value"] and field["label"] != "🔑 Пароль":
                continue

            field_card = ctk.CTkFrame(scroll_frame, fg_color=ModernDesign.BG_CARD, corner_radius=12)
            field_card.grid(row=fields.index(field) + 1, column=0, sticky="ew", pady=5)
            field_card.grid_columnconfigure(0, weight=1)

            field_content = ctk.CTkFrame(field_card, fg_color="transparent")
            field_content.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
            field_content.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                field_content,
                text=field["label"],
                font=("Segoe UI", 12, "bold"),
                text_color=ModernDesign.TEXT_SECONDARY,
                anchor="w"
            ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

            if field.get("multiline"):
                text_box = ctk.CTkTextbox(
                    field_content,
                    height=100,
                    font=("Segoe UI", 12),
                    fg_color=ModernDesign.BG_HOVER,
                    corner_radius=8
                )
                text_box.grid(row=1, column=0, columnspan=3, sticky="ew")
                text_box.insert("1.0", field["value"])
                text_box.configure(state="disabled")
            else:
                entry = ctk.CTkEntry(
                    field_content,
                    font=("Segoe UI", 13),
                    height=40,
                    fg_color=ModernDesign.BG_HOVER,
                    border_width=0,
                    corner_radius=8
                )
                entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))
                entry.insert(0, field["value"])
                entry.configure(state="readonly")

                if field.get("password"):
                    entry.configure(show="●")

                    toggle_btn = ctk.CTkButton(
                        field_content,
                        text="👁️",
                        command=partial(self._toggle_password_visibility, entry),
                        width=50,
                        height=40,
                        fg_color=ModernDesign.PRIMARY,
                        hover_color=ModernDesign.PRIMARY_DARK,
                        corner_radius=8,
                        font=("Segoe UI", 16)
                    )
                    toggle_btn.grid(row=1, column=1, padx=(0, 10))

                if field.get("copy"):
                    copy_btn = ctk.CTkButton(
                        field_content,
                        text="📋",
                        command=partial(self._copy_field_to_clipboard, view_window, field["value"], field["label"]),
                        width=50,
                        height=40,
                        fg_color=ModernDesign.SUCCESS,
                        hover_color="#00C853",
                        corner_radius=8,
                        font=("Segoe UI", 16)
                    )
                    copy_btn.grid(row=1, column=2 if field.get("password") else 1)

        delete_btn = ctk.CTkButton(
            scroll_frame,
            text="🗑️ Удалить пароль",
            command=partial(self.delete_password_and_close, password_id, view_window),
            font=("Segoe UI", 13, "bold"),
            height=45,
            fg_color=ModernDesign.DANGER,
            hover_color="#C62828",
            corner_radius=10
        )
        delete_btn.grid(row=10, column=0, sticky="ew", pady=(20, 0))

    def _toggle_password_visibility(self, entry):
        """Переключает видимость пароля"""
        try:
            if entry.winfo_exists():
                if entry.cget('show') == '●':
                    entry.configure(show='')
                else:
                    entry.configure(show='●')
        except:
            pass

    def _copy_field_to_clipboard(self, window, value, label):
        """Копирует поле в буфер обмена"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(value)
            ToastNotification.show(window, f"{label} скопирован!", "success")
        except Exception as e:
            ToastNotification.show(window, f"Ошибка: {e}", "error")

    def delete_password_and_close(self, password_id, window):
        """Удаляет пароль и закрывает окно"""
        result = messagebox.askyesno(
            "Подтверждение",
            "Удалить этот пароль? Действие нельзя отменить."
        )

        if result:
            try:
                self.db.delete_password(password_id)
                window.destroy()
                self.invalidate_cache()
                self.update_header_stats()
                self.load_passwords()
                ToastNotification.show(self.root, "Пароль удален", "success")
            except Exception as e:
                ToastNotification.show(self.root, f"Ошибка: {e}", "error")

    def show_add_password(self):
        """✅ Открывает окно добавления через after()"""
        self.root.after(50, self._open_add_password_window)

    def _open_add_password_window(self):
        try:
            from gui.add_password import AddPasswordWindow
            if self.add_password_window and self.add_password_window.winfo_exists():
                self.add_password_window.focus()
            else:
                self.add_password_window = AddPasswordWindow(self.root, self.db, self.encryptor, self)
                self.invalidate_cache()
        except Exception as e:
            ToastNotification.show(self.root, f"Ошибка: {e}", "error")

    def show_settings(self):
        """✅ Открывает настройки через after()"""
        self.root.after(50, self._open_settings_window)

    def _open_settings_window(self):
        try:
            from gui.settings import SettingsWindow
            if self.settings_window and self.settings_window.winfo_exists():
                self.settings_window.focus()
            else:
                self.settings_window = SettingsWindow(self.root, self.db, self.encryptor, self)
        except Exception as e:
            ToastNotification.show(self.root, f"Ошибка: {e}", "error")

    def show_password_generator(self):
        ToastNotification.show(self.root, "Генератор паролей открывается...", "info")

    def check_password_strength(self):
        ToastNotification.show(self.root, "Выберите пароль для проверки", "info")

    def backup_data(self):
        ToastNotification.show(self.root, "Создание резервной копии...", "info")