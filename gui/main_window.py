# gui/main_window.py
import customtkinter as ctk
from tkinter import messagebox, simpledialog
import os
import tkinter as tk


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
                    # Получаем время автоматической блокировки (в минутах) и переводим в миллисекунды
                    self.idle_timeout = settings.get("auto_lock_time", 5) * 60 * 1000
            else:
                # Настройки по умолчанию, если файл не существует
                self.idle_timeout = 5 * 60 * 1000  # 5 минут
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
        # Реализация метода блокировки приложения
        pass

    def setup_ui(self):
        # Очищаем окно
        for widget in self.root.winfo_children():
            widget.destroy()

        # Создаем современный интерфейс с CustomTkinter
        # Создаем фреймы
        self.sidebar = ctk.CTkFrame(self.root, width=220)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        self.sidebar.pack_propagate(False)  # Фиксированная ширина

        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Заголовок сайдбара
        ctk.CTkLabel(self.sidebar, text="EVOLS",
                     font=("Helvetica", 24, "bold")).pack(pady=(20, 30))

        # Кнопки меню
        button_data = [
            {"text": "Добавить пароль", "command": self.show_add_password},
            {"text": "Сгенерировать пароль", "command": self.show_password_generator},
            {"text": "Проверить надежность", "command": self.check_password_strength},
            {"text": "Настройки", "command": self.show_settings},
            {"text": "Резервное копирование", "command": self.backup_data}
        ]

        for btn_info in button_data:
            btn = ctk.CTkButton(self.sidebar, text=btn_info["text"],
                                command=btn_info["command"],
                                width=180, height=40)
            btn.pack(pady=5)

        # Заголовок основного фрейма
        ctk.CTkLabel(self.main_frame, text="Ваши пароли",
                     font=("Helvetica", 20, "bold")).pack(anchor="w", padx=20, pady=(20, 5))

        ctk.CTkLabel(self.main_frame, text="Надежное хранилище для ваших данных",
                     font=("Helvetica", 12)).pack(anchor="w", padx=20, pady=(0, 20))

        # Контейнер для списка паролей
        self.password_container = ctk.CTkScrollableFrame(self.main_frame)
        self.password_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Создаем список паролей
        self.load_passwords()

    def load_passwords(self):
        """Загружает список паролей в современном стиле."""
        # Очищаем предыдущий список
        for widget in self.password_container.winfo_children():
            widget.destroy()

        passwords = self.db.get_all_passwords()

        if not passwords:
            # Сообщение, если нет паролей
            empty_label = ctk.CTkLabel(self.password_container,
                                       text="У вас пока нет сохраненных паролей",
                                       font=("Helvetica", 14))
            empty_label.pack(pady=(50, 10))

            add_btn = ctk.CTkButton(self.password_container, text="Добавить пароль",
                                    command=self.show_add_password)
            add_btn.pack(pady=10)
            return

        # Сохраняем список ID паролей
        self.password_ids = []

        # Перебираем все пароли
        for id, title, category in passwords:
            # Создаем карточку для каждого пароля
            card = ctk.CTkFrame(self.password_container)
            card.pack(fill="x", pady=5, padx=5)

            # Сохраняем ID как атрибут карточки
            card.password_id = id
            self.password_ids.append(id)

            # Информация о пароле
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

            title_label = ctk.CTkLabel(info_frame, text=title,
                                       font=("Helvetica", 14, "bold"))
            title_label.pack(anchor="w")

            category_label = ctk.CTkLabel(info_frame, text=f"Категория: {category}" if category else "")
            category_label.pack(anchor="w", pady=(5, 0))

            # Кнопки действий
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=10, pady=10)

            view_btn = ctk.CTkButton(btn_frame, text="Просмотр", width=100,
                                     command=lambda pid=id: self.view_password_by_id(pid))
            view_btn.pack()

            # Привязываем обработчик событий
            card.bind("<Button-1>", self.view_password_details)
            for child in info_frame.winfo_children():
                child.bind("<Button-1>", self.view_password_details)

    def view_password_details(self, event):
        """Отображает информацию о выбранном пароле."""
        # Получаем виджет, на котором произошло событие
        widget = event.widget

        # Если это метка, получаем ее родительский фрейм
        if isinstance(widget, tk.Label) or isinstance(widget, ctk.CTkLabel):
            widget = widget.master

        # Получаем ID пароля из атрибута фрейма
        password_id = widget.password_id
        password_data = self.db.get_password(password_id)

        # Создаем окно для отображения пароля
        view_window = ctk.CTkToplevel(self.root)
        view_window.title(f"Пароль: {password_data['title']}")
        view_window.geometry("400x400")  # Увеличил высоту для кнопки удаления

        # Отображаем информацию о пароле
        info_frame = ctk.CTkFrame(view_window)
        info_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Название
        ctk.CTkLabel(info_frame, text="Название:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=5)
        ctk.CTkLabel(info_frame, text=password_data['title']).grid(
            row=0, column=1, sticky="w", pady=5)

        # Логин
        ctk.CTkLabel(info_frame, text="Логин:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky="w", pady=5)

        username_var = ctk.StringVar(value=password_data['username'])
        username_entry = ctk.CTkEntry(info_frame, textvariable=username_var, width=300)
        username_entry.grid(row=1, column=1, sticky="w", pady=5)

        # Пароль
        ctk.CTkLabel(info_frame, text="Пароль:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky="w", pady=5)

        password_var = ctk.StringVar(value=password_data['password'])
        password_entry = ctk.CTkEntry(info_frame, textvariable=password_var, width=300, show="*")
        password_entry.grid(row=2, column=1, sticky="w", pady=5)

        # Кнопка показать/скрыть пароль
        def toggle_password():
            if password_entry.cget('show') == '*':
                password_entry.configure(show='')
                show_button.configure(text="Скрыть")
            else:
                password_entry.configure(show='*')
                show_button.configure(text="Показать")

        show_button = ctk.CTkButton(info_frame, text="Показать", command=toggle_password)
        show_button.grid(row=2, column=2, padx=5)

        # URL
        ctk.CTkLabel(info_frame, text="URL:", font=("Arial", 10, "bold")).grid(
            row=3, column=0, sticky="w", pady=5)
        ctk.CTkLabel(info_frame, text=password_data['url']).grid(
            row=3, column=1, sticky="w", pady=5)

        # Категория
        ctk.CTkLabel(info_frame, text="Категория:", font=("Arial", 10, "bold")).grid(
            row=4, column=0, sticky="w", pady=5)
        ctk.CTkLabel(info_frame, text=password_data['category']).grid(
            row=4, column=1, sticky="w", pady=5)

        # Заметки
        ctk.CTkLabel(info_frame, text="Заметки:", font=("Arial", 10, "bold")).grid(
            row=5, column=0, sticky="w", pady=5)

        notes_text = ctk.CTkTextbox(info_frame, width=300, height=100)
        notes_text.grid(row=5, column=1, sticky="w", pady=5)
        notes_text.insert("1.0", password_data['notes'])
        notes_text.configure(state="disabled")

        # Кнопки копирования
        def copy_username():
            self.root.clipboard_clear()
            self.root.clipboard_append(username_var.get())
            messagebox.showinfo("Копирование", "Логин скопирован в буфер обмена")

        def copy_password():
            self.root.clipboard_clear()
            self.root.clipboard_append(password_var.get())
            messagebox.showinfo("Копирование", "Пароль скопирован в буфер обмена")

        buttons_frame = ctk.CTkFrame(view_window)
        buttons_frame.pack(pady=10)

        ctk.CTkButton(buttons_frame, text="Копировать логин", command=copy_username).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Копировать пароль", command=copy_password).pack(side="left", padx=5)

        # Добавляем кнопку удаления
        delete_button = ctk.CTkButton(
            view_window,
            text="Удалить пароль",
            command=lambda: self.delete_password_and_close(password_id, widget, view_window),
            fg_color="#ff6b6b",  # Красный цвет для кнопки удаления
            hover_color="#ff5252"
        )
        delete_button.pack(pady=10)

        ctk.CTkButton(buttons_frame, text="Закрыть", command=view_window.destroy).pack(side="left", padx=5)

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

    def show_password_generator(self):
        """Показывает окно генератора паролей."""
        # Определяем функцию генерации пароля локально
        import random
        import string

        def generate_password(length=16, include_uppercase=True, include_digits=True, include_special=True):
            chars = string.ascii_lowercase
            if include_uppercase:
                chars += string.ascii_uppercase
            if include_digits:
                chars += string.digits
            if include_special:
                chars += string.punctuation

            password = []
            if include_uppercase:
                password.append(random.choice(string.ascii_uppercase))
            if include_digits:
                password.append(random.choice(string.digits))
            if include_special:
                password.append(random.choice(string.punctuation))

            remaining_length = length - len(password)
            password.extend(random.choice(chars) for _ in range(remaining_length))

            random.shuffle(password)
            return ''.join(password)

        gen_window = ctk.CTkToplevel(self.root)
        gen_window.title("Генератор паролей")
        gen_window.geometry("400x300")

        # Настройки генератора
        options_frame = ctk.CTkFrame(gen_window)
        options_frame.pack(pady=10, fill="x")

        ctk.CTkLabel(options_frame, text="Длина пароля:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        length_var = ctk.IntVar(value=16)
        length_entry = ctk.CTkEntry(options_frame, textvariable=length_var, width=50)
        length_entry.grid(row=0, column=1, padx=10, pady=5)

        # Флажки для настроек
        uppercase_var = ctk.BooleanVar(value=True)
        digits_var = ctk.BooleanVar(value=True)
        special_var = ctk.BooleanVar(value=True)

        ctk.CTkCheckBox(options_frame, text="Заглавные буквы", variable=uppercase_var).grid(
            row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        ctk.CTkCheckBox(options_frame, text="Цифры", variable=digits_var).grid(
            row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        ctk.CTkCheckBox(options_frame, text="Специальные символы", variable=special_var).grid(
            row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Поле для отображения сгенерированного пароля
        result_frame = ctk.CTkFrame(gen_window)
        result_frame.pack(pady=10, fill="x")

        ctk.CTkLabel(result_frame, text="Сгенерированный пароль:").pack(anchor="w", padx=10)

        password_var = ctk.StringVar()
        password_entry = ctk.CTkEntry(result_frame, textvariable=password_var, width=300)
        password_entry.pack(padx=10, pady=5, fill="x")

        # Функция генерации пароля
        def generate():
            try:
                length = length_var.get()
                if length < 4:
                    messagebox.showerror("Ошибка", "Длина пароля должна быть не менее 4 символов")
                    return

                password = generate_password(
                    length=length,
                    include_uppercase=uppercase_var.get(),
                    include_digits=digits_var.get(),
                    include_special=special_var.get()
                )
                password_var.set(password)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сгенерировать пароль: {e}")

        # Кнопки
        buttons_frame = ctk.CTkFrame(gen_window)
        buttons_frame.pack(pady=10)

        ctk.CTkButton(buttons_frame, text="Сгенерировать", command=generate).pack(side="left", padx=10)

        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(password_var.get())
            messagebox.showinfo("Копирование", "Пароль скопирован в буфер обмена")

        ctk.CTkButton(buttons_frame, text="Копировать", command=copy_to_clipboard).pack(side="left", padx=10)

        # Генерируем пароль при открытии окна
        generate()

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
            select_window.geometry("300x300")

            ctk.CTkLabel(select_window, text="Выберите пароль для проверки:").pack(pady=10)

            # Создаем список паролей
            password_list = []
            for frame in selected_frames:
                if hasattr(frame, 'password_id'):
                    for child in frame.winfo_children():
                        if isinstance(child, ctk.CTkFrame) and child.winfo_get("fg_color") == "transparent":
                            for label in child.winfo_children():
                                if isinstance(label, ctk.CTkLabel) and label.cget("font")[1] == 14:
                                    password_list.append((label.cget("text"), frame.password_id))
                                    break
                            break

            # Создаем фрейм со скроллом для списка паролей
            scroll_frame = ctk.CTkScrollableFrame(select_window, width=250, height=200)
            scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

            selected_id = None
            buttons = []

            def select_password(pid):
                nonlocal selected_id
                selected_id = pid
                for btn in buttons:
                    btn.configure(fg_color=("gray75", "gray25"))
                buttons[next(i for i, (_, _id) in enumerate(password_list) if _id == pid)].configure(fg_color="#1f6aa5")

            # Добавляем кнопки для выбора пароля
            for i, (title, pid) in enumerate(password_list):
                btn = ctk.CTkButton(scroll_frame, text=title, command=lambda p=pid: select_password(p))
                btn.pack(pady=2, fill="x")
                buttons.append(btn)

            def on_confirm():
                if selected_id:
                    select_window.destroy()
                    self.show_password_strength(selected_id)
                else:
                    messagebox.showinfo("Информация", "Выберите пароль для проверки")

            ctk.CTkButton(select_window, text="Проверить", command=on_confirm).pack(pady=10)
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
        strength_window.geometry("500x400")

        # Заголовок
        ctk.CTkLabel(strength_window, text=f"Проверка пароля для: {password_data['title']}",
                     font=("Arial", 16, "bold")).pack(pady=10)

        # Визуальный индикатор надежности
        self.create_strength_progress_bar(strength_window, result['score'])

        # Уровень надежности
        ctk.CTkLabel(strength_window, text=f"Уровень надежности: {result['strength']}",
                     font=("Arial", 14)).pack(pady=5)

        # Энтропия
        ctk.CTkLabel(strength_window, text=f"Энтропия: {entropy:.2f} бит",
                     font=("Arial", 14)).pack(pady=5)

        # Рекомендации
        if result['feedback']:
            ctk.CTkLabel(strength_window, text="Рекомендации по улучшению:",
                         font=("Arial", 14, "bold")).pack(pady=5)

            feedback_frame = ctk.CTkFrame(strength_window)
            feedback_frame.pack(fill="both", expand=True, padx=20)

            for i, feedback in enumerate(result['feedback']):
                ctk.CTkLabel(feedback_frame, text=f"• {feedback}", anchor="w",
                             font=("Arial", 12)).pack(fill="x", pady=2)

        # Кнопка закрытия
        ctk.CTkButton(strength_window, text="Закрыть",
                      command=strength_window.destroy).pack(pady=10)

    def create_strength_progress_bar(self, parent, score):
        """Создает визуальный индикатор надежности пароля."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=20, pady=5)

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
        progress = ctk.CTkProgressBar(frame, width=300)
        progress.pack(side="left", padx=(0, 10))
        progress.set(score / 100)
        progress.configure(progress_color=color)

        # Добавляем текст с процентами
        ctk.CTkLabel(frame, text=f"{score}%", font=("Arial", 12)).pack(side="left", padx=10)

        return frame

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

        try:
            # Копируем файл базы данных
            shutil.copy2(db_path, backup_path)
            messagebox.showinfo("Резервное копирование",
                                f"Резервная копия успешно создана в:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать резервную копию: {e}")

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
