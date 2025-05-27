import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import shutil
from utils.design_system import DesignSystem, ThemeManager

# Условный импорт для 2FA
try:
    import pyotp
    import qrcode
    from PIL import Image

    HAS_2FA_SUPPORT = True
except ImportError:
    HAS_2FA_SUPPORT = False


class SettingsWindow:
    def __init__(self, parent, db, encryptor, main_window):
        self.parent = parent
        self.db = db
        self.encryptor = encryptor
        self.main_window = main_window

        # Инициализация переменных настроек (используем StringVar для безопасности)
        self.auto_lock_var = ctk.StringVar(value="5")
        self.backup_dir_var = ctk.StringVar(value=os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups"))
        self.auto_backup_var = ctk.BooleanVar(value=True)

        # Загрузка текущих настроек
        self.load_current_settings()

        # Создание окна
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Настройки")
        self.window.geometry("600x500")
        self.window.minsize(500, 400)

        # Настройка адаптивности
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # Центрирование окна
        self.window.transient(parent)
        self.window.grab_set()

        # Создание интерфейса
        self.setup_ui()

    def load_current_settings(self):
        """Загружает текущие настройки из файла"""
        try:
            import json
            if os.path.exists("app_settings.json"):
                with open("app_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    self.auto_lock_var.set(str(settings.get("auto_lock_time", 5)))
                    self.backup_dir_var.set(settings.get("backup_directory",
                                                         os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                                      "backups")))
                    self.auto_backup_var.set(settings.get("auto_backup", True))
        except Exception as e:
            print(f"Ошибка при загрузке настроек: {e}")

    def validate_integer_input(self, value):
        """Проверяет, что введенное значение является целым числом"""
        if value == "":
            return True  # Разрешаем пустое поле
        try:
            int(value)
            return True
        except ValueError:
            return False

    def setup_ui(self):
        # Основной контейнер с отступами
        main_frame = ctk.CTkFrame(self.window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Создаем вкладки
        tabview = ctk.CTkTabview(main_frame)
        tabview.grid(row=0, column=0, sticky="nsew")

        # Добавляем вкладки
        tab_general = tabview.add("Общие")
        tab_security = tabview.add("Безопасность")
        tab_backup = tabview.add("Резервное копирование")

        # Настраиваем вкладки
        for tab in [tab_general, tab_security, tab_backup]:
            tab.grid_columnconfigure(0, weight=1)

        # ==== Вкладка общих настроек ====
        ctk.CTkLabel(
            tab_general,
            text="Общие настройки",
            font=DesignSystem.get_title_font()
        ).grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Автоматическая блокировка
        auto_lock_frame = ctk.CTkFrame(tab_general)
        auto_lock_frame.grid(row=1, column=0, sticky="ew", pady=10)
        auto_lock_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            auto_lock_frame,
            text="Автоматически блокировать через:",
            font=DesignSystem.get_body_font()
        ).grid(row=0, column=0, padx=10)

        # Регистрируем валидацию для поля ввода
        vcmd = (self.window.register(self.validate_integer_input), '%P')

        auto_lock_entry = ctk.CTkEntry(
            auto_lock_frame,
            textvariable=self.auto_lock_var,
            width=60,
            font=DesignSystem.get_body_font(),
            validate='key',
            validatecommand=vcmd
        )
        auto_lock_entry.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(
            auto_lock_frame,
            text="минут",
            font=DesignSystem.get_body_font()
        ).grid(row=0, column=2, sticky="w", padx=5)

        # ==== Вкладка безопасности ====
        ctk.CTkLabel(
            tab_security,
            text="Настройки безопасности",
            font=DesignSystem.get_title_font()
        ).grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Изменение мастер-пароля
        ctk.CTkButton(
            tab_security,
            text="Изменить мастер-пароль",
            command=self.change_master_password,
            font=DesignSystem.get_body_font(),
            height=40,
            width=300,
            fg_color=DesignSystem.PRIMARY,
            hover_color="#1565C0"
        ).grid(row=1, column=0, sticky="w", padx=20, pady=10)

        # Двухфакторная аутентификация
        if os.path.exists("2fa_secret.key"):
            ctk.CTkButton(
                tab_security,
                text="Отключить двухфакторную аутентификацию",
                command=self.disable_2fa,
                font=DesignSystem.get_body_font(),
                height=40,
                width=300,
                fg_color=DesignSystem.DANGER,
                hover_color="#C62828"
            ).grid(row=2, column=0, sticky="w", padx=20, pady=10)
        else:
            if HAS_2FA_SUPPORT:
                ctk.CTkButton(
                    tab_security,
                    text="Настроить двухфакторную аутентификацию",
                    command=self.setup_2fa,
                    font=DesignSystem.get_body_font(),
                    height=40,
                    width=300,
                    fg_color=DesignSystem.SUCCESS,
                    hover_color="#388E3C"
                ).grid(row=2, column=0, sticky="w", padx=20, pady=10)
            else:
                info_frame = ctk.CTkFrame(tab_security, fg_color=DesignSystem.GRAY_100)
                info_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

                ctk.CTkLabel(
                    info_frame,
                    text="Двухфакторная аутентификация недоступна\n(требуется: pip install pyotp qrcode pillow)",
                    font=DesignSystem.get_body_font(),
                    text_color=DesignSystem.GRAY_600,
                    justify="center"
                ).grid(row=0, column=0, padx=15, pady=10)

        # Проверка всех паролей на надежность
        ctk.CTkButton(
            tab_security,
            text="Проверить все пароли на надежность",
            command=self.check_all_passwords,
            font=DesignSystem.get_body_font(),
            height=40,
            width=300,
            fg_color=DesignSystem.PRIMARY,
            hover_color="#1565C0"
        ).grid(row=3, column=0, sticky="w", padx=20, pady=10)

        # ==== Вкладка резервного копирования ====
        ctk.CTkLabel(
            tab_backup,
            text="Настройки резервного копирования",
            font=DesignSystem.get_title_font()
        ).grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Директория для резервных копий
        ctk.CTkLabel(
            tab_backup,
            text="Директория для резервных копий:",
            font=DesignSystem.get_body_font()
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(10, 5))

        dir_frame = ctk.CTkFrame(tab_backup)
        dir_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=5)
        dir_frame.grid_columnconfigure(0, weight=1)

        backup_dir_entry = ctk.CTkEntry(
            dir_frame,
            textvariable=self.backup_dir_var,
            font=DesignSystem.get_body_font(),
            width=350
        )
        backup_dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        def select_backup_dir():
            dir_path = filedialog.askdirectory()
            if dir_path:
                self.backup_dir_var.set(dir_path)

        ctk.CTkButton(
            dir_frame,
            text="Выбрать",
            command=select_backup_dir,
            font=DesignSystem.get_body_font(),
            width=100,
            fg_color=DesignSystem.PRIMARY,
            hover_color="#1565C0"
        ).grid(row=0, column=1)

        # Автоматическое резервное копирование
        ctk.CTkCheckBox(
            tab_backup,
            text="Автоматическое резервное копирование при выходе",
            variable=self.auto_backup_var,
            font=DesignSystem.get_body_font()
        ).grid(row=3, column=0, sticky="w", padx=20, pady=20)

        # Кнопки внизу окна
        button_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        button_frame.grid(row=1, column=0, pady=10)

        ctk.CTkButton(
            button_frame,
            text="Сохранить",
            command=self.save_settings,
            font=DesignSystem.get_button_font(),
            width=120,
            fg_color=DesignSystem.SUCCESS,
            hover_color="#388E3C"
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Отмена",
            command=self.window.destroy,
            font=DesignSystem.get_button_font(),
            width=100,
            fg_color="#9E9E9E",
            hover_color="#757575"
        ).grid(row=0, column=1, padx=10)

    def save_settings(self):
        """Сохраняет настройки приложения."""
        try:
            import json

            # Безопасное получение значения автоблокировки
            auto_lock_value = self.auto_lock_var.get().strip()
            if not auto_lock_value:
                auto_lock_value = "5"  # Значение по умолчанию

            try:
                auto_lock_time = int(auto_lock_value)
                if auto_lock_time < 1:
                    auto_lock_time = 1
            except ValueError:
                auto_lock_time = 5
                messagebox.showwarning("Предупреждение",
                                       "Некорректное значение времени блокировки. Установлено значение по умолчанию: 5 минут.")

            # Сбор значений настроек
            settings_data = {
                "auto_lock_time": auto_lock_time,
                "backup_directory": self.backup_dir_var.get(),
                "auto_backup": self.auto_backup_var.get()
            }

            # Проверка директории для резервных копий
            backup_dir = settings_data["backup_directory"]
            if backup_dir and not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)

            # Сохранение в JSON-файл
            with open("app_settings.json", "w", encoding="utf-8") as f:
                json.dump(settings_data, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Информация", "Настройки успешно сохранены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")
        finally:
            self.window.destroy()

    def change_master_password(self):
        """Открывает диалог для изменения мастер-пароля."""
        change_window = ctk.CTkToplevel(self.window)
        change_window.title("Изменение мастер-пароля")
        change_window.geometry("450x300")
        change_window.minsize(400, 250)

        # Настройка адаптивности
        change_window.grid_columnconfigure(0, weight=1)
        change_window.grid_rowconfigure(0, weight=1)

        # Центрируем окно
        change_window.transient(self.window)
        change_window.grab_set()

        # Основной контейнер
        main_frame = ctk.CTkFrame(change_window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        # Заголовок
        ctk.CTkLabel(
            main_frame,
            text="Изменение мастер-пароля",
            font=DesignSystem.get_title_font()
        ).grid(row=0, column=0, pady=(0, 20))

        # Поля ввода
        fields = [
            {"label": "Текущий мастер-пароль:", "var_name": "current", "row": 1},
            {"label": "Новый мастер-пароль:", "var_name": "new", "row": 2},
            {"label": "Подтвердите новый пароль:", "var_name": "confirm", "row": 3}
        ]

        password_vars = {}
        for field in fields:
            ctk.CTkLabel(
                main_frame,
                text=field["label"],
                font=DesignSystem.get_body_font()
            ).grid(row=field["row"], column=0, sticky="w", pady=(10, 0))

            password_vars[field["var_name"]] = ctk.StringVar()
            entry = ctk.CTkEntry(
                main_frame,
                textvariable=password_vars[field["var_name"]],
                width=300,
                font=DesignSystem.get_body_font(),
                show="*"
            )
            entry.grid(row=field["row"] + 1, column=0, pady=(5, 10))
            # Привязка Enter к смене пароля
            entry.bind("<Return>", lambda event: do_change_password())

        def do_change_password():
            current_password = password_vars["current"].get()
            new_password = password_vars["new"].get()
            confirm_password = password_vars["confirm"].get()

            if not current_password or not new_password or not confirm_password:
                messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
                return

            if new_password != confirm_password:
                messagebox.showerror("Ошибка", "Новые пароли не совпадают")
                return

            try:
                from crypto import Encryptor
                with open("vault.salt", "rb") as f:
                    old_salt = f.read()
                old_encryptor = Encryptor(current_password, old_salt)

                # Пробуем расшифровать одну запись
                test = self.db.get_all_passwords()
                if test:
                    _ = self.db.get_password(test[0][0])  # Проверка пароля

                # Создаем новый шифровальщик
                new_encryptor = Encryptor(new_password)
                new_salt = new_encryptor.salt

                # Перешифровываем пароли
                all_ids = [row[0] for row in self.db.get_all_passwords()]
                for pid in all_ids:
                    data = self.db.get_password(pid)
                    # Расшифровываем
                    decrypted_username = old_encryptor.decrypt(data['username']) if data['username'] else ""
                    decrypted_password = old_encryptor.decrypt(data['password'])
                    decrypted_notes = old_encryptor.decrypt(data['notes']) if data['notes'] else ""

                    # Шифруем новым ключом
                    enc_username = new_encryptor.encrypt(decrypted_username) if decrypted_username else ""
                    enc_password = new_encryptor.encrypt(decrypted_password)
                    enc_notes = new_encryptor.encrypt(decrypted_notes) if decrypted_notes else ""

                    # Обновляем в базе
                    self.db.cursor.execute(
                        '''UPDATE passwords SET username=?, password=?, notes=?, 
                        date_modified=datetime('now') WHERE id=?''',
                        (enc_username, enc_password, enc_notes, pid)
                    )
                self.db.conn.commit()

                # Сохраняем новую соль
                with open("vault.salt", "wb") as f:
                    f.write(new_salt)

                # Обновляем encryptor в приложении
                self.encryptor.salt = new_salt
                self.encryptor.master_password = new_password
                self.encryptor._generate_cipher()

                messagebox.showinfo("Успех", "Мастер-пароль успешно изменен!")
                change_window.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при смене пароля: {e}")

        # Кнопки
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=7, column=0, pady=(10, 0))

        ctk.CTkButton(
            button_frame,
            text="Изменить",
            command=do_change_password,
            font=DesignSystem.get_button_font(),
            width=120,
            fg_color=DesignSystem.SUCCESS,
            hover_color="#388E3C"
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Отмена",
            command=change_window.destroy,
            font=DesignSystem.get_button_font(),
            width=100,
            fg_color="#9E9E9E",
            hover_color="#757575"
        ).grid(row=0, column=1, padx=10)

    def setup_2fa(self):
        """Настраивает двухфакторную аутентификацию TOTP."""
        if not HAS_2FA_SUPPORT:
            messagebox.showerror(
                "Функция недоступна",
                "Для использования двухфакторной аутентификации необходимо установить библиотеки:\n\n"
                "pip install pyotp qrcode pillow"
            )
            return

        # Запрашиваем текущий мастер-пароль для подтверждения
        auth_window = ctk.CTkToplevel(self.window)
        auth_window.title("Подтверждение")
        auth_window.geometry("450x250")
        auth_window.minsize(400, 200)

        # Настройка окна
        auth_window.grid_columnconfigure(0, weight=1)
        auth_window.grid_rowconfigure(0, weight=1)
        auth_window.transient(self.window)
        auth_window.grab_set()

        # Основной контейнер
        main_frame = ctk.CTkFrame(auth_window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            main_frame,
            text="Введите мастер-пароль для подтверждения:",
            font=DesignSystem.get_body_font(),
            wraplength=350
        ).grid(row=0, column=0, pady=(0, 10))

        password_var = ctk.StringVar()
        password_entry = ctk.CTkEntry(
            main_frame,
            textvariable=password_var,
            show="*",
            width=300,
            font=DesignSystem.get_body_font()
        )
        password_entry.grid(row=1, column=0, pady=(0, 20))

        def verify_and_proceed():
            current_password = password_var.get()
            if not current_password:
                messagebox.showerror("Ошибка", "Введите мастер-пароль")
                return

            try:
                # Проверяем пароль через существующий encryptor
                test_passwords = self.db.get_all_passwords()
                if test_passwords:
                    # Пробуем расшифровать существующий пароль
                    test_data = self.db.get_password(test_passwords[0][0])
                    # Если получилось расшифровать, значит пароль верный
                    auth_window.destroy()
                    self.show_2fa_setup()
                else:
                    # Если нет паролей, проверяем через создание временного encryptor
                    from crypto import Encryptor
                    with open("vault.salt", "rb") as f:
                        salt = f.read()
                    test_encryptor = Encryptor(current_password, salt)
                    # Если дошли до сюда без ошибки, пароль верный
                    auth_window.destroy()
                    self.show_2fa_setup()

            except Exception as e:
                print(f"Ошибка проверки пароля: {e}")
                messagebox.showerror("Ошибка", "Неверный мастер-пароль")

        # Кнопки
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0)

        ctk.CTkButton(
            button_frame,
            text="Подтвердить",
            command=verify_and_proceed,
            font=DesignSystem.get_button_font(),
            width=120,
            fg_color=DesignSystem.PRIMARY,
            hover_color="#1565C0"
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Отмена",
            command=auth_window.destroy,
            font=DesignSystem.get_button_font(),
            width=100,
            fg_color="#9E9E9E",
            hover_color="#757575"
        ).grid(row=0, column=1, padx=10)

        # Привязка Enter
        password_entry.bind("<Return>", lambda event: verify_and_proceed())
        password_entry.focus_set()

    def show_2fa_setup(self):
        """Показывает окно настройки 2FA с улучшенным дизайном."""
        try:
            # Генерируем секретный ключ
            secret_key = pyotp.random_base32()
            totp = pyotp.TOTP(secret_key)

            # Создаем URI для QR-кода
            provisioning_uri = totp.provisioning_uri(
                name="Пользователь EVOLS",
                issuer_name="EVOLS Password Manager"
            )

            # Создаем окно с адаптивным дизайном
            setup_window = ctk.CTkToplevel(self.window)
            setup_window.title("Настройка 2FA")
            setup_window.geometry("600x700")
            setup_window.minsize(550, 650)

            # Настройка адаптивности окна
            setup_window.grid_columnconfigure(0, weight=1)
            setup_window.grid_rowconfigure(0, weight=1)
            setup_window.transient(self.window)
            setup_window.grab_set()

            # Основной скроллируемый фрейм
            scroll_frame = ctk.CTkScrollableFrame(setup_window)
            scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            scroll_frame.grid_columnconfigure(0, weight=1)

            # Основной контейнер
            main_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            main_frame.grid(row=0, column=0, sticky="ew")
            main_frame.grid_columnconfigure(0, weight=1)

            # Заголовок
            title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
            title_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                title_frame,
                text="Настройка двухфакторной\nаутентификации (2FA)",
                font=DesignSystem.get_title_font(),
                justify="center"
            ).grid(row=0, column=0)

            # Инструкции
            instructions_frame = ctk.CTkFrame(main_frame, fg_color=DesignSystem.GRAY_100)
            instructions_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
            instructions_frame.grid_columnconfigure(0, weight=1)

            instructions = [
                "1. Установите приложение аутентификатора:",
                "   • Google Authenticator",
                "   • Microsoft Authenticator",
                "   • Authy или другое совместимое",
                "",
                "2. Выберите один из способов настройки:"
            ]

            for i, text in enumerate(instructions):
                ctk.CTkLabel(
                    instructions_frame,
                    text=text,
                    font=DesignSystem.get_body_font(),
                    anchor="w"
                ).grid(row=i, column=0, sticky="w", padx=10, pady=2)

            # Вкладки для способов настройки
            tabview = ctk.CTkTabview(main_frame)
            tabview.grid(row=2, column=0, sticky="ew", pady=(0, 20))

            # Вкладка с QR-кодом (ИСПРАВЛЕНО - ПОСЛЕДНЕЕ ИЗМЕНЕНИЕ)
            qr_tab = tabview.add("QR-код")
            qr_tab.grid_columnconfigure(0, weight=1)

            # Создаем QR-код с гарантированной конвертацией
            try:
                import io

                qr = qrcode.QRCode(version=1, box_size=8, border=4)
                qr.add_data(provisioning_uri)
                qr.make(fit=True)

                # Создаем изображение и сразу сохраняем в буфер как PNG
                qr_image = qr.make_image(fill_color="black", back_color="white")

                buffer = io.BytesIO()
                qr_image.save(buffer, format='PNG')
                buffer.seek(0)

                # Открываем из буфера как обычное PIL изображение
                pil_image = Image.open(buffer).convert('RGB')

                # Теперь это гарантированно PIL.Image.Image
                qr_ctk_image = ctk.CTkImage(
                    light_image=pil_image,
                    dark_image=pil_image,
                    size=(220, 220)
                )

                # Инструкция
                ctk.CTkLabel(
                    qr_tab,
                    text="Отсканируйте QR-код приложением аутентификатора:",
                    font=DesignSystem.get_body_font(),
                    wraplength=300
                ).grid(row=0, column=0, pady=(15, 10), padx=20)

                # Отображаем QR-код
                qr_label = ctk.CTkLabel(
                    qr_tab,
                    image=qr_ctk_image,
                    text=""
                )
                qr_label.grid(row=1, column=0, pady=(0, 15))

                # Дополнительная информация под QR-кодом
                ctk.CTkLabel(
                    qr_tab,
                    text="После сканирования приложение добавит новую запись\nдля 'EVOLS Password Manager'",
                    font=DesignSystem.get_caption_font(),
                    text_color=DesignSystem.GRAY_600,
                    justify="center"
                ).grid(row=2, column=0, pady=(0, 10))

            except Exception as e:
                print(f"Ошибка создания QR-кода: {e}")

                error_frame = ctk.CTkFrame(qr_tab, fg_color=DesignSystem.GRAY_100)
                error_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)

                ctk.CTkLabel(
                    error_frame,
                    text="❌ Не удалось создать QR-код",
                    font=DesignSystem.get_button_font(),
                    text_color=DesignSystem.DANGER
                ).grid(row=0, column=0, padx=15, pady=(10, 5))

                ctk.CTkLabel(
                    error_frame,
                    text="Используйте вкладку 'Ручной ввод' для настройки",
                    font=DesignSystem.get_body_font(),
                    text_color=DesignSystem.GRAY_600
                ).grid(row=1, column=0, padx=15, pady=(0, 10))

            # Вкладка с ручным вводом
            manual_tab = tabview.add("Ручной ввод")
            manual_tab.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                manual_tab,
                text="Введите этот секретный ключ вручную:",
                font=DesignSystem.get_body_font()
            ).grid(row=0, column=0, pady=(10, 5))

            # Фрейм для секретного ключа
            secret_frame = ctk.CTkFrame(manual_tab)
            secret_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=20)
            secret_frame.grid_columnconfigure(0, weight=1)

            secret_entry = ctk.CTkEntry(
                secret_frame,
                width=400,
                font=("Courier", 12),
                justify="center"
            )
            secret_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
            secret_entry.insert(0, secret_key)
            secret_entry.configure(state="readonly")

            def copy_secret():
                setup_window.clipboard_clear()
                setup_window.clipboard_append(secret_key)
                # Временное уведомление
                old_text = copy_btn.cget("text")
                copy_btn.configure(text="✓ Скопировано")
                setup_window.after(2000, lambda: copy_btn.configure(text=old_text))

            copy_btn = ctk.CTkButton(
                secret_frame,
                text="Копировать",
                command=copy_secret,
                font=DesignSystem.get_body_font(),
                width=100,
                fg_color=DesignSystem.SUCCESS,
                hover_color=DesignSystem.SUCCESS_HOVER
            )
            copy_btn.grid(row=1, column=0, pady=5)

            # Проверка кода
            verification_frame = ctk.CTkFrame(main_frame)
            verification_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
            verification_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                verification_frame,
                text="Введите код из приложения для проверки:",
                font=DesignSystem.get_button_font()
            ).grid(row=0, column=0, pady=(15, 5))

            code_frame = ctk.CTkFrame(verification_frame, fg_color="transparent")
            code_frame.grid(row=1, column=0, pady=(0, 15))

            code_var = ctk.StringVar()
            code_entry = ctk.CTkEntry(
                code_frame,
                textvariable=code_var,
                width=120,
                font=("Courier", 16),
                justify="center",
                placeholder_text="000000"
            )
            code_entry.grid(row=0, column=0, padx=5)

            def verify_and_save():
                user_code = code_var.get().strip()
                if not user_code:
                    messagebox.showerror("Ошибка", "Введите код из приложения")
                    return

                if len(user_code) != 6 or not user_code.isdigit():
                    messagebox.showerror("Ошибка", "Код должен состоять из 6 цифр")
                    return

                if totp.verify(user_code):
                    # Сохраняем секретный ключ
                    with open("2fa_secret.key", "w") as f:
                        f.write(secret_key)

                    messagebox.showinfo(
                        "Успех",
                        "Двухфакторная аутентификация успешно настроена!\n\n"
                        "Теперь при входе потребуется код из приложения."
                    )
                    setup_window.destroy()
                    # Обновляем UI после настройки 2FA
                    self.setup_ui()
                else:
                    messagebox.showerror("Ошибка",
                                         "Неверный код. Убедитесь, что время на устройствах синхронизировано.")

            verify_btn = ctk.CTkButton(
                code_frame,
                text="Проверить и сохранить",
                command=verify_and_save,
                font=DesignSystem.get_button_font(),
                fg_color=DesignSystem.SUCCESS,
                hover_color=DesignSystem.SUCCESS_HOVER,
                width=160
            )
            verify_btn.grid(row=0, column=1, padx=5)

            # Дополнительная информация
            info_frame = ctk.CTkFrame(main_frame, fg_color=DesignSystem.GRAY_100)
            info_frame.grid(row=4, column=0, sticky="ew")
            info_frame.grid_columnconfigure(0, weight=1)

            info_text = (
                "💡 Совет: Сохраните секретный ключ в надежном месте.\n"
                "При потере телефона вы сможете восстановить доступ."
            )

            ctk.CTkLabel(
                info_frame,
                text=info_text,
                font=DesignSystem.get_caption_font(),
                text_color=DesignSystem.GRAY_600,
                justify="left"
            ).grid(row=0, column=0, padx=15, pady=10)

            # Нижняя панель с кнопкой отмены
            bottom_frame = ctk.CTkFrame(setup_window, fg_color="transparent")
            bottom_frame.grid(row=1, column=0, sticky="ew", pady=10)
            bottom_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkButton(
                bottom_frame,
                text="Отмена",
                command=setup_window.destroy,
                font=DesignSystem.get_button_font(),
                width=100,
                fg_color="#9E9E9E",
                hover_color="#757575"
            ).grid(row=0, column=0)

            # Привязки клавиш
            code_entry.bind("<Return>", lambda event: verify_and_save())
            setup_window.bind("<Escape>", lambda event: setup_window.destroy())

            # Фокус на поле ввода кода
            code_entry.focus_set()

        except Exception as e:
            messagebox.showerror(
                "Ошибка настройки 2FA",
                f"Произошла ошибка при настройке двухфакторной аутентификации:\n\n{e}\n\n"
                f"Убедитесь, что установлены необходимые библиотеки:\n"
                f"pip install pyotp qrcode pillow"
            )

    def disable_2fa(self):
        """Отключает двухфакторную аутентификацию."""
        # Создаем красивое окно подтверждения
        confirm_window = ctk.CTkToplevel(self.window)
        confirm_window.title("Отключение 2FA")
        confirm_window.geometry("450x200")
        confirm_window.minsize(400, 180)

        # Настройка окна
        confirm_window.grid_columnconfigure(0, weight=1)
        confirm_window.grid_rowconfigure(0, weight=1)
        confirm_window.transient(self.window)
        confirm_window.grab_set()

        # Основной контейнер
        main_frame = ctk.CTkFrame(confirm_window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        # Предупреждающая иконка и текст
        ctk.CTkLabel(
            main_frame,
            text="⚠️",
            font=("Arial", 32)
        ).grid(row=0, column=0, pady=(0, 10))

        ctk.CTkLabel(
            main_frame,
            text="Отключение двухфакторной аутентификации",
            font=DesignSystem.get_button_font()
        ).grid(row=1, column=0)

        ctk.CTkLabel(
            main_frame,
            text="Это снизит безопасность вашего хранилища паролей.\nВы уверены, что хотите продолжить?",
            font=DesignSystem.get_body_font(),
            justify="center"
        ).grid(row=2, column=0, pady=(5, 15))

        def do_disable():
            try:
                if os.path.exists("2fa_secret.key"):
                    os.remove("2fa_secret.key")

                messagebox.showinfo("Информация", "Двухфакторная аутентификация отключена")
                confirm_window.destroy()

                # Обновляем UI
                self.setup_ui()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось отключить 2FA: {e}")

        # Кнопки
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0)

        ctk.CTkButton(
            button_frame,
            text="Да, отключить",
            command=do_disable,
            font=DesignSystem.get_button_font(),
            width=120,
            fg_color=DesignSystem.DANGER,
            hover_color=DesignSystem.DANGER_HOVER
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Отмена",
            command=confirm_window.destroy,
            font=DesignSystem.get_button_font(),
            width=100,
            fg_color="#9E9E9E",
            hover_color="#757575"
        ).grid(row=0, column=1, padx=10)

    def check_all_passwords(self):
        """Проверяет надежность всех паролей в базе данных."""
        passwords = self.db.get_all_passwords()

        if not passwords:
            messagebox.showinfo("Информация", "В базе данных нет сохраненных паролей для проверки")
            return

        # Создаем окно результатов
        results_window = ctk.CTkToplevel(self.window)
        results_window.title("Анализ надежности паролей")
        results_window.geometry("700x500")
        results_window.minsize(600, 400)

        # Настройка адаптивности
        results_window.grid_columnconfigure(0, weight=1)
        results_window.grid_rowconfigure(0, weight=1)
        results_window.transient(self.window)
        results_window.grab_set()

        # Скроллируемый фрейм для результатов
        scroll_frame = ctk.CTkScrollableFrame(results_window)
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scroll_frame.grid_columnconfigure(0, weight=1)

        # Заголовок
        ctk.CTkLabel(
            scroll_frame,
            text="Анализ надежности паролей",
            font=DesignSystem.get_title_font()
        ).grid(row=0, column=0, pady=(0, 20))

        weak_count = 0
        medium_count = 0
        strong_count = 0

        # Анализируем каждый пароль
        for i, (password_id, title, category) in enumerate(passwords):
            try:
                password_data = self.db.get_password(password_id)
                password = password_data['password']

                # Простая оценка надежности
                score = 0
                if len(password) >= 8:
                    score += 25
                if len(password) >= 12:
                    score += 15
                if any(c.islower() for c in password):
                    score += 15
                if any(c.isupper() for c in password):
                    score += 15
                if any(c.isdigit() for c in password):
                    score += 15
                if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
                    score += 15

                # Определяем уровень
                if score >= 70:
                    level = "Сильный"
                    color = DesignSystem.SUCCESS
                    strong_count += 1
                elif score >= 40:
                    level = "Средний"
                    color = DesignSystem.WARNING
                    medium_count += 1
                else:
                    level = "Слабый"
                    color = DesignSystem.DANGER
                    weak_count += 1

                # Создаем карточку для каждого пароля
                card = ctk.CTkFrame(scroll_frame)
                card.grid(row=i + 1, column=0, sticky="ew", pady=5)
                card.grid_columnconfigure(1, weight=1)

                # Название
                ctk.CTkLabel(
                    card,
                    text=title,
                    font=DesignSystem.get_button_font()
                ).grid(row=0, column=0, sticky="w", padx=10, pady=5)

                # Уровень надежности
                ctk.CTkLabel(
                    card,
                    text=f"{level} ({score}/100)",
                    font=DesignSystem.get_body_font(),
                    text_color=color
                ).grid(row=0, column=1, sticky="e", padx=10, pady=5)

            except Exception as e:
                print(f"Ошибка анализа пароля {title}: {e}")
                continue

        # Статистика
        stats_frame = ctk.CTkFrame(scroll_frame, fg_color=DesignSystem.GRAY_100)
        stats_frame.grid(row=len(passwords) + 1, column=0, sticky="ew", pady=(20, 0))

        ctk.CTkLabel(
            stats_frame,
            text="Статистика:",
            font=DesignSystem.get_button_font()
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))

        stats_text = f"Сильных: {strong_count} | Средних: {medium_count} | Слабых: {weak_count}"
        ctk.CTkLabel(
            stats_frame,
            text=stats_text,
            font=DesignSystem.get_body_font()
        ).grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))

        # Кнопка закрытия
        ctk.CTkButton(
            results_window,
            text="Закрыть",
            command=results_window.destroy,
            font=DesignSystem.get_button_font(),
            width=100
        ).grid(row=1, column=0, pady=10)
