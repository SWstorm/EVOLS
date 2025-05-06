# utils/password_strength.py
import re
import math
import os


class PasswordStrength:
    def __init__(self, common_passwords_file=None):
        self.common_passwords = set()
        if common_passwords_file and os.path.exists(common_passwords_file):
            self._load_common_passwords(common_passwords_file)

    def _load_common_passwords(self, file_path):
        """Загружает список распространенных паролей из файла."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    password = line.strip()
                    if password and not password.startswith('#'):
                        self.common_passwords.add(password.lower())
        except Exception as e:
            print(f"Ошибка при загрузке списка распространенных паролей: {e}")

    def check_password(self, password):
        """Проверяет надежность пароля и возвращает оценку от 0 до 100."""
        score = 0
        feedback = []

        # Проверка длины
        if len(password) < 8:
            feedback.append("Пароль слишком короткий (минимум 8 символов)")
        else:
            score += min(len(password) * 2, 30)  # До 30 баллов за длину

        # Проверка наличия символов разных категорий
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_digits = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[^A-Za-z0-9]', password))

        category_count = sum([has_lowercase, has_uppercase, has_digits, has_special])
        score += category_count * 10  # До 40 баллов за разнообразие символов

        if not has_lowercase:
            feedback.append("Добавьте строчные буквы")
        if not has_uppercase:
            feedback.append("Добавьте заглавные буквы")
        if not has_digits:
            feedback.append("Добавьте цифры")
        if not has_special:
            feedback.append("Добавьте специальные символы")

        # Проверка на повторяющиеся последовательности
        if re.search(r'(.)\1{2,}', password):  # Три и более одинаковых символа подряд
            score -= 15
            feedback.append("Избегайте повторяющихся символов")

        # Проверка на последовательности клавиатуры
        keyboard_sequences = ['qwerty', 'asdfgh', '123456', 'zxcvbn']
        for seq in keyboard_sequences:
            if seq in password.lower():
                score -= 15
                feedback.append("Избегайте простых последовательностей клавиатуры")
                break

        # Проверка на наличие в списке распространенных паролей
        if password.lower() in self.common_passwords:
            score -= 30
            feedback.append("Этот пароль слишком распространен")

        # Ограничиваем оценку в диапазоне от 0 до 100
        score = max(0, min(score, 100))

        # Определяем уровень надежности
        if score < 30:
            strength = "Очень слабый"
        elif score < 50:
            strength = "Слабый"
        elif score < 70:
            strength = "Средний"
        elif score < 90:
            strength = "Сильный"
        else:
            strength = "Очень сильный"

        return {
            'score': score,
            'strength': strength,
            'feedback': feedback
        }

    def calculate_entropy(self, password):
        """Рассчитывает энтропию пароля в битах."""
        charset_size = 0
        if re.search(r'[a-z]', password):
            charset_size += 26
        if re.search(r'[A-Z]', password):
            charset_size += 26
        if re.search(r'\d', password):
            charset_size += 10
        if re.search(r'[^A-Za-z0-9]', password):
            charset_size += 33  # Примерное количество специальных символов

        if charset_size == 0:
            return 0

        # Формула энтропии: log2(charset_size^length)
        entropy = len(password) * math.log2(charset_size)
        return entropy
