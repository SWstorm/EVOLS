import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import os
import shutil


class SettingsWindow:
    def __init__(self, parent, db, encryptor, main_window):
        self.parent = parent
        self.db = db
        self.encryptor = encryptor
        self.main_window = main_window

        # Добавляем атрибуты класса для хранения значений
        self.auto_lock_var = tk.IntVar(value=5)
        self.backup_dir_var = tk.StringVar(value=os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups"))
        self.auto_backup_var = tk.BooleanVar(value=True)

        self.window = tk.Toplevel(parent)
        self.window.title("Настройки")
        self.window.geometry("500x400")

        self.setup_ui()

    def setup_ui(self):
        # Создаем вкладки для различных настроек
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка общих настроек
        general_tab = tk.Frame(notebook)
        notebook.add(general_tab, text="Общие")

        # Вкладка безопасности
        security_tab = tk.Frame(notebook)
        notebook.add(security_tab, text="Безопасность")

        # Вкладка резервного копирования
        backup_tab = tk.Frame(notebook)
        notebook.add(backup_tab, text="Резервное копирование")

        # Настройки на вкладке общих настроек
        tk.Label(general_tab, text="Общие настройки", font=("Arial", 12, "bold")).pack(pady=10)

        # Автоматическое закрытие приложения
        auto_lock_frame = tk.Frame(general_tab)
        auto_lock_frame.pack(fill=tk.X, pady=5)

        tk.Label(auto_lock_frame, text="Автоматически блокировать через:").pack(side=tk.LEFT, padx=10)
        auto_lock_entry = tk.Entry(auto_lock_frame, textvariable=self.auto_lock_var, width=5)
        auto_lock_entry.pack(side=tk.LEFT)
        tk.Label(auto_lock_frame, text="минут").pack(side=tk.LEFT, padx=5)

        # Настройки на вкладке безопасности
        tk.Label(security_tab, text="Настройки безопасности", font=("Arial", 12, "bold")).pack(pady=10)

        # Изменение мастер-пароля
        change_password_frame = tk.Frame(security_tab)
        change_password_frame.pack(fill=tk.X, pady=10)

        tk.Button(change_password_frame, text="Изменить мастер-пароль",
                  command=self.change_master_password).pack(padx=10)

        # Двухфакторная аутентификация
        twofa_frame = tk.Frame(security_tab)
        twofa_frame.pack(fill=tk.X, pady=10)

        # Проверяем, настроена ли 2FA
        if os.path.exists("2fa_secret.key"):
            tk.Button(twofa_frame, text="Отключить двухфакторную аутентификацию",
                      command=self.disable_2fa).pack(pady=10, padx=10, fill=tk.X)
        else:
            tk.Button(twofa_frame, text="Настроить двухфакторную аутентификацию",
                      command=self.setup_2fa).pack(pady=10, padx=10, fill=tk.X)

        # Проверка всех паролей на надежность
        check_all_frame = tk.Frame(security_tab)
        check_all_frame.pack(fill=tk.X, pady=10)

        tk.Button(check_all_frame, text="Проверить все пароли на надежность",
                  command=self.check_all_passwords).pack(padx=10)

        # Настройки на вкладке резервного копирования
        tk.Label(backup_tab, text="Настройки резервного копирования",
                 font=("Arial", 12, "bold")).pack(pady=10)

        # Директория для резервных копий
        backup_dir_frame = tk.Frame(backup_tab)
        backup_dir_frame.pack(fill=tk.X, pady=5)

        tk.Label(backup_dir_frame, text="Директория для резервных копий:").pack(anchor="w", padx=10)
        backup_dir_entry = tk.Entry(backup_dir_frame, textvariable=self.backup_dir_var, width=40)
        backup_dir_entry.pack(anchor="w", padx=10, pady=5)

        def select_backup_dir():
            dir_path = filedialog.askdirectory()
            if dir_path:
                self.backup_dir_var.set(dir_path)

        tk.Button(backup_dir_frame, text="Выбрать...", command=select_backup_dir).pack(anchor="w", padx=10)

        # Автоматическое резервное копирование
        auto_backup_frame = tk.Frame(backup_tab)
        auto_backup_frame.pack(fill=tk.X, pady=10)

        tk.Checkbutton(auto_backup_frame, text="Автоматическое резервное копирование при выходе",
                       variable=self.auto_backup_var).pack(anchor="w", padx=10)

        # Кнопки внизу окна
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Сохранить", command=self.save_settings).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=10)

    def change_master_password(self):
        """Открывает диалог для изменения мастер-пароля."""
        change_window = tk.Toplevel(self.window)
        change_window.title("Изменение мастер-пароля")
        change_window.geometry("400x200")

        tk.Label(change_window, text="Текущий мастер-пароль:").pack(anchor="w", padx=10, pady=5)
        current_password_entry = tk.Entry(change_window, show="*", width=30)
        current_password_entry.pack(anchor="w", padx=10)

        tk.Label(change_window, text="Новый мастер-пароль:").pack(anchor="w", padx=10, pady=5)
        new_password_entry = tk.Entry(change_window, show="*", width=30)
        new_password_entry.pack(anchor="w", padx=10)

        tk.Label(change_window, text="Подтвердите новый мастер-пароль:").pack(anchor="w", padx=10, pady=5)
        confirm_password_entry = tk.Entry(change_window, show="*", width=30)
        confirm_password_entry.pack(anchor="w", padx=10)

        def do_change_password():
            current_password = current_password_entry.get()
            new_password = new_password_entry.get()
            confirm_password = confirm_password_entry.get()

            if not current_password or not new_password or not confirm_password:
                messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
                return

            if new_password != confirm_password:
                messagebox.showerror("Ошибка", "Новые пароли не совпадают")
                return

            # Проверяем текущий мастер-пароль
            try:
                from crypto import Encryptor
                with open("vault.salt", "rb") as f:
                    old_salt = f.read()
                old_encryptor = Encryptor(current_password, old_salt)
                # Пробуем расшифровать одну запись, чтобы проверить пароль
                test = self.db.get_all_passwords()
                if test:
                    _ = self.db.get_password(test[0][0])  # если не выбросило исключение - пароль верный
            except Exception:
                messagebox.showerror("Ошибка", "Текущий мастер-пароль неверный")
                return

            # Создаем новый шифровальщик с новой солью
            import os
            new_encryptor = Encryptor(new_password)
            new_salt = new_encryptor.salt

            # Перешифровываем все пароли
            try:
                all_ids = [row[0] for row in self.db.get_all_passwords()]
                for pid in all_ids:
                    data = self.db.get_password(pid)
                    # Расшифровываем старым шифровальщиком
                    decrypted_username = old_encryptor.decrypt(data['username']) if data['username'] else ""
                    decrypted_password = old_encryptor.decrypt(data['password'])
                    decrypted_notes = old_encryptor.decrypt(data['notes']) if data['notes'] else ""

                    # Шифруем новым шифровальщиком
                    enc_username = new_encryptor.encrypt(decrypted_username) if decrypted_username else ""
                    enc_password = new_encryptor.encrypt(decrypted_password)
                    enc_notes = new_encryptor.encrypt(decrypted_notes) if decrypted_notes else ""

                    # Обновляем запись в базе
                    self.db.cursor.execute(
                        '''UPDATE passwords SET username=?, password=?, notes=?, date_modified=datetime('now') WHERE id=?''',
                        (enc_username, enc_password, enc_notes, pid)
                    )
                self.db.conn.commit()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при перешифровке: {e}")
                return

            # Сохраняем новую соль
            with open("vault.salt", "wb") as f:
                f.write(new_salt)

            # Обновляем encryptor в приложении
            self.encryptor.salt = new_salt
            self.encryptor.master_password = new_password
            self.encryptor._generate_cipher()

            messagebox.showinfo("Успех", "Мастер-пароль успешно изменен!")
            change_window.destroy()

        button_frame = tk.Frame(change_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Изменить", command=do_change_password).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Отмена", command=change_window.destroy).pack(side=tk.LEFT, padx=10)

    def setup_2fa(self):
        """Настраивает двухфакторную аутентификацию TOTP."""
        # Запрашиваем текущий мастер-пароль для подтверждения
        auth_window = tk.Toplevel(self.window)
        auth_window.title("Подтверждение")
        auth_window.geometry("400x150")

        tk.Label(auth_window, text="Введите мастер-пароль для подтверждения:").pack(anchor="w", padx=10, pady=5)
        password_entry = tk.Entry(auth_window, show="*", width=30)
        password_entry.pack(anchor="w", padx=10)

        def verify_and_proceed():
            # Проверка мастер-пароля
            current_password = password_entry.get()
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

        button_frame = tk.Frame(auth_window)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Подтвердить", command=verify_and_proceed).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Отмена", command=auth_window.destroy).pack(side=tk.LEFT, padx=10)

    def show_2fa_setup(self):
        """Показывает окно настройки 2FA с QR-кодом."""
        try:
            import pyotp
            import qrcode
            from PIL import Image, ImageTk
            import io
        except ImportError:
            messagebox.showerror("Ошибка",
                                 "Необходимо установить библиотеки: pyotp, qrcode, pillow\n\nВыполните команду: pip install pyotp qrcode pillow")
            return

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
        setup_window = tk.Toplevel(self.window)
        setup_window.title("Настройка двухфакторной аутентификации")
        setup_window.geometry("500x600")

        tk.Label(setup_window, text="Настройка двухфакторной аутентификации (2FA)",
                 font=("Arial", 12, "bold")).pack(pady=10)

        tk.Label(setup_window, text="1. Установите приложение аутентификатора (Google Authenticator, \n"
                                    "Microsoft Authenticator или другой совместимый) на ваш смартфон."
                 ).pack(pady=5, padx=10, anchor="w")

        tk.Label(setup_window, text="2. Отсканируйте следующий QR-код с помощью приложения:").pack(pady=5, padx=10,
                                                                                                   anchor="w")

        # Преобразуем QR-код в формат, подходящий для Tkinter
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        qr_img = Image.open(buffer)
        qr_img = qr_img.resize((250, 250), Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS)
        qr_photo = ImageTk.PhotoImage(qr_img)

        qr_label = tk.Label(setup_window, image=qr_photo)
        qr_label.image = qr_photo  # Сохраняем ссылку на изображение
        qr_label.pack(pady=10)

        tk.Label(setup_window, text="3. Или введите этот секретный ключ вручную:").pack(pady=5, padx=10, anchor="w")

        secret_frame = tk.Frame(setup_window)
        secret_frame.pack(pady=5)

        secret_entry = tk.Entry(secret_frame, width=40)
        secret_entry.insert(0, secret_key)
        secret_entry.config(state="readonly")
        secret_entry.pack(side=tk.LEFT, padx=5)

        def copy_secret():
            setup_window.clipboard_clear()
            setup_window.clipboard_append(secret_key)
            messagebox.showinfo("Копирование", "Секретный ключ скопирован в буфер обмена")

        tk.Button(secret_frame, text="Копировать", command=copy_secret).pack(side=tk.LEFT)

        tk.Label(setup_window, text="4. Введите код из приложения для проверки настройки:").pack(pady=5, padx=10,
                                                                                                 anchor="w")

        verification_frame = tk.Frame(setup_window)
        verification_frame.pack(pady=5)

        code_entry = tk.Entry(verification_frame, width=10)
        code_entry.pack(side=tk.LEFT, padx=5)

        def verify_and_save():
            # Проверяем введенный код
            user_code = code_entry.get().strip()
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

        tk.Button(verification_frame, text="Проверить и сохранить", command=verify_and_save).pack(side=tk.LEFT, padx=5)

        # Кнопка отмены
        tk.Button(setup_window, text="Отмена", command=setup_window.destroy).pack(pady=20)

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
        """Проверяет надежность всех паролей в базе данных."""
        from utils.password_strength import PasswordStrength

        # Получаем все пароли
        passwords = self.db.get_all_passwords()

        if not passwords:
            messagebox.showinfo("Информация", "В базе нет сохраненных паролей")
            return

        # Создаем окно для отображения результатов
        result_window = tk.Toplevel(self.window)
        result_window.title("Проверка надежности всех паролей")
        result_window.geometry("600x500")

        # Заголовок
        tk.Label(result_window, text="Результаты проверки надежности паролей",
                 font=("Arial", 12, "bold")).pack(pady=10)

        # Создаем фрейм с прокруткой для отображения результатов
        frame_canvas = tk.Frame(result_window)
        frame_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Добавляем вертикальную прокрутку
        scrollbar = tk.Scrollbar(frame_canvas, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Создаем canvas с прокруткой
        canvas = tk.Canvas(frame_canvas, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Настраиваем прокрутку
        scrollbar.config(command=canvas.yview)

        # Создаем фрейм внутри canvas для размещения результатов
        results_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=results_frame, anchor="nw")

        # Путь к файлу с распространенными паролями
        common_passwords_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                             "data", "common-passwords.txt")

        checker = PasswordStrength(common_passwords_file)

        # Проверяем каждый пароль и отображаем результаты
        weak_passwords = []

        for i, (id, title, category) in enumerate(passwords):
            password_data = self.db.get_password(id)
            result = checker.check_password(password_data["password"])

            # Если пароль слабый, добавляем его в список
            if result['score'] < 50:
                weak_passwords.append((title, result['score'], result['strength']))

            # Создаем фрейм для отображения результата
            password_frame = tk.Frame(results_frame, bd=1, relief=tk.SOLID)
            password_frame.pack(fill=tk.X, pady=5, padx=5)

            # Заголовок с названием пароля
            tk.Label(password_frame, text=f"{title}",
                     font=("Arial", 10, "bold")).pack(anchor="w", padx=5, pady=5)

            # Индикатор надежности
            self.create_strength_progress_bar(password_frame, result['score'])

            # Уровень надежности
            tk.Label(password_frame, text=f"Уровень надежности: {result['strength']}",
                     font=("Arial", 9)).pack(anchor="w", padx=5)

        # Обновляем размеры canvas после добавления всех элементов
        results_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Отображаем сводку о слабых паролях
        if weak_passwords:
            summary_frame = tk.Frame(result_window)
            summary_frame.pack(fill=tk.X, pady=10, padx=10)

            tk.Label(summary_frame, text="Слабые пароли, требующие внимания:",
                     font=("Arial", 11, "bold")).pack(anchor="w")

            for title, score, strength in weak_passwords:
                tk.Label(summary_frame, text=f"• {title} - {strength} ({score}%)",
                         font=("Arial", 10)).pack(anchor="w", pady=2)

        # Кнопка закрытия
        tk.Button(result_window, text="Закрыть",
                  command=result_window.destroy).pack(pady=10)

    def create_strength_progress_bar(self, parent, score):
        """Создает визуальный индикатор надежности пароля."""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, padx=5, pady=5)

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
        bar_width = 300
        bar_height = 20

        bg_bar = tk.Canvas(frame, width=bar_width, height=bar_height, bg="#EEEEEE",
                           highlightthickness=1, highlightbackground="#CCCCCC")
        bg_bar.pack(side=tk.LEFT)

        # Рисуем заполненную часть прогресс-бара
        filled_width = int(bar_width * score / 100)
        bg_bar.create_rectangle(0, 0, filled_width, bar_height, fill=color, outline="")

        # Добавляем текст с процентами
        tk.Label(frame, text=f"{score}%", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)

        return frame

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
