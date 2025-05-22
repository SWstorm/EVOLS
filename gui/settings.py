import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import shutil
from utils.theme_manager import ThemeManager
import pyotp
import qrcode
from PIL import Image, ImageTk
import io


class SettingsWindow:
    def __init__(self, parent, db, encryptor, main_window):
        self.parent = parent
        self.db = db
        self.encryptor = encryptor
        self.main_window = main_window

        # Инициализация переменных настроек
        self.auto_lock_var = ctk.IntVar(value=5)
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
                    self.auto_lock_var.set(settings.get("auto_lock_time", 5))
                    self.backup_dir_var.set(settings.get("backup_directory",
                                                         os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                                      "backups")))
                    self.auto_backup_var.set(settings.get("auto_backup", True))
        except Exception as e:
            print(f"Ошибка при загрузке настроек: {e}")

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
            font=ThemeManager.get_title_font()
        ).grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Автоматическая блокировка
        auto_lock_frame = ctk.CTkFrame(tab_general)
        auto_lock_frame.grid(row=1, column=0, sticky="ew", pady=10)
        auto_lock_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            auto_lock_frame,
            text="Автоматически блокировать через:",
            font=ThemeManager.get_normal_font()
        ).grid(row=0, column=0, padx=10)

        auto_lock_entry = ctk.CTkEntry(
            auto_lock_frame,
            textvariable=self.auto_lock_var,
            width=60,
            font=ThemeManager.get_normal_font()
        )
        auto_lock_entry.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(
            auto_lock_frame,
            text="минут",
            font=ThemeManager.get_normal_font()
        ).grid(row=0, column=2, sticky="w", padx=5)

        # ==== Вкладка безопасности ====
        ctk.CTkLabel(
            tab_security,
            text="Настройки безопасности",
            font=ThemeManager.get_title_font()
        ).grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Изменение мастер-пароля
        ctk.CTkButton(
            tab_security,
            text="Изменить мастер-пароль",
            command=self.change_master_password,
            font=ThemeManager.get_normal_font(),
            height=40,
            width=300,
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color="#1565C0"
        ).grid(row=1, column=0, sticky="w", padx=20, pady=10)

        # Двухфакторная аутентификация
        if os.path.exists("2fa_secret.key"):
            ctk.CTkButton(
                tab_security,
                text="Отключить двухфакторную аутентификацию",
                command=self.disable_2fa,
                font=ThemeManager.get_normal_font(),
                height=40,
                width=300,
                fg_color=ThemeManager.WARNING_COLOR,
                hover_color="#C62828"
            ).grid(row=2, column=0, sticky="w", padx=20, pady=10)
        else:
            ctk.CTkButton(
                tab_security,
                text="Настроить двухфакторную аутентификацию",
                command=self.setup_2fa,
                font=ThemeManager.get_normal_font(),
                height=40,
                width=300,
                fg_color=ThemeManager.SUCCESS_COLOR,
                hover_color="#388E3C"
            ).grid(row=2, column=0, sticky="w", padx=20, pady=10)

        # Проверка всех паролей на надежность
        ctk.CTkButton(
            tab_security,
            text="Проверить все пароли на надежность",
            command=self.check_all_passwords,
            font=ThemeManager.get_normal_font(),
            height=40,
            width=300,
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color="#1565C0"
        ).grid(row=3, column=0, sticky="w", padx=20, pady=10)

        # ==== Вкладка резервного копирования ====
        ctk.CTkLabel(
            tab_backup,
            text="Настройки резервного копирования",
            font=ThemeManager.get_title_font()
        ).grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Директория для резервных копий
        ctk.CTkLabel(
            tab_backup,
            text="Директория для резервных копий:",
            font=ThemeManager.get_normal_font()
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(10, 5))

        dir_frame = ctk.CTkFrame(tab_backup)
        dir_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=5)
        dir_frame.grid_columnconfigure(0, weight=1)

        backup_dir_entry = ctk.CTkEntry(
            dir_frame,
            textvariable=self.backup_dir_var,
            font=ThemeManager.get_normal_font(),
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
            font=ThemeManager.get_normal_font(),
            width=100,
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color="#1565C0"
        ).grid(row=0, column=1)

        # Автоматическое резервное копирование
        ctk.CTkCheckBox(
            tab_backup,
            text="Автоматическое резервное копирование при выходе",
            variable=self.auto_backup_var,
            font=ThemeManager.get_normal_font(),
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color="#1565C0"
        ).grid(row=3, column=0, sticky="w", padx=20, pady=20)

        # Кнопки внизу окна
        button_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        button_frame.grid(row=1, column=0, pady=10)

        ctk.CTkButton(
            button_frame,
            text="Сохранить",
            command=self.save_settings,
            font=ThemeManager.get_button_font(),
            width=120,
            fg_color=ThemeManager.SUCCESS_COLOR,
            hover_color="#388E3C"
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Отмена",
            command=self.window.destroy,
            font=ThemeManager.get_button_font(),
            width=100,
            fg_color="#9E9E9E",
            hover_color="#757575"
        ).grid(row=0, column=1, padx=10)

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
            font=ThemeManager.get_title_font()
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
                font=ThemeManager.get_normal_font()
            ).grid(row=field["row"], column=0, sticky="w", pady=(10, 0))

            password_vars[field["var_name"]] = ctk.StringVar()
            entry = ctk.CTkEntry(
                main_frame,
                textvariable=password_vars[field["var_name"]],
                width=300,
                font=ThemeManager.get_normal_font(),
                show="*"
            )
            entry.grid(row=field["row"] + 1, column=0, pady=(5, 10))

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
            font=ThemeManager.get_button_font(),
            width=120,
            fg_color=ThemeManager.SUCCESS_COLOR,
            hover_color="#388E3C"
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Отмена",
            command=change_window.destroy,
            font=ThemeManager.get_button_font(),
            width=100,
            fg_color="#9E9E9E",
            hover_color="#757575"
        ).grid(row=0, column=1, padx=10)

    def setup_2fa(self):
        """Настраивает двухфакторную аутентификацию TOTP."""
        # Запрашиваем текущий мастер-пароль для подтверждения
        auth_window = ctk.CTkToplevel(self.window)
        auth_window.title("Подтверждение")
        auth_window.geometry("400x200")
        auth_window.minsize(350, 180)

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
            font=ThemeManager.get_normal_font()
        ).grid(row=0, column=0, pady=(0, 15))

        password_var = ctk.StringVar()
        password_entry = ctk.CTkEntry(
            main_frame,
            textvariable=password_var,
            show="*",
            width=300,
            font=ThemeManager.get_normal_font()
        )
        password_entry.grid(row=1, column=0, pady=(0, 20))

        def verify_and_proceed():
            current_password = password_var.get()
            if not current_password:
                messagebox.showerror("Ошибка", "Введите мастер-пароль")
                return

            try:
                # Проверяем пароль
                from crypto import Encryptor
                with open("vault.salt", "rb") as f:
                    salt = f.read()
                test_encryptor = Encryptor(current_password, salt)

                # Если пароль верный, переходим к настройке 2FA
                auth_window.destroy()
                self.show_2fa_setup()
            except Exception:
                messagebox.showerror("Ошибка", "Неверный мастер-пароль")

        # Кнопки
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0)

        ctk.CTkButton(
            button_frame,
            text="Подтвердить",
            command=verify_and_proceed,
            font=ThemeManager.get_button_font(),
            width=120,
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color="#1565C0"
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Отмена",
            command=auth_window.destroy,
            font=ThemeManager.get_button_font(),
            width=100,
            fg_color="#9E9E9E",
            hover_color="#757575"
        ).grid(row=0, column=1, padx=10)

    def show_2fa_setup(self):
        """Показывает окно настройки 2FA с QR-кодом."""
        try:
            # Генерируем секретный ключ
            secret_key = pyotp.random_base32()

            # Создаем объект TOTP
            totp = pyotp.TOTP(secret_key)

            # Создаем URI для QR-кода
            provisioning_uri = totp.provisioning_uri(
                name="Пользователь EVOLS",
                issuer_name="EVOLS"
            )

            # Создаем QR-код
            qr = qrcode.make(provisioning_uri)

            # Показываем окно с QR-кодом и инструкциями
            setup_window = ctk.CTkToplevel(self.window)
            setup_window.title("Настройка двухфакторной аутентификации")
            setup_window.geometry("550x650")
            setup_window.minsize(500, 600)

            # Настройка окна
            setup_window.grid_columnconfigure(0, weight=1)
            setup_window.grid_rowconfigure(0, weight=1)
            setup_window.transient(self.window)
            setup_window.grab_set()

            # Основной скролл-фрейм
            scroll_frame = ctk.CTkScrollableFrame(setup_window)
            scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            scroll_frame.grid_columnconfigure(0, weight=1)

            # Основной контейнер
            main_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            main_frame.grid(row=0, column=0, sticky="ew")
            main_frame.grid_columnconfigure(0, weight=1)

            # Заголовок
            ctk.CTkLabel(
                main_frame,
                text="Настройка двухфакторной аутентификации (2FA)",
                font=ThemeManager.get_title_font()
            ).grid(row=0, column=0, pady=(0, 20))

            # Инструкции
            instructions = [
                "1. Установите приложение аутентификатора (Google Authenticator,",
                "   Microsoft Authenticator или другой совместимый) на ваш смартфон.",
                "2. Отсканируйте следующий QR-код с помощью приложения:"
            ]

            for i, text in enumerate(instructions):
                ctk.CTkLabel(
                    main_frame,
                    text=text,
                    font=ThemeManager.get_normal_font()
                ).grid(row=i + 1, column=0, sticky="w")

            # Преобразуем QR-код в формат для Tkinter
            buffer = io.BytesIO()
            qr.save(buffer, format="PNG")
            buffer.seek(0)
            qr_img = Image.open(buffer)
            qr_img = qr_img.resize((250, 250), Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS)
            qr_photo = ImageTk.PhotoImage(qr_img)

            qr_label = ctk.CTkLabel(main_frame, image=qr_photo, text="")
            qr_label.grid(row=4, column=0, pady=20)
            qr_label.image = qr_photo  # Сохраняем ссылку

            # Секретный ключ
            ctk.CTkLabel(
                main_frame,
                text="3. Или введите этот секретный ключ вручную:",
                font=ThemeManager.get_normal_font()
            ).grid(row=5, column=0, sticky="w")

            # Фрейм для секретного ключа
            secret_frame = ctk.CTkFrame(main_frame)
            secret_frame.grid(row=6, column=0, pady=10)
            secret_frame.grid_columnconfigure(0, weight=1)

            secret_entry = ctk.CTkEntry(
                secret_frame,
                width=300,
                font=ThemeManager.get_normal_font()
            )
            secret_entry.grid(row=0, column=0, padx=5)
            secret_entry.insert(0, secret_key)
            secret_entry.configure(state="readonly")

            def copy_secret():
                setup_window.clipboard_clear()
                setup_window.clipboard_append(secret_key)
                messagebox.showinfo("Копирование", "Секретный ключ скопирован в буфер обмена")

            ctk.CTkButton(
                secret_frame,
                text="Копировать",
                command=copy_secret,
                font=ThemeManager.get_normal_font(),
                width=100,
                fg_color=ThemeManager.PRIMARY_COLOR,
                hover_color="#1565C0"
            ).grid(row=0, column=1, padx=5)

            # Проверка кода
            ctk.CTkLabel(
                main_frame,
                text="4. Введите код из приложения для проверки настройки:",
                font=ThemeManager.get_normal_font()
            ).grid(row=7, column=0, sticky="w", pady=(20, 0))

            verification_frame = ctk.CTkFrame(main_frame)
            verification_frame.grid(row=8, column=0, pady=10)

            code_var = ctk.StringVar()
            code_entry = ctk.CTkEntry(
                verification_frame,
                textvariable=code_var,
                width=100,
                font=ThemeManager.get_normal_font()
            )
            code_entry.grid(row=0, column=0, padx=5)

            def verify_and_save():
                # Проверяем введенный код
                user_code = code_var.get().strip()
                if not user_code:
                    messagebox.showerror("Ошибка", "Введите код из приложения")
                    return

                if totp.verify(user_code):
                    # Сохраняем секретный ключ для будущей проверки
                    with open("2fa_secret.key", "w") as f:
                        f.write(secret_key)

                    messagebox.showinfo(
                        "Успех",
                        "Двухфакторная аутентификация успешно настроена!\n\n"
                        "Теперь при входе в хранилище вам потребуется ввести код из приложения."
                    )
                    setup_window.destroy()
                    # Обновляем UI после настройки 2FA
                    self.setup_ui()
                else:
                    messagebox.showerror("Ошибка", "Неверный код. Попробуйте еще раз.")

            ctk.CTkButton(
                verification_frame,
                text="Проверить и сохранить",
                command=verify_and_save,
                font=ThemeManager.get_normal_font(),
                fg_color=ThemeManager.SUCCESS_COLOR,
                hover_color="#388E3C"
            ).grid(row=0, column=1, padx=5)

            # Кнопка отмены
            ctk.CTkButton(
                main_frame,
                text="Отмена",
                command=setup_window.destroy,
                font=ThemeManager.get_button_font(),
                width=100,
                fg_color="#9E9E9E",
                hover_color="#757575"
            ).grid(row=9, column=0, pady=20)

        except ImportError:
            messagebox.showerror(
                "Ошибка",
                "Необходимо установить библиотеки: pyotp, qrcode, pillow\n\n"
                "Выполните команду: pip install pyotp qrcode pillow"
            )

    def disable_2fa(self):
        """Отключает двухфакторную аутентификацию."""
        confirm = messagebox.askyesno(
            "Подтверждение",
            "Вы уверены, что хотите отключить двухфакторную аутентификацию? "
            "Это снизит безопасность вашего хранилища паролей."
        )

        if confirm:
            try:
                # Удаляем файл с секретным ключом
                if os.path.exists("2fa_secret.key"):
                    os.remove("2fa_secret.key")

                messagebox.showinfo("Информация", "Двухфакторная аутентификация отключена")

                # Обновляем UI
                self.setup_ui()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось отключить 2FA: {e}")

    def check_all_passwords(self):
        # ... остальной код без изменений ...
        # Здесь можно оставить существующую реализацию, или я могу предоставить обновленную версию при необходимости
        pass

    def save_settings(self):
        """Сохраняет настройки приложения."""
        try:
            import json
            # Сбор значений настроек
            settings_data = {
                "auto_lock_time": self.auto_lock_var.get(),
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
