import customtkinter as ctk


class ThemeManager:
    # Цветовая схема
    PRIMARY_COLOR = "#1976D2"  # Основной синий
    SECONDARY_COLOR = "#FF4081"  # Акцентный розовый
    SUCCESS_COLOR = "#4CAF50"  # Зеленый для успешных операций
    WARNING_COLOR = "#ff6b6b"  # Красный для предупреждений
    BG_COLOR = "#f5f5f5"  # Светлый фон

    # Шрифты - убираем проверку на существование, которая вызывает ошибку
    FONT_FAMILY = "Helvetica"  # Безопасное значение по умолчанию
    FONT_SMALL = 12
    FONT_NORMAL = 14
    FONT_LARGE = 16
    FONT_TITLE = 20

    # Отступы
    PADDING_SMALL = 5
    PADDING_NORMAL = 10
    PADDING_LARGE = 20

    # Размеры окон
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    DIALOG_WIDTH = 500
    DIALOG_HEIGHT = 400

    @classmethod
    def setup_theme(cls, root=None):
        """Настраивает тему приложения и шрифты после создания корневого окна"""
        # Настройка внешнего вида CustomTkinter
        ctk.set_appearance_mode("System")  # Системная тема (темная/светлая)
        ctk.set_default_color_theme("blue")  # Основная цветовая тема

        # Теперь можно безопасно проверить наличие шрифта
        if root is not None:
            try:
                test_font = ctk.CTkFont(family="Roboto")
                cls.FONT_FAMILY = "Roboto"
            except:
                cls.FONT_FAMILY = "Helvetica"

    @classmethod
    def get_title_font(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=cls.FONT_TITLE, weight="bold")

    @classmethod
    def get_normal_font(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=cls.FONT_NORMAL)

    @classmethod
    def get_button_font(cls):
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=cls.FONT_NORMAL, weight="bold")
