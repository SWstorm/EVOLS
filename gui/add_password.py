import customtkinter as ctk
from tkinter import messagebox
from utils.design_system import DesignSystem, UIComponents


class AddPasswordWindow:
    def __init__(self, parent, db, encryptor, main_window):
        self.parent = parent
        self.db = db
        self.encryptor = encryptor
        self.main_window = main_window

        # Создаем окно
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Добавить новый пароль")
        self.window.geometry("550x650")
        self.window.minsize(500, 600)

        # Настройка адаптивности
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # Модальное окно
        self.window.transient(parent)
        self.window.grab_set()

        # Применяем тему
        DesignSystem.setup_theme(self.window)

        # Центрируем окно
        self.center_window()

        # Создаем интерфейс
        self.setup_ui()

    def center_window(self):
        """Центрирует окно относительно родительского окна."""
        self.window.update_idletasks()

        # Получаем размеры окна
        width = self.window.winfo_width()
        height = self.window.winfo_height()

        # Центрируем относительно родительского окна
        try:
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()

            x = parent_x + (parent_width // 2) - (width // 2)
            y = parent_y + (parent_height // 2) - (height // 2)
        except:
            # Если не получается, центрируем относительно экрана
            x = (self.window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.window.winfo_screenheight() // 2) - (height // 2)

        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """Создает интерфейс окна добавления пароля."""
        # Основной скроллируемый контейнер
        scroll_frame = ctk.CTkScrollableFrame(self.window)
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=DesignSystem.SPACE_4,
                          pady=DesignSystem.SPACE_4)
        scroll_frame.grid_columnconfigure(0, weight=1)

        # Основной контейнер для формы
        main_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="ew", padx=DesignSystem.SPACE_6,
                            pady=DesignSystem.SPACE_6)
        main_container.grid_columnconfigure(0, weight=1)

        # Заголовок
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, DesignSystem.SPACE_8))
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = UIComponents.create_section_title(header_frame, "Добавить новый пароль")
        title_label.grid(row=0, column=0, sticky="w")

        subtitle_label = UIComponents.create_subtitle(header_frame, "Заполните информацию о новой записи")
        subtitle_label.grid(row=1, column=0, sticky="w", pady=(DesignSystem.SPACE_1, 0))

        # Форма с полями
        form_frame = ctk.CTkFrame(main_container)
        form_frame.grid(row=1, column=0, sticky="ew", pady=(0, DesignSystem.SPACE_6))
        form_frame.grid_columnconfigure(0, weight=1)

        # Создаем переменные для полей
        self.title_var = ctk.StringVar()
        self.username_var = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.url_var = ctk.StringVar()
        self.category_var = ctk.StringVar()
        self.notes_var = ctk.StringVar()

        # Список полей формы
        fields = [
            {
                "label": "Название*",
                "var": self.title_var,
                "placeholder": "Например: Gmail, Facebook, Банк",
                "required": True
            },
            {
                "label": "Имя пользователя/Email",
                "var": self.username_var,
                "placeholder": "username@example.com"
            },
            {
                "label": "Пароль*",
                "var": self.password_var,
                "placeholder": "Введите пароль",
                "is_password": True,
                "required": True
            },
            {
                "label": "URL веб-сайта",
                "var": self.url_var,
                "placeholder": "https://example.com"
            },
            {
                "label": "Категория",
                "var": self.category_var,
                "placeholder": "Социальные сети, Работа, Банки...",
                "is_combobox": True
            }
        ]

        # Создаем поля формы
        for i, field in enumerate(fields):
            # Контейнер для каждого поля
            field_container = ctk.CTkFrame(form_frame, fg_color="transparent")
            field_container.grid(row=i, column=0, sticky="ew", pady=DesignSystem.SPACE_3)
            field_container.grid_columnconfigure(1, weight=1)

            # Метка поля
            label_text = field["label"]
            label = ctk.CTkLabel(
                field_container,
                text=label_text,
                font=DesignSystem.get_button_font(),
                anchor="w"
            )
            label.grid(row=0, column=0, sticky="nw", padx=(DesignSystem.SPACE_4, DesignSystem.SPACE_2),
                       pady=(DesignSystem.SPACE_2, 0))

            # Создаем поле ввода
            if field.get("is_combobox"):
                # Выпадающий список для категорий
                categories = [
                    "Социальные сети", "Работа", "Банки", "Покупки",
                    "Развлечения", "Образование", "Здоровье", "Другое"
                ]
                entry = ctk.CTkComboBox(
                    field_container,
                    variable=field["var"],
                    values=categories,
                    width=350,
                    height=DesignSystem.INPUT_HEIGHT,
                    font=DesignSystem.get_body_font()
                )
                entry.set("")  # Пустое значение по умолчанию
            else:
                # Обычное поле ввода
                show_char = "*" if field.get("is_password") else None
                entry = UIComponents.create_input_field(
                    field_container,
                    placeholder=field["placeholder"],
                    width=350,
                    show=show_char
                )
                entry.configure(textvariable=field["var"])

            entry.grid(row=1, column=0, columnspan=2, sticky="ew",
                       padx=DesignSystem.SPACE_4, pady=(DesignSystem.SPACE_1, 0))

            # Кнопка показать/скрыть для пароля и кнопка генерации
            if field.get("is_password"):
                button_container = ctk.CTkFrame(field_container, fg_color="transparent")
                button_container.grid(row=2, column=0, columnspan=2, sticky="ew",
                                      padx=DesignSystem.SPACE_4, pady=(DesignSystem.SPACE_2, 0))

                def toggle_password():
                    if entry.cget('show') == '*':
                        entry.configure(show='')
                        show_button.configure(text="Скрыть")
                    else:
                        entry.configure(show='*')
                        show_button.configure(text="Показать")

                show_button = ctk.CTkButton(
                    button_container,
                    text="Показать",
                    command=toggle_password,
                    width=80,
                    height=30,
                    font=DesignSystem.get_caption_font()
                )
                show_button.grid(row=0, column=0, sticky="w")

                generate_button = ctk.CTkButton(
                    button_container,
                    text="Сгенерировать",
                    command=self.generate_password,
                    width=120,
                    height=30,
                    font=DesignSystem.get_caption_font(),
                    fg_color=DesignSystem.SUCCESS,
                    hover_color=DesignSystem.SUCCESS_HOVER
                )
                generate_button.grid(row=0, column=1, sticky="w", padx=(DesignSystem.SPACE_2, 0))

        # Поле для заметок (отдельно, так как это текстовое поле)
        notes_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        notes_container.grid(row=len(fields), column=0, sticky="ew", pady=DesignSystem.SPACE_3)
        notes_container.grid_columnconfigure(0, weight=1)

        notes_label = ctk.CTkLabel(
            notes_container,
            text="Заметки",
            font=DesignSystem.get_button_font(),
            anchor="w"
        )
        notes_label.grid(row=0, column=0, sticky="w", padx=DesignSystem.SPACE_4,
                         pady=(DesignSystem.SPACE_2, 0))

        self.notes_textbox = ctk.CTkTextbox(
            notes_container,
            width=350,
            height=80,
            font=DesignSystem.get_body_font()
        )
        self.notes_textbox.grid(row=1, column=0, sticky="ew", padx=DesignSystem.SPACE_4,
                                pady=(DesignSystem.SPACE_1, 0))

        # Информационное сообщение
        info_frame = ctk.CTkFrame(main_container, fg_color=DesignSystem.GRAY_100)
        info_frame.grid(row=2, column=0, sticky="ew", pady=(0, DesignSystem.SPACE_6))

        info_label = ctk.CTkLabel(
            info_frame,
            text="* Обязательные поля для заполнения",
            font=DesignSystem.get_caption_font(),
            text_color=DesignSystem.GRAY_600
        )
        info_label.grid(row=0, column=0, padx=DesignSystem.SPACE_4, pady=DesignSystem.SPACE_3)

        # Нижняя панель с кнопками (вне скролла)
        bottom_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        bottom_frame.grid(row=1, column=0, sticky="ew", pady=DesignSystem.SPACE_4)
        bottom_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Кнопки действий
        save_button = UIComponents.create_primary_button(
            bottom_frame,
            "Сохранить",
            command=self.save_password,
            width=120
        )
        save_button.grid(row=0, column=0, padx=DesignSystem.SPACE_2)

        test_button = ctk.CTkButton(
            bottom_frame,
            text="Проверить пароль",
            command=self.test_password_strength,
            width=140,
            font=DesignSystem.get_button_font(),
            fg_color=DesignSystem.WARNING,
            hover_color=DesignSystem.WARNING_HOVER
        )
        test_button.grid(row=0, column=1, padx=DesignSystem.SPACE_2)

        cancel_button = UIComponents.create_secondary_button(
            bottom_frame,
            "Отмена",
            command=self.window.destroy,
            width=100
        )
        cancel_button.grid(row=0, column=2, padx=DesignSystem.SPACE_2)

        # Устанавливаем фокус на первое поле
        fields[0]["var"] and self.window.after(100, lambda: self.focus_first_field())

    def focus_first_field(self):
        """Устанавливает фокус на первое поле формы."""
        try:
            # Находим первое поле ввода и устанавливаем на него фокус
            for widget in self.window.winfo_children():
                if isinstance(widget, ctk.CTkScrollableFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, ctk.CTkEntry):
                            child.focus_set()
                            return
        except:
            pass

    def generate_password(self):
        """Генерирует случайный пароль."""
        import random
        import string

        # Параметры генерации
        length = 16
        chars = string.ascii_letters + string.digits + "!@#$%^&*"

        # Генерируем пароль
        password = ''.join(random.choice(chars) for _ in range(length))

        # Устанавливаем в поле
        self.password_var.set(password)

        # Показываем уведомление
        messagebox.showinfo("Генератор паролей", f"Сгенерирован пароль длиной {length} символов")

    def test_password_strength(self):
        """Проверяет надежность введенного пароля."""
        password = self.password_var.get()

        if not password:
            messagebox.showwarning("Предупреждение", "Сначала введите пароль для проверки")
            return

        # Простая проверка надежности
        score = 0
        feedback = []

        if len(password) >= 8:
            score += 25
        else:
            feedback.append("Увеличьте длину до 8+ символов")

        if any(c.islower() for c in password):
            score += 15
        else:
            feedback.append("Добавьте строчные буквы")

        if any(c.isupper() for c in password):
            score += 15
        else:
            feedback.append("Добавьте заглавные буквы")

        if any(c.isdigit() for c in password):
            score += 15
        else:
            feedback.append("Добавьте цифры")

        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 30
        else:
            feedback.append("Добавьте специальные символы")

        # Определяем уровень
        if score >= 80:
            level = "Отличный"
            color = "зеленый"
        elif score >= 60:
            level = "Хороший"
            color = "желтый"
        elif score >= 40:
            level = "Средний"
            color = "оранжевый"
        else:
            level = "Слабый"
            color = "красный"

        # Формируем сообщение
        message = f"Уровень надежности: {level} ({score}/100)\n"
        if feedback:
            message += "\nРекомендации:\n• " + "\n• ".join(feedback)

        messagebox.showinfo("Проверка пароля", message)

    def save_password(self):
        """Сохраняет пароль в базу данных."""
        # Получаем значения полей
        title = self.title_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get()
        url = self.url_var.get().strip()
        category = self.category_var.get().strip()
        notes = self.notes_textbox.get("1.0", "end-1c").strip()

        # Проверяем обязательные поля
        if not title:
            messagebox.showerror("Ошибка", "Название записи обязательно для заполнения!")
            return

        if not password:
            messagebox.showerror("Ошибка", "Пароль обязателен для заполнения!")
            return

        try:
            # Сохраняем в базу данных
            password_id = self.db.add_password(
                title=title,
                username=username,
                password=password,
                url=url,
                category=category,
                notes=notes
            )

            # Показываем сообщение об успехе
            messagebox.showinfo("Успех", f"Пароль '{title}' успешно сохранен!")

            # Обновляем главное окно
            if hasattr(self.main_window, 'load_passwords'):
                self.main_window.load_passwords()

            # Закрываем окно
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить пароль: {e}")

    def validate_url(self, url):
        """Проверяет корректность URL."""
        if not url:
            return True

        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// или https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # домен
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # порт
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return url_pattern.match(url) is not None
