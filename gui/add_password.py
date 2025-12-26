import customtkinter as ctk
from tkinter import messagebox
import random
import string
import re



class GlobalHotkeys:
    """Глобальные горячие клавиши для всех окон"""
    
    @staticmethod
    def setup(window):
        """Настраивает горячие клавиши для любого окна"""
        
        def select_all(event=None):
            """Ctrl+A - выделить все"""
            try:
                focused = window.focus_get()
                if focused:
                    if hasattr(focused, 'select_range'):
                        focused.select_range(0, 'end')
                        focused.icursor('end')
                    elif hasattr(focused, 'tag_add'):
                        focused.tag_add('sel', '1.0', 'end')
                        focused.mark_set('insert', 'end')
            except:
                pass
            return "break"
        
        def copy_text(event=None):
            """Ctrl+C - копировать"""
            try:
                focused = window.focus_get()
                if focused:
                    try:
                        if hasattr(focused, 'selection_get'):
                            text = focused.selection_get()
                            window.clipboard_clear()
                            window.clipboard_append(text)
                    except:
                        if hasattr(focused, 'get'):
                            try:
                                text = focused.get() if hasattr(focused, 'index') else focused.get('1.0', 'end-1c')
                                if text:
                                    window.clipboard_clear()
                                    window.clipboard_append(text)
                            except:
                                pass
            except:
                pass
            return "break"
        
        def paste_text(event=None):
            """Ctrl+V - вставить"""
            try:
                clipboard_text = window.clipboard_get()
                focused = window.focus_get()
                
                if focused and hasattr(focused, 'insert'):
                    try:
                        if hasattr(focused, 'selection_present') and focused.selection_present():
                            focused.delete('sel.first', 'sel.last')
                    except:
                        pass
                    focused.insert('insert', clipboard_text)
            except:
                pass
            return "break"
        
        def cut_text(event=None):
            """Ctrl+X - вырезать"""
            try:
                focused = window.focus_get()
                if focused:
                    try:
                        text = focused.selection_get()
                        window.clipboard_clear()
                        window.clipboard_append(text)
                        if hasattr(focused, 'delete'):
                            focused.delete('sel.first', 'sel.last')
                    except:
                        pass
            except:
                pass
            return "break"
        
        # Привязываем клавиши
        window.bind('<Control-a>', select_all)
        window.bind('<Control-A>', select_all)
        window.bind('<Control-c>', copy_text)
        window.bind('<Control-C>', copy_text)
        window.bind('<Control-v>', paste_text)
        window.bind('<Control-V>', paste_text)
        window.bind('<Control-x>', cut_text)
        window.bind('<Control-X>', cut_text)


class ModernDesign:
    """Крутая система дизайна"""

    # Цвета
    PRIMARY = "#2962FF"
    PRIMARY_DARK = "#0039CB"
    SECONDARY = "#00E5FF"
    SUCCESS = "#00E676"
    DANGER = "#FF1744"
    WARNING = "#ffba8f"

    # Фон
    BG_DARK = "#0F172A"
    BG_CARD = "#1E293B"
    BG_HOVER = "#334155"
    SIDEBAR_BG = "#1A1F36"

    # Текст
    TEXT_PRIMARY = "#F8FAFC"
    TEXT_SECONDARY = "#94A3B8"
    TEXT_MUTED = "#64748B"

    @staticmethod
    def get_title_font():
        return ("Segoe UI", 28, "bold")

    @staticmethod
    def get_subtitle_font():
        return ("Segoe UI", 16)

    @staticmethod
    def get_body_font():
        return ("Segoe UI", 12)

    @staticmethod
    def get_button_font():
        return ("Segoe UI", 13, "bold")

    @staticmethod
    def get_caption_font():
        return ("Segoe UI", 11)


class PasswordStrengthIndicator:
    """Индикатор надёжности пароля"""

    @staticmethod
    def check_strength(password):
        """Возвращает оценку и цвет"""
        if not password:
            return 0, ModernDesign.TEXT_MUTED, "Введите пароль"

        score = 0
        feedback = []

        # Длина
        if len(password) >= 8:
            score += 25
        else:
            feedback.append("минимум 8 символов")

        if len(password) >= 12:
            score += 15

        # Разнообразие символов
        if re.search(r'[a-z]', password):
            score += 15
        else:
            feedback.append("строчные буквы")

        if re.search(r'[A-Z]', password):
            score += 15
        else:
            feedback.append("заглавные буквы")

        if re.search(r'\d', password):
            score += 15
        else:
            feedback.append("цифры")

        if re.search(r'[!@#$%^&*()_+\-=\[\]{};:\',.<>?]', password):
            score += 15
        else:
            feedback.append("спецсимволы")

        # Определяем уровень
        if score < 40:
            color = ModernDesign.DANGER
            level = "Слабый"
        elif score < 70:
            color = ModernDesign.WARNING
            level = "Средний"
        else:
            color = ModernDesign.SUCCESS
            level = "Сильный"

        hint = f"{level} • Добавьте: {', '.join(feedback[:2])}" if feedback else level

        return score, color, hint


class ToastNotification:
    """Красивые toast-уведомления"""

    @staticmethod
    def show(parent, message, type="info", duration=3000):
        try:
            if not parent.winfo_exists():
                return
        except:
            return

        toast = ctk.CTkFrame(
            parent,
            fg_color=ModernDesign.BG_CARD,
            corner_radius=12,
            border_width=2
        )

        border_colors = {
            "info": ModernDesign.PRIMARY,
            "success": ModernDesign.SUCCESS,
            "error": ModernDesign.DANGER,
            "warning": ModernDesign.WARNING
        }
        toast.configure(border_color=border_colors.get(type, ModernDesign.PRIMARY))

        icons = {
            "info": "ℹ️",
            "success": "✓",
            "error": "✕",
            "warning": "⚠️"
        }

        content_frame = ctk.CTkFrame(toast, fg_color="transparent")
        content_frame.pack(padx=20, pady=15, fill="both", expand=True)

        ctk.CTkLabel(
            content_frame,
            text=icons.get(type, "ℹ️"),
            font=("Segoe UI", 20),
            text_color=border_colors.get(type, ModernDesign.PRIMARY)
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            content_frame,
            text=message,
            font=ModernDesign.get_body_font(),
            text_color=ModernDesign.TEXT_PRIMARY,
            wraplength=300
        ).pack(side="left", fill="both", expand=True)

        toast.place(relx=0.5, rely=0.1, anchor="n")
        toast.lift()

        def fade_out():
            try:
                if toast.winfo_exists():
                    toast.destroy()
            except:
                pass

        parent.after(duration, fade_out)


class AddPasswordWindow:
    def __init__(self, parent, db, encryptor, main_window):
        self.parent = parent
        self.db = db
        self.encryptor = encryptor
        self.main_window = main_window

        # Создаем окно
        self.window = ctk.CTkToplevel(parent)
        self.window.title("➕ Добавить пароль")
        self.window.geometry("600x750")
        self.window.minsize(550, 700)
        self.window.configure(fg_color=ModernDesign.BG_DARK)

        # Настройка адаптивности
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # Модальное окно
        self.window.transient(parent)
        self.window.grab_set()

        # Центрируем окно
        self.center_window()

        # Создаем интерфейс
        self.setup_ui()

    def center_window(self):
        """Центрирует окно относительно родительского окна."""
        self.window.update_idletasks()

        width = self.window.winfo_width()
        height = self.window.winfo_height()

        try:
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()

            x = parent_x + (parent_width // 2) - (width // 2)
            y = parent_y + (parent_height // 2) - (height // 2)
        except:
            x = (self.window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.window.winfo_screenheight() // 2) - (height // 2)

        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """Создает современный интерфейс окна"""
        # Основной скроллируемый контейнер
        scroll_frame = ctk.CTkScrollableFrame(
            self.window,
            fg_color="transparent"
        )
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        scroll_frame.grid_columnconfigure(0, weight=1)

        # === ЗАГОЛОВОК ===
        header_frame = ctk.CTkFrame(scroll_frame, fg_color=ModernDesign.BG_CARD, corner_radius=15)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(padx=25, pady=20)

        ctk.CTkLabel(
            header_content,
            text="➕",
            font=("Segoe UI", 48)
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            header_content,
            text="Добавить новый пароль",
            font=("Segoe UI", 24, "bold"),
            text_color=ModernDesign.TEXT_PRIMARY
        ).pack()

        ctk.CTkLabel(
            header_content,
            text="Заполните информацию о новой записи",
            font=("Segoe UI", 12),
            text_color=ModernDesign.TEXT_SECONDARY
        ).pack(pady=(5, 0))

        # === ФОРМА ===
        # Переменные для полей
        self.title_var = ctk.StringVar()
        self.username_var = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.url_var = ctk.StringVar()
        self.category_var = ctk.StringVar()

        # Индикатор надежности
        self.strength_label = ctk.CTkLabel(
            scroll_frame,
            text="",
            font=ModernDesign.get_caption_font(),
            text_color=ModernDesign.TEXT_MUTED
        )

        self.strength_bar = ctk.CTkProgressBar(
            scroll_frame,
            width=400,
            height=8,
            progress_color=ModernDesign.TEXT_MUTED
        )

        # 1. Название
        self._create_field(
            scroll_frame, 1,
            "🏷️Название*",
            self.title_var,
            "Например: Gmail, Facebook, Банк"
        )

        # 2. Логин
        self._create_field(
            scroll_frame, 2,
            "👤 Логин/Email",
            self.username_var,
            "username@example.com"
        )

        # 3. Пароль (с кнопками)
        password_card = self._create_password_field(scroll_frame, 3)

        # 4. URL
        self._create_field(
            scroll_frame, 4,
            "🌐 URL веб-сайта",
            self.url_var,
            "https://example.com"
        )

        # 5. Категория
        self._create_category_field(scroll_frame, 5)

        # 6. Заметки
        self._create_notes_field(scroll_frame, 6)

        # === ИНФОРМАЦИЯ ===
        info_frame = ctk.CTkFrame(scroll_frame, fg_color=ModernDesign.BG_HOVER, corner_radius=10)
        info_frame.grid(row=7, column=0, sticky="ew", pady=(10, 20))

        ctk.CTkLabel(
            info_frame,
            text="ℹ️ * Обязательные поля для заполнения",
            font=ModernDesign.get_caption_font(),
            text_color=ModernDesign.TEXT_SECONDARY
        ).pack(padx=15, pady=10)

        # === КНОПКИ ===
        buttons_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        buttons_frame.grid(row=8, column=0, sticky="ew", pady=(10, 0))
        buttons_frame.grid_columnconfigure((0, 1), weight=1)

        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Сохранить",
            command=self.save_password,
            font=("Segoe UI", 14, "bold"),
            height=50,
            fg_color=ModernDesign.SUCCESS,
            hover_color="#00C853",
            corner_radius=10
        )
        save_btn.grid(row=0, column=0, padx=5, sticky="ew")

        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="✕ Отмена",
            command=self.window.destroy,
            font=("Segoe UI", 14, "bold"),
            height=50,
            fg_color=ModernDesign.BG_HOVER,
            hover_color="#475569",
            corner_radius=10
        )
        cancel_btn.grid(row=0, column=1, padx=5, sticky="ew")

    def _create_field(self, parent, row, label, variable, placeholder):
        """Создаёт обычное поле ввода"""
        field_card = ctk.CTkFrame(parent, fg_color=ModernDesign.BG_CARD, corner_radius=12)
        field_card.grid(row=row, column=0, sticky="ew", pady=5)

        field_content = ctk.CTkFrame(field_card, fg_color="transparent")
        field_content.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            field_content,
            text=label,
            font=("Segoe UI", 12, "bold"),
            text_color=ModernDesign.TEXT_SECONDARY,
            anchor="w"
        ).pack(anchor="w", pady=(0, 8))

        entry = ctk.CTkEntry(
            field_content,
            textvariable=variable,
            placeholder_text=placeholder,
            height=45,
            font=("Segoe UI", 13),
            border_width=0,
            fg_color=ModernDesign.BG_HOVER,
            corner_radius=8
        )
        entry.pack(fill="x")

        return entry

    def _create_password_field(self, parent, row):
        field_card = ctk.CTkFrame(parent, fg_color=ModernDesign.BG_CARD, corner_radius=12)
        field_card.grid(row=row, column=0, sticky="ew", pady=5)

        field_content = ctk.CTkFrame(field_card, fg_color="transparent")
        field_content.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            field_content,
            text="🔑 Пароль*",
            font=("Segoe UI", 12, "bold"),
            text_color=ModernDesign.TEXT_SECONDARY,
            anchor="w"
        ).pack(anchor="w", pady=(0, 8))

        # Поле ввода + кнопка показать
        entry_container = ctk.CTkFrame(field_content, fg_color="transparent")
        entry_container.pack(fill="x")
        entry_container.grid_columnconfigure(0, weight=1)

        password_entry = ctk.CTkEntry(
            entry_container,
            textvariable=self.password_var,
            placeholder_text="Введите надёжный пароль",
            show="●",
            height=45,
            font=("Segoe UI", 13),
            border_width=0,
            fg_color=ModernDesign.BG_HOVER,
            corner_radius=8
        )
        password_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        show_btn = ctk.CTkButton(
            entry_container,
            text="",
            width=50,
            height=45,
            fg_color=ModernDesign.PRIMARY,
            hover_color=ModernDesign.PRIMARY_DARK,
            corner_radius=8
        )
        show_btn.grid(row=0, column=1)

        eye_icon = ctk.CTkLabel(
            show_btn,
            text="👁️",
            font=("Segoe UI Emoji", 22),
            text_color="white",
            fg_color="transparent",
            cursor="hand2"
        )
        eye_icon.place(relx=0.5, rely=0.48, anchor="center")

        def on_press(e):
            password_entry.configure(show='')
            show_btn.configure(fg_color=ModernDesign.PRIMARY_DARK)
            eye_icon.configure(text="👁")

        def on_release(e):
            password_entry.configure(show='●')
            show_btn.configure(fg_color=ModernDesign.PRIMARY)
            eye_icon.configure(text="👁️")

        show_btn.bind("<ButtonPress-1>", on_press)
        show_btn.bind("<ButtonRelease-1>", on_release)
        eye_icon.bind("<ButtonPress-1>", on_press)
        eye_icon.bind("<ButtonRelease-1>", on_release)

        # === ИНДИКАТОР СВЕРХУ (появляется при вводе) ===
        strength_container = ctk.CTkFrame(field_content, fg_color="transparent")
        
        self.strength_bar = ctk.CTkProgressBar(
            strength_container,
            height=4,
            progress_color=ModernDesign.TEXT_MUTED
        )
        self.strength_bar.pack(fill="x", pady=(8, 6))
        self.strength_bar.set(0)

        self.strength_label = ctk.CTkLabel(
            strength_container,
            text="",
            font=("Segoe UI", 10),
            text_color=ModernDesign.TEXT_SECONDARY,
            anchor="w"
        )
        self.strength_label.pack(anchor="w")

        self.strength_visible = False

        def on_password_change(*args):
            password = self.password_var.get()
            
            if not password:
                if self.strength_visible:
                    strength_container.pack_forget()
                    self.strength_visible = False
                return

            if not self.strength_visible:
                strength_container.pack(fill="x", pady=(8, 0))
                self.strength_visible = True

            score, color, hint = PasswordStrengthIndicator.check_strength(password)
            
            self.strength_bar.set(score / 100)
            self.strength_bar.configure(progress_color=color)
            
            if score < 40:
                level = "Слабый"
                emoji = "🔴"
            elif score < 70:
                level = "Средний"
                emoji = "🟡"
            else:
                level = "Сильный"
                emoji = "🟢"
            
            length = len(password)
            has_lower = bool(re.search(r'[a-z]', password))
            has_upper = bool(re.search(r'[A-Z]', password))
            has_digit = bool(re.search(r'\d', password))
            has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};:\',.<>?]', password))
            
            missing = []
            if length < 12: missing.append("длина")
            if not has_lower: missing.append("a-z")
            if not has_upper: missing.append("A-Z")
            if not has_digit: missing.append("0-9")
            if not has_special: missing.append("!@#")
            
            if missing:
                hint_text = f"Добавьте: {', '.join(missing)}"
            else:
                hint_text = "Отличный пароль!"
            
            self.strength_label.configure(
                text=f"{emoji} {level} • {hint_text}",
                text_color=color
            )

        self.password_var.trace("w", on_password_change)

        # === КНОПКА ГЕНЕРАЦИИ СНИЗУ ===
        buttons_container = ctk.CTkFrame(field_content, fg_color="transparent")
        buttons_container.pack(fill="x", pady=(10, 0))

        generate_btn = ctk.CTkButton(
            buttons_container,
            text="🎲 Сгенерировать надежный пароль",
            command=self.generate_password,
            font=("Segoe UI", 12, "bold"),
            height=40,
            fg_color=ModernDesign.PRIMARY,
            hover_color=ModernDesign.PRIMARY_DARK,
            corner_radius=8
        )
        generate_btn.pack(fill="x")

        return field_card




    def _create_category_field(self, parent, row):
        """Создаёт поле выбора категории"""
        field_card = ctk.CTkFrame(parent, fg_color=ModernDesign.BG_CARD, corner_radius=12)
        field_card.grid(row=row, column=0, sticky="ew", pady=5)

        field_content = ctk.CTkFrame(field_card, fg_color="transparent")
        field_content.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            field_content,
            text="📁 Категория",
            font=("Segoe UI", 12, "bold"),
            text_color=ModernDesign.TEXT_SECONDARY,
            anchor="w"
        ).pack(anchor="w", pady=(0, 8))

        categories = [
            "Работа",
            "Личное",
            "Финансы",
            "Соцсети",
            "Email",
            "Другое"
        ]

        category_combo = ctk.CTkComboBox(
            field_content,
            variable=self.category_var,
            values=categories,
            height=45,
            font=("Segoe UI", 13),
            border_width=0,
            fg_color=ModernDesign.BG_HOVER,
            button_color=ModernDesign.PRIMARY,
            button_hover_color=ModernDesign.PRIMARY_DARK,
            corner_radius=8
        )
        category_combo.pack(fill="x")
        category_combo.set("")

        return field_card

    def _create_notes_field(self, parent, row):
        """Создаёт поле для заметок"""
        field_card = ctk.CTkFrame(parent, fg_color=ModernDesign.BG_CARD, corner_radius=12)
        field_card.grid(row=row, column=0, sticky="ew", pady=5)

        field_content = ctk.CTkFrame(field_card, fg_color="transparent")
        field_content.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            field_content,
            text="📝 Заметки",
            font=("Segoe UI", 12, "bold"),
            text_color=ModernDesign.TEXT_SECONDARY,
            anchor="w"
        ).pack(anchor="w", pady=(0, 8))

        self.notes_textbox = ctk.CTkTextbox(
            field_content,
            height=100,
            font=("Segoe UI", 12),
            fg_color=ModernDesign.BG_HOVER,
            corner_radius=8
        )
        self.notes_textbox.pack(fill="x")

        return field_card

    def generate_password(self):
        """Генерирует случайный пароль"""
        length = 16
        chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-="

        password = ''.join(random.choice(chars) for _ in range(length))
        self.password_var.set(password)

        ToastNotification.show(self.window, f"Сгенерирован пароль ({length} символов)", "success")

    def test_password_strength(self):
        """Проверяет надежность пароля"""
        password = self.password_var.get()

        if not password:
            ToastNotification.show(self.window, "Сначала введите пароль", "warning")
            return

        score, color, hint = PasswordStrengthIndicator.check_strength(password)

        # Детальное сообщение
        feedback = []
        if len(password) < 8:
            feedback.append("• Увеличьте длину до 8+ символов")
        if not re.search(r'[a-z]', password):
            feedback.append("• Добавьте строчные буквы (a-z)")
        if not re.search(r'[A-Z]', password):
            feedback.append("• Добавьте заглавные буквы (A-Z)")
        if not re.search(r'\d', password):
            feedback.append("• Добавьте цифры (0-9)")
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\',.<>?]', password):
            feedback.append("• Добавьте спецсимволы (!@#$%...)")

        level = "Отличный" if score >= 80 else "Хороший" if score >= 60 else "Средний" if score >= 40 else "Слабый"

        message = f"Уровень: {level} ({score}/100)\n"
        if feedback:
            message += "\nРекомендации:\n" + "\n".join(feedback)
        else:
            message += "\n✓ Пароль надёжный!"

        messagebox.showinfo("Проверка пароля", message)

    def save_password(self):
        """Сохраняет пароль в БД"""
        title = self.title_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get()
        url = self.url_var.get().strip()
        category = self.category_var.get().strip()
        notes = self.notes_textbox.get("1.0", "end-1c").strip()

        # Валидация
        if not title:
            ToastNotification.show(self.window, "Введите название записи!", "error")
            return

        if not password:
            ToastNotification.show(self.window, "Введите пароль!", "error")
            return

        try:
            # Сохраняем
            password_id = self.db.add_password(
                title=title,
                username=username,
                password=password,
                url=url,
                category=category,
                notes=notes
            )

            ToastNotification.show(self.window, f"Пароль '{title}' сохранён!", "success")

            # Обновляем главное окно
            if hasattr(self.main_window, 'invalidate_cache'):
                self.main_window.invalidate_cache()
            if hasattr(self.main_window, 'update_header_stats'):
                self.main_window.update_header_stats()
            if hasattr(self.main_window, 'load_passwords'):
                self.main_window.load_passwords()

            # Закрываем через 500ms чтобы увидеть toast
            self.window.after(500, self.window.destroy)

        except Exception as e:
            ToastNotification.show(self.window, f"Ошибка: {e}", "error")