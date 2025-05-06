import random
import string


def generate_password(length=16, include_uppercase=True, include_digits=True, include_special=True):
    chars = string.ascii_lowercase
    if include_uppercase:
        chars += string.ascii_uppercase
    if include_digits:
        chars += string.digits
    if include_special:
        chars += string.punctuation

    # Убедимся, что пароль содержит хотя бы по одному символу из каждой группы
    password = []
    if include_uppercase:
        password.append(random.choice(string.ascii_uppercase))
    if include_digits:
        password.append(random.choice(string.digits))
    if include_special:
        password.append(random.choice(string.punctuation))

    # Добавляем остальные символы
    remaining_length = length - len(password)
    password.extend(random.choice(chars) for _ in range(remaining_length))

    # Перемешиваем пароль
    random.shuffle(password)

    return ''.join(password)
