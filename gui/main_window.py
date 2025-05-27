import customtkinter as ctk
from tkinter import messagebox, simpledialog, filedialog
import os
import tkinter as tk
from utils.design_system import DesignSystem, ThemeManager

class MainWindow:
    def __init__(self, root, db, encryptor):
        self.root = root
        self.db = db
        self.encryptor = encryptor

        # Ссылки на другие окна
        self.add_password_window = None
        self.settings_window = None

        # Переменные для отслеживания бездействия
        self.idle_timer_id = None
        self.idle_timeout = 5 * 60 * 1000

        # Применяем тему приложения
        DesignSystem.setup_theme(root)

        # Настройка размера и заголовка основного окна
        self.root.title("EVOLS Password Manager")
        self.root.geometry(f"{DesignSystem.WINDOW_MIN_WIDTH}x{DesignSystem.WINDOW_MIN_HEIGHT}")
        self.root.minsize(700, 500)  # Минимальный размер окна

        # Загружаем настройки
        self.load_settings()

        self.setup_ui()

        # Настраиваем таймер бездействия
        self.setup_idle_timer()

        # Привязываем события для сброса таймера
        self.root.bind("<Key>", self.reset_idle_timer)
        self.root.bind("<Motion>", self.reset_idle_timer)
        self.root.bind("<Button>", self.reset_idle_timer)

    def load_settings(self):
        """Загружает настройки приложения."""
        try:
            import json
            if os.path.exists("app_settings.json"):
                with open("app_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    # Безопасное получение и приведение к int
                    auto_lock_time = settings.get("auto_lock_time", 5)

                    # Приводим к int, если значение строка
                    if isinstance(auto_lock_time, str):
                        try:
                            auto_lock_time = int(auto_lock_time) if auto_lock_time.isdigit() else 5
                        except (ValueError, AttributeError):
                            auto_lock_time = 5
                    elif not isinstance(auto_lock_time, (int, float)):
                        auto_lock_time = 5

                    # Переводим в миллисекунды
                    self.idle_timeout = auto_lock_time * 60 * 1000
            else:
                # Настройки по умолчанию, если файл не существует
                self.idle_timeout = 5 * 60 * 1000
        except Exception as e:
            print(f"Ошибка при загрузке настроек: {e}")
            # Значения по умолчанию
            self.idle_timeout = 5 * 60 * 1000

    def setup_idle_timer(self):
        """Настраивает таймер бездействия."""
        if self.idle_timeout > 0:
            # Отменяем предыдущий таймер, если он был установлен
            if self.idle_timer_id:
                self.root.after_cancel(self.idle_timer_id)
            # Устанавливаем новый таймер
            self.idle_timer_id = self.root.after(self.idle_timeout, self.lock_application)

    def reset_idle_timer(self, event=None):
        """Сбрасывает таймер бездействия при активности пользователя."""
        # Отменяем текущий таймер и устанавливаем новый
        self.setup_idle_timer()

    def lock_application(self):
        """Блокирует приложение и требует повторного ввода пароля."""
        # Скрываем главное окно
        self.root.withdraw()

        def on_unlock_success():
            """Вызывается при успешной разблокировке."""
            self.root.deiconify()  # Показываем главное окно
            self.setup_idle_timer()  # Перезапускаем таймер бездействия

        def on_unlock_cancel():
            """Вызывается при отмене разблокировки."""
            self.root.quit()
            self.root.destroy()
            import sys
            sys.exit(0)

        # Импортируем и показываем стилизованное окно разблокировки
        from gui.unlock_window import UnlockWindow
        unlock_window = UnlockWindow(
            parent=self.root,
            on_success_callback=on_unlock_success,
            on_cancel_callback=on_unlock_cancel
        )

    def setup_ui(self):
        # Очищаем окно
        for widget in self.root.winfo_children():
            widget.destroy()

        # Настраиваем корневой контейнер для адаптивности
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Создаем главный контейнер с grid вместо pack
        main_container = ctk.CTkFrame(self.root)
        main_container.grid(row=0, column=0, sticky="nsew")

        # Настраиваем сетку для адаптивности
        main_container.grid_columnconfigure(0, weight=0)  # Сайдбар не растягивается
        main_container.grid_columnconfigure(1, weight=1)  # Основная область растягивается
        main_container.grid_rowconfigure(0, weight=1)  # Растягивается по вертикали

        # Боковая панель фиксированной ширины
        self.sidebar = ctk.CTkFrame(main_container, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(DesignSystem.SPACE_4, 0),
                          pady=DesignSystem.SPACE_4)
        self.sidebar.grid_propagate(False)  # Фиксируем размер

        # Главная панель растягивается
        main_panel = ctk.CTkFrame(main_container)
        main_panel.grid(row=0, column=1, sticky="nsew", padx=DesignSystem.SPACE_4,
                        pady=DesignSystem.SPACE_4)
        main_panel.grid_columnconfigure(0, weight=1)
        main_panel.grid_rowconfigure(1, weight=1)  # Область списка паролей растягивается

        # Настройка сетки для сайдбара
        self.sidebar.grid_columnconfigure(0, weight=1)
        # Настраиваем ячейки для элементов в сайдбаре
        for i in range(10):  # Предполагаем максимум 10 элементов в меню
            self.sidebar.grid_rowconfigure(i, weight=0)

        # Заголовок сайдбара
        logo_label = ctk.CTkLabel(
            self.sidebar,
            text="EVOLS",
            font=DesignSystem.get_title_font()
        )
        logo_label.grid(row=0, column=0, pady=(30, 20))

        # Кнопки меню
        button_data = [
            {"text": "Добавить пароль", "command": self.show_add_password},
            {"text": "Сгенерировать пароль", "command": self.show_password_generator},
            {"text": "Проверить надежность", "command": self.check_password_strength},
            {"text": "Настройки", "command": self.show_settings},
            {"text": "Резервное копирование", "command": self.backup_data}
        ]

        for i, data in enumerate(button_data):
            btn = ctk.CTkButton(
                self.sidebar,
                text=data["text"],
                command=data["command"],
                font=DesignSystem.get_body_font(),
                height=40,
                width=180,
                fg_color=DesignSystem.PRIMARY,
                hover_color="#1565C0"
            )
            btn.grid(row=i + 1, column=0, pady=DesignSystem.SPACE_2, sticky="ew")

        # Заголовок основной области
        header_frame = ctk.CTkFrame(main_panel, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=DesignSystem.SPACE_4,
                          pady=DesignSystem.SPACE_4)
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="Ваши пароли",
            font=DesignSystem.get_title_font()
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header_frame,
            text="Надежное хранилище для ваших данных",
            font=DesignSystem.get_body_font()
        ).grid(row=1, column=0, sticky="w", pady=(5, 0))

        # Создаем контейнер для списка паролей с прокруткой
        self.password_container = ctk.CTkScrollableFrame(main_panel)
        self.password_container.grid(row=1, column=0, sticky="nsew", padx=DesignSystem.SPACE_4,
                                     pady=(0, DesignSystem.SPACE_4))

        # Настраиваем сетку для password_container
        self.password_container.grid_columnconfigure(0, weight=1)

        # Загружаем пароли
        self.load_passwords()

    def load_passwords(self):
        """Загружает список паролей в современном стиле."""
        # Очищаем предыдущий список
        for widget in self.password_container.winfo_children():
            widget.destroy()

        passwords = self.db.get_all_passwords()

        if not passwords:
            # Сообщение, если нет паролей
            empty_label = ctk.CTkLabel(
                self.password_container,
                text="У вас пока нет сохраненных паролей",
                font=DesignSystem.get_body_font()
            )
            empty_label.grid(row=0, column=0, pady=(50, 10))

            add_btn = ctk.CTkButton(
                self.password_container,
                text="Добавить пароль",
                command=self.show_add_password,
                font=DesignSystem.get_body_font(),
                fg_color=DesignSystem.SUCCESS,
                hover_color="#388E3C"
            )
            add_btn.grid(row=1, column=0, pady=10)
            return

        # Настройка строк для карточек
        for i in range(len(passwords)):
            self.password_container.grid_rowconfigure(i, weight=0)

        # Сохраняем список ID паролей
        self.password_ids = []

        # Перебираем все пароли
        for i, (id, title, category) in enumerate(passwords):
            # Создаем карточку для каждого пароля
            card = ctk.CTkFrame(self.password_container)
            card.grid(row=i, column=0, sticky="ew", pady=5, padx=5)
            card.grid_columnconfigure(0, weight=1)
            card.grid_columnconfigure(1, weight=0)

            # Сохраняем ID как атрибут карточки
            card.password_id = id
            self.password_ids.append(id)

            # Информация о пароле
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
            info_frame.grid_columnconfigure(0, weight=1)

            title_label = ctk.CTkLabel(
                info_frame,
                text=title,
                font=DesignSystem.get_button_font()
            )
            title_label.grid(row=0, column=0, sticky="w")

            category_label = ctk.CTkLabel(
                info_frame,
                text=f"Категория: {category}" if category else "",
                font=DesignSystem.get_body_font()
            )
            category_label.grid(row=1, column=0, sticky="w", pady=(5, 0))

            # Кнопки действий
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.grid(row=0, column=1, padx=10, pady=10)

            view_btn = ctk.CTkButton(
                btn_frame,
                text="Просмотр",
                width=100,
                font=DesignSystem.get_body_font(),
                command=lambda pid=id: self.view_password_by_id(pid)
            )
            view_btn.grid(row=0, column=0)

            # Привязываем обработчик событий
            card.bind("<Button-1>", self.view_password_details)
            info_frame.bind("<Button-1>", self.view_password_details)
            title_label.bind("<Button-1>", self.view_password_details)
            category_label.bind("<Button-1>", self.view_password_details)

    def view_password_details(self, event):
        """Отображает информацию о выбранном пароле."""
        # Получаем виджет, на котором произошло событие
        widget = event.widget

        # Если это метка, получаем ее родительский фрейм
        if isinstance(widget, tk.Label) or isinstance(widget, ctk.CTkLabel):
            parent_frame = widget.master
            while not hasattr(parent_frame, 'password_id') and parent_frame is not None:
                parent_frame = parent_frame.master
            widget = parent_frame

        # Если это фрейм без ID, получаем родительский фрейм
        if not hasattr(widget, 'password_id'):
            parent_frame = widget.master
            while not hasattr(parent_frame, 'password_id') and parent_frame is not None:
                parent_frame = parent_frame.master
            widget = parent_frame

        # Получаем ID пароля из атрибута фрейма
        password_id = widget.password_id
        password_data = self.db.get_password(password_id)

        # Создаем окно для отображения пароля
        view_window = ctk.CTkToplevel(self.root)
        view_window.title(f"Пароль: {password_data['title']}")
        view_window.geometry("450x500")
        view_window.minsize(400, 450)

        # Настройка адаптивности окна
        view_window.grid_columnconfigure(0, weight=1)
        view_window.grid_rowconfigure(0, weight=1)

        # Центрируем окно относительно родителя
        view_window.transient(self.root)
        view_window.grab_set()

        # Создаем основной скроллируемый фрейм
        scroll_frame = ctk.CTkScrollableFrame(view_window)
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scroll_frame.grid_columnconfigure(0, weight=1)

        # Основной фрейм содержимого
        main_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="ew", padx=DesignSystem.SPACE_8, pady=DesignSystem.SPACE_8)
        main_frame.grid_columnconfigure(1, weight=1)  # Растягиваем поля ввода

        # Заголовок
        header = ctk.CTkLabel(
            main_frame,
            text=f"Пароль: {password_data['title']}",
            font=DesignSystem.get_title_font()
        )
        header.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, DesignSystem.SPACE_8))

        # Отображаем информацию о пароле
        fields = [
            {"label": "Название:", "value": password_data['title'], "row": 1},
            {"label": "Логин:", "value": password_data['username'], "row": 2, "is_entry": True, "var_name": "username"},
            {"label": "Пароль:", "value": password_data['password'], "row": 3, "is_entry": True, "var_name": "password",
             "is_password": True},
            {"label": "URL:", "value": password_data['url'], "row": 4},
            {"label": "Категория:", "value": password_data['category'], "row": 5},
            {"label": "Заметки:", "value": password_data['notes'], "row": 6, "is_textbox": True}
        ]

        # Словарь для хранения ссылок на переменные
        self.detail_vars = {}

        for field in fields:
            # Метка
            ctk.CTkLabel(
                main_frame,
                text=field["label"],
                font=DesignSystem.get_button_font()
            ).grid(row=field["row"], column=0, sticky="nw", pady=DesignSystem.SPACE_4)

            if field.get("is_entry"):
                # Создаем переменную для поля ввода
                var = ctk.StringVar(value=field["value"])
                self.detail_vars[field.get("var_name")] = var

                # Поле ввода
                entry = ctk.CTkEntry(
                    main_frame,
                    textvariable=var,
                    width=300,
                    font=DesignSystem.get_body_font()
                )
                if field.get("is_password"):
                    entry.configure(show="*")
                entry.grid(row=field["row"], column=1, sticky="ew", pady=DesignSystem.SPACE_4)

                # Кнопка показать/скрыть для пароля
                if field.get("is_password"):
                    def toggle_password():
                        if entry.cget('show') == '*':
                            entry.configure(show='')
                            show_button.configure(text="Скрыть")
                        else:
                            entry.configure(show='*')
                            show_button.configure(text="Показать")

                    show_button = ctk.CTkButton(
                        main_frame,
                        text="Показать",
                        command=toggle_password,
                        width=80,
                        font=DesignSystem.get_body_font()
                    )
                    show_button.grid(row=field["row"], column=2, padx=(DesignSystem.SPACE_2, 0),
                                     pady=DesignSystem.SPACE_4)

            elif field.get("is_textbox"):
                # Текстовое поле для заметок
                notes_text = ctk.CTkTextbox(
                    main_frame,
                    width=300,
                    height=100,
                    font=DesignSystem.get_body_font()
                )
                notes_text.grid(row=field["row"], column=1, columnspan=2, sticky="ew", pady=DesignSystem.SPACE_4)
                notes_text.insert("1.0", field["value"])
                notes_text.configure(state="disabled")

            else:
                # Обычная метка для значения
                ctk.CTkLabel(
                    main_frame,
                    text=field["value"],
                    font=DesignSystem.get_body_font()
                ).grid(row=field["row"], column=1, sticky="w", pady=DesignSystem.SPACE_4)

        # Фрейм для кнопок внутри скролл области
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.grid(row=7, column=0, columnspan=3, pady=DesignSystem.SPACE_4)
        buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Функции копирования
        def copy_username():
            self.root.clipboard_clear()
            self.root.clipboard_append(self.detail_vars["username"].get())
            messagebox.showinfo("Копирование", "Логин скопирован в буфер обмена")

        def copy_password():
            self.root.clipboard_clear()
            self.root.clipboard_append(self.detail_vars["password"].get())
            messagebox.showinfo("Копирование", "Пароль скопирован в буфер обмена")

        # Кнопки копирования
        ctk.CTkButton(
            buttons_frame,
            text="Копировать логин",
            command=copy_username,
            font=DesignSystem.get_body_font(),
            width=150
        ).grid(row=0, column=0, padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Копировать пароль",
            command=copy_password,
            font=DesignSystem.get_body_font(),
            width=150
        ).grid(row=0, column=1, padx=5)

        # Кнопка закрытия
        ctk.CTkButton(
            buttons_frame,
            text="Закрыть",
            command=view_window.destroy,
            font=DesignSystem.get_body_font(),
            width=100
        ).grid(row=0, column=2, padx=5)

        # Нижняя панель для кнопки удаления (вне скролла)
        bottom_frame = ctk.CTkFrame(view_window, fg_color="transparent")
        bottom_frame.grid(row=1, column=0, sticky="ew", pady=10)
        bottom_frame.grid_columnconfigure(0, weight=1)

        # Добавляем кнопку удаления отдельно для выделения
        delete_button = ctk.CTkButton(
            bottom_frame,
            text="Удалить пароль",
            command=lambda: self.delete_password_and_close(password_id, widget, view_window),
            fg_color=DesignSystem.DANGER,
            hover_color="#C62828",
            font=DesignSystem.get_button_font()
        )
        delete_button.grid(row=0, column=0, pady=5)

    def view_password_by_id(self, password_id):
        """Отображает информацию о пароле по его ID."""

        # Создаем фиктивное событие
        class FakeEvent:
            def __init__(self, widget):
                self.widget = widget

        # Находим карточку с нужным ID
        for frame in self.password_container.winfo_children():
            if hasattr(frame, 'password_id') and frame.password_id == password_id:
                event = FakeEvent(frame)
                self.view_password_details(event)
                break

    def show_add_password(self):
        """Открывает окно добавления пароля."""
        from gui.add_password import AddPasswordWindow
        self.add_password_window = AddPasswordWindow(self.root, self.db, self.encryptor, self)

    def show_settings(self):
        """Открывает окно настроек."""
        from gui.settings import SettingsWindow
        self.settings_window = SettingsWindow(self.root, self.db, self.encryptor, self)

    def check_password_strength(self):
        """Проверяет надежность выбранного пароля."""
        # Получаем выбранные карточки
        selected_frames = self.password_container.winfo_children()

        if not selected_frames:
            messagebox.showinfo("Информация", "У вас нет сохраненных паролей для проверки")
            return

        # Показываем диалог выбора пароля, если есть несколько
        if len(selected_frames) > 1:
            select_window = ctk.CTkToplevel(self.root)
            select_window.title("Выберите пароль для проверки")
            select_window.geometry("400x300")
            select_window.minsize(350, 250)
            select_window.transient(self.root)
            select_window.grab_set()

            # Настройка адаптивности окна
            select_window.grid_columnconfigure(0, weight=1)
            select_window.grid_rowconfigure(0, weight=1)

            # Создаем основной фрейм с отступами
            main_frame = ctk.CTkFrame(select_window)
            main_frame.grid(row=0, column=0, sticky="nsew", padx=DesignSystem.SPACE_8,
                            pady=DesignSystem.SPACE_8)
            main_frame.grid_columnconfigure(0, weight=1)
            main_frame.grid_rowconfigure(1, weight=1)

            ctk.CTkLabel(
                main_frame,
                text="Выберите пароль для проверки:",
                font=DesignSystem.get_title_font()
            ).grid(row=0, column=0, pady=DesignSystem.SPACE_4)

            # Создаем фрейм со скроллом для списка паролей
            scroll_frame = ctk.CTkScrollableFrame(main_frame, width=300, height=150)
            scroll_frame.grid(row=1, column=0, sticky="nsew", padx=DesignSystem.SPACE_4,
                              pady=DesignSystem.SPACE_4)
            scroll_frame.grid_columnconfigure(0, weight=1)

            selected_id = [None]  # Используем список для хранения выбранного ID
            buttons = []

            def select_password(pid):
                selected_id[0] = pid
                for btn in buttons:
                    btn.configure(fg_color=DesignSystem.PRIMARY)
                buttons[next(i for i, (_, _id) in enumerate(password_list) if _id == pid)].configure(
                    fg_color="#1565C0"  # Темнее при выборе
                )

            # Составляем список паролей
            password_list = []
            for frame in selected_frames:
                if hasattr(frame, 'password_id'):
                    password_data = self.db.get_password(frame.password_id)
                    password_list.append((password_data['title'], frame.password_id))

            # Добавляем кнопки для выбора пароля
            for i, (title, pid) in enumerate(password_list):
                btn = ctk.CTkButton(
                    scroll_frame,
                    text=title,
                    command=lambda p=pid: select_password(p),
                    font=DesignSystem.get_body_font(),
                    fg_color=DesignSystem.PRIMARY
                )
                btn.grid(row=i, column=0, sticky="ew", pady=DesignSystem.SPACE_2)
                buttons.append(btn)
                scroll_frame.grid_rowconfigure(i, weight=0)

            def on_confirm():
                if selected_id[0]:
                    select_window.destroy()
                    self.show_password_strength(selected_id[0])
                else:
                    messagebox.showinfo("Информация", "Выберите пароль для проверки")

            ctk.CTkButton(
                main_frame,
                text="Проверить",
                command=on_confirm,
                font=DesignSystem.get_button_font()
            ).grid(row=2, column=0, pady=DesignSystem.SPACE_4)
        else:
            # Если есть только один пароль
            frame = selected_frames[0]
            if hasattr(frame, 'password_id'):
                self.show_password_strength(frame.password_id)

    def show_password_strength(self, password_id):
        """Показывает окно с результатами проверки надежности пароля."""
        password_data = self.db.get_password(password_id)

        # Определяем функцию проверки надежности локально
        import re
        import math

        class PasswordStrength:
            def __init__(self, common_passwords_file=None):
                self.common_passwords = set()
                if common_passwords_file and os.path.exists(common_passwords_file):
                    self._load_common_passwords(common_passwords_file)

            def _load_common_passwords(self, file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            password = line.strip()
                            if password and not password.startswith('#'):
                                self.common_passwords.add(password.lower())
                except Exception as e:
                    print(f"Ошибка при загрузке списка распространенных паролей: {e}")

            def check_password(self, password):
                score = 0
                feedback = []

                # Проверка длины
                if len(password) < 8:
                    feedback.append("Пароль слишком короткий (минимум 8 символов)")
                else:
                    score += min(len(password) * 2, 30)  # До 30 баллов за длину

                # Проверка наличия символов разных категорий
                has_lowercase = bool(re.search(r'[a-z]', password))
                has_uppercase = bool(re.search(r'[A-Z]', password))
                has_digits = bool(re.search(r'\d', password))
                has_special = bool(re.search(r'[^A-Za-z0-9]', password))

                category_count = sum([has_lowercase, has_uppercase, has_digits, has_special])
                score += category_count * 10  # До 40 баллов за разнообразие символов

                if not has_lowercase:
                    feedback.append("Добавьте строчные буквы")
                if not has_uppercase:
                    feedback.append("Добавьте заглавные буквы")
                if not has_digits:
                    feedback.append("Добавьте цифры")
                if not has_special:
                    feedback.append("Добавьте специальные символы")

                # Проверка на повторяющиеся последовательности
                if re.search(r'(.)\1{2,}', password):  # Три и более одинаковых символа подряд
                    score -= 15
                    feedback.append("Избегайте повторяющихся символов")

                # Проверка на последовательности клавиатуры
                keyboard_sequences = ['qwerty', 'asdfgh', '123456', 'zxcvbn']
                for seq in keyboard_sequences:
                    if seq in password.lower():
                        score -= 15
                        feedback.append("Избегайте простых последовательностей клавиатуры")
                        break

                # Проверка на наличие в списке распространенных паролей
                if password.lower() in self.common_passwords:
                    score -= 30
                    feedback.append("Этот пароль слишком распространен")

                # Ограничиваем оценку в диапазоне от 0 до 100
                score = max(0, min(score, 100))

                # Определяем уровень надежности
                if score < 30:
                    strength = "Очень слабый"
                elif score < 50:
                    strength = "Слабый"
                elif score < 70:
                    strength = "Средний"
                elif score < 90:
                    strength = "Сильный"
                else:
                    strength = "Очень сильный"

                return {
                    'score': score,
                    'strength': strength,
                    'feedback': feedback
                }

            def calculate_entropy(self, password):
                charset_size = 0
                if re.search(r'[a-z]', password):
                    charset_size += 26
                if re.search(r'[A-Z]', password):
                    charset_size += 26
                if re.search(r'\d', password):
                    charset_size += 10
                if re.search(r'[^A-Za-z0-9]', password):
                    charset_size += 33  # Примерное количество специальных символов

                if charset_size == 0:
                    return 0

                # Формула энтропии: log2(charset_size^length)
                entropy = len(password) * math.log2(charset_size)
                return entropy

        # Путь к файлу с распространенными паролями
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        common_passwords_file = os.path.join(data_dir, "common-passwords.txt")

        # Создаем файл с распространенными паролями, если его нет
        if not os.path.exists(common_passwords_file):
            common_passwords = [
                "123456", "password", "12345678", "qwerty", "123456789",
                "12345", "1234", "111111", "1234567", "dragon",
                "123123", "baseball", "abc123", "football", "monkey",
                "letmein", "696969", "shadow", "master", "666666",
                "qwertyuiop", "123321", "mustang", "1234567890", "michael",
                "654321", "superman", "1qaz2wsx", "7777777", "fuckyou",
                "121212", "000000", "qazwsx", "123qwe", "killer",
                "trustno1", "jordan", "jennifer", "zxcvbnm", "asdfgh"
            ]

            with open(common_passwords_file, 'w', encoding='utf-8') as f:
                for password in common_passwords:
                    f.write(f"{password}\n")

        checker = PasswordStrength(common_passwords_file)
        result = checker.check_password(password_data["password"])

        # Рассчитываем энтропию
        entropy = checker.calculate_entropy(password_data["password"])

        # Создаем окно с результатами
        strength_window = ctk.CTkToplevel(self.root)
        strength_window.title("Проверка надежности пароля")
        strength_window.geometry("550x450")
        strength_window.minsize(500, 400)
        strength_window.transient(self.root)
        strength_window.grab_set()

        # Настройка адаптивности окна
        strength_window.grid_columnconfigure(0, weight=1)
        strength_window.grid_rowconfigure(0, weight=1)

        # Создаем основной скроллируемый фрейм
        scroll_frame = ctk.CTkScrollableFrame(strength_window)
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scroll_frame.grid_columnconfigure(0, weight=1)

        # Создаем содержимое
        main_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="ew")
        main_frame.grid_columnconfigure(0, weight=1)

        # Современный заголовок с иконкой
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)

        # Иконка
        ctk.CTkLabel(
            header_frame,
            text="🔍",
            font=("Arial", 32)
        ).grid(row=0, column=0, padx=(0, 10))

        # Заголовок и подзаголовок
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.grid(row=0, column=1, sticky="ew")
        title_container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            title_container,
            text="Анализ надежности пароля",
            font=DesignSystem.get_title_font(),
            anchor="w"
        ).grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            title_container,
            text=f"Результаты для: {password_data['title']}",
            font=DesignSystem.get_caption_font(),
            text_color=DesignSystem.GRAY_600,
            anchor="w"
        ).grid(row=1, column=0, sticky="ew", pady=(2, 0))

        # Разделительная линия
        separator = ctk.CTkFrame(main_frame, height=2, fg_color=DesignSystem.GRAY_200)
        separator.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        # Карточка с результатами
        results_card = ctk.CTkFrame(main_frame)
        results_card.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        results_card.grid_columnconfigure(0, weight=1)

        # Секция оценки
        score_section = ctk.CTkFrame(results_card, fg_color="transparent")
        score_section.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        score_section.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            score_section,
            text="📊 Общая оценка",
            font=DesignSystem.get_button_font(),
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Визуальный индикатор надежности
        progress_frame = ctk.CTkFrame(score_section, fg_color="transparent")
        progress_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.create_strength_progress_bar(progress_frame, result['score'])

        # Уровень надежности с цветом
        strength_color = self.get_strength_color(result['score'])
        strength_label = ctk.CTkLabel(
            score_section,
            text=f"Уровень надежности: {result['strength']}",
            font=DesignSystem.get_body_font(),
            text_color=strength_color
        )
        strength_label.grid(row=2, column=0, sticky="w", pady=(0, 5))

        # Энтропия
        ctk.CTkLabel(
            score_section,
            text=f"Энтропия: {entropy:.1f} бит",
            font=DesignSystem.get_body_font()
        ).grid(row=3, column=0, sticky="w")

        # Рекомендации
        if result['feedback']:
            recommendations_card = ctk.CTkFrame(main_frame)
            recommendations_card.grid(row=3, column=0, sticky="ew", pady=(0, 15))
            recommendations_card.grid_columnconfigure(0, weight=1)

            rec_section = ctk.CTkFrame(recommendations_card, fg_color="transparent")
            rec_section.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
            rec_section.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                rec_section,
                text="💡 Рекомендации по улучшению",
                font=DesignSystem.get_button_font(),
                anchor="w"
            ).grid(row=0, column=0, sticky="w", pady=(0, 10))

            for i, feedback in enumerate(result['feedback']):
                ctk.CTkLabel(
                    rec_section,
                    text=f"• {feedback}",
                    anchor="w",
                    font=DesignSystem.get_body_font(),
                    wraplength=450
                ).grid(row=i + 1, column=0, sticky="w", pady=2)

        # Нижняя панель для кнопки закрытия
        bottom_frame = ctk.CTkFrame(strength_window, fg_color="transparent")
        bottom_frame.grid(row=1, column=0, sticky="ew", pady=10)
        bottom_frame.grid_columnconfigure(0, weight=1)

        # Кнопка закрытия
        ctk.CTkButton(
            bottom_frame,
            text="✓ Закрыть",
            command=strength_window.destroy,
            font=DesignSystem.get_button_font(),
            width=120,
            height=40,
            corner_radius=8
        ).grid(row=0, column=0)

    def create_strength_progress_bar(self, parent, score):
        """Создает визуальный индикатор надежности пароля."""
        parent.grid_columnconfigure(0, weight=1)

        # Определяем цвет в зависимости от оценки
        color = self.get_strength_color(score)

        # Создаем прогресс-бар
        progress = ctk.CTkProgressBar(parent, width=350, height=20)
        progress.grid(row=0, column=0, sticky="ew", padx=(0, DesignSystem.SPACE_4))
        progress.set(score / 100)
        progress.configure(progress_color=color)

        # Добавляем текст с процентами
        ctk.CTkLabel(
            parent,
            text=f"{score}/100",
            font=DesignSystem.get_button_font()
        ).grid(row=0, column=1, sticky="w", padx=DesignSystem.SPACE_4)

        return parent

    def get_strength_color(self, score):
        """Возвращает цвет в зависимости от оценки надежности."""
        if score < 30:
            return DesignSystem.DANGER
        elif score < 50:
            return DesignSystem.WARNING
        elif score < 70:
            return "#FFCC00"  # Желтый
        elif score < 90:
            return DesignSystem.SUCCESS
        else:
            return "#00AA00"  # Темно-зеленый

    def show_password_generator(self):
        """Показывает окно генератора паролей с адаптивным дизайном."""
        # Создаем окно с увеличенным размером
        gen_window = ctk.CTkToplevel(self.root)
        gen_window.title("Генератор паролей")
        gen_window.geometry("600x500")  # Увеличиваем размер
        gen_window.minsize(500, 450)  # Увеличиваем минимальный размер

        # Настройка адаптивности окна
        gen_window.grid_columnconfigure(0, weight=1)
        gen_window.grid_rowconfigure(0, weight=1)

        # Центрируем окно
        gen_window.transient(self.root)
        gen_window.grab_set()

        # Основной скроллируемый контейнер для предотвращения обрезания
        scroll_frame = ctk.CTkScrollableFrame(gen_window)
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scroll_frame.grid_columnconfigure(0, weight=1)

        # Основной контейнер с правильной адаптивностью
        main_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="ew")
        main_frame.grid_columnconfigure(0, weight=1)  # Растягиваем по горизонтали

        # Заголовок
        title_label = ctk.CTkLabel(
            main_frame,
            text="Генератор паролей",
            font=DesignSystem.get_title_font()
        )
        title_label.grid(row=0, column=0, pady=(0, DesignSystem.SPACE_8), sticky="ew")

        # Настройки генератора с адаптивностью
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.grid(row=1, column=0, sticky="ew", pady=DesignSystem.SPACE_4)
        options_frame.grid_columnconfigure(0, weight=1)  # Растягиваем настройки

        # Заголовок настроек
        ctk.CTkLabel(
            options_frame,
            text="Настройки генерации:",
            font=DesignSystem.get_button_font()
        ).grid(row=0, column=0, sticky="w", padx=DesignSystem.SPACE_4, pady=(DesignSystem.SPACE_4, 0))

        # Контейнер для длины пароля
        length_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        length_frame.grid(row=1, column=0, sticky="ew", padx=DesignSystem.SPACE_4, pady=DesignSystem.SPACE_2)
        length_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            length_frame,
            text="Длина пароля:",
            font=DesignSystem.get_body_font()
        ).grid(row=0, column=0, sticky="w")

        # Переменные для настроек
        length_var = ctk.IntVar(value=16)
        uppercase_var = ctk.BooleanVar(value=True)
        digits_var = ctk.BooleanVar(value=True)
        special_var = ctk.BooleanVar(value=True)
        password_var = ctk.StringVar()

        length_entry = ctk.CTkEntry(
            length_frame,
            textvariable=length_var,
            width=80,  # Уменьшаем ширину
            font=DesignSystem.get_body_font()
        )
        length_entry.grid(row=0, column=1, sticky="w", padx=(DesignSystem.SPACE_4, 0))

        # Флажки для настроек с улучшенным размещением
        checkboxes = [
            {"text": "Заглавные буквы (A-Z)", "var": uppercase_var, "row": 2},
            {"text": "Цифры (0-9)", "var": digits_var, "row": 3},
            {"text": "Специальные символы (!@#$)", "var": special_var, "row": 4}
        ]

        for checkbox in checkboxes:
            ctk.CTkCheckBox(
                options_frame,
                text=checkbox["text"],
                variable=checkbox["var"],
                font=DesignSystem.get_body_font()
            ).grid(row=checkbox["row"], column=0, sticky="w", padx=DesignSystem.SPACE_4,
                   pady=DesignSystem.SPACE_1)

        # Поле для отображения сгенерированного пароля с полной адаптивностью
        result_frame = ctk.CTkFrame(main_frame)
        result_frame.grid(row=2, column=0, sticky="ew", pady=DesignSystem.SPACE_6)
        result_frame.grid_columnconfigure(0, weight=1)  # Растягиваем поле результата

        ctk.CTkLabel(
            result_frame,
            text="Сгенерированный пароль:",
            font=DesignSystem.get_button_font()
        ).grid(row=0, column=0, sticky="w", padx=DesignSystem.SPACE_4, pady=(DesignSystem.SPACE_4, 0))

        # Адаптивное поле для пароля
        password_entry = ctk.CTkEntry(
            result_frame,
            textvariable=password_var,
            font=DesignSystem.get_body_font(),
            state="readonly"
        )
        password_entry.grid(row=1, column=0, sticky="ew", padx=DesignSystem.SPACE_4,
                            pady=DesignSystem.SPACE_4)  # sticky="ew" для растягивания

        # Информация о пароле
        info_frame = ctk.CTkFrame(main_frame, fg_color=DesignSystem.GRAY_100)
        info_frame.grid(row=3, column=0, sticky="ew", pady=DesignSystem.SPACE_4)
        info_frame.grid_columnconfigure(0, weight=1)

        password_info_var = ctk.StringVar(value="Пароль еще не сгенерирован")
        info_label = ctk.CTkLabel(
            info_frame,
            textvariable=password_info_var,
            font=DesignSystem.get_caption_font(),
            text_color=DesignSystem.GRAY_600
        )
        info_label.grid(row=0, column=0, padx=DesignSystem.SPACE_4, pady=DesignSystem.SPACE_3)

        # Функция генерации пароля с обновлением информации
        def generate_password():
            """Генерирует пароль с заданными параметрами"""
            try:
                import random
                import string

                # Получаем длину пароля
                try:
                    length = length_var.get()
                    if length < 4:
                        messagebox.showerror("Ошибка", "Длина пароля должна быть не менее 4 символов")
                        return
                    if length > 128:
                        messagebox.showerror("Ошибка", "Длина пароля не должна превышать 128 символов")
                        return
                except (ValueError, tk.TclError):
                    messagebox.showerror("Ошибка", "Введите корректное число для длины пароля")
                    return

                # Формируем набор символов
                chars = ""
                required_chars = []
                char_types = []

                # Строчные буквы всегда включены
                chars += string.ascii_lowercase
                required_chars.append(random.choice(string.ascii_lowercase))
                char_types.append("строчные буквы")

                if uppercase_var.get():
                    chars += string.ascii_uppercase
                    required_chars.append(random.choice(string.ascii_uppercase))
                    char_types.append("заглавные буквы")

                if digits_var.get():
                    chars += string.digits
                    required_chars.append(random.choice(string.digits))
                    char_types.append("цифры")

                if special_var.get():
                    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
                    chars += special_chars
                    required_chars.append(random.choice(special_chars))
                    char_types.append("спец. символы")

                if not chars:
                    messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов")
                    return

                # Генерируем пароль
                password_list = required_chars.copy()

                for _ in range(length - len(required_chars)):
                    password_list.append(random.choice(chars))

                random.shuffle(password_list)
                final_password = ''.join(password_list)

                # Обновляем поле пароля
                password_entry.configure(state="normal")
                password_var.set(final_password)
                password_entry.configure(state="readonly")

                # Обновляем информацию о пароле
                info_text = f"Длина: {length} символов | Типы: {', '.join(char_types)}"
                password_info_var.set(info_text)

                # Обновляем интерфейс
                gen_window.update_idletasks()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сгенерировать пароль: {e}")

        # Функция копирования
        def copy_to_clipboard():
            password = password_var.get()
            if not password:
                messagebox.showwarning("Предупреждение", "Сначала сгенерируйте пароль")
                return

            try:
                gen_window.clipboard_clear()
                gen_window.clipboard_append(password)
                # Временно показываем статус копирования
                old_text = password_info_var.get()
                password_info_var.set("✓ Пароль скопирован в буфер обмена")
                gen_window.after(2000, lambda: password_info_var.set(old_text))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось скопировать пароль: {e}")

        def check_strength():
            password = password_var.get()
            if not password:
                messagebox.showwarning("Предупреждение", "Сначала сгенерируйте пароль")
                return

            score = 0
            feedback = []

            if len(password) >= 12:
                score += 25
            elif len(password) >= 8:
                score += 15
            else:
                feedback.append("Рекомендуется длина не менее 12 символов")

            has_lower = any(c.islower() for c in password)
            has_upper = any(c.isupper() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

            char_types = sum([has_lower, has_upper, has_digit, has_special])
            score += char_types * 15

            if char_types < 3:
                feedback.append("Используйте больше типов символов")

            if score >= 70:
                strength = "Отличный"
            elif score >= 50:
                strength = "Хороший"
            elif score >= 30:
                strength = "Средний"
            else:
                strength = "Слабый"

            message = f"Надежность: {strength} ({score}/100 баллов)"
            if feedback:
                message += f"\n\nРекомендации:\n• " + "\n• ".join(feedback)

            messagebox.showinfo("Оценка пароля", message)

        # Нижняя панель для кнопок (ВНЕ скролла)
        bottom_frame = ctk.CTkFrame(gen_window, fg_color="transparent")
        bottom_frame.grid(row=1, column=0, sticky="ew", pady=10)
        bottom_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)  # Равномерное распределение

        # Кнопки с равномерным распределением
        generate_btn = ctk.CTkButton(
            bottom_frame,
            text="Сгенерировать",
            command=generate_password,
            font=DesignSystem.get_button_font(),
            fg_color=DesignSystem.PRIMARY,
            height=35
        )
        generate_btn.grid(row=0, column=0, padx=5, sticky="ew")

        copy_btn = ctk.CTkButton(
            bottom_frame,
            text="Копировать",
            command=copy_to_clipboard,
            font=DesignSystem.get_button_font(),
            fg_color=DesignSystem.SUCCESS,
            height=35
        )
        copy_btn.grid(row=0, column=1, padx=5, sticky="ew")

        strength_btn = ctk.CTkButton(
            bottom_frame,
            text="Оценить",
            command=check_strength,
            font=DesignSystem.get_button_font(),
            fg_color=DesignSystem.WARNING,
            height=35
        )
        strength_btn.grid(row=0, column=2, padx=5, sticky="ew")

        close_btn = ctk.CTkButton(
            bottom_frame,
            text="Закрыть",
            command=gen_window.destroy,
            font=DesignSystem.get_button_font(),
            fg_color=DesignSystem.GRAY_400,
            height=35
        )
        close_btn.grid(row=0, column=3, padx=5, sticky="ew")

        # Привязка горячих клавиш
        length_entry.bind("<Return>", lambda event: generate_password())
        gen_window.bind("<Control-g>", lambda event: generate_password())
        gen_window.bind("<Control-c>", lambda event: copy_to_clipboard())
        gen_window.bind("<Escape>", lambda event: gen_window.destroy())

        # Автоматически генерируем пароль при открытии
        gen_window.after(100, generate_password)

        # Устанавливаем фокус на поле длины
        length_entry.focus_set()

    def create_strength_progress_bar(self, parent, score):
        """Создает визуальный индикатор надежности пароля."""
        parent.grid_columnconfigure(0, weight=1)

        # Определяем цвет в зависимости от оценки
        if score < 30:
            color = "#FF4444"  # Красный
        elif score < 50:
            color = "#FFAA33"  # Оранжевый
        elif score < 70:
            color = "#FFFF44"  # Желтый
        elif score < 90:
            color = "#44FF44"  # Зеленый
        else:
            color = "#00AA00"  # Темно-зеленый

        # Создаем прогресс-бар
        progress = ctk.CTkProgressBar(parent, width=300)
        progress.grid(row=0, column=0, sticky="w", padx=(0, DesignSystem.SPACE_4))
        progress.set(score / 100)
        progress.configure(progress_color=color)

        # Добавляем текст с процентами
        ctk.CTkLabel(
            parent,
            text=f"{score}%",
            font=DesignSystem.get_body_font()
        ).grid(row=0, column=1, sticky="w", padx=DesignSystem.SPACE_4)

        return parent

    def backup_data(self):
        """Создает резервную копию базы данных."""
        import shutil
        import datetime

        # Получаем текущую дату и время для имени файла
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")

        # Создаем директорию для резервных копий, если она не существует
        os.makedirs(backup_dir, exist_ok=True)

        # Путь к файлу базы данных
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "passwords.db")

        # Путь к файлу резервной копии
        backup_path = os.path.join(backup_dir, f"passwords_backup_{now}.db")

        # Создаем диалог для выбора места сохранения
        backup_window = ctk.CTkToplevel(self.root)
        backup_window.title("Резервное копирование")
        backup_window.geometry("500x300")
        backup_window.minsize(400, 250)
        backup_window.transient(self.root)
        backup_window.grab_set()

        # Настройка адаптивности окна
        backup_window.grid_columnconfigure(0, weight=1)
        backup_window.grid_rowconfigure(0, weight=1)

        # Создаем основной фрейм
        main_frame = ctk.CTkFrame(backup_window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)

        # Заголовок
        ctk.CTkLabel(
            main_frame,
            text="Резервное копирование базы данных",
            font=DesignSystem.get_title_font()
        ).grid(row=0, column=0, pady=DesignSystem.SPACE_4)

        # Информация
        ctk.CTkLabel(
            main_frame,
            text="Резервная копия будет сохранена по умолчанию в:",
            font=DesignSystem.get_body_font()
        ).grid(row=1, column=0, sticky="w", pady=(DesignSystem.SPACE_4, 0))

        ctk.CTkLabel(
            main_frame,
            text=backup_path,
            font=DesignSystem.get_body_font()
        ).grid(row=2, column=0, sticky="w", pady=(0, DesignSystem.SPACE_4))

        # Фрейм для выбора пользовательского расположения
        custom_frame = ctk.CTkFrame(main_frame)
        custom_frame.grid(row=3, column=0, sticky="ew", pady=DesignSystem.SPACE_4)
        custom_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            custom_frame,
            text="Или выберите другое расположение:",
            font=DesignSystem.get_body_font()
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=DesignSystem.SPACE_2)

        custom_path_var = ctk.StringVar(value=backup_path)
        path_entry = ctk.CTkEntry(
            custom_frame,
            textvariable=custom_path_var,
            font=DesignSystem.get_body_font(),
            width=300
        )
        path_entry.grid(row=1, column=0, sticky="ew", padx=(0, DesignSystem.SPACE_2),
                        pady=DesignSystem.SPACE_2)

        def browse_path():
            # Запрос на выбор директории
            dir_path = filedialog.askdirectory()
            if dir_path:
                filename = f"passwords_backup_{now}.db"
                full_path = os.path.join(dir_path, filename)
                custom_path_var.set(full_path)

        browse_button = ctk.CTkButton(
            custom_frame,
            text="Обзор",
            command=browse_path,
            font=DesignSystem.get_body_font(),
            width=80
        )
        browse_button.grid(row=1, column=1, sticky="e", pady=DesignSystem.SPACE_2)

        # Нижняя панель с кнопками
        button_frame = ctk.CTkFrame(backup_window, fg_color="transparent")
        button_frame.grid(row=1, column=0, sticky="ew", pady=10)
        button_frame.grid_columnconfigure((0, 1), weight=1)

        def perform_backup():
            try:
                # Используем выбранный путь
                selected_path = custom_path_var.get()

                # Создаем директорию, если она не существует
                os.makedirs(os.path.dirname(selected_path), exist_ok=True)

                # Копируем файл базы данных
                shutil.copy2(db_path, selected_path)

                messagebox.showinfo(
                    "Резервное копирование",
                    f"Резервная копия успешно создана в:\n{selected_path}"
                )
                backup_window.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать резервную копию: {e}")

        ctk.CTkButton(
            button_frame,
            text="Создать резервную копию",
            command=perform_backup,
            font=DesignSystem.get_button_font(),
            fg_color=DesignSystem.SUCCESS,
            hover_color="#388E3C",
            width=200
        ).grid(row=0, column=0, padx=DesignSystem.SPACE_4)

        ctk.CTkButton(
            button_frame,
            text="Отмена",
            command=backup_window.destroy,
            font=DesignSystem.get_button_font(),
            width=100
        ).grid(row=0, column=1, padx=DesignSystem.SPACE_4)

    def delete_password(self, password_id, item_frame):
        """Удаляет пароль из базы данных."""
        # Запрашиваем подтверждение
        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить этот пароль? Это действие нельзя отменить."
        )

        if confirm:
            # Удаляем пароль из базы данных
            result = self.db.delete_password(password_id)
            print(f"Результат удаления: {result}")  # Отладочный вывод

            # Удаляем элемент из интерфейса независимо от результата
            item_frame.destroy()
            messagebox.showinfo("Успех", "Пароль успешно удален")

    def delete_password_and_close(self, password_id, item_frame, window):
        """Удаляет пароль и закрывает окно просмотра."""
        self.delete_password(password_id, item_frame)
        window.destroy()
        # Обновляем список паролей
        self.load_passwords()
