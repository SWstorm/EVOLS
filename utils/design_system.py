import customtkinter as ctk


class DesignSystem:
    """Профессиональная система дизайна для приложения"""

    # === ЦВЕТОВАЯ ПАЛИТРА ===
    # Основные цвета
    PRIMARY = "#2563EB"  # Основной синий
    PRIMARY_HOVER = "#1D4ED8"  # Синий при наведении
    PRIMARY_LIGHT = "#DBEAFE"  # Светлый синий для фона

    # Вторичные цвета
    SECONDARY = "#64748B"  # Серый для текста
    SECONDARY_LIGHT = "#F1F5F9"  # Светло-серый фон

    # Семантические цвета
    SUCCESS = "#10B981"  # Зеленый успех
    SUCCESS_HOVER = "#059669"
    WARNING = "#F59E0B"  # Оранжевый предупреждение
    WARNING_HOVER = "#D97706"
    DANGER = "#EF4444"  # Красный опасность
    DANGER_HOVER = "#DC2626"

    # Нейтральные цвета
    WHITE = "#FFFFFF"
    GRAY_50 = "#F9FAFB"
    GRAY_100 = "#F3F4F6"
    GRAY_200 = "#E5E7EB"
    GRAY_300 = "#D1D5DB"
    GRAY_400 = "#9CA3AF"
    GRAY_500 = "#6B7280"
    GRAY_600 = "#4B5563"
    GRAY_700 = "#374151"
    GRAY_800 = "#1F2937"
    GRAY_900 = "#111827"

    # === ТИПОГРАФИКА ===
    FONT_FAMILY = "Arial"  # Безопасный шрифт

    # Размеры шрифтов (используем систему 8pt grid)
    TEXT_XS = 10  # Очень мелкий текст
    TEXT_SM = 12  # Мелкий текст
    TEXT_BASE = 14  # Основной текст
    TEXT_LG = 16  # Крупный текст
    TEXT_XL = 18  # Очень крупный текст
    TEXT_2XL = 24  # Заголовки
    TEXT_3XL = 30  # Крупные заголовки

    # === ОТСТУПЫ И РАЗМЕРЫ (8pt grid system) ===
    SPACE_1 = 4  # 0.25rem
    SPACE_2 = 8  # 0.5rem
    SPACE_3 = 12  # 0.75rem
    SPACE_4 = 16  # 1rem
    SPACE_5 = 20  # 1.25rem
    SPACE_6 = 24  # 1.5rem
    SPACE_8 = 32  # 2rem
    SPACE_10 = 40  # 2.5rem
    SPACE_12 = 48  # 3rem
    SPACE_16 = 64  # 4rem
    SPACE_20 = 80  # 5rem

    # === АЛИАСЫ ДЛЯ СОВМЕСТИМОСТИ (ПОСЛЕ определения SPACE_*) ===
    PADDING_SMALL = SPACE_2
    PADDING_NORMAL = SPACE_4
    PADDING_LARGE = SPACE_8

    PRIMARY_COLOR = PRIMARY
    SUCCESS_COLOR = SUCCESS
    WARNING_COLOR = DANGER

    # === РАЗМЕРЫ КОМПОНЕНТОВ ===
    BUTTON_HEIGHT_SM = 32
    BUTTON_HEIGHT_MD = 40
    BUTTON_HEIGHT_LG = 48

    INPUT_HEIGHT = 40

    BORDER_RADIUS_SM = 6
    BORDER_RADIUS_MD = 8
    BORDER_RADIUS_LG = 12

    # === РАЗМЕРЫ ОКОН ===
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600
    DIALOG_WIDTH = 500
    DIALOG_HEIGHT = 400

    @classmethod
    def get_normal_font(cls):
        """Шрифт для обычного текста"""
        return cls.get_body_font()

    @classmethod
    def setup_theme(cls, root=None):
        """Настройка глобальной темы приложения"""
        ctk.set_appearance_mode("light")  # Светлая тема для профессионального вида
        ctk.set_default_color_theme("blue")

        if root:
            # Настройка шрифтов по умолчанию (безопасная версия)
            try:
                root.option_add("*Font", f"{cls.FONT_FAMILY} {cls.TEXT_BASE}")
            except Exception:
                pass  # Игнорируем ошибки настройки шрифтов

    @classmethod
    def get_font(cls, size=None, weight="normal"):
        """Получить объект шрифта с обработкой ошибок"""
        size = size or cls.TEXT_BASE

        # Пробуем создать шрифт
        try:
            return ctk.CTkFont(family=cls.FONT_FAMILY, size=size, weight=weight)
        except Exception:
            try:
                return ctk.CTkFont(size=size, weight=weight)
            except Exception:
                return None

    @classmethod
    def get_title_font(cls, size=None):
        """Шрифт для заголовков"""
        size = size or cls.TEXT_2XL
        return cls.get_font(size, "bold")

    @classmethod
    def get_subtitle_font(cls):
        """Шрифт для подзаголовков"""
        return cls.get_font(cls.TEXT_LG, "normal")

    @classmethod
    def get_body_font(cls):
        """Шрифт для основного текста"""
        return cls.get_font(cls.TEXT_BASE, "normal")

    @classmethod
    def get_caption_font(cls):
        """Шрифт для подписей"""
        return cls.get_font(cls.TEXT_SM, "normal")

    @classmethod
    def get_button_font(cls):
        """Шрифт для кнопок"""
        return cls.get_font(cls.TEXT_BASE, "bold")


class UIComponents:
    """Переиспользуемые UI компоненты"""

    @staticmethod
    def create_primary_button(parent, text, command=None, width=None):
        """Создает основную кнопку"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width or 140,
            height=DesignSystem.BUTTON_HEIGHT_MD,
            font=DesignSystem.get_button_font(),
            fg_color=DesignSystem.PRIMARY,
            hover_color=DesignSystem.PRIMARY_HOVER,
            corner_radius=DesignSystem.BORDER_RADIUS_MD
        )

    @staticmethod
    def create_secondary_button(parent, text, command=None, width=None):
        """Создает вторичную кнопку"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width or 100,
            height=DesignSystem.BUTTON_HEIGHT_MD,
            font=DesignSystem.get_button_font(),
            fg_color=DesignSystem.GRAY_200,
            hover_color=DesignSystem.GRAY_300,
            text_color=DesignSystem.GRAY_700,
            corner_radius=DesignSystem.BORDER_RADIUS_MD
        )

    @staticmethod
    def create_danger_button(parent, text, command=None, width=None):
        """Создает кнопку опасного действия"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width or 120,
            height=DesignSystem.BUTTON_HEIGHT_MD,
            font=DesignSystem.get_button_font(),
            fg_color=DesignSystem.DANGER,
            hover_color=DesignSystem.DANGER_HOVER,
            corner_radius=DesignSystem.BORDER_RADIUS_MD
        )

    @staticmethod
    def create_input_field(parent, placeholder="", width=None, show=None):
        """Создает поле ввода"""
        return ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            width=width or 300,
            height=DesignSystem.INPUT_HEIGHT,
            font=DesignSystem.get_body_font(),
            show=show,
            corner_radius=DesignSystem.BORDER_RADIUS_MD
        )

    @staticmethod
    def create_card(parent):
        """Создает карточку для группировки контента"""
        return ctk.CTkFrame(
            parent,
            corner_radius=DesignSystem.BORDER_RADIUS_LG
        )

    @staticmethod
    def create_section_title(parent, text):
        """Создает заголовок секции"""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=DesignSystem.get_title_font()
        )

    @staticmethod
    def create_subtitle(parent, text):
        """Создает подзаголовок"""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=DesignSystem.get_subtitle_font()
        )

    @staticmethod
    def create_body_text(parent, text):
        """Создает основной текст"""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=DesignSystem.get_body_font()
        )

    @staticmethod
    def create_caption(parent, text):
        """Создает текст-подпись"""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=DesignSystem.get_caption_font()
        )


# Для обратной совместимости со старым кодом
class ThemeManager:
    """Класс для обратной совместимости с предыдущим кодом"""

    # Основные цвета
    PRIMARY_COLOR = DesignSystem.PRIMARY
    SECONDARY_COLOR = DesignSystem.SECONDARY
    SUCCESS_COLOR = DesignSystem.SUCCESS
    WARNING_COLOR = DesignSystem.DANGER
    BG_COLOR = DesignSystem.GRAY_50

    # Отступы
    PADDING_SMALL = DesignSystem.SPACE_2
    PADDING_NORMAL = DesignSystem.SPACE_4
    PADDING_LARGE = DesignSystem.SPACE_8

    # Размеры окон
    WINDOW_WIDTH = DesignSystem.WINDOW_WIDTH
    WINDOW_HEIGHT = DesignSystem.WINDOW_HEIGHT
    DIALOG_WIDTH = DesignSystem.DIALOG_WIDTH
    DIALOG_HEIGHT = DesignSystem.DIALOG_HEIGHT

    @classmethod
    def setup_theme(cls, root=None):
        """Настройка темы приложения"""
        return DesignSystem.setup_theme(root)

    @classmethod
    def get_title_font(cls):
        """Шрифт для заголовков"""
        return DesignSystem.get_title_font()

    @classmethod
    def get_normal_font(cls):
        """Шрифт для обычного текста"""
        return DesignSystem.get_body_font()

    @classmethod
    def get_button_font(cls):
        """Шрифт для кнопок"""
        return DesignSystem.get_button_font()
