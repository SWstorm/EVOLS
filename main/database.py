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
        self._upgrade_database()  # Автоматическое обновление структуры


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
            date_modified TEXT,
            folder TEXT DEFAULT NULL
        )
        ''')
        self.conn.commit()


    def _upgrade_database(self):
        """Обновляет структуру базы данных (добавляет новые поля)."""
        try:
            # Проверяем наличие колонки folder
            self.cursor.execute("PRAGMA table_info(passwords)")
            columns = [column[1] for column in self.cursor.fetchall()]

            if 'folder' not in columns:
                print("📁 Добавление колонки 'folder' в таблицу passwords...")
                self.cursor.execute("ALTER TABLE passwords ADD COLUMN folder TEXT DEFAULT NULL")
                self.conn.commit()
                print("✅ Колонка 'folder' успешно добавлена!")
        except Exception as e:
            print(f"⚠️ Ошибка при обновлении структуры БД: {e}")


    def add_password(self, title, username, password, url="", category="", notes="", folder=None):
        """Добавляет новый пароль в базу данных с поддержкой папок."""
        encrypted_password = self.encryptor.encrypt(password)
        encrypted_username = self.encryptor.encrypt(username) if username else ""
        encrypted_notes = self.encryptor.encrypt(notes) if notes else ""

        self.cursor.execute('''
        INSERT INTO passwords (title, username, password, url, category, notes, folder, date_created, date_modified)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ''', (title, encrypted_username, encrypted_password, url, category, encrypted_notes, folder))
        self.conn.commit()
        return self.cursor.lastrowid


    def get_password(self, id):
        """Получает пароль по ID с расшифровкой и поддержкой папок."""
        try:
            # Проверяем наличие колонки folder
            self.cursor.execute("PRAGMA table_info(passwords)")
            columns = [column[1] for column in self.cursor.fetchall()]

            if 'folder' in columns:
                self.cursor.execute("SELECT * FROM passwords WHERE id=?", (id,))
                row = self.cursor.fetchone()

                if row:
                    return {
                        'id': row[0],
                        'title': row[1],
                        'username': self.encryptor.decrypt(row[2]) if row[2] else "",
                        'password': self.encryptor.decrypt(row[3]),
                        'url': row[4],
                        'category': row[5],
                        'notes': self.encryptor.decrypt(row[6]) if row[6] else "",
                        'date_created': row[7],
                        'date_modified': row[8],
                        'folder': row[9] if len(row) > 9 else None
                    }
            else:
                # Старая структура без folder
                self.cursor.execute("SELECT * FROM passwords WHERE id=?", (id,))
                row = self.cursor.fetchone()

                if row:
                    return {
                        'id': row[0],
                        'title': row[1],
                        'username': self.encryptor.decrypt(row[2]) if row[2] else "",
                        'password': self.encryptor.decrypt(row[3]),
                        'url': row[4],
                        'category': row[5],
                        'notes': self.encryptor.decrypt(row[6]) if row[6] else "",
                        'date_created': row[7],
                        'date_modified': row[8],
                        'folder': None
                    }
        except Exception as e:
            print(f"Ошибка при получении пароля: {e}")
            raise

        return None


    def get_all_passwords(self):
        """Получает список всех паролей с поддержкой папок (без расшифровки для производительности)."""
        try:
            # Проверяем наличие колонки folder
            self.cursor.execute("PRAGMA table_info(passwords)")
            columns = [column[1] for column in self.cursor.fetchall()]

            if 'folder' in columns:
                self.cursor.execute("SELECT id, title, category, username, password, url, folder FROM passwords ORDER BY title")
            else:
                # Возвращаем NULL вместо folder если колонки нет
                self.cursor.execute("SELECT id, title, category, username, password, url, NULL as folder FROM passwords ORDER BY title")

            return self.cursor.fetchall()

        except Exception as e:
            print(f"⚠️ Ошибка при получении паролей: {e}")
            # Возвращаем минимальную структуру
            self.cursor.execute("SELECT id, title, category FROM passwords ORDER BY title")
            return self.cursor.fetchall()


    def update_password(self, id, title, username, password, url, category, notes, folder=None):
        """Обновляет существующий пароль с поддержкой папок."""
        encrypted_password = self.encryptor.encrypt(password)
        encrypted_username = self.encryptor.encrypt(username) if username else ""
        encrypted_notes = self.encryptor.encrypt(notes) if notes else ""

        try:
            # Проверяем наличие колонки folder
            self.cursor.execute("PRAGMA table_info(passwords)")
            columns = [column[1] for column in self.cursor.fetchall()]

            if 'folder' in columns:
                self.cursor.execute('''
                UPDATE passwords 
                SET title=?, username=?, password=?, url=?, category=?, notes=?, folder=?, date_modified=datetime('now')
                WHERE id=?
                ''', (title, encrypted_username, encrypted_password, url, category, encrypted_notes, folder, id))
            else:
                # Обновление без folder
                self.cursor.execute('''
                UPDATE passwords 
                SET title=?, username=?, password=?, url=?, category=?, notes=?, date_modified=datetime('now')
                WHERE id=?
                ''', (title, encrypted_username, encrypted_password, url, category, encrypted_notes, id))

            self.conn.commit()
            return self.cursor.rowcount > 0

        except Exception as e:
            print(f"Ошибка при обновлении пароля: {e}")
            self.conn.rollback()
            return False


    def update_password_folder(self, password_id, folder_name):
        """
        Обновляет папку для конкретного пароля.

        Args:
            password_id: ID пароля
            folder_name: Название папки (или None для удаления из папки)
        """
        try:
            # Проверяем наличие колонки folder
            self.cursor.execute("PRAGMA table_info(passwords)")
            columns = [column[1] for column in self.cursor.fetchall()]

            if 'folder' not in columns:
                print("📁 Добавление колонки 'folder'...")
                self.cursor.execute("ALTER TABLE passwords ADD COLUMN folder TEXT DEFAULT NULL")
                self.conn.commit()

            # Обновляем папку
            self.cursor.execute(
                "UPDATE passwords SET folder = ?, date_modified = datetime('now') WHERE id = ?",
                (folder_name, password_id)
            )
            self.conn.commit()
            print(f"✅ Пароль #{password_id} перемещён в папку '{folder_name}'")
            return True

        except Exception as e:
            print(f"❌ Ошибка при обновлении папки: {e}")
            self.conn.rollback()
            return False


    def rename_password_folder(self, old_name, new_name):
        """
        Переименовывает папку у всех паролей.

        Args:
            old_name: Старое название папки
            new_name: Новое название папки
        """
        try:
            self.cursor.execute(
                "UPDATE passwords SET folder = ? WHERE folder = ?",
                (new_name, old_name)
            )
            self.conn.commit()

            affected = self.cursor.rowcount
            print(f"✅ Папка '{old_name}' переименована в '{new_name}'. Обновлено паролей: {affected}")
            return True

        except Exception as e:
            print(f"❌ Ошибка при переименовании папки: {e}")
            self.conn.rollback()
            return False


    def move_passwords_from_folder(self, folder_name, new_folder=None):
        """
        Перемещает все пароли из удаляемой папки в другую папку.

        Args:
            folder_name: Имя удаляемой папки
            new_folder: Новая папка (если None, пароли переместятся в корень)
        """
        try:
            self.cursor.execute(
                "UPDATE passwords SET folder = ? WHERE folder = ?",
                (new_folder, folder_name)
            )
            self.conn.commit()

            affected = self.cursor.rowcount
            target = new_folder if new_folder else "корневую папку"
            print(f"✅ Перемещено {affected} паролей из '{folder_name}' в {target}")
            return True

        except Exception as e:
            print(f"❌ Ошибка при перемещении паролей: {e}")
            self.conn.rollback()
            return False


    def get_passwords_by_folder(self, folder_name):
        """
        Получает все пароли из конкретной папки.

        Args:
            folder_name: Название папки (или None для паролей без папки)
        """
        try:
            if folder_name is None:
                self.cursor.execute(
                    "SELECT id, title, category FROM passwords WHERE folder IS NULL ORDER BY title"
                )
            else:
                self.cursor.execute(
                    "SELECT id, title, category FROM passwords WHERE folder = ? ORDER BY title",
                    (folder_name,)
                )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении паролей из папки: {e}")
            return []


    def get_folder_statistics(self):
        """Возвращает статистику по папкам."""
        try:
            self.cursor.execute('''
            SELECT folder, COUNT(*) 
            FROM passwords 
            GROUP BY folder
            ORDER BY COUNT(*) DESC
            ''')

            stats = {}
            for folder, count in self.cursor.fetchall():
                folder_name = folder if folder else "Без папки"
                stats[folder_name] = count

            return stats
        except Exception as e:
            print(f"Ошибка при получении статистики папок: {e}")
            return {}


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
        try:
            # Проверяем наличие колонки folder
            self.cursor.execute("PRAGMA table_info(passwords)")
            columns = [column[1] for column in self.cursor.fetchall()]

            if 'folder' in columns:
                self.cursor.execute('''
                SELECT id, title, category, url, folder 
                FROM passwords 
                WHERE title LIKE ? OR url LIKE ? OR category LIKE ?
                ORDER BY title
                ''', (search_query, search_query, search_query))
            else:
                self.cursor.execute('''
                SELECT id, title, category, url 
                FROM passwords 
                WHERE title LIKE ? OR url LIKE ? OR category LIKE ?
                ORDER BY title
                ''', (search_query, search_query, search_query))

            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при поиске паролей: {e}")
            return []


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
        """Возвращает расширенную статистику по базе паролей."""
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

        # Статистика по папкам
        stats['by_folder'] = self.get_folder_statistics()

        return stats


    def export_to_json(self, output_file, include_passwords=False):
        """Экспортирует базу данных в JSON файл с поддержкой папок."""
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
        """Импортирует пароли из JSON файла с поддержкой папок."""
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
                    notes=item.get('notes', ''),
                    folder=item.get('folder', None)  # Поддержка папок при импорте
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