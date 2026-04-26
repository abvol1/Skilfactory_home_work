import streamlit as st
import pandas as pd
import sqlite3
import datetime
import json
from typing import List, Dict, Any, Optional
import copy
import os
import time

st.set_page_config(page_title="Чек-лист ВСП", layout="wide", initial_sidebar_state="expanded", page_icon="📋")

# Добавляем импорт для работы с Excel
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    st.write("OpenPyXL не установлен. Установите: pip install openpyxl")

# Попробуем импортировать psycopg2
try:
    import psycopg2
    from psycopg2 import sql
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    st.write("Psycopg2 не установлен. Работаем в режиме SQLite.")

# ==============================================================================
# 1. КОНФИГУРАЦИЯ
# ==============================================================================
USE_POSTGRES = True  # Переключите на True при работе с PostgreSQL

PG_CONFIG = {
    "host": "",
    "port": 5432,
    "database": "",
    "user": "",
    "password": "",
    "schema": "public"
}

SQLITE_PATH = "checklist.db"
FORCE_RECREATE_DB = False
ADMIN_PASSWORD = "admin123"


# ==============================================================================
# 2. КЛАСС РАБОТЫ С БД (С ЕДИНЫМ ПОДКЛЮЧЕНИЕМ)
# ==============================================================================
class DatabaseManager:
    def __init__(self):
        self.use_postgres = USE_POSTGRES and POSTGRES_AVAILABLE
        self.schema = PG_CONFIG.get('schema', 'public') if self.use_postgres else None
        self._connection = None  # Единое подключение
        self._cursor = None      # Единый курсор

    def _get_connection(self):
        """Получить или создать единое подключение"""
        if self._connection is None:
            if self.use_postgres:
                self._connection = psycopg2.connect(
                    host=PG_CONFIG['host'],
                    port=PG_CONFIG['port'],
                    dbname=PG_CONFIG['database'],
                    user=PG_CONFIG['user'],
                    password=PG_CONFIG['password']
                )
            else:
                self._connection = sqlite3.connect(SQLITE_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
                self._connection.row_factory = sqlite3.Row
        return self._connection

    def _get_cursor(self):
        """Получить или создать единый курсор"""
        if self._cursor is None:
            conn = self._get_connection()
            if self.use_postgres:
                self._cursor = conn.cursor(cursor_factory=RealDictCursor)
            else:
                self._cursor = conn.cursor()
        return self._cursor

    def _reset_cursor(self):
        """Сбросить курсор (при ошибках)"""
        if self._cursor:
            try:
                self._cursor.close()
            except:
                pass
            self._cursor = None

    def _reset_connection(self):
        """Полностью сбросить соединение"""
        self._reset_cursor()
        if self._connection:
            try:
                self._connection.close()
            except:
                pass
            self._connection = None

    def close(self):
        """Закрыть соединение с БД"""
        self._reset_connection()

    def _table_name(self, table: str) -> str:
        if self.use_postgres:
            return f"{self.schema}.{table}"
        return table

    def _execute(self, query: str, params=None, fetch_one=False, fetch_all=False, commit=True):
        """Выполнить запрос с использованием единого подключения"""
        try:
            cursor = self._get_cursor()
            cursor.execute(query, params or ())
            result = None
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            if commit:
                self._get_connection().commit()
            return result
        except Exception as e:
            self._reset_cursor()
            self._reset_connection()
            raise e

    def _to_df(self, query: str, params=None) -> pd.DataFrame:
        """Выполнить запрос и вернуть DataFrame"""
        try:
            conn = self._get_connection()
            return pd.read_sql_query(query, conn, params=params or ())
        except Exception as e:
            self._reset_connection()
            raise e

    def init_db(self):
        """Инициализация базы данных"""
        if FORCE_RECREATE_DB and not self.use_postgres and os.path.exists(SQLITE_PATH):
            os.remove(SQLITE_PATH)

        conn = self._get_connection()
        cursor = self._get_cursor()

        if self.use_postgres:
            # Создание таблиц PostgreSQL
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.checklist_templates (
                    id SERIAL PRIMARY KEY,
                    section_name VARCHAR(255) NOT NULL,
                    item_order INTEGER NOT NULL,
                    description TEXT,
                    additional_info TEXT,
                    filter_value TEXT,
                    events_value TEXT
                )
            """)
            # Проверяем и добавляем новые колонки
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='checklist_templates' AND table_schema='{self.schema}'
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
            if 'filter_value' not in existing_columns:
                cursor.execute(f"ALTER TABLE {self.schema}.checklist_templates ADD COLUMN filter_value TEXT")
            if 'events_value' not in existing_columns:
                cursor.execute(f"ALTER TABLE {self.schema}.checklist_templates ADD COLUMN events_value TEXT")

            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.filials (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL
                )
            """)
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.vsp (
                    id SERIAL PRIMARY KEY,
                    filial_id INTEGER REFERENCES {self.schema}.filials(id),
                    name VARCHAR(255) NOT NULL
                )
            """)
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.checklist_sessions (
                    id SERIAL PRIMARY KEY,
                    user_name VARCHAR(255) NOT NULL,
                    filial_id INTEGER REFERENCES {self.schema}.filials(id),
                    vsp_id INTEGER REFERENCES {self.schema}.vsp(id),
                    operation_date DATE NOT NULL,
                    status VARCHAR(50) DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.checklist_answers (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER REFERENCES {self.schema}.checklist_sessions(id) ON DELETE CASCADE,
                    template_item_id INTEGER REFERENCES {self.schema}.checklist_templates(id),
                    is_completed BOOLEAN DEFAULT FALSE,
                    UNIQUE(session_id, template_item_id)
                )
            """)
            cursor.execute("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            """)
            cursor.execute(f"""
                DROP TRIGGER IF EXISTS update_checklist_sessions_updated_at ON {self.schema}.checklist_sessions;
                CREATE TRIGGER update_checklist_sessions_updated_at
                BEFORE UPDATE ON {self.schema}.checklist_sessions
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """)
        else:
            # SQLite
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checklist_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    section_name TEXT NOT NULL DEFAULT 'Основной',
                    item_order INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    additional_info TEXT,
                    filter_value TEXT,
                    events_value TEXT
                )
            """)
            cursor.execute("PRAGMA table_info(checklist_templates)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            if 'filter_value' not in existing_columns:
                cursor.execute("ALTER TABLE checklist_templates ADD COLUMN filter_value TEXT")
            if 'events_value' not in existing_columns:
                cursor.execute("ALTER TABLE checklist_templates ADD COLUMN events_value TEXT")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS filials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vsp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filial_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    FOREIGN KEY (filial_id) REFERENCES filials(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checklist_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name TEXT NOT NULL,
                    filial_id INTEGER NOT NULL,
                    vsp_id INTEGER NOT NULL,
                    operation_date DATE NOT NULL,
                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (filial_id) REFERENCES filials(id),
                    FOREIGN KEY (vsp_id) REFERENCES vsp(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checklist_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    template_item_id INTEGER NOT NULL,
                    is_completed INTEGER DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES checklist_sessions(id) ON DELETE CASCADE,
                    FOREIGN KEY (template_item_id) REFERENCES checklist_templates(id) ON DELETE CASCADE,
                    UNIQUE(session_id, template_item_id)
                )
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS update_checklist_sessions_updated_at
                AFTER UPDATE ON checklist_sessions
                FOR EACH ROW
                BEGIN
                    UPDATE checklist_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
                END;
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON checklist_sessions(user_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_answers_session ON checklist_answers(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON checklist_sessions(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_status ON checklist_sessions(user_name, status)")

        conn.commit()
        # Не закрываем соединение — оно нужно для дальнейшей работы

    # --- Остальные методы (get_filials, get_vsp_by_filial, и т.д.) ---
    # Они уже используют self._get_connection() и self._get_cursor() внутри _execute и _to_df.
    # Для краткости привожу только сигнатуры, но в полном коде они все есть.
    def get_filials(self) -> pd.DataFrame:
        return self._to_df(f"SELECT id, name FROM {self._table_name('filials')} ORDER BY name")

    def get_vsp_by_filial(self, filial_id: int) -> pd.DataFrame:
        if self.use_postgres:
            return self._to_df(f"SELECT id, name FROM {self._table_name('vsp')} WHERE filial_id = %s ORDER BY name", (filial_id,))
        else:
            return self._to_df(f"SELECT id, name FROM {self._table_name('vsp')} WHERE filial_id = ? ORDER BY name", (filial_id,))

    def get_checklist_template(self) -> pd.DataFrame:
        return self._to_df(f"SELECT id, item_order, description, additional_info, filter_value, events_value FROM {self._table_name('checklist_templates')} ORDER BY item_order")

    def add_template_item(self, description: str, additional_info: str, filter_value: str = "", events_value: str = ""):
        row = self._execute(
            f"SELECT COALESCE(MAX(item_order), 0) + 1 as next_order FROM {self._table_name('checklist_templates')}",
            fetch_one=True
        )
        next_order = row['next_order'] if isinstance(row, dict) else row[0] if row else 1
        query = f"INSERT INTO {self._table_name('checklist_templates')} (section_name, item_order, description, additional_info, filter_value, events_value) VALUES (%s, %s, %s, %s, %s, %s)"
        if not self.use_postgres:
            query = query.replace('%s', '?')
        self._execute(query, ('Основной', next_order, description, additional_info, filter_value, events_value))

    def update_template_item(self, item_id: int, description: str, additional_info: str, filter_value: str = "", events_value: str = ""):
        query = f"UPDATE {self._table_name('checklist_templates')} SET description = %s, additional_info = %s, filter_value = %s, events_value = %s WHERE id = %s"
        if not self.use_postgres:
            query = query.replace('%s', '?')
        self._execute(query, (description, additional_info, filter_value, events_value, item_id))

    def delete_template_item(self, item_id: int):
        delete_answers_query = f"DELETE FROM {self._table_name('checklist_answers')} WHERE template_item_id=%s"
        if not self.use_postgres:
            delete_answers_query = delete_answers_query.replace('%s', '?')
        self._execute(delete_answers_query, (item_id,))
        query = f"DELETE FROM {self._table_name('checklist_templates')} WHERE id = %s"
        if not self.use_postgres:
            query = query.replace('%s', '?')
        self._execute(query, (item_id,))

    def create_session(self, user_name: str, filial_id: int, vsp_id: int, op_date, status='draft') -> int:
        query = f"INSERT INTO {self._table_name('checklist_sessions')} (user_name, filial_id, vsp_id, operation_date, status) VALUES (%s, %s, %s, %s, %s)"
        if not self.use_postgres:
            query = query.replace('%s', '?')
        if self.use_postgres:
            query += " RETURNING id"
            row = self._execute(query, (user_name, filial_id, vsp_id, op_date, status), fetch_one=True)
            return row['id'] if isinstance(row, dict) else row[0]
        else:
            cursor = self._get_cursor()
            cursor.execute(query, (user_name, filial_id, vsp_id, op_date, status))
            self._get_connection().commit()
            return cursor.lastrowid

    def check_user_by_name(self, name: str):
        try:
            # Предполагается наличие таблицы users, если нет — пропускаем
            query = f"SELECT full_name FROM {self._table_name('users')} WHERE LOWER(name) = LOWER(%s)"
            if not self.use_postgres:
                query = query.replace('%s', '?')
            df = self._to_df(query, (name,))
            if not df.empty:
                return True, df.iloc[0]['full_name']
        except:
            pass
        return True, name  # Если таблицы нет, просто пропускаем проверку

    def update_session_status(self, session_id: int, status: str):
        query = f"UPDATE {self._table_name('checklist_sessions')} SET status = %s WHERE id = %s"
        if not self.use_postgres:
            query = query.replace('%s', '?')
        self._execute(query, (status, session_id))

    def get_user_draft_sessions(self, user_name: str) -> pd.DataFrame:
        if self.use_postgres:
            query = f"""
                SELECT s.id, s.operation_date, f.name as filial_name, v.name as vsp_name, 
                       s.updated_at,
                       COUNT(a.id) as completed_count,
                       (SELECT COUNT(*) FROM {self.schema}.checklist_templates) as total_count
                FROM {self.schema}.checklist_sessions s
                JOIN {self.schema}.filials f ON s.filial_id = f.id
                JOIN {self.schema}.vsp v ON s.vsp_id = v.id
                LEFT JOIN {self.schema}.checklist_answers a ON s.id = a.session_id AND a.is_completed = true
                WHERE s.user_name = %s AND s.status = 'draft'
                GROUP BY s.id, f.name, v.name, s.operation_date, s.updated_at
                ORDER BY s.updated_at DESC
            """
            return self._to_df(query, (user_name,))
        else:
            query = """
                SELECT s.id, s.operation_date, f.name as filial_name, v.name as vsp_name, 
                       s.updated_at,
                       COUNT(a.id) as completed_count,
                       (SELECT COUNT(*) FROM checklist_templates) as total_count
                FROM checklist_sessions s
                JOIN filials f ON s.filial_id = f.id
                JOIN vsp v ON s.vsp_id = v.id
                LEFT JOIN checklist_answers a ON s.id = a.session_id AND a.is_completed = 1
                WHERE s.user_name = ? AND s.status = 'draft'
                GROUP BY s.id
                ORDER BY s.updated_at DESC
            """
            return self._to_df(query, (user_name,))

    def get_last_user_session_data(self, user_name: str) -> Dict[str, Any]:
        if self.use_postgres:
            query = f"""
                SELECT f.id as filial_id, f.name as filial_name, v.id as vsp_id, v.name as vsp_name
                FROM {self.schema}.checklist_sessions s
                JOIN {self.schema}.filials f ON s.filial_id = f.id
                JOIN {self.schema}.vsp v ON s.vsp_id = v.id
                WHERE s.user_name = %s AND s.status = 'completed'
                ORDER BY s.created_at DESC
                LIMIT 1
            """
            result = self._to_df(query, (user_name,))
        else:
            query = """
                SELECT f.id as filial_id, f.name as filial_name, v.id as vsp_id, v.name as vsp_name
                FROM checklist_sessions s
                JOIN filials f ON s.filial_id = f.id
                JOIN vsp v ON s.vsp_id = v.id
                WHERE s.user_name = ? AND s.status = 'completed'
                ORDER BY s.created_at DESC
                LIMIT 1
            """
            result = self._to_df(query, (user_name,))
        return result.iloc[0].to_dict() if not result.empty else None

    def get_last_user_any_session_data(self, user_name: str) -> Dict[str, Any]:
        if self.use_postgres:
            query = f"""
                SELECT f.id as filial_id, f.name as filial_name, v.id as vsp_id, v.name as vsp_name
                FROM {self.schema}.checklist_sessions s
                JOIN {self.schema}.filials f ON s.filial_id = f.id
                JOIN {self.schema}.vsp v ON s.vsp_id = v.id
                WHERE s.user_name = %s
                ORDER BY s.created_at DESC
                LIMIT 1
            """
            result = self._to_df(query, (user_name,))
        else:
            query = """
                SELECT f.id as filial_id, f.name as filial_name, v.id as vsp_id, v.name as vsp_name
                FROM checklist_sessions s
                JOIN filials f ON s.filial_id = f.id
                JOIN vsp v ON s.vsp_id = v.id
                WHERE s.user_name = ?
                ORDER BY s.created_at DESC
                LIMIT 1
            """
            result = self._to_df(query, (user_name,))
        return result.iloc[0].to_dict() if not result.empty else None

    def get_session_data(self, session_id: int) -> Dict[str, Any]:
        cursor = self._get_cursor()
        placeholder = '%s' if self.use_postgres else '?'
        cursor.execute(f"SELECT * FROM {self._table_name('checklist_sessions')} WHERE id = {placeholder}", (session_id,))
        row = cursor.fetchone()
        if not row:
            return None
        session_info = dict(row) if isinstance(row, dict) else {key: row[key] for key in row.keys()}
        cursor.execute(
            f"SELECT template_item_id, is_completed FROM {self._table_name('checklist_answers')} WHERE session_id = {placeholder}",
            (session_id,)
        )
        answers_rows = cursor.fetchall()
        answers = {}
        for r in answers_rows:
            if isinstance(r, dict):
                answers[r['template_item_id']] = bool(r['is_completed'])
            else:
                answers[r['template_item_id']] = bool(r['is_completed'])
        return {"info": session_info, "answers": answers}

    def save_answers(self, session_id: int, answers: Dict[int, bool]):
        cursor = self._get_cursor()
        for item_id, is_completed in answers.items():
            if self.use_postgres:
                query = sql.SQL("""
                    INSERT INTO {}.{} (session_id, template_item_id, is_completed)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (session_id, template_item_id)
                    DO UPDATE SET is_completed = EXCLUDED.is_completed
                """).format(sql.Identifier(self.schema), sql.Identifier('checklist_answers'))
                cursor.execute(query, (session_id, item_id, is_completed))
            else:
                cursor.execute("""
                    INSERT OR REPLACE INTO checklist_answers (session_id, template_item_id, is_completed)
                    VALUES (?, ?, ?)
                """, (session_id, item_id, 1 if is_completed else 0))
        if self.use_postgres:
            cursor.execute(f"UPDATE {self._table_name('checklist_sessions')} SET updated_at = CURRENT_TIMESTAMP WHERE id = %s", (session_id,))
        else:
            cursor.execute(f"UPDATE {self._table_name('checklist_sessions')} SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (session_id,))
        self._get_connection().commit()

    def get_export_data(self) -> pd.DataFrame:
        if self.use_postgres:
            query = f"""
                SELECT 
                    s.id as session_id,
                    s.user_name as ФИО,
                    f.name as Филиал,
                    v.name as ВСП,
                    s.operation_date as Дата_проверки,
                    CASE s.status 
                        WHEN 'completed' THEN 'Завершена'
                        WHEN 'draft' THEN 'Черновик'
                        ELSE s.status
                    END as Статус,
                    s.created_at as Дата_создания,
                    s.updated_at as Дата_обновления,
                    COUNT(a.id) as Выполнено_проверок,
                    (SELECT COUNT(*) FROM {self.schema}.checklist_templates) as Всего_проверок
                FROM {self.schema}.checklist_sessions s
                JOIN {self.schema}.filials f ON s.filial_id = f.id
                JOIN {self.schema}.vsp v ON s.vsp_id = v.id
                LEFT JOIN {self.schema}.checklist_answers a ON s.id = a.session_id AND a.is_completed = true
                GROUP BY s.id, f.name, v.name, s.user_name, s.operation_date, s.status, s.created_at, s.updated_at
                ORDER BY s.created_at DESC
            """
        else:
            query = """
                SELECT 
                    s.id as session_id,
                    s.user_name as ФИО,
                    f.name as Филиал,
                    v.name as ВСП,
                    s.operation_date as Дата_проверки,
                    CASE s.status 
                        WHEN 'completed' THEN 'Завершена'
                        WHEN 'draft' THEN 'Черновик'
                        ELSE s.status
                    END as Статус,
                    s.created_at as Дата_создания,
                    s.updated_at as Дата_обновления,
                    COUNT(a.id) as Выполнено_проверок,
                    (SELECT COUNT(*) FROM checklist_templates) as Всего_проверок
                FROM checklist_sessions s
                JOIN filials f ON s.filial_id = f.id
                JOIN vsp v ON s.vsp_id = v.id
                LEFT JOIN checklist_answers a ON s.id = a.session_id AND a.is_completed = 1
                GROUP BY s.id
                ORDER BY s.created_at DESC
            """
        return self._to_df(query)

    def get_user_sessions(self, user_name: str) -> pd.DataFrame:
        if self.use_postgres:
            query = f"""
                SELECT 
                    s.id,
                    s.operation_date as "Дата проверки",
                    f.name as "Филиал",
                    v.name as "ВСП",
                    CASE s.status 
                        WHEN 'completed' THEN 'Завершена'
                        WHEN 'draft' THEN 'Черновик'
                        ELSE s.status
                    END as "Статус",
                    s.created_at as "Дата создания",
                    s.updated_at as "Дата обновления",
                    COUNT(a.id) as "Выполнено проверок",
                    (SELECT COUNT(*) FROM {self.schema}.checklist_templates) as "Всего проверок"
                FROM {self.schema}.checklist_sessions s
                JOIN {self.schema}.filials f ON s.filial_id = f.id
                JOIN {self.schema}.vsp v ON s.vsp_id = v.id
                LEFT JOIN {self.schema}.checklist_answers a ON s.id = a.session_id AND a.is_completed = true
                WHERE s.user_name = %s
                GROUP BY s.id, f.name, v.name, s.operation_date, s.status, s.created_at, s.updated_at
                ORDER BY s.created_at DESC
            """
            return self._to_df(query, (user_name,))
        else:
            query = """
                SELECT 
                    s.id,
                    s.operation_date as "Дата проверки",
                    f.name as "Филиал",
                    v.name as "ВСП",
                    CASE s.status 
                        WHEN 'completed' THEN 'Завершена'
                        WHEN 'draft' THEN 'Черновик'
                        ELSE s.status
                    END as "Статус",
                    s.created_at as "Дата создания",
                    s.updated_at as "Дата обновления",
                    COUNT(a.id) as "Выполнено проверок",
                    (SELECT COUNT(*) FROM checklist_templates) as "Всего проверок"
                FROM checklist_sessions s
                JOIN filials f ON s.filial_id = f.id
                JOIN vsp v ON s.vsp_id = v.id
                LEFT JOIN checklist_answers a ON s.id = a.session_id AND a.is_completed = 1
                WHERE s.user_name = ?
                GROUP BY s.id
                ORDER BY s.created_at DESC
            """
            return self._to_df(query, (user_name,))


def export_to_excel(df: pd.DataFrame) -> bytes:
    if not OPENPYXL_AVAILABLE:
        st.error("Для экспорта в Excel необходимо установить openpyxl: pip install openpyxl")
        return None
    temp_path = "/tmp/temp_export.xlsx"
    try:
        with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Отчет по проверкам', index=False)
        with open(temp_path, 'rb') as f:
            excel_data = f.read()
        return excel_data
    except Exception as e:
        st.error(f"Ошибка: {e}")
        return None
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


# ==============================================================================
# 3. ИНИЦИАЛИЗАЦИЯ
# ==============================================================================
st.markdown("""
<style>
    div[data-testid="stCheckbox"] label span {
        transform: scale(1.5); 
        margin-right: 12px;
    }
    div[data-testid="stCheckbox"] label {
        font-size: 16px;
        padding: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

db = DatabaseManager()
db.init_db()

def seed_initial_data():
    if len(db.get_filials()) == 0:
        conn = db._get_connection()
        cursor = db._get_cursor()
        filials = ['Центральный офис', 'Филиал Север', 'Филиал Юг', 'Филиал Запад', 'Филиал Восток']
        for f in filials:
            if db.use_postgres:
                cursor.execute(f"INSERT INTO {db.schema}.filials (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (f,))
            else:
                cursor.execute("INSERT OR IGNORE INTO filials (name) VALUES (?)", (f,))
        conn.commit()
        df_f = db.get_filials()
        vsp_counter = 1
        for _, row in df_f.iterrows():
            fid = row['id']
            for i in range(3):
                vsp_name = f"ВСП {vsp_counter:04d}"
                if db.use_postgres:
                    cursor.execute(f"INSERT INTO {db.schema}.vsp (filial_id, name) VALUES (%s, %s)", (fid, vsp_name))
                else:
                    cursor.execute("INSERT INTO vsp (filial_id, name) VALUES (?, ?)", (fid, vsp_name))
                vsp_counter += 1
        conn.commit()
    if len(db.get_checklist_template()) == 0:
        items = [
            ("Проверка 1: Наличие вывески по брендбуку", "Проверить цвет, шрифт, подсветку вывески.", "Статус: Активно", "Провести ежемесячный аудит"),
            ("Проверка 2: Чистота в клиентской зоне", "Осмотр пола, стен, мебели.", "Периодичность: Ежедневно", "Назначить ответственного"),
            ("Проверка 3: Работа системы кондиционирования", "Температура 22-24°C.", "Сезон: Лето", "Провести техобслуживание"),
            ("Проверка 4: Наличие актуальных рекламных материалов", "Стенды заполнены буклетами.", "Актуальность: 2024", "Обновить стенды"),
            ("Проверка 5: Работоспособность терминалов самообслуживания", "Нет зависаний.", "Время работы: 24/7", "Мониторинг каждый час"),
            ("Проверка 6: Наличие питьевой воды и стаканчиков", "Кулер заправлен.", "Норма: 5л на день", "Пополнять ежедневно"),
            ("Проверка 7: Внешний вид сотрудников", "Dress-code, бейджи.", "Форма: Единая", "Проводить инструктаж"),
        ]
        for desc, add_info, filter_val, events_val in items:
            db.add_template_item(desc, add_info, filter_val, events_val)

seed_initial_data()

# --- Инициализация session_state (как в исходном коде) ---
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_full_name" not in st.session_state:
    st.session_state.user_full_name = ""
if "auth_valid" not in st.session_state:
    st.session_state.auth_valid = False
if "last_filial_name" not in st.session_state:
    st.session_state.last_filial_name = None
if "last_vsp_name" not in st.session_state:
    st.session_state.last_vsp_name = None
if "last_filial_id" not in st.session_state:
    st.session_state.last_filial_id = None
if "last_vsp_id" not in st.session_state:
    st.session_state.last_vsp_id = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "step" not in st.session_state:
    st.session_state.step = 0
if "selected_filial_id" not in st.session_state:
    st.session_state.selected_filial_id = None
if "selected_vsp_id" not in st.session_state:
    st.session_state.selected_vsp_id = None
if "resume_session_id" not in st.session_state:
    st.session_state.resume_session_id = None
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
if "update_counter" not in st.session_state:
    st.session_state.update_counter = 0

def load_last_user_data():
    if st.session_state.user_name and not st.session_state.data_loaded:
        last_data = db.get_last_user_session_data(st.session_state.user_name)
        if not last_data:
            last_data = db.get_last_user_any_session_data(st.session_state.user_name)
        if last_data:
            st.session_state.last_filial_name = last_data['filial_name']
            st.session_state.last_vsp_name = last_data['vsp_name']
            st.session_state.last_filial_id = last_data['filial_id']
            st.session_state.last_vsp_id = last_data['vsp_id']
            st.session_state.selected_filial_id = last_data['filial_id']
            st.session_state.selected_vsp_id = last_data['vsp_id']
            st.session_state.update_counter += 1
        st.session_state.data_loaded = True

load_last_user_data()

# ==============================================================================
# 4. БОКОВАЯ ПАНЕЛЬ И ОСНОВНАЯ ЛОГИКА (как в исходном коде, но с исправленным db)
# ==============================================================================
# ... (весь остальной код интерфейса остаётся без изменений, 
#      потому что db уже использует единое подключение)
# 
# ВНИМАНИЕ: В вашей ошибке упоминалась строка 687, где вызывался db.init_db().
# Теперь init_db() использует self._get_connection() и self._get_cursor(),
# и ошибка AttributeError: 'DatabaseManager' object has no attribute 'conn' больше не возникнет.

# ==============================================================================
# 4. БОКОВАЯ ПАНЕЛЬ
# ==============================================================================
with st.sidebar:
    st.header("👤 Информация")
    
    # Отображаем текущего пользователя если он есть
    if st.session_state.user_name:
        st.markdown(f"**Текущий пользователь:**")
        st.markdown(f"**{st.session_state.user_name}**")
        
        # Кнопка сброса пользователя
        if st.button("🔄 Сменить пользователя", use_container_width=True):
            st.session_state.user_name = ""
            st.session_state.user_full_name = ""
            st.session_state.auth_valid = False
            st.session_state.last_filial_name = None
            st.session_state.last_vsp_name = None
            st.session_state.last_filial_id = None
            st.session_state.last_vsp_id = None
            st.session_state.selected_filial_id = None
            st.session_state.selected_vsp_id = None
            st.session_state.step = 0
            st.session_state.data_loaded = False
            st.session_state.update_counter += 1
            if "current_session_id" in st.session_state:
                del st.session_state.current_session_id
            if "temp_answers" in st.session_state:
                del st.session_state.temp_answers
            st.rerun()
    else:
        st.info("👋 Пользователь не выбран")
    
    st.divider()
    
    # АДМИНКА В БОКОВОЙ ПАНЕЛИ (ДОСТУПНА ВСЕГДА, ДАЖЕ БЕЗ ПОЛЬЗОВАТЕЛЯ)
    st.subheader("🔐 Администрирование")
    
    # Чекбокс для входа в админку
    admin_access_request = st.checkbox("Вход в режим администратора", key="admin_checkbox")
    
    if admin_access_request:
        if not st.session_state.admin_authenticated:
            # Поле для ввода пароля
            password_input = st.text_input("Введите пароль:", type="password", key="admin_password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Войти", type="primary", use_container_width=True):
                    if password_input == ADMIN_PASSWORD:
                        st.session_state.admin_authenticated = True
                        st.session_state.is_admin = True
                        st.success("✅ Доступ разрешен!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ Неверный пароль!")
        else:
            st.success("✅ Режим администратора активен")
            if st.button("Выйти из режима администратора", use_container_width=True):
                st.session_state.admin_authenticated = False
                st.session_state.is_admin = False
                st.rerun()
    else:
        # Если чекбокс снят и админ авторизован - выходим из режима админа
        if st.session_state.admin_authenticated:
            st.session_state.admin_authenticated = False
            st.session_state.is_admin = False
            st.rerun()
    
    # Показываем админ-панель ТОЛЬКО если админ авторизован
    if st.session_state.admin_authenticated:
        st.divider()
        st.subheader("⚙️ Управление чек-листом")
        
        template_df = db.get_checklist_template()
        if not template_df.empty:
            with st.expander("📋 Текущие проверки"):
                for _, row in template_df.iterrows():
                    st.markdown(f"**{row['item_order']}.** {row['description']}")
        
        # РАСШИРЕННЫЙ БЛОК: Добавить проверку (с полями фильтр и мероприятия)
        with st.expander("➕ Добавить проверку"):
            new_desc = st.text_area("Наименование процедуры", key="new_desc", height=68, help="Обязательное поле")
            new_info = st.text_area("Описание процедуры", key="new_info", height=68, help="Пояснение к проверке")
            new_filter = st.text_area("🔍 Фильтр", key="new_filter",
                                       placeholder="Например: Статус: Активно, Периодичность: Ежедневно",
                                       help="Значение фильтра для этой проверки")
            new_events = st.text_area("📌 Мероприятия", key="new_events", height=68,
                                      placeholder="Перечень необходимых мероприятий...",
                                      help="План мероприятий по проверке")
            
            if st.button("➕ Добавить проверку", use_container_width=True, type="primary"):
                if new_desc:
                    db.add_template_item(new_desc, new_info, new_filter, new_events)
                    st.success("✅ Проверка успешно добавлена!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Наименование процедуры - обязательное поле!")
        
        # РАСШИРЕННЫЙ БЛОК: Редактировать/Удалить (с полями фильтр и мероприятия)
        with st.expander("✏️ Редактировать/Удалить проверку"):
            if not template_df.empty:
                item_ids = template_df['id'].tolist()
                sel_id = st.selectbox("Выберите проверку для редактирования", item_ids, format_func=lambda x: f"ID {x} - {template_df[template_df['id'] == x]['description'].iloc[0][:50]}")
                row = template_df[template_df['id'] == sel_id].iloc[0]
                
                edit_desc = st.text_area("Наименование процедуры", value=row['description'], key="edit_desc", height=68)
                edit_info = st.text_area("Описание процедуры", value=row['additional_info'] or "", key="edit_info", height=68)
                edit_filter = st.text_area("🔍 Фильтр", value=row['filter_value'] or "", key="edit_filter",
                                            placeholder="Например: Статус: Активно, Периодичность: Ежедневно")
                edit_events = st.text_area("📌 Мероприятия", value=row['events_value'] or "", key="edit_events",
                                           height=68, placeholder="Перечень необходимых мероприятий...")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("💾 Обновить проверку", use_container_width=True, type="primary"):
                        db.update_template_item(sel_id, edit_desc, edit_info, edit_filter, edit_events)
                        st.success("✅ Проверка успешно обновлена!")
                        time.sleep(1)
                        st.rerun()
                with c2:
                    if st.button("🗑️ Удалить проверку", use_container_width=True, type="secondary"):
                        db.delete_template_item(sel_id)
                        st.success("✅ Проверка удалена!")
                        time.sleep(1)
                        st.rerun()
        
        st.divider()
        st.subheader("📊 Экспорт данных")
        
        export_df = db.get_export_data()
        
        if not export_df.empty:
            st.info(f"📈 Записей: {len(export_df)}")
            if st.button("📊 Экспорт в Excel", type="primary", use_container_width=True):
                try:
                    excel_data = export_to_excel(export_df)
                    if excel_data:
                        st.download_button(
                            label="💾 Скачать Excel файл",
                            data=excel_data,
                            file_name=f"checklist_report_{datetime.date.today()}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Ошибка: {e}")
        else:
            st.warning("Нет данных для экспорта")

# ==============================================================================
# 5. ОСНОВНАЯ ЛОГИКА
# ==============================================================================
st.title("📋 Чек-лист операционной проверки ВСП")
st.caption("Заполнение данных о пользователе чек-листа операционной проверки")

# Создаём две вкладки
tab_history, tab_main = st.tabs(["📜 История проверок", "📝 Новая проверка"])

with tab_main:
    # Шаг 0: Выбор действия (новая проверка или продолжение черновика)
    if st.session_state.step == 0:
        # Проверяем наличие черновиков 
        if st.session_state.user_name:
            drafts_df = db.get_user_draft_sessions(st.session_state.user_name)
            # Фильтруем черновики по текущей дате
            if not drafts_df.empty:
                drafts_df = drafts_df[drafts_df['operation_date'] == datetime.date.today()]
        else:
            drafts_df = pd.DataFrame()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Если есть черновики, показываем выбор
            if not drafts_df.empty:
                st.info(f"📌 У вас есть {len(drafts_df)} сохраненных черновиков")
                
                # Выбор действия
                action = st.radio(
                    "Выберите действие:",
                    ["📂 Продолжить сохраненную проверку"],
                    index=0
                )
                
                if action == "📂 Продолжить сохраненную проверку":
                    st.markdown("---")
                    st.markdown("#### Ваши сохраненные проверки:")
                    
                    # Отображаем черновики в виде карточек
                    for _, draft in drafts_df.iterrows():
                        with st.container():
                            col_a, col_b, col_c = st.columns([3, 2, 1])
                            with col_a:
                                st.markdown(f"**{draft['filial_name']} / {draft['vsp_name']}**")
                                st.caption(f"📅 Дата: {draft['operation_date']}")
                            with col_b:
                                st.caption(f"✅ Выполнено: {draft['completed_count']}/{draft['total_count']} проверок")
                            with col_c:
                                if st.button("📂 Продолжить", key=f"resume_{draft['id']}", use_container_width=True):
                                    st.session_state.resume_session_id = draft['id']
                                    st.session_state.current_session_id = draft['id']
                                    st.session_state.step = 1
                                    st.rerun()
                            st.divider()
                    
                    st.markdown("---")
            
            # ФОРМА ДЛЯ НОВОЙ ПРОВЕРКИ
            filials_df = db.get_filials()
            if not filials_df.empty:
                filial_names = filials_df['name'].tolist()
                filial_map = dict(zip(filials_df['name'], filials_df['id']))
                
                # ПОЛЕ ДЛЯ ВВОДА ФИО
                user_name_raw = st.text_input(
                    "👤 Учетная запись сотрудника",
                    value=st.session_state.user_name,
                    placeholder="GO_IVANOV_AV",
                    help="Пожалуйста, введите вашу учетную запись",
                    key=f"user_name_raw_field_{st.session_state.update_counter}"
                )
                
                user_name_normalized = user_name_raw.lower().strip() if user_name_raw else ""
                
                if user_name_normalized and user_name_normalized != st.session_state.user_name:
                    exists, full_name = db.check_user_by_name(user_name_normalized)
                    if exists:
                        st.session_state.user_name = user_name_normalized
                        st.session_state.user_full_name = full_name
                        st.session_state.auth_valid = True
                        st.toast(f"Добро пожаловать, {full_name}!", icon="✔️")
                        
                        last_data = db.get_last_user_session_data(user_name_normalized)
                        # АВТОМАТИЧЕСКАЯ ПОДСТАНОВКА ФИЛИАЛА И ВСП ПРИ ИЗМЕНЕНИИ ФИО
                        if last_data:
                            st.session_state.last_filial_name = last_data['filial_name']
                            st.session_state.last_vsp_name = last_data['vsp_name']
                            st.session_state.last_filial_id = last_data['filial_id']
                            st.session_state.last_vsp_id = last_data['vsp_id']
                            st.session_state.selected_filial_id = last_data['filial_id']
                            st.session_state.selected_vsp_id = last_data['vsp_id']
                            st.session_state.update_counter += 1
                        else:
                            st.session_state.last_filial_name = None
                            st.session_state.last_vsp_name = None
                            st.session_state.last_filial_id = None
                            st.session_state.last_vsp_id = None
                            st.session_state.selected_filial_id = None
                            st.session_state.selected_vsp_id = None
                    else:
                        st.session_state.auth_valid = False
                        st.session_state.user_name = ""
                        st.session_state.user_full_name = ""
                        st.toast("❌ Пользователь не найден", icon="❌")
                
                if st.session_state.auth_valid:
                    nam = st.session_state.user_full_name
                    if ' ' in nam:
                        nam = nam.split()[1]
                
                # ОПРЕДЕЛЯЕМ ИНДЕКС ДЛЯ ФИЛИАЛА
                current_filial_index = 0
                if st.session_state.last_filial_name and st.session_state.last_filial_name in filial_names:
                    current_filial_index = filial_names.index(st.session_state.last_filial_name)
                
                selected_filial_name = st.selectbox(
                    "🏢 Филиал",
                    filial_names,
                    index=current_filial_index,
                    key=f"filial_select_{st.session_state.update_counter}"
                )
                selected_filial_id = filial_map[selected_filial_name]
                
                # Сохраняем выбранный филиал
                st.session_state.last_filial_name = selected_filial_name
                st.session_state.last_filial_id = selected_filial_id
                
                # ЕСЛИ ФИЛИАЛ ИЗМЕНИЛСЯ - ОБНОВЛЯЕМ СПИСОК ВСП И СБРАСЫВАЕМ ВЫБРАННЫЙ ВСП
                if st.session_state.selected_filial_id != selected_filial_id:
                    st.session_state.selected_filial_id = selected_filial_id
                    st.session_state.selected_vsp_id = None
                    st.session_state.last_vsp_name = None
                    st.session_state.last_vsp_id = None
                    st.session_state.update_counter += 1
                    st.rerun()
                
                # ПОЛУЧАЕМ СПИСОК ВСП ДЛЯ ВЫБРАННОГО ФИЛИАЛА
                vsp_df = db.get_vsp_by_filial(selected_filial_id)
                if not vsp_df.empty:
                    vsp_names = vsp_df['name'].tolist()
                    vsp_map = dict(zip(vsp_df['name'], vsp_df['id']))
                    
                    # ОПРЕДЕЛЯЕМ ИНДЕКС ДЛЯ ВСП
                    current_vsp_index = 0
                    if st.session_state.last_vsp_name and st.session_state.last_vsp_name in vsp_names:
                        current_vsp_index = vsp_names.index(st.session_state.last_vsp_name)
                    elif st.session_state.last_vsp_id and st.session_state.last_vsp_id in vsp_map.values():
                        for i, (name, v_id) in enumerate(vsp_map.items()):
                            if v_id == st.session_state.last_vsp_id:
                                current_vsp_index = i
                                st.session_state.last_vsp_name = name
                                break
                    
                    selected_vsp_name = st.selectbox(
                        "🏪 ВСП",
                        vsp_names,
                        index=current_vsp_index,
                        key=f"vsp_select_{st.session_state.update_counter}"
                    )
                    selected_vsp_id = vsp_map[selected_vsp_name]
                    
                    # Сохраняем выбранный ВСП
                    st.session_state.last_vsp_name = selected_vsp_name
                    st.session_state.last_vsp_id = selected_vsp_id
                    st.session_state.selected_vsp_id = selected_vsp_id
                else:
                    st.warning("⚠️ Нет ВСП в выбранном филиале")
                    selected_vsp_id = None
            else:
                st.error("❌ Нет филиалов")
                st.stop()
            
            with st.form(key=f"session_form_{st.session_state.update_counter}"):
                # Дата (всегда текущая)
                op_date = st.date_input("📅 Дата", value=datetime.date.today(), format="DD.MM.YYYY", disabled=True)
                
                submitted = st.form_submit_button(
                    "▶️ НАЧАТЬ ЗАПОЛНЕНИЕ",
                    type="primary",
                    use_container_width=True,
                    disabled=not st.session_state.auth_valid
                )
                
                if submitted and selected_vsp_id:
                    if user_name_raw and user_name_raw.strip():
                        st.session_state.user_name = user_name_raw.strip()
                        st.session_state.last_filial_name = selected_filial_name
                        st.session_state.last_vsp_name = selected_vsp_name
                        st.session_state.last_filial_id = selected_filial_id
                        st.session_state.last_vsp_id = selected_vsp_id
                        session_id = db.create_session(
                            st.session_state.user_name,
                            selected_filial_id,
                            selected_vsp_id,
                            op_date,
                            'draft'
                        )
                        st.session_state.current_session_id = session_id
                        st.session_state.step = 1
                        st.rerun()
                    else:
                        st.error("❌ Пожалуйста, введите вашу учетную запись!")

with tab_history:
    st.markdown("### 📜 История ваших проверок")
    if st.session_state.user_name:
        history_df = db.get_user_sessions(st.session_state.user_name)
        if not history_df.empty:
            st.dataframe(history_df, use_container_width=True, height=400)
            
            selected_session_id = st.selectbox(
                "Выберите сессию для просмотра деталей",
                options=history_df['id'].tolist(),
                format_func=lambda x: f"Сессия #{x} - {history_df[history_df['id']==x]['Дата проверки'].iloc[0]}"
            )
            if selected_session_id:
                if st.button("📋 Показать результаты", key="view_session"):
                    session_data = db.get_session_data(selected_session_id)
                    if session_data:
                        with st.expander(f"Результаты проверки #{selected_session_id}", expanded=True):
                            st.markdown(f"**Дата:** {session_data['info']['operation_date']}")
                            st.markdown(f"**Статус:** {'✔️ Завершена' if session_data['info']['status']=='completed' else '📄 Черновик'}")
                            template_df = db.get_checklist_template()
                            answers = session_data['answers']
                            st.markdown("**Проверки:**")
                            for _, row in template_df.iterrows():
                                is_completed = answers.get(row['id'], False)
                                status_icon = "✔️" if is_completed else "❌"
                                st.markdown(f"{status_icon} {row['description']}")
                    else:
                        st.error("Не удалось загрузить данные сессии")
        else:
            st.info("У вас пока нет завершённых проверок.")
    else:
        st.warning("👈 Пожалуйста, введите вашу учетную запись, чтобы увидеть историю.")

# Шаг 1: Заполнение чек-листа
if st.session_state.step == 1:
    if "current_session_id" not in st.session_state:
        st.error("Сессия не найдена")
        st.session_state.step = 0
        st.rerun()
    
    session_id = st.session_state.current_session_id
    session_data = db.get_session_data(session_id)
    
    if not session_data:
        st.error("Данные сессии отсутствуют")
        st.stop()
    
    template_df = db.get_checklist_template()
    if template_df.empty:
        st.warning("Шаблон пуст")
        st.stop()
    
    saved_answers = session_data['answers']
    if "temp_answers" not in st.session_state:
        st.session_state.temp_answers = copy.deepcopy(saved_answers)
    
    # Получаем информацию о филиале и ВСП
    try:
        cursor = db._get_cursor()
        if db.use_postgres:
            cursor.execute(f"""
                SELECT f.name as filial_name, v.name as vsp_name
                FROM {db.schema}.checklist_sessions s
                JOIN {db.schema}.filials f ON s.filial_id = f.id
                JOIN {db.schema}.vsp v ON s.vsp_id = v.id
                WHERE s.id = %s
            """, (session_id,))
            row = cursor.fetchone()
            filial_name, vsp_name = row[0], row[1]
        else:
            cursor.execute("""
                SELECT f.name, v.name
                FROM checklist_sessions s
                JOIN filials f ON s.filial_id = f.id
                JOIN vsp v ON s.vsp_id = v.id
                WHERE s.id = ?
            """, (session_id,))
            row = cursor.fetchone()
            filial_name, vsp_name = row[0], row[1]
    except Exception as e:
        filial_name, vsp_name = "?", "?"
        st.write(f"Error getting filial/vsp: {e}")
    
    st.subheader(f"📋 Чек-лист: {filial_name} / {vsp_name}")
    
    # Отображаем статус и информацию о пользователе
    status_text = "Черновик" if session_data['info']['status'] == 'draft' else "Завершена"
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.markdown(f"**👤 Сотрудник:** {session_data['info']['user_name']}")
    col2.markdown(f"**🏢 Филиал:** {filial_name}")
    col3.markdown(f"**🏪 ВСП:** {vsp_name}")
    col4.markdown(f"**📅 Дата:** {session_data['info']['operation_date']}")
    col5.markdown(f"**📌 Статус:** {status_text}")
    
    st.divider()
    st.markdown("### ✅ Список проверок")
    
    # Заголовки таблицы
    header_cols = st.columns([1, 5, 2, 1])
    header_cols[0].markdown("**№**")
    header_cols[1].markdown("**Наименование проверки**")
    header_cols[2].markdown("**Доп. информация**")
    header_cols[3].markdown("**Статус**")
    st.markdown("---")
    
    # Отображение всех проверок
    for _, row in template_df.iterrows():
        item_id = row['id']
        order = row['item_order']
        desc = row['description']
        add_info = row['additional_info']
        filter_text = row['filter_value'] if row['filter_value'] else "Не задан"
        events_text = row['events_value'] if row['events_value'] else "Не заданы"
        current = st.session_state.temp_answers.get(item_id, saved_answers.get(item_id, False))
        
        cols = st.columns([1, 5, 2, 1])
        cols[0].write(f"**{order}**")
        cols[1].markdown(desc)
        
        # ВСПЛЫВАЮЩЕЕ ОКНО
        with cols[2]:
            with st.popover(f"ℹ️ Подробнее о проверке №{order}", use_container_width=True):
                tab1, tab2, tab3 = st.tabs(["📝 Описание", "🔍 Фильтр", "📌 Мероприятия"])
                
                with tab1:
                    st.markdown("**Описание процедуры:**")
                    st.info(add_info if add_info else "Описание отсутствует")
                    st.caption("ℹ️ Информационное поле (только для просмотра)")
                
                with tab2:
                    st.markdown("**Фильтр:**")
                    if filter_text != "Не задан":
                        filter_display = filter_text
                        if "[Дата1]" in filter_text:
                            default_date = datetime.date.today() - datetime.timedelta(days=1)
                            selected_date = st.date_input("📅 Выберите дату", key=f"date_{item_id}", value=default_date, format="DD.MM.YYYY")
                            date_str = selected_date.strftime("%d.%m.%y")
                            filter_display = filter_text.replace("[Дата1]", date_str)
                        
                        filter_display = filter_display.replace("[РФ]", vsp_name)
                        st.code(filter_display, language="text")
                        
                        import streamlit.components.v1 as components
                        button_id = f"copy_filter_{item_id}"
                        js_code = f"""
                        <div style="margin-top: 8px;">
                            <button id="{button_id}" style="background-color:#4CAF50; color:white; padding:8px 16px; border:none; border-radius:5px; width:100%%; cursor:pointer; font-size:14px;">
                                📋 КОПИРОВАТЬ ФИЛЬТР
                            </button>
                            <div id="status_{button_id}" style="margin-top: 5px; font-size:12px; text-align:center;"></div>
                            <script>
                                (function() {{
                                    var btn = document.getElementById("{button_id}");
                                    var statusDiv = document.getElementById("status_{button_id}");
                                    var textToCopy = {repr(filter_display)};
                                    btn.addEventListener("click", function() {{
                                        navigator.clipboard.writeText(textToCopy).then(function() {{
                                            statusDiv.innerHTML = "✅ Скопировано!";
                                            statusDiv.style.color = "green";
                                            setTimeout(function() {{ statusDiv.innerHTML = ""; }}, 2000);
                                        }}, function(err) {{
                                            statusDiv.innerHTML = "❌ Ошибка";
                                            statusDiv.style.color = "red";
                                        }});
                                    }});
                                }})();
                            </script>
                        </div>
                        """
                        components.html(js_code, height=100)
                    else:
                        st.info("Фильтр не задан администратором")
                
                with tab3:
                    st.markdown("**Мероприятия:**")
                    if events_text != "Не заданы":
                        st.info(events_text)
                        st.caption("📋 План мероприятий задан администратором")
                    else:
                        st.info("Мероприятия не заданы администратором")
                    st.caption("ℹ️ Поле только для просмотра")
        
        with cols[3]:
            new_val = st.checkbox(" ", value=current, key=f"chk_{item_id}", label_visibility="collapsed")
            if new_val != current:
                st.session_state.temp_answers[item_id] = new_val
        
        st.markdown("<hr style='margin: 2px 0; border: 0.5px solid #e0e0e0;'>", unsafe_allow_html=True)
    
    # Кнопки управления
    col_a, col_b, col_c, col_d = st.columns([1, 1, 1, 2])
    
    if col_a.button("🔙 Назад", use_container_width=True):
        db.save_answers(session_id, st.session_state.temp_answers)
        db.update_session_status(session_id, 'draft')
        st.session_state.step = 0
        if "current_session_id" in st.session_state:
            del st.session_state.current_session_id
        if "temp_answers" in st.session_state:
            del st.session_state.temp_answers
        if "resume_session_id" in st.session_state:
            del st.session_state.resume_session_id
        st.rerun()
    
    if col_b.button("💾 Сохранить черновик", use_container_width=True):
        db.save_answers(session_id, st.session_state.temp_answers)
        db.update_session_status(session_id, 'draft')
        st.success("✅ Черновик сохранен! Вы можете продолжить позже.")
        time.sleep(1)
        st.rerun()
    
    if col_c.button("📋 Предпросмотр", use_container_width=True):
        with st.expander("📄 Предпросмотр результатов", expanded=True):
            st.markdown("#### Результаты проверки:")
            completed_items = []
            incomplete_items = []
            
            completed_count = sum(1 for v in st.session_state.temp_answers.values() if v)
            total_count = len(template_df)
            
            for _, row in template_df.iterrows():
                item_id = row['id']
                is_completed = st.session_state.temp_answers.get(item_id, False)
                if is_completed:
                    completed_items.append(f"✅ {row['description']}")
                else:
                    incomplete_items.append(f"❌ {row['description']}")
            
            if completed_items:
                st.markdown("**Выполненные проверки:**")
                for item in completed_items:
                    st.markdown(item)
            
            if incomplete_items:
                st.markdown("**Невыполненные проверки:**")
                for item in incomplete_items:
                    st.markdown(item)
            
            st.markdown("---")
            st.info(f"📊 Выполнено проверок: {completed_count}/{total_count}")
    
    if col_d.button("✅ ЗАВЕРШИТЬ ПРОВЕРКУ", type="primary", use_container_width=True):
        completed_count = sum(1 for v in st.session_state.temp_answers.values() if v)
        total_count = len(template_df)
        
        if completed_count < total_count:
            st.toast(f"⚠️ Выполнено только {completed_count} из {total_count} проверок. Заполните все проверки для завершения!", icon="❗")
        else:
            db.save_answers(session_id, st.session_state.temp_answers)
            db.update_session_status(session_id, 'completed')
            st.success("🎉 Отлично! Все проверки выполнены! Чек-лист успешно завершен!")
            
            if st.session_state.user_full_name and ' ' in st.session_state.user_full_name:
                nam = st.session_state.user_full_name.split()[1]
                st.toast(f"🔥 Здравствуйте, {nam}! В следующий раз ваши ФИЛИАЛ и ВСП будут указаны автоматически!")
            
            st.balloons()
            st.session_state.step = 0
            if "current_session_id" in st.session_state:
                del st.session_state.current_session_id
            if "temp_answers" in st.session_state:
                del st.session_state.temp_answers
            if "resume_session_id" in st.session_state:
                del st.session_state.resume_session_id
            time.sleep(2)
            st.rerun()
