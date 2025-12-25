import sqlite3
import json
from datetime import datetime


class PasswordDatabase:
    def __init__(self, db_path, encryptor):
        """Инициализация базы данных."""
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.encryptor = encryptor
        self._create_tables()

    def _create_tables(self):
        """Создает таблицы в базе данных, если они не существуют."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            username TEXT,
            password TEXT NOT NULL,
            url TEXT,
            category TEXT,
            notes TEXT,
            date_created TEXT,
            date_modified TEXT
        )
        ''')
        self.conn.commit()

    def add_password(self, title, username, password, url="", category="", notes=""):
        """Добавляет новый пароль в базу данных."""
        encrypted_password = self.encryptor.encrypt(password)
        encrypted_username = self.encryptor.encrypt(username) if username else ""
        encrypted_notes = self.encryptor.encrypt(notes) if notes else ""

        self.cursor.execute('''
        INSERT INTO passwords (title, username, password, url, category, notes, date_created, date_modified)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ''', (title, encrypted_username, encrypted_password, url, category, encrypted_notes))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_password(self, id):
        """Получает пароль по ID с расшифровкой."""
        self.cursor.execute("SELECT * FROM passwords WHERE id=?", (id,))
        row = self.cursor.fetchone()
        if row:
            row_dict = {
                'id': row[0],
                'title': row[1],
                'username': self.encryptor.decrypt(row[2]) if row[2] else "",
                'password': self.encryptor.decrypt(row[3]),
                'url': row[4],
                'category': row[5],
                'notes': self.encryptor.decrypt(row[6]) if row[6] else "",
                'date_created': row[7],
                'date_modified': row[8]
            }
            return row_dict
        return None

    def get_all_passwords(self):
        """Получает список всех паролей (без расшифровки для производительности)."""
        self.cursor.execute("SELECT id, title, category FROM passwords ORDER BY title")
        return self.cursor.fetchall()

    def update_password(self, id, title, username, password, url, category, notes):
        """Обновляет существующий пароль."""
        encrypted_password = self.encryptor.encrypt(password)
        encrypted_username = self.encryptor.encrypt(username) if username else ""
        encrypted_notes = self.encryptor.encrypt(notes) if notes else ""

        self.cursor.execute('''
        UPDATE passwords 
        SET title=?, username=?, password=?, url=?, category=?, notes=?, date_modified=datetime('now')
        WHERE id=?
        ''', (title, encrypted_username, encrypted_password, url, category, encrypted_notes, id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_password(self, password_id):
        """Удаляет пароль из базы данных по его ID."""
        try:
            self.cursor.execute("DELETE FROM passwords WHERE id=?", (password_id,))
            rows_affected = self.cursor.rowcount
            self.conn.commit()
            return rows_affected > 0
        except Exception as e:
            print(f"Ошибка при удалении пароля: {e}")
            return False

    def search_passwords(self, query):
        """Поиск паролей по названию, URL или категории."""
        search_query = f"%{query}%"
        self.cursor.execute('''
        SELECT id, title, category, url 
        FROM passwords 
        WHERE title LIKE ? OR url LIKE ? OR category LIKE ?
        ORDER BY title
        ''', (search_query, search_query, search_query))
        return self.cursor.fetchall()

    def get_passwords_by_category(self, category):
        """Получает все пароли определенной категории."""
        self.cursor.execute('''
        SELECT id, title, category 
        FROM passwords 
        WHERE category=?
        ORDER BY title
        ''', (category,))
        return self.cursor.fetchall()

    def get_all_categories(self):
        """Получает список всех уникальных категорий."""
        self.cursor.execute("SELECT DISTINCT category FROM passwords WHERE category != '' ORDER BY category")
        return [row[0] for row in self.cursor.fetchall()]

    def password_exists(self, title):
        """Проверяет, существует ли пароль с данным названием."""
        self.cursor.execute("SELECT COUNT(*) FROM passwords WHERE title=?", (title,))
        return self.cursor.fetchone()[0] > 0

    def get_password_count(self):
        """Возвращает общее количество паролей в базе."""
        self.cursor.execute("SELECT COUNT(*) FROM passwords")
        return self.cursor.fetchone()[0]

    def get_statistics(self):
        """Возвращает статистику по базе паролей."""
        stats = {}
        stats['total'] = self.get_password_count()

        # Количество по категориям
        self.cursor.execute('''
        SELECT category, COUNT(*) 
        FROM passwords 
        WHERE category != ''
        GROUP BY category
        ORDER BY COUNT(*) DESC
        ''')
        stats['by_category'] = dict(self.cursor.fetchall())

        # Количество без категории
        self.cursor.execute("SELECT COUNT(*) FROM passwords WHERE category = '' OR category IS NULL")
        stats['uncategorized'] = self.cursor.fetchone()[0]

        return stats

    def export_to_json(self, output_file, include_passwords=False):
        """Экспортирует базу данных в JSON файл."""
        self.cursor.execute("SELECT id FROM passwords")
        all_ids = [row[0] for row in self.cursor.fetchall()]

        export_data = []
        for pwd_id in all_ids:
            pwd_data = self.get_password(pwd_id)
            if not include_passwords:
                pwd_data['password'] = '***HIDDEN***'
            export_data.append(pwd_data)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return len(export_data)

    def import_from_json(self, input_file):
        """Импортирует пароли из JSON файла."""
        with open(input_file, 'r', encoding='utf-8') as f:
            import_data = json.load(f)

        imported_count = 0
        for item in import_data:
            try:
                if item.get('password') == '***HIDDEN***':
                    continue

                self.add_password(
                    title=item.get('title', 'Без названия'),
                    username=item.get('username', ''),
                    password=item.get('password', ''),
                    url=item.get('url', ''),
                    category=item.get('category', ''),
                    notes=item.get('notes', '')
                )
                imported_count += 1
            except Exception as e:
                print(f"Ошибка импорта записи '{item.get('title', 'Unknown')}': {e}")
                continue

        return imported_count

    def backup_database(self, backup_path):
        """Создает резервную копию базы данных."""
        try:
            backup_conn = sqlite3.connect(backup_path)
            self.conn.backup(backup_conn)
            backup_conn.close()
            return True
        except Exception as e:
            print(f"Ошибка создания резервной копии: {e}")
            return False

    def close(self):
        """Закрывает соединение с базой данных."""
        if self.conn:
            self.conn.close()
