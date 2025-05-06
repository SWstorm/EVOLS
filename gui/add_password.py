# Исправленный файл gui/add_password.py с использованием customtkinter
import os
import customtkinter as ctk
from tkinter import messagebox

from utils.password_generator import generate_password


class AddPasswordWindow:
    def __init__(self, parent, db, encryptor, main_window):
        self.title_entry = None
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Добавить пароль")
        self.window.geometry("500x550")

        # Центрирование окна относительно родителя
        self.window.transient(parent)
        self.window.grab_set()

        self.db = db
        self.encryptor = encryptor
        self.main_window = main_window

        self.setup_ui()

    def setup_ui(self):
        # Создаем поля ввода
        ctk.CTkLabel(self.window, text="Название:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.title_entry = ctk.CTkEntry(self.window, width=300)
        self.title_entry.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(self.window, text="Логин:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.username_entry = ctk.CTkEntry(self.window, width=300)
        self.username_entry.grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(self.window, text="Пароль:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.password_entry = ctk.CTkEntry(self.window, width=300, show="*")
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)

        # Кнопка для генерации пароля
        ctk.CTkButton(self.window, text="Сгенерировать", command=self.generate_password).grid(
            row=2, column=2, padx=5, pady=5)

        ctk.CTkLabel(self.window, text="URL:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.url_entry = ctk.CTkEntry(self.window, width=300)
        self.url_entry.grid(row=3, column=1, padx=10, pady=5)

        ctk.CTkLabel(self.window, text="Категория:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.category_entry = ctk.CTkEntry(self.window, width=300)
        self.category_entry.grid(row=4, column=1, padx=10, pady=5)

        ctk.CTkLabel(self.window, text="Заметки:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.notes_text = ctk.CTkTextbox(self.window, width=300, height=100)
        self.notes_text.grid(row=5, column=1, padx=10, pady=5)

        # Фрейм для отображения надежности пароля
        self.strength_frame = ctk.CTkFrame(self.window)
        self.strength_frame.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Отслеживаем изменения в поле пароля
        self.password_var = ctk.StringVar()
        self.password_entry.configure(textvariable=self.password_var)
        self.password_var.trace_add("write", self.check_password_on_change)

        # Кнопки сохранения и отмены
        button_frame = ctk.CTkFrame(self.window)
        button_frame.grid(row=7, column=0, columnspan=3, pady=15)

        ctk.CTkButton(button_frame, text="Сохранить", command=self.save_password).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Отмена", command=self.window.destroy).pack(side="left", padx=10)

    def generate_password(self):
        """Генерирует пароль и вставляет его в поле ввода."""
        password = generate_password()
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, password)

    def check_password_on_change(self, *args):
        """Проверяет надежность пароля при изменении поля ввода."""
        password = self.password_var.get()

        # Очищаем фрейм
        for widget in self.strength_frame.winfo_children():
            widget.destroy()

        if password:
            from utils.password_strength import PasswordStrength
            common_passwords_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                 "data", "common-passwords.txt")
            checker = PasswordStrength(common_passwords_file)
            result = checker.check_password(password)

            # Отображаем результат
            ctk.CTkLabel(self.strength_frame, text=f"Надежность: {result['strength']}",
                         font=("Arial", 10, "bold")).pack(anchor="w")

            # Добавляем прогресс-бар
            self.create_strength_progress_bar(self.strength_frame, result['score'])

            # Отображаем рекомендации
            if result['feedback']:
                ctk.CTkLabel(self.strength_frame, text="Рекомендации:",
                             font=("Arial", 10)).pack(anchor="w", pady=(10, 0))
                for feedback in result['feedback']:
                    ctk.CTkLabel(self.strength_frame, text=f"• {feedback}",
                                 font=("Arial", 9)).pack(anchor="w")

    def create_strength_progress_bar(self, parent, score):
        """Создает визуальный индикатор надежности пароля."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=5)

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
        progress.set(score / 100)  # Устанавливаем значение (от 0 до 1)

        # Задаем цвет полоски прогресса
        progress.configure(progress_color=color)

        # Добавляем текст с процентами
        ctk.CTkLabel(frame, text=f"{score}%", font=("Arial", 10)).pack(side="left")

        return frame

    def save_password(self):
        """Сохраняет пароль в базу данных."""
        title = self.title_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        url = self.url_entry.get()
        category = self.category_entry.get()
        notes = self.notes_text.get("1.0", "end").strip()

        if not title or not password:
            messagebox.showerror("Ошибка", "Название и пароль обязательны!")
            return

        try:
            self.db.add_password(title, username, password, url, category, notes)
            self.main_window.load_passwords()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить пароль: {e}")
