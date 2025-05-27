import customtkinter as ctk
from tkinter import messagebox
import os
from utils.design_system import DesignSystem


def on_login():
    pass


class UnlockWindow:
    def __init__(self, parent, on_success_callback, on_cancel_callback=None):
        """
        Создает окно разблокировки приложения.

        Args:
            parent: Родительское окно
            on_success_callback: Функция, вызываемая при успешной разблокировке
            on_cancel_callback: Функция, вызываемая при отмене (необязательно)
        """
        self.parent = parent
        self.on_success = on_success_callback
        self.on_cancel = on_cancel_callback or self.default_cancel

        # Создаем окно
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Разблокировка хранилища")
        self.window.geometry("450x300")
        self.window.minsize(400, 250)

        # Настройки окна
        self.window.grab_set()  # Модальное окно
        self.window.transient(parent)  # Поверх родительского окна
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)  # Обработка закрытия
        self.window.resizable(False, False)  # Запрещаем изменение размера

        # Настраиваем адаптивность
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # Применяем тему
        DesignSystem.setup_theme(self.window)

        # Центрируем окно
        self.center_window()

        # Создаем интерфейс
        self.setup_ui()

        # Устанавливаем фокус на поле ввода
        self.password_entry.focus_set()

    def center_window(self):
        """Центрирует окно относительно родительского окна или экрана."""
        self.window.update_idletasks()

        # Получаем размеры окна
        width = self.window.winfo_width()
        height = self.window.winfo_height()

        # Пытаемся центрировать относительно родительского окна
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
        """Создает интерфейс окна разблокировки."""
        # Основной контейнер
        main_frame = ctk.CTkFrame(self.window)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        # Иконка блокировки (эмодзи или текст)
        lock_label = ctk.CTkLabel(
            main_frame,
            text="🔒",
            font=("Arial", 48)
        )
        lock_label.grid(row=0, column=0, pady=(0, 10))

        # Заголовок
        title_label = ctk.CTkLabel(
            main_frame,
            text="Хранилище заблокировано",
            font=DesignSystem.get_title_font()
        )
        title_label.grid(row=1, column=0, pady=(0, 10))

        # Подзаголовок
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Введите мастер-пароль для разблокировки",
            font=DesignSystem.get_normal_font()
        )
        subtitle_label.grid(row=2, column=0, pady=(0, 20))

        # Поле ввода пароля
        self.password_entry = ctk.CTkEntry(
            main_frame,
            width=300,
            height=40,
            font=DesignSystem.get_normal_font(),
            show="*",
            placeholder_text="Мастер-пароль"
        )
        self.password_entry.grid(row=3, column=0, pady=(0, 20))

        # Привязываем Enter к кнопке разблокировки
        self.password_entry.bind("<Return>", lambda event: on_login())

        # Фрейм для кнопок
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, pady=(10, 0))

        # Кнопка разблокировки
        unlock_button = ctk.CTkButton(
            button_frame,
            text="Разблокировать",
            width=150,
            height=40,
            font=DesignSystem.get_button_font(),
            fg_color=DesignSystem.PRIMARY_COLOR,
            hover_color="#1565C0",
            command=self.unlock
        )
        unlock_button.grid(row=0, column=0, padx=(0, 10))

        # Кнопка выхода
        exit_button = ctk.CTkButton(
            button_frame,
            text="Выход",
            width=100,
            height=40,
            font=DesignSystem.get_button_font(),
            fg_color="#9E9E9E",
            hover_color="#757575",
            command=self.on_close
        )
        exit_button.grid(row=0, column=1)

        # Дополнительная информация (опционально)
        info_label = ctk.CTkLabel(
            main_frame,
            text="Приложение было заблокировано из-за бездействия",
            font=("Arial", 10),
            text_color="gray"
        )
        info_label.grid(row=5, column=0, pady=(20, 0))

    def unlock(self):
        """Обрабатывает попытку разблокировки."""
        password = self.password_entry.get()

        if not password:
            # Анимация тряски для поля ввода
            self.shake_widget(self.password_entry)
            messagebox.showerror("Ошибка", "Введите мастер-пароль")
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
                self.success_unlock()

        except Exception as e:
            # Анимация тряски при неверном пароле
            self.shake_widget(self.password_entry)
            self.password_entry.delete(0, "end")
            messagebox.showerror("Ошибка", "Неверный мастер-пароль")

    def check_2fa(self, master_password):
        """Запрашивает код двухфакторной аутентификации."""
        # Создаем новое окно для ввода кода 2FA
        twofa_window = ctk.CTkToplevel(self.window)
        twofa_window.title("Двухфакторная аутентификация")
        twofa_window.geometry("400x250")
        twofa_window.minsize(350, 200)

        # Настройки окна
        twofa_window.grab_set()
        twofa_window.transient(self.window)
        twofa_window.resizable(False, False)

        # Центрируем окно 2FA
        twofa_window.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() // 2) - (twofa_window.winfo_width() // 2)
        y = self.window.winfo_y() + (self.window.winfo_height() // 2) - (twofa_window.winfo_height() // 2)
        twofa_window.geometry(f"+{x}+{y}")

        # Настраиваем адаптивность
        twofa_window.grid_columnconfigure(0, weight=1)
        twofa_window.grid_rowconfigure(0, weight=1)

        # Основной контейнер для 2FA
        twofa_frame = ctk.CTkFrame(twofa_window)
        twofa_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        twofa_frame.grid_columnconfigure(0, weight=1)

        # Заголовок
        ctk.CTkLabel(
            twofa_frame,
            text="Двухфакторная аутентификация",
            font=DesignSystem.get_title_font()
        ).grid(row=0, column=0, pady=(0, 20))

        # Инструкция
        ctk.CTkLabel(
            twofa_frame,
            text="Введите код из приложения аутентификатора:",
            font=DesignSystem.get_normal_font()
        ).grid(row=1, column=0, pady=(0, 15))

        # Поле ввода кода
        code_entry = ctk.CTkEntry(
            twofa_frame,
            width=150,
            height=40,
            font=DesignSystem.get_normal_font(),
            placeholder_text="000000"
        )
        code_entry.grid(row=2, column=0, pady=(0, 20))
        code_entry.focus_set()

        def verify_2fa():
            code = code_entry.get().strip()

            if not code:
                self.shake_widget(code_entry)
                messagebox.showerror("Ошибка", "Введите код аутентификации")
                return

            try:
                import pyotp

                # Читаем секретный ключ
                with open("2fa_secret.key", "r") as f:
                    secret_key = f.read().strip()

                # Проверяем код
                totp = pyotp.TOTP(secret_key)
                if totp.verify(code):
                    twofa_window.destroy()
                    self.success_unlock()
                else:
                    self.shake_widget(code_entry)
                    code_entry.delete(0, "end")
                    messagebox.showerror("Ошибка", "Неверный код аутентификации")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при проверке 2FA: {e}")

        # Привязываем Enter к проверке кода
        code_entry.bind("<Return>", lambda event: verify_2fa())

        # Кнопки
        button_frame = ctk.CTkFrame(twofa_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0)

        ctk.CTkButton(
            button_frame,
            text="Подтвердить",
            width=120,
            height=35,
            font=DesignSystem.get_button_font(),
            fg_color=DesignSystem.PRIMARY_COLOR,
            hover_color="#1565C0",
            command=verify_2fa
        ).grid(row=0, column=0, padx=(0, 10))

        ctk.CTkButton(
            button_frame,
            text="Отмена",
            width=80,
            height=35,
            font=DesignSystem.get_button_font(),
            fg_color="#9E9E9E",
            hover_color="#757575",
            command=twofa_window.destroy
        ).grid(row=0, column=1)

    def success_unlock(self):
        """Вызывается при успешной разблокировке."""
        self.window.destroy()
        self.on_success()

    def shake_widget(self, widget):
        """Создает эффект тряски для виджета при ошибке."""
        original_x = widget.winfo_x()

        def shake_step(step):
            if step < 10:
                # Смещаем виджет влево-вправо
                offset = 5 if step % 2 == 0 else -5
                try:
                    widget.place(x=original_x + offset, y=widget.winfo_y())
                    self.window.after(50, lambda: shake_step(step + 1))
                except:
                    pass
            else:
                # Возвращаем в исходное положение
                try:
                    widget.place(x=original_x, y=widget.winfo_y())
                    # Возвращаем к grid управлению
                    widget.place_forget()
                except:
                    pass

        # Запускаем анимацию тряски
        shake_step(0)

    def default_cancel(self):
        """Стандартное действие при отмене - выход из приложения."""
        self.parent.quit()
        self.parent.destroy()

    def on_close(self):
        """Обрабатывает закрытие окна."""
        self.window.destroy()
        self.on_cancel()


# Дополнительный класс для более расширенного окна разблокировки
class AdvancedUnlockWindow(UnlockWindow):
    """Расширенная версия окна разблокировки с дополнительными функциями."""

    def setup_ui(self):
        """Создает расширенный интерфейс окна разблокировки."""
        super().setup_ui()

        # Добавляем индикатор попыток входа
        self.on_close()