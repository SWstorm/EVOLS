import sqlite3
import json


class PasswordDatabase:
    def __init__(self, db_path, encryptor):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.encryptor = encryptor
        self._create_tables()

    # ... другие методы класса ...

    def get_all_passwords(self):
        self.cursor.execute("SELECT id, title, category FROM passwords")
        return self.cursor.fetchall()

    # Добавьте метод delete_password сюда
    def delete_password(self, password_id):
        """Удаляет пароль из базы данных по его ID."""
        try:
            self.cursor.execute("DELETE FROM passwords WHERE id=?", (password_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка при удалении пароля: {e}")
            return False

    # ... другие методы класса ...

    def _create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY,
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
        encrypted_password = self.encryptor.encrypt(password)
        encrypted_username = self.encryptor.encrypt(username) if username else ""
        encrypted_notes = self.encryptor.encrypt(notes) if notes else ""

        self.cursor.execute('''
        INSERT INTO passwords (title, username, password, url, category, notes, date_created, date_modified)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ''', (title, encrypted_username, encrypted_password, url, category, encrypted_notes))
        self.conn.commit()

    def get_password(self, id):
        self.cursor.execute("SELECT * FROM passwords WHERE id=?", (id,))
        row = self.cursor.fetchone()
        if row:
            # Расшифровываем пароль и другие зашифрованные поля
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
        self.cursor.execute("SELECT id, title, category FROM passwords")
        return self.cursor.fetchall()

    def update_password(self, id, title, username, password, url, category, notes):
        encrypted_password = self.encryptor.encrypt(password)
        encrypted_username = self.encryptor.encrypt(username) if username else ""
        encrypted_notes = self.encryptor.encrypt(notes) if notes else ""

        self.cursor.execute('''
        UPDATE passwords 
        SET title=?, username=?, password=?, url=?, category=?, notes=?, date_modified=datetime('now')
        WHERE id=?
        ''', (title, encrypted_username, encrypted_password, url, category, encrypted_notes, id))
        self.conn.commit()

    def delete_password(self, password_id):
        """Удаляет пароль из базы данных по его ID."""
        try:
            self.cursor.execute("DELETE FROM passwords WHERE id=?", (password_id,))
            rows_affected = self.cursor.rowcount  # Проверяем, сколько строк было удалено
            self.conn.commit()
            return rows_affected > 0  # Возвращаем True, если хотя бы одна строка была удалена
        except Exception as e:
            print(f"Ошибка при удалении пароля: {e}")
            return False

    def close(self):
        self.conn.close()
