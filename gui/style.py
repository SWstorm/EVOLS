import tkinter as tk
from tkinter import ttk, font
import os
import platform


class AppStyle:
    # Основные цвета приложения
    PRIMARY_COLOR = "#1976D2"  # Синий
    SECONDARY_COLOR = "#388E3C"  # Зеленый
    BG_COLOR = "#f5f5f5"  # Светло-серый фон
    ACCENT_COLOR = "#FF4081"  # Розовый акцент
    WARNING_COLOR = "#ff6b6b"  # Красный для предупреждений

    # Текстовые цвета
    TEXT_COLOR = "#333333"  # Темно-серый для текста
    TEXT_LIGHT = "#757575"  # Светло-серый для вторичного текста

    # Размеры шрифтов
    FONT_SMALL = 9
    FONT_NORMAL = 10
    FONT_LARGE = 12
    FONT_HEADER = 14

    @staticmethod
    def apply(root):
        """Применяет стили к корневому окну и всем виджетам."""
        # Настройка шрифтов
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI" if platform.system() == "Windows" else "Helvetica",
                               size=AppStyle.FONT_NORMAL)

        text_font = font.nametofont("TkTextFont")
        text_font.configure(family="Segoe UI" if platform.system() == "Windows" else "Helvetica",
                            size=AppStyle.FONT_NORMAL)

        # Настройка стилей ttk
        style = ttk.Style()

        # Настройка темы
        if platform.system() == "Windows":
            style.theme_use('vista')
        else:
            style.theme_use('clam')

        # Настройка Notebook (вкладки)
        style.configure("TNotebook", background=AppStyle.BG_COLOR)
        style.configure("TNotebook.Tab", background=AppStyle.BG_COLOR, foreground=AppStyle.TEXT_COLOR,
                        padding=[10, 5], font=(None, AppStyle.FONT_NORMAL))
        style.map("TNotebook.Tab", background=[("selected", AppStyle.PRIMARY_COLOR)],
                  foreground=[("selected", "white")])

        # Настройка Button
        style.configure("TButton", background=AppStyle.PRIMARY_COLOR, foreground="white",
                        padding=[10, 5], font=(None, AppStyle.FONT_NORMAL))
        style.map("TButton", background=[("active", AppStyle.PRIMARY_COLOR), ("pressed", "#0D47A1")])

        # Зеленая кнопка
        style.configure("Green.TButton", background=AppStyle.SECONDARY_COLOR, foreground="white")
        style.map("Green.TButton", background=[("active", AppStyle.SECONDARY_COLOR), ("pressed", "#1B5E20")])

        # Красная кнопка
        style.configure("Red.TButton", background=AppStyle.WARNING_COLOR, foreground="white")
        style.map("Red.TButton", background=[("active", AppStyle.WARNING_COLOR), ("pressed", "#C62828")])

        # Настройка Entry
        style.configure("TEntry", padding=[5, 3], borderwidth=1, relief="solid")

        # Настройка Frame
        style.configure("TFrame", background=AppStyle.BG_COLOR)

        # Настройка Label
        style.configure("TLabel", background=AppStyle.BG_COLOR, foreground=AppStyle.TEXT_COLOR,
                        font=(None, AppStyle.FONT_NORMAL))

        # Заголовок
        style.configure("Header.TLabel", font=(None, AppStyle.FONT_HEADER, "bold"))

        # Вторичный текст
        style.configure("Secondary.TLabel", foreground=AppStyle.TEXT_LIGHT)

        # Настройка корневого окна
        root.configure(background=AppStyle.BG_COLOR)

        return style
