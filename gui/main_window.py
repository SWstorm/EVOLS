import customtkinter as ctk
from tkinter import messagebox, simpledialog
import os
import json
from functools import partial


# ==================== ГЛОБАЛЬНЫЕ ГОРЯЧИЕ КЛАВИШИ ====================

class GlobalHotkeys:
    """Управление глобальными горячими клавишами для всех окон приложения"""

    @staticmethod
    def setup(window):
        """
        Настраивает стандартные горячие клавиши для окна

        Args:
            window: Окно tkinter/customtkinter для привязки горячих клавиш
        """

        def select_all(event=None):
            """Ctrl+A - выделить весь текст"""
            try:
                focused = window.focus_get()
                if focused:
                    if hasattr(focused, 'select_range'):
                        focused.select_range(0, 'end')
                        focused.icursor('end')
                    elif hasattr(focused, 'tag_add'):
                        focused.tag_add('sel', '1.0', 'end')
                        focused.mark_set('insert', 'end')
            except:
                pass
            return "break"

        def copy_text(event=None):
            """Ctrl+C - копировать выделенный текст"""
            try:
                focused = window.focus_get()
                if focused:
                    try:
                        if hasattr(focused, 'selection_get'):
                            text = focused.selection_get()
                            window.clipboard_clear()
                            window.clipboard_append(text)
                    except:
                        if hasattr(focused, 'get'):
                            try:
                                text = focused.get() if hasattr(focused, 'index') else focused.get('1.0', 'end-1c')
                                if text:
                                    window.clipboard_clear()
                                    window.clipboard_append(text)
                            except:
                                pass
            except:
                pass
            return "break"

        def paste_text(event=None):
            """Ctrl+V - вставить текст из буфера обмена"""
            try:
                clipboard_text = window.clipboard_get()
                focused = window.focus_get()

                if focused and hasattr(focused, 'insert'):
                    try:
                        if hasattr(focused, 'selection_present') and focused.selection_present():
                            focused.delete('sel.first', 'sel.last')
                    except:
                        pass
                    focused.insert('insert', clipboard_text)
            except:
                pass
            return "break"

        def cut_text(event=None):
            """Ctrl+X - вырезать выделенный текст"""
            try:
                focused = window.focus_get()
                if focused:
                    try:
                        text = focused.selection_get()
                        window.clipboard_clear()
                        window.clipboard_append(text)
                        if hasattr(focused, 'delete'):
                            focused.delete('sel.first', 'sel.last')
                    except:
                        pass
            except:
                pass
            return "break"

        # Привязываем горячие клавиши
        window.bind('<Control-a>', select_all)
        window.bind('<Control-A>', select_all)
        window.bind('<Control-c>', copy_text)
        window.bind('<Control-C>', copy_text)
        window.bind('<Control-v>', paste_text)
        window.bind('<Control-V>', paste_text)
        window.bind('<Control-x>', cut_text)
        window.bind('<Control-X>', cut_text)


# ==================== СИСТЕМА ДИЗАЙНА ====================

class ModernDesign:
    """Единая система дизайна для всего приложения"""

    # Основные цвета
    PRIMARY = "#2962FF"
    PRIMARY_DARK = "#0039CB"
    SECONDARY = "#00E5FF"
    SUCCESS = "#00E676"
    DANGER = "#FF1744"
    WARNING = "#FFD600"
    FOLDER = "#FFA726"  # Цвет для папок

    # Фоновые цвета
    BG_DARK = "#0F172A"
    BG_CARD = "#1E293B"
    BG_HOVER = "#334155"
    SIDEBAR_BG = "#1A1F36"

    # Цвета текста
    TEXT_PRIMARY = "#F8FAFC"
    TEXT_SECONDARY = "#94A3B8"
    TEXT_MUTED = "#64748B"

    # Цвета категорий
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


# ==================== TOAST УВЕДОМЛЕНИЯ ====================

class ToastNotification:
    """Система всплывающих уведомлений без утечек памяти"""

    _active_toasts = []

    @staticmethod
    def show(parent, message, type="info", duration=3000):
        """
        Показывает toast уведомление

        Args:
            parent: Родительское окно
            message: Текст сообщения
            type: Тип уведомления (info, success, error, warning)
            duration: Длительность показа в миллисекундах
        """
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
        toast.update_idletasks()
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
        """Очищает все активные уведомления при закрытии приложения"""
        for toast in ToastNotification._active_toasts[:]:
            try:
                if hasattr(toast, 'timer_id'):
                    toast.master.after_cancel(toast.timer_id)
                toast.destroy()
            except:
                pass
        ToastNotification._active_toasts.clear()


# ==================== МЕНЕДЖЕР ПАПОК ====================

class FolderManager:
    """Управление папками для организации паролей"""

    def __init__(self):
        self.folders_file = "folders.json"
        self.folders = self.load_folders()

    def load_folders(self):
        """Загружает список папок из файла"""
        try:
            if os.path.exists(self.folders_file):
                with open(self.folders_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Гарантируем наличие папки "Все пароли"
                    if "Все пароли" not in data:
                        data.insert(0, "Все пароли")
                    return data
            else:
                return ["Все пароли", "Работа", "Личное", "Финансы"]
        except Exception as e:
            print(f"Ошибка загрузки папок: {e}")
            return ["Все пароли", "Работа", "Личное", "Финансы"]

    def save_folders(self):
        """Сохраняет список папок в файл"""
        try:
            with open(self.folders_file, 'w', encoding='utf-8') as f:
                json.dump(self.folders, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения папок: {e}")

    def add_folder(self, folder_name):
        """Добавляет новую папку"""
        if folder_name and folder_name not in self.folders:
            self.folders.append(folder_name)
            self.save_folders()
            return True
        return False

    def rename_folder(self, old_name, new_name):
        """Переименовывает папку"""
        if old_name == "Все пароли":
            return False
        if old_name in self.folders and new_name not in self.folders:
            idx = self.folders.index(old_name)
            self.folders[idx] = new_name
            self.save_folders()
            return True
        return False

    def delete_folder(self, folder_name):
        """Удаляет папку"""
        if folder_name == "Все пароли":
            return False
        if folder_name in self.folders:
            self.folders.remove(folder_name)
            self.save_folders()
            return True
        return False

    def get_folders(self):
        """Возвращает список папок"""
        return self.folders[:]


class AutoHideScrollableFrame(ctk.CTkScrollableFrame):
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._check_scrollbar_needed()
        self.bind("<Configure>", lambda e: self._check_scrollbar_needed())
    
    def _check_scrollbar_needed(self):
        try:
            self.update_idletasks()
            content_height = self._parent_canvas.bbox("all")
            if content_height:
                content_h = content_height[3] - content_height[1]
                visible_h = self._parent_canvas.winfo_height()
                if content_h <= visible_h:
                    self._scrollbar.grid_remove()
                else:
                    self._scrollbar.grid()
        except:
            pass

class MainWindow:
    """Главное окно менеджера паролей с системой папок"""

    def __init__(self, root, db, encryptor):
        """
        Инициализация главного окна

        Args:
            root: Корневое окно приложения
            db: Объект базы данных
            encryptor: Объект для шифрования/дешифрования
        """
        self.root = root
        self.db = db
        self.encryptor = encryptor

        # Дочерние окна
        self.add_password_window = None
        self.settings_window = None

        # Таймер автоблокировки
        self.idle_timer_id = None
        self.idle_timeout = 5 * 60 * 1000

        # Оптимизация: debounce для поиска
        self.search_debounce_timer = None

        # Оптимизация: кэширование паролей
        self.passwords_cache = []
        self.cache_valid = False

        # Виртуализация списка
        self.visible_passwords_count = 20
        self.current_passwords = []

        # Поиск
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.on_search_change_debounced)

        # Отслеживание событий для очистки
        self.bound_events = []

        # ✨ Менеджер папок
        self.folder_manager = FolderManager()
        self.current_folder = "Все пароли"
        self.folder_buttons = {}

        # Настройка темной темы
        ctk.set_appearance_mode("dark")

        # Конфигурация окна
        self.root.title("EVOLS Password Manager")
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)
        self.root.configure(fg_color=ModernDesign.BG_DARK)

        # Инициализация
        self.load_settings()
        self.setup_ui()
        self.setup_idle_timer()

        # Привязка событий для автоблокировки
        self.root.bind("<Key>", self.reset_idle_timer)
        self.root.bind("<Motion>", self.reset_idle_timer)
        self.root.bind("<Button>", self.reset_idle_timer)

        # Обработка закрытия
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Настройка горячих клавиш
        GlobalHotkeys.setup(self.root)

    # ==================== УПРАВЛЕНИЕ ЖИЗНЕННЫМ ЦИКЛОМ ====================

    def on_closing(self):
        """Корректное закрытие приложения с очисткой ресурсов"""
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
        """Загружает настройки приложения из файла"""
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

    # ==================== АВТОБЛОКИРОВКА ====================

    def setup_idle_timer(self):
        """Настраивает таймер автоблокировки"""
        if self.idle_timeout > 0:
            if self.idle_timer_id:
                self.root.after_cancel(self.idle_timer_id)
            self.idle_timer_id = self.root.after(self.idle_timeout, self.lock_application)

    def reset_idle_timer(self, event=None):
        """Сбрасывает таймер при активности пользователя"""
        self.setup_idle_timer()

    def lock_application(self):
        """Блокирует приложение и показывает окно разблокировки"""
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

    # ==================== СОЗДАНИЕ ИНТЕРФЕЙСА ====================

    def setup_ui(self):
        """Создает и настраивает пользовательский интерфейс"""
        self.cleanup_bound_events()

        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        main_container = ctk.CTkFrame(self.root, fg_color=ModernDesign.BG_DARK)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=0)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        self._create_sidebar(main_container)
        self._create_main_panel(main_container)

    def _create_sidebar(self, parent):
        """Создает боковую панель навигации"""
        self.sidebar = ctk.CTkFrame(
            parent,
            width=260,
            corner_radius=0,
            fg_color=ModernDesign.SIDEBAR_BG
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Логотип
        self._create_logo()

        # Разделитель
        ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color=ModernDesign.BG_HOVER
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

        # Кнопки меню
        self._create_menu_buttons()

        # Разделитель перед папками
        ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color=ModernDesign.BG_HOVER
        ).grid(row=5, column=0, sticky="ew", padx=20, pady=20)

        # ✨ СЕКЦИЯ ПАПОК
        self._create_folders_section()

    def _create_logo(self):
        """Создает логотип и название приложения"""
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
        ).grid(row=2, column=0)

    def _create_menu_buttons(self):
        """Создает кнопки меню в сайдбаре"""
        menu_buttons = [
            {"icon": "➕", "text": "Добавить пароль", "command": self.show_add_password},
            {"icon": "💾", "text": "Резервная копия", "command": self.backup_data},
            {"icon": "⚙️", "text": "Настройки", "command": self.show_settings}
        ]

        for i, btn_data in enumerate(menu_buttons):
            btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            btn_frame.grid(row=i + 2, column=0, pady=3, padx=15, sticky="ew")
            btn_frame.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                btn_frame,
                text=btn_data["icon"],
                font=("Segoe UI", 18),
                width=40
            ).grid(row=0, column=0, padx=(10, 5))

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

    # ==================== СЕКЦИЯ ПАПОК ====================

    def _create_folders_section(self):
        """Создает секцию управления папками"""
        # Заголовок секции
        folders_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        folders_header.grid(row=6, column=0, sticky="ew", padx=15, pady=(0, 10))
        folders_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            folders_header,
            text="📁 ПАПКИ",
            font=("Segoe UI", 11, "bold"),
            text_color=ModernDesign.TEXT_SECONDARY,
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=10)

        # Кнопка управления папками
        manage_btn = ctk.CTkButton(
            folders_header,
            text="⚙️",
            command=self.manage_folders,
            width=30,
            height=30,
            fg_color="transparent",
            hover_color=ModernDesign.BG_HOVER,
            font=("Segoe UI", 14)
        )
        manage_btn.grid(row=0, column=1)

        # Скроллируемая область для папок
        self.folders_container = AutoHideScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            height=200
        )
        self.folders_container.grid(row=7, column=0, sticky="nsew", padx=10)
        self.folders_container.grid_columnconfigure(0, weight=1)

        # Загружаем папки
        self.load_folder_buttons()

    def load_folder_buttons(self):
        """Загружает кнопки папок"""
        # Очищаем контейнер
        for widget in self.folders_container.winfo_children():
            widget.destroy()

        self.folder_buttons.clear()

        # Создаём кнопки для каждой папки
        folders = self.folder_manager.get_folders()

        for idx, folder_name in enumerate(folders):
            is_selected = folder_name == self.current_folder

            btn = ctk.CTkButton(
                self.folders_container,
                text=f"📁 {folder_name}",
                command=partial(self.select_folder, folder_name),
                font=ModernDesign.get_body_font(),
                height=40,
                fg_color=ModernDesign.PRIMARY if is_selected else "transparent",
                hover_color=ModernDesign.PRIMARY_DARK if is_selected else ModernDesign.BG_HOVER,
                anchor="w",
                border_width=0
            )
            btn.grid(row=idx, column=0, sticky="ew", pady=2)

            self.folder_buttons[folder_name] = btn

    def select_folder(self, folder_name):
        """Выбирает папку для фильтрации"""
        self.current_folder = folder_name

        # Обновляем стили кнопок
        for fname, btn in self.folder_buttons.items():
            if fname == folder_name:
                btn.configure(fg_color=ModernDesign.PRIMARY, hover_color=ModernDesign.PRIMARY_DARK)
            else:
                btn.configure(fg_color="transparent", hover_color=ModernDesign.BG_HOVER)

        # Перезагружаем пароли
        self.invalidate_cache()
        self.load_passwords()

        ToastNotification.show(self.root, f"Выбрана папка: {folder_name}", "info", 800)

    def manage_folders(self):
        """Открывает окно управления папками"""
        manage_window = ctk.CTkToplevel(self.root)
        manage_window.title("Управление папками")
        manage_window.geometry("450x550")
        manage_window.configure(fg_color=ModernDesign.BG_DARK)
        manage_window.transient(self.root)
        manage_window.grab_set()

        manage_window.grid_columnconfigure(0, weight=1)
        manage_window.grid_rowconfigure(1, weight=1)

        # Заголовок
        header = ctk.CTkFrame(manage_window, fg_color=ModernDesign.BG_CARD, corner_radius=15)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)

        ctk.CTkLabel(
            header,
            text="📁 Управление папками",
            font=("Segoe UI", 20, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY
        ).pack(pady=15)

        # Список папок
        folders_frame = AutoHideScrollableFrame(manage_window, fg_color="transparent")
        folders_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        folders_frame.grid_columnconfigure(0, weight=1)

        def refresh_folder_list():
            for widget in folders_frame.winfo_children():
                widget.destroy()

            folders = self.folder_manager.get_folders()

            for idx, folder in enumerate(folders):
                folder_card = ctk.CTkFrame(folders_frame, fg_color=ModernDesign.BG_CARD, corner_radius=10)
                folder_card.grid(row=idx, column=0, sticky="ew", pady=5)
                folder_card.grid_columnconfigure(1, weight=1)

                ctk.CTkLabel(
                    folder_card,
                    text="📁",
                    font=("Segoe UI", 20)
                ).grid(row=0, column=0, padx=15, pady=10)

                ctk.CTkLabel(
                    folder_card,
                    text=folder,
                    font=("Segoe UI", 13),
                    text_color=ModernDesign.TEXT_PRIMARY,
                    anchor="w"
                ).grid(row=0, column=1, sticky="w", padx=5, pady=10)

                if folder != "Все пароли":
                    # Кнопка переименования
                    rename_btn = ctk.CTkButton(
                        folder_card,
                        text="✏️",
                        command=partial(rename_folder_dialog, folder),
                        width=35,
                        height=35,
                        fg_color=ModernDesign.PRIMARY,
                        hover_color=ModernDesign.PRIMARY_DARK,
                        corner_radius=8
                    )
                    rename_btn.grid(row=0, column=2, padx=5, pady=10)

                    # Кнопка удаления
                    delete_btn = ctk.CTkButton(
                        folder_card,
                        text="🗑️",
                        command=partial(delete_folder_confirm, folder),
                        width=35,
                        height=35,
                        fg_color=ModernDesign.DANGER,
                        hover_color="#C62828",
                        corner_radius=8
                    )
                    delete_btn.grid(row=0, column=3, padx=5, pady=10)

        def add_new_folder():
            folder_name = simpledialog.askstring(
                "Новая папка",
                "Введите название папки:",
                parent=manage_window
            )

            if folder_name:
                if self.folder_manager.add_folder(folder_name):
                    refresh_folder_list()
                    self.load_folder_buttons()
                    ToastNotification.show(manage_window, f"Папка '{folder_name}' создана!", "success")
                else:
                    ToastNotification.show(manage_window, "Папка уже существует", "warning")

        def rename_folder_dialog(old_name):
            new_name = simpledialog.askstring(
                "Переименовать папку",
                f"Новое название для '{old_name}':",
                parent=manage_window,
                initialvalue=old_name
            )

            if new_name and new_name != old_name:
                if self.folder_manager.rename_folder(old_name, new_name):
                    # Обновляем текущую папку если она была переименована
                    if self.current_folder == old_name:
                        self.current_folder = new_name

                    # Обновляем папки у всех паролей в БД
                    self.db.rename_password_folder(old_name, new_name)

                    refresh_folder_list()
                    self.load_folder_buttons()
                    self.invalidate_cache()
                    self.load_passwords()
                    ToastNotification.show(manage_window, f"Папка переименована в '{new_name}'", "success")
                else:
                    ToastNotification.show(manage_window, "Не удалось переименовать папку", "error")

        def delete_folder_confirm(folder_name):
            result = messagebox.askyesno(
                "Удалить папку?",
                f"Удалить папку '{folder_name}'?\n\nПароли из этой папки переместятся в 'Все пароли'",
                parent=manage_window
            )

            if result:
                if self.folder_manager.delete_folder(folder_name):
                    # Перемещаем пароли в "Все пароли"
                    self.db.move_passwords_from_folder(folder_name, None)

                    # Если удалена текущая папка, переключаемся на "Все пароли"
                    if self.current_folder != "Все пароли":
                        passwords = [
                            p for p in passwords 
                            if len(p) > 6 and p[6] == self.current_folder
                        ]

                    refresh_folder_list()
                    self.load_folder_buttons()
                    self.invalidate_cache()
                    self.load_passwords()
                    ToastNotification.show(manage_window, f"Папка '{folder_name}' удалена", "success")

        refresh_folder_list()

        # Кнопка добавления папки
        add_btn = ctk.CTkButton(
            manage_window,
            text="➕ Создать новую папку",
            command=add_new_folder,
            font=ModernDesign.get_button_font(),
            height=45,
            fg_color=ModernDesign.SUCCESS,
            hover_color="#00C853",
            corner_radius=10
        )
        add_btn.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))

    def _create_main_panel(self, parent):
        """Создает основную панель с паролями"""
        main_panel = ctk.CTkFrame(parent, fg_color=ModernDesign.BG_DARK)
        main_panel.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_panel.grid_columnconfigure(0, weight=1)
        main_panel.grid_rowconfigure(2, weight=1)

        # Заголовок и статистика
        self.header_frame = ctk.CTkFrame(main_panel, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.update_header_stats()

        # Поле поиска
        self._create_search_bar(main_panel)

        # Список паролей
        self.password_container = AutoHideScrollableFrame(
            main_panel,
            fg_color="transparent"
        )
        self.password_container.grid(row=2, column=0, sticky="nsew")
        self.password_container.grid_columnconfigure(0, weight=1)

        self.load_passwords()

    def _create_search_bar(self, parent):
        """Создает строку поиска"""
        search_frame = ctk.CTkFrame(parent, fg_color=ModernDesign.BG_CARD, corner_radius=12)
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

    def update_header_stats(self):
        """Обновляет статистику в заголовке"""
        for widget in self.header_frame.winfo_children():
            widget.destroy()

        # Заголовок с названием текущей папки
        title_text = f"{self.current_folder}"

        ctk.CTkLabel(
            self.header_frame,
            text=title_text,
            font=ModernDesign.get_title_font(),
            text_color=ModernDesign.TEXT_PRIMARY,
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        if not self.cache_valid:
            self.passwords_cache = self.db.get_all_passwords()
            self.cache_valid = True

        # Фильтрация по папке
        if self.current_folder == "Все пароли":
            filtered_passwords = self.passwords_cache
        else:
            filtered_passwords = [
                p for p in self.passwords_cache 
                if len(p) > 6 and p[6] == self.current_folder
            ]


        password_count = len(filtered_passwords)

        stats_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="w", pady=(10, 0))

        stats = [
            {"icon": "📊", "value": str(password_count), "label": "Паролей в папке"},
            {"icon": "🔒", "value": str(len(self.passwords_cache)), "label": "Всего паролей"},
            {"icon": "⚡", "value": "256-bit", "label": "AES шифрование"}
        ]

        for i, stat in enumerate(stats):
            self._create_stat_card(stats_frame, stat, i)

    def _create_stat_card(self, parent, stat, column):
        """Создает карточку статистики"""
        stat_card = ctk.CTkFrame(parent, fg_color=ModernDesign.BG_CARD, corner_radius=10)
        stat_card.grid(row=0, column=column, padx=(0, 10), sticky="w")

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

    # ==================== ПОИСК И ФИЛЬТРАЦИЯ ====================

    def on_search_change_debounced(self, *args):
        """Отложенная фильтрация с debounce 300ms"""
        if self.search_debounce_timer:
            self.root.after_cancel(self.search_debounce_timer)

        self.search_debounce_timer = self.root.after(300, self.load_passwords)

    # ==================== УПРАВЛЕНИЕ КЕШЕМ И СОБЫТИЯМИ ====================

    def cleanup_bound_events(self):
        """Очищает все привязанные события"""
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

    # ==================== ЗАГРУЗКА ПАРОЛЕЙ ====================

    def load_passwords(self):
        """Оптимизированная загрузка паролей с виртуализацией"""
        self.show_loading_indicator()
        self.root.after(10, self._load_passwords_async)

    def show_loading_indicator(self):
        """Показывает индикатор загрузки"""
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
        """Асинхронная загрузка паролей"""
        try:
            self.cleanup_bound_events()

            if not self.cache_valid:
                self.passwords_cache = self.db.get_all_passwords()
                self.cache_valid = True

            passwords = self.passwords_cache[:]

            # ✨ Фильтрация по папке
            if self.current_folder != "Все пароли":
                passwords = [p for p in passwords if p[6] == self.current_folder]

            # Фильтрация по поисковому запросу
            search_term = self.search_var.get().lower()
            if search_term:
                passwords = [
                    p for p in passwords 
                    if search_term in p[1].lower() or (p[2] and search_term in p[2].lower())
                ]

            self.current_passwords = passwords

            # Обновляем статистику
            self.update_header_stats()

            for widget in self.password_container.winfo_children():
                widget.destroy()

            if not passwords:
                self._show_empty_state(search_term)
                return

            visible_passwords = passwords[:self.visible_passwords_count]

            self.password_ids = []

            self._create_password_cards_progressive(visible_passwords, 0)

            if len(passwords) > self.visible_passwords_count:
                self._show_load_more_button(len(passwords) - self.visible_passwords_count)

        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            ToastNotification.show(self.root, f"Ошибка: {e}", "error")

    def _create_password_cards_progressive(self, passwords, index):
        """Создает карточки паролей постепенно (по 5 штук)"""
        if index >= len(passwords):
            return

        batch_size = 5
        end_index = min(index + batch_size, len(passwords))

        for i in range(index, end_index):
            id, title, category = passwords[i][:3]
            self._create_password_card(i, id, title, category)

        if end_index < len(passwords):
            self.root.after(10, lambda: self._create_password_cards_progressive(passwords, end_index))

    def _create_password_card(self, row_index, id, title, category):
        """Создает одну карточку пароля"""
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

        self._create_card_title(content_frame, title, category, category_color)
        self._create_card_buttons(card, id)

        on_enter = partial(self._card_hover, card, ModernDesign.PRIMARY)
        on_leave = partial(self._card_hover, card, ModernDesign.BG_HOVER)

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        self.bound_events.append((card, "<Enter>"))
        self.bound_events.append((card, "<Leave>"))

    def _create_card_title(self, parent, title, category, category_color):
        """Создает заголовок карточки с иконкой"""
        title_frame = ctk.CTkFrame(parent, fg_color="transparent")
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

    def _create_card_buttons(self, card, id):
        """Создает кнопки для карточки"""
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

        if search_term:
            message = "Ничего не найдено"
            submessage = "Попробуйте другой запрос"
        elif self.current_folder != "Все пароли":
            message = f"В папке '{self.current_folder}' пока нет паролей"
            submessage = "Добавьте пароль и выберите эту папку"
        else:
            message = "У вас пока нет сохраненных паролей"
            submessage = "Нажмите '➕ Добавить пароль' чтобы начать"

        ctk.CTkLabel(
            empty_content,
            text=message,
            font=("Segoe UI", 16),
            text_color=ModernDesign.TEXT_SECONDARY
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            empty_content,
            text=submessage,
            font=ModernDesign.get_caption_font(),
            text_color=ModernDesign.TEXT_MUTED
        ).pack(pady=(0, 20))

        if not search_term and self.current_folder == "Все пароли":
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
        """Эффект наведения на карточку"""
        try:
            if card.winfo_exists():
                card.configure(border_color=color)
        except:
            pass

    # ==================== ДЕЙСТВИЯ С ПАРОЛЯМИ ====================

    def quick_copy_password(self, password_id):
        """Быстрое копирование пароля в буфер обмена"""
        try:
            password_data = self.db.get_password(password_id)
            self.root.clipboard_clear()
            self.root.clipboard_append(password_data['password'])
            ToastNotification.show(self.root, f"Пароль '{password_data['title']}' скопирован!", "success")
        except Exception as e:
            ToastNotification.show(self.root, f"Ошибка: {e}", "error")

    def view_password_by_id(self, password_id):
        """Открывает окно просмотра пароля"""
        self.root.after(50, lambda: self._open_view_window(password_id))

    def _open_view_window(self, password_id):
        """Внутренний метод открытия окна просмотра"""
        try:
            password_data = self.db.get_password(password_id)
            self.view_password_details_direct(password_id, password_data)
        except Exception as e:
            ToastNotification.show(self.root, f"Ошибка: {e}", "error")

    def view_password_details_direct(self, password_id, password_data):
        """Показывает детальное окно просмотра пароля с единым компактным дизайном"""
        view_window = ctk.CTkToplevel(self.root)
        view_window.title(f"{password_data['title']}")
        view_window.geometry("620x700")
        view_window.minsize(580, 650)
        view_window.configure(fg_color=ModernDesign.BG_DARK)

        view_window.grid_columnconfigure(0, weight=1)
        view_window.grid_rowconfigure(0, weight=1)
        view_window.transient(self.root)
        view_window.grab_set()

        scroll_frame = AutoHideScrollableFrame(view_window, fg_color="transparent")
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        scroll_frame.grid_columnconfigure(0, weight=1)

        # ============= ЗАГОЛОВОК =============
        header = ctk.CTkFrame(scroll_frame, fg_color=ModernDesign.BG_CARD, corner_radius=15)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))

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

        # ============= ВСЕ ПОЛЯ В ЕДИНОМ КОМПАКТНОМ СТИЛЕ =============

        # ПАПКА
        self._create_compact_field(
            scroll_frame,
            row=1,
            icon="📁",
            label="Папка",
            value=password_data.get('folder', 'Без папки'),
            field_type="folder",
            password_id=password_id,
            window=view_window
        )

        # ЛОГИН
        self._create_compact_field(
            scroll_frame,
            row=2,
            icon="👤",
            label="Логин",
            value=password_data['username'],
            field_type="username",
            window=view_window
        )

        # ПАРОЛЬ
        self._create_compact_field(
            scroll_frame,
            row=3,
            icon="🔑",
            label="Пароль",
            value=password_data['password'],
            field_type="password",
            window=view_window
        )

        # URL
        if password_data['url']:
            self._create_compact_field(
                scroll_frame,
                row=4,
                icon="🌐",
                label="URL",
                value=password_data['url'],
                field_type="url",
                window=view_window
            )

        # ЗАМЕТКИ
        if password_data['notes']:
            notes_card = ctk.CTkFrame(scroll_frame, fg_color=ModernDesign.BG_CARD, corner_radius=12)
            notes_card.grid(row=5, column=0, sticky="ew", pady=(0, 10))

            notes_inner = ctk.CTkFrame(notes_card, fg_color="transparent")
            notes_inner.pack(padx=20, pady=15, fill="both", expand=True)

            # Заголовок
            header_frame = ctk.CTkFrame(notes_inner, fg_color="transparent")
            header_frame.pack(fill="x", pady=(0, 8))

            ctk.CTkLabel(
                header_frame,
                text="📝",
                font=("Segoe UI", 18),
                width=30
            ).pack(side="left", padx=(0, 8))

            ctk.CTkLabel(
                header_frame,
                text="Заметки",
                font=("Segoe UI", 12, "bold"),
                text_color=ModernDesign.TEXT_SECONDARY,
                anchor="w"
            ).pack(side="left")

            text_box = ctk.CTkTextbox(
                notes_inner,
                height=100,
                font=("Segoe UI", 12),
                fg_color=ModernDesign.BG_HOVER,
                corner_radius=8,
                border_width=0
            )
            text_box.pack(fill="both", expand=True)
            text_box.insert("1.0", password_data['notes'])
            text_box.configure(state="disabled")

        # ============= КНОПКА УДАЛЕНИЯ =============
        delete_btn = ctk.CTkButton(
            scroll_frame,
            text="🗑️ Удалить пароль",
            command=partial(self.delete_password_and_close, password_id, view_window),
            font=("Segoe UI", 13, "bold"),
            height=50,
            fg_color=ModernDesign.DANGER,
            hover_color="#C62828",
            corner_radius=10
        )
        delete_btn.grid(row=10, column=0, sticky="ew", pady=(20, 0))


    def _create_compact_field(self, parent, row, icon, label, value, field_type, window, password_id=None):
        """Создаёт компактное поле в едином стиле"""

        field_card = ctk.CTkFrame(parent, fg_color=ModernDesign.BG_CARD, corner_radius=12)
        field_card.grid(row=row, column=0, sticky="ew", pady=(0, 10))

        field_inner = ctk.CTkFrame(field_card, fg_color="transparent")
        field_inner.pack(padx=20, pady=15, fill="both", expand=True)
        field_inner.grid_columnconfigure(1, weight=1)

        # Иконка слева
        ctk.CTkLabel(
            field_inner,
            text=icon,
            font=("Segoe UI", 18),
            width=30
        ).grid(row=0, column=0, padx=(0, 10), sticky="w")

        # ============= ПАПКА =============
        if field_type == "folder":
            # Лейбл
            ctk.CTkLabel(
                field_inner,
                text=f"{label}:",
                font=("Segoe UI", 12, "bold"),
                text_color=ModernDesign.TEXT_SECONDARY,
                anchor="w"
            ).grid(row=0, column=1, sticky="w")

            # Выпадающий список и кнопка на новой строке
            folder_container = ctk.CTkFrame(field_inner, fg_color="transparent")
            folder_container.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(8, 0))
            folder_container.grid_columnconfigure(0, weight=1)

            current_folder_val = value if value else 'Без папки'
            folder_var = ctk.StringVar(value=current_folder_val)
            folders = self.folder_manager.get_folders()[1:]

            folder_dropdown = ctk.CTkOptionMenu(
                folder_container,
                values=folders if folders else ["Без папки"],
                variable=folder_var,
                font=("Segoe UI", 12),
                fg_color=ModernDesign.BG_HOVER,
                button_color=ModernDesign.PRIMARY,
                button_hover_color=ModernDesign.PRIMARY_DARK,
                dropdown_fg_color=ModernDesign.BG_CARD,
                corner_radius=8,
                height=38
            )
            folder_dropdown.grid(row=0, column=0, sticky="ew", padx=(0, 8))

            def save_folder_change():
                new_folder = folder_var.get()
                try:
                    self.db.update_password_folder(password_id, new_folder)
                    self.invalidate_cache()
                    self.load_passwords()
                    ToastNotification.show(window, f"Папка изменена", "success")
                except Exception as e:
                    ToastNotification.show(window, f"Ошибка: {e}", "error")

            save_btn = ctk.CTkButton(
                folder_container,
                text="💾",
                command=save_folder_change,
                width=50,
                height=38,
                fg_color=ModernDesign.SUCCESS,
                hover_color="#00C853",
                corner_radius=8,
                font=("Segoe UI", 16)
            )
            save_btn.grid(row=0, column=1)

        # ============= ЛОГИН =============
        elif field_type == "username":
            # Лейбл и значение в одной строке
            label_text = ctk.CTkLabel(
                field_inner,
                text=f"{label}:",
                font=("Segoe UI", 12, "bold"),
                text_color=ModernDesign.TEXT_SECONDARY,
                anchor="w"
            )
            label_text.grid(row=0, column=1, sticky="w", padx=(0, 8))

            value_label = ctk.CTkLabel(
                field_inner,
                text=value if value else "Не указан",
                font=("Segoe UI", 12),
                text_color=ModernDesign.TEXT_PRIMARY if value else ModernDesign.TEXT_MUTED,
                anchor="w"
            )
            value_label.grid(row=0, column=2, sticky="w")

            # Кнопка копирования
            if value:
                copy_btn = ctk.CTkButton(
                    field_inner,
                    text="📋",
                    command=partial(self._copy_field_to_clipboard, window, value, label),
                    width=40,
                    height=38,
                    fg_color=ModernDesign.SUCCESS,
                    hover_color="#00C853",
                    corner_radius=8,
                    font=("Segoe UI", 16)
                )
                copy_btn.grid(row=0, column=3, padx=(8, 0))

        # ============= ПАРОЛЬ =============
        elif field_type == "password":
            # Лейбл
            label_text = ctk.CTkLabel(
                field_inner,
                text=f"{label}:",
                font=("Segoe UI", 12, "bold"),
                text_color=ModernDesign.TEXT_SECONDARY,
                anchor="w"
            )
            label_text.grid(row=0, column=1, sticky="w", padx=(0, 8))

            # Значение (скрытое/открытое)
            password_var = ctk.StringVar(value="●" * 12)
            password_visible = [False]

            value_label = ctk.CTkLabel(
                field_inner,
                textvariable=password_var,
                font=("Segoe UI", 12),
                text_color=ModernDesign.TEXT_PRIMARY,
                anchor="w"
            )
            value_label.grid(row=0, column=2, sticky="w")

            # Кнопки
            buttons_container = ctk.CTkFrame(field_inner, fg_color="transparent")
            buttons_container.grid(row=0, column=3, padx=(8, 0))

            def toggle_password():
                password_visible[0] = not password_visible[0]
                if password_visible[0]:
                    password_var.set(value)
                    toggle_btn.configure(text="🙈")
                else:
                    password_var.set("●" * 12)
                    toggle_btn.configure(text="👁️")

            toggle_btn = ctk.CTkButton(
                buttons_container,
                text="👁️",
                command=toggle_password,
                width=40,
                height=38,
                fg_color=ModernDesign.PRIMARY,
                hover_color=ModernDesign.PRIMARY_DARK,
                corner_radius=8,
                font=("Segoe UI", 16)
            )
            toggle_btn.pack(side="left", padx=(0, 4))

            copy_btn = ctk.CTkButton(
                buttons_container,
                text="📋",
                command=partial(self._copy_field_to_clipboard, window, value, label),
                width=40,
                height=38,
                fg_color=ModernDesign.SUCCESS,
                hover_color="#00C853",
                corner_radius=8,
                font=("Segoe UI", 16)
            )
            copy_btn.pack(side="left")

        # ============= URL =============
        elif field_type == "url":
            # Лейбл
            ctk.CTkLabel(
                field_inner,
                text=f"{label}:",
                font=("Segoe UI", 12, "bold"),
                text_color=ModernDesign.TEXT_SECONDARY,
                anchor="w"
            ).grid(row=0, column=1, sticky="w", padx=(0, 8))

            # Кликабельная ссылка
            url_link = ctk.CTkLabel(
                field_inner,
                text=value,
                font=("Segoe UI", 12),
                text_color=ModernDesign.PRIMARY,
                anchor="w",
                cursor="hand2"
            )
            url_link.grid(row=0, column=2, sticky="w")

            def open_url(e=None):
                import webbrowser
                webbrowser.open(value)

            url_link.bind("<Button-1>", open_url)

            # Кнопка открыть
            open_btn = ctk.CTkButton(
                field_inner,
                text="🔗",
                command=open_url,
                width=40,
                height=38,
                fg_color=ModernDesign.PRIMARY,
                hover_color=ModernDesign.PRIMARY_DARK,
                corner_radius=8,
                font=("Segoe UI", 16)
            )
            open_btn.grid(row=0, column=3, padx=(8, 0))


    def _create_view_header(self, parent, password_data):
        """Создает заголовок окна просмотра"""
        header = ctk.CTkFrame(parent, fg_color=ModernDesign.BG_CARD, corner_radius=15)
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

    def _create_view_field(self, parent, field, window, row):
        """Создает поле в окне просмотра"""
        field_card = ctk.CTkFrame(parent, fg_color=ModernDesign.BG_CARD, corner_radius=12)
        field_card.grid(row=row, column=0, sticky="ew", pady=5)
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
                    command=partial(self._copy_field_to_clipboard, window, field["value"], field["label"]),
                    width=50,
                    height=40,
                    fg_color=ModernDesign.SUCCESS,
                    hover_color="#00C853",
                    corner_radius=8,
                    font=("Segoe UI", 16)
                )
                copy_btn.grid(row=1, column=2 if field.get("password") else 1)

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

    # ==================== ОТКРЫТИЕ ДОЧЕРНИХ ОКОН ====================

    def show_add_password(self):
        """Открывает окно добавления пароля"""
        self.root.after(50, self._open_add_password_window)

    def _open_add_password_window(self):
        try:
            from gui.add_password import AddPasswordWindow
            if self.add_password_window and self.add_password_window.window.winfo_exists():
                self.add_password_window.window.focus()
            else:
                self.add_password_window = AddPasswordWindow(self.root, self.db, self.encryptor, self)
                self.invalidate_cache()
        except Exception as e:
            ToastNotification.show(self.root, f"Ошибка: {e}", "error")

    def show_settings(self):
        """Открывает окно настроек"""
        self.root.after(50, self._open_settings_window)

    def _open_settings_window(self):
        try:
            from gui.settings import SettingsWindow
            if self.settings_window and self.settings_window.window.winfo_exists():
                self.settings_window.window.focus()
            else:
                self.settings_window = SettingsWindow(self.root, self.db, self.encryptor, self)
        except Exception as e:
            ToastNotification.show(self.root, f"Ошибка: {e}", "error")

    def backup_data(self):
        """Создает резервную копию данных"""
        ToastNotification.show(self.root, "Создание резервной копии...", "info")