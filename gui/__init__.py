from customtkinter import ThemeManager


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

    # Применяем тему приложения, передавая корневое окно
    ThemeManager.setup_theme(root)

    # ... остальной код без изменений
