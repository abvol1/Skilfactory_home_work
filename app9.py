import streamlit as st
import pandas as pd
import sqlite3
import datetime
import json
from typing import List, Dict, Any, Optional
import copy
import os
import time

# Excel
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

# PostgreSQL
try:
    import psycopg2
    from psycopg2 import sql
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# ==============================================================================
# КОНФИГУРАЦИЯ
# ==============================================================================
USE_POSTGRES = False          # Переключите на True при работе с PostgreSQL
PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "checklist_db",
    "user": "postgres",
    "password": "password",
    "schema": "public"
}
SQLITE_PATH = "checklist_app.db"
FORCE_RECREATE_DB = False
ADMIN_PASSWORD = "admin123"

# ==============================================================================
# КЛАСС РАБОТЫ С БД (SQLite / PostgreSQL)
# ==============================================================================
class DatabaseManager:
    def __init__(self):
        self.use_postgres = USE_POSTGRES and POSTGRES_AVAILABLE
        self.schema = PG_CONFIG.get('schema', 'public') if self.use_postgres else None

    def get_connection(self):
        if self.use_postgres:
            return psycopg2.connect(
                host=PG_CONFIG['host'],
                port=PG_CONFIG['port'],
                dbname=PG_CONFIG['database'],
                user=PG_CONFIG['user'],
                password=PG_CONFIG['password'],
                cursor_factory=psycopg2.extras.RealDictCursor   # ← ключевое изменение
            )
        else:
            conn = sqlite3.connect(SQLITE_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory = sqlite3.Row
            return conn

    def _table_name(self, table: str) -> str:
        if self.use_postgres:
            return f"{self.schema}.{table}"
        return table

    def _execute(self, query: str, params=None, fetch_one=False, fetch_all=False):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(query, params or ())
            if fetch_one:
                result = cur.fetchone()
            elif fetch_all:
                result = cur.fetchall()
            else:
                result = None
            conn.commit()
            return result
        finally:
            conn.close()

    def _to_df(self, query: str, params=None) -> pd.DataFrame:
        conn = self.get_connection()
        try:
            return pd.read_sql_query(query, conn, params=params or ())
        finally:
            conn.close()

    # ------------------- Инициализация БД -------------------
    def init_db(self):
        if FORCE_RECREATE_DB and not self.use_postgres and os.path.exists(SQLITE_PATH):
            os.remove(SQLITE_PATH)

        conn = self.get_connection()
        cursor = conn.cursor()

        if self.use_postgres:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.checklist_templates (
                    id SERIAL PRIMARY KEY,
                    section_name VARCHAR(255) NOT NULL,
                    item_order INTEGER NOT NULL,
                    description TEXT,
                    additional_info TEXT
                )
            """)
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
                    status VARCHAR(50) DEFAULT 'completed',
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
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checklist_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    section_name TEXT NOT NULL DEFAULT 'Основной',
                    item_order INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    additional_info TEXT
                )
            """)
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
                    status TEXT DEFAULT 'completed',
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

        conn.commit()
        conn.close()

    # ------------------- Справочники -------------------
    def get_filials(self) -> pd.DataFrame:
        return self._to_df(f"SELECT id, name FROM {self._table_name('filials')} ORDER BY name")

    def get_vsp_by_filial(self, filial_id: int) -> pd.DataFrame:
        if self.use_postgres:
            return self._to_df(f"SELECT id, name FROM {self._table_name('vsp')} WHERE filial_id = %s ORDER BY name", (filial_id,))
        else:
            return self._to_df(f"SELECT id, name FROM {self._table_name('vsp')} WHERE filial_id = ? ORDER BY name", (filial_id,))

    # ------------------- Шаблон чек-листа -------------------
    def get_checklist_template(self) -> pd.DataFrame:
        return self._to_df(f"SELECT id, item_order, description, additional_info FROM {self._table_name('checklist_templates')} ORDER BY item_order")

    def add_template_item(self, description: str, additional_info: str):
        next_order = self._execute(f"SELECT COALESCE(MAX(item_order), 0) + 1 FROM {self._table_name('checklist_templates')}", fetch_one=True)[0]
        query = f"INSERT INTO {self._table_name('checklist_templates')} (section_name, item_order, description, additional_info) VALUES (%s, %s, %s, %s)"
        if not self.use_postgres:
            query = query.replace('%s', '?')
        self._execute(query, ('Основной', next_order, description, additional_info))

    def update_template_item(self, item_id: int, description: str, additional_info: str):
        query = f"UPDATE {self._table_name('checklist_templates')} SET description = %s, additional_info = %s WHERE id = %s"
        if not self.use_postgres:
            query = query.replace('%s', '?')
        self._execute(query, (description, additional_info, item_id))

    def delete_template_item(self, item_id: int):
        query = f"DELETE FROM {self._table_name('checklist_templates')} WHERE id = %s"
        if not self.use_postgres:
            query = query.replace('%s', '?')
        self._execute(query, (item_id,))

    # ------------------- Сессии и ответы -------------------
    def create_session(self, user_name: str, filial_id: int, vsp_id: int, op_date) -> int:
        query = f"INSERT INTO {self._table_name('checklist_sessions')} (user_name, filial_id, vsp_id, operation_date, status) VALUES (%s, %s, %s, %s, 'completed')"
        if not self.use_postgres:
            query = query.replace('%s', '?')
        if self.use_postgres:
            query += " RETURNING id"
            row = self._execute(query, (user_name, filial_id, vsp_id, op_date), fetch_one=True)
            return row['id']
        else:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(query, (user_name, filial_id, vsp_id, op_date))
            session_id = cur.lastrowid
            conn.commit()
            conn.close()
            return session_id

    def get_session_data(self, session_id: int) -> Dict[str, Any]:
        conn = self.get_connection()
        cur = conn.cursor()
        placeholder = '%s' if self.use_postgres else '?'
        cur.execute(f"SELECT * FROM {self._table_name('checklist_sessions')} WHERE id = {placeholder}", (session_id,))
        row = cur.fetchone()
        if not row:
            return None
        # row уже словарь (RealDictCursor для PG или Row для SQLite)
        session_info = dict(row) if not self.use_postgres else dict(row)  # RealDictCursor тоже поддерживает dict()
        cur.execute(
            f"SELECT template_item_id, is_completed FROM {self._table_name('checklist_answers')} WHERE session_id = {placeholder}",
            (session_id,)
        )
        answers = {}
        for r in cur.fetchall():
            if self.use_postgres:
                answers[r['template_item_id']] = bool(r['is_completed'])
            else:
                answers[r['template_item_id']] = bool(r['is_completed'])
        conn.close()
        return {"info": session_info, "answers": answers}

    def save_answers(self, session_id: int, answers: Dict[int, bool]):
        conn = self.get_connection()
        cur = conn.cursor()
        for item_id, is_completed in answers.items():
            if self.use_postgres:
                query = sql.SQL("""
                    INSERT INTO {}.{} (session_id, template_item_id, is_completed)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (session_id, template_item_id)
                    DO UPDATE SET is_completed = EXCLUDED.is_completed
                """).format(sql.Identifier(self.schema), sql.Identifier('checklist_answers'))
                cur.execute(query, (session_id, item_id, is_completed))
            else:
                cur.execute("""
                    INSERT OR REPLACE INTO checklist_answers (session_id, template_item_id, is_completed)
                    VALUES (?, ?, ?)
                """, (session_id, item_id, 1 if is_completed else 0))
        # Обновляем updated_at
        if self.use_postgres:
            cur.execute(f"UPDATE {self._table_name('checklist_sessions')} SET updated_at = CURRENT_TIMESTAMP WHERE id = %s", (session_id,))
        else:
            cur.execute(f"UPDATE {self._table_name('checklist_sessions')} SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()

    def get_export_data(self) -> pd.DataFrame:
        if self.use_postgres:
            query = f"""
                SELECT 
                    s.id as session_id,
                    s.user_name as ФИО,
                    f.name as Филиал,
                    v.name as ВСП,
                    s.operation_date as Дата_проверки,
                    s.status as Статус,
                    s.created_at as Дата_создания,
                    s.updated_at as Дата_обновления,
                    COUNT(a.id) as Выполнено_проверок
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
                    s.status as Статус,
                    s.created_at as Дата_создания,
                    s.updated_at as Дата_обновления,
                    COUNT(a.id) as Выполнено_проверок
                FROM checklist_sessions s
                JOIN filials f ON s.filial_id = f.id
                JOIN vsp v ON s.vsp_id = v.id
                LEFT JOIN checklist_answers a ON s.id = a.session_id AND a.is_completed = 1
                GROUP BY s.id
                ORDER BY s.created_at DESC
            """
        return self._to_df(query)


# ==============================================================================
# ФУНКЦИЯ ЭКСПОРТА В EXCEL
# ==============================================================================
def export_to_excel(df: pd.DataFrame) -> bytes:
    if not OPENPYXL_AVAILABLE:
        st.error("Для экспорта в Excel установите openpyxl: pip install openpyxl")
        return None
    output = pd.ExcelWriter('temp_export.xlsx', engine='openpyxl')
    df.to_excel(output, sheet_name='Отчет по проверкам', index=False)
    output.close()
    with open('temp_export.xlsx', 'rb') as f:
        data = f.read()
    os.remove('temp_export.xlsx')
    return data


# ==============================================================================
# ИНИЦИАЛИЗАЦИЯ И НАЧАЛЬНЫЕ ДАННЫЕ
# ==============================================================================
st.set_page_config(page_title="Чек-лист ВСП", layout="wide", initial_sidebar_state="expanded", page_icon="📋")

db = DatabaseManager()
db.init_db()

def seed_initial_data():
    if len(db.get_filials()) == 0:
        conn = db.get_connection()
        cursor = conn.cursor()
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
        conn.close()

    if len(db.get_checklist_template()) == 0:
        items = [
            ("Проверка 1: Наличие вывески по брендбуку", "Проверить цвет, шрифт, подсветку вывески."),
            ("Проверка 2: Чистота в клиентской зоне", "Осмотр пола, стен, мебели."),
            ("Проверка 3: Работа системы кондиционирования", "Температура 22-24°C."),
            ("Проверка 4: Наличие актуальных рекламных материалов", "Стенды заполнены буклетами."),
            ("Проверка 5: Работоспособность терминалов самообслуживания", "Нет зависаний."),
            ("Проверка 6: Наличие питьевой воды и стаканчиков", "Кулер заправлен."),
            ("Проверка 7: Внешний вид сотрудников", "Dress-code, бейджи."),
        ]
        for desc, add_info in items:
            db.add_template_item(desc, add_info)

seed_initial_data()

# Состояние пользователя
if "user_name" not in st.session_state:
    st.session_state.user_name = "Иванов Иван Иванович"
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

# ==============================================================================
# БОКОВАЯ ПАНЕЛЬ (АДМИНКА)
# ==============================================================================
with st.sidebar:
    st.header("👤 Информация")
    st.markdown(f"**Пользователь:** {st.session_state.user_name}")
    if st.button("🚪 Сменить пользователя", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ['user_name', 'step', 'selected_filial_id', 'selected_vsp_id']:
                del st.session_state[key]
        st.rerun()
    st.divider()

    st.subheader("🔐 Администрирование")
    admin_access = st.checkbox("Вход в режим администратора", key="admin_checkbox")
    if admin_access:
        if not st.session_state.admin_authenticated:
            pwd = st.text_input("Введите пароль:", type="password", key="admin_password")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Войти", type="primary", use_container_width=True):
                    if pwd == ADMIN_PASSWORD:
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
        if st.session_state.admin_authenticated:
            st.session_state.admin_authenticated = False
            st.session_state.is_admin = False
            st.rerun()

    if st.session_state.admin_authenticated:
        st.divider()
        st.subheader("⚙️ Управление чек-листом")
        tpl_df = db.get_checklist_template()
        if not tpl_df.empty:
            with st.expander("📋 Текущие проверки"):
                for _, row in tpl_df.iterrows():
                    st.markdown(f"**{row['item_order']}.** {row['description']}")

        with st.expander("➕ Добавить проверку"):
            new_desc = st.text_area("Наименование", height=68)
            new_info = st.text_area("Пояснение", height=68)
            if st.button("Добавить", use_container_width=True):
                if new_desc:
                    db.add_template_item(new_desc, new_info)
                    st.rerun()

        with st.expander("✏️ Редактировать/Удалить"):
            if not tpl_df.empty:
                ids = tpl_df['id'].tolist()
                sel_id = st.selectbox("Выберите проверку", ids, format_func=lambda x: f"ID {x} - {tpl_df[tpl_df['id'] == x]['description'].iloc[0][:50]}")
                row = tpl_df[tpl_df['id'] == sel_id].iloc[0]
                edit_desc = st.text_area("Наименование", value=row['description'])
                edit_info = st.text_area("Пояснение", value=row['additional_info'] or "")
                c1, c2 = st.columns(2)
                if c1.button("Обновить"):
                    db.update_template_item(sel_id, edit_desc, edit_info)
                    st.rerun()
                if c2.button("Удалить", type="secondary"):
                    db.delete_template_item(sel_id)
                    st.rerun()

        st.divider()
        st.subheader("📊 Экспорт данных")
        export_df = db.get_export_data()
        if not export_df.empty:
            st.info(f"📈 Записей: {len(export_df)}")
            if st.button("📊 Экспорт в Excel", type="primary"):
                data = export_to_excel(export_df)
                if data:
                    st.download_button("💾 Скачать Excel", data, f"checklist_{datetime.date.today()}.xlsx")
        else:
            st.warning("Нет данных")

# ==============================================================================
# ОСНОВНАЯ ЛОГИКА
# ==============================================================================
st.title("📋 Система контроля качества ВСП")
st.caption("Заполнение чек-листа операционной проверки")

if st.session_state.step == 0:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 📝 Регистрация проверки")
        filials_df = db.get_filials()
        if filials_df.empty:
            st.error("Нет филиалов")
            st.stop()

        filial_names = filials_df['name'].tolist()
        filial_map = dict(zip(filials_df['name'], filials_df['id']))
        cur_filial_idx = 0
        if st.session_state.selected_filial_id:
            for i, (name, fid) in enumerate(filial_map.items()):
                if fid == st.session_state.selected_filial_id:
                    cur_filial_idx = i
                    break
        sel_filial_name = st.selectbox("🏢 Филиал", filial_names, index=cur_filial_idx)
        sel_filial_id = filial_map[sel_filial_name]
        if st.session_state.selected_filial_id != sel_filial_id:
            st.session_state.selected_filial_id = sel_filial_id
            st.session_state.selected_vsp_id = None
            st.rerun()

        vsp_df = db.get_vsp_by_filial(sel_filial_id)
        if vsp_df.empty:
            st.warning("Нет ВСП в выбранном филиале")
            sel_vsp_id = None
        else:
            vsp_names = vsp_df['name'].tolist()
            vsp_map = dict(zip(vsp_df['name'], vsp_df['id']))
            cur_vsp_idx = 0
            if st.session_state.selected_vsp_id:
                for i, (name, vid) in enumerate(vsp_map.items()):
                    if vid == st.session_state.selected_vsp_id:
                        cur_vsp_idx = i
                        break
            sel_vsp_name = st.selectbox("🏪 ВСП", vsp_names, index=cur_vsp_idx)
            sel_vsp_id = vsp_map[sel_vsp_name]
            st.session_state.selected_vsp_id = sel_vsp_id

        with st.form("reg_form"):
            st.text_input("👤 ФИО", value=st.session_state.user_name, disabled=True)
            op_date = st.date_input("📅 Дата", datetime.date.today(), format="DD.MM.YYYY")
            submitted = st.form_submit_button("▶️ НАЧАТЬ ЗАПОЛНЕНИЕ", type="primary", use_container_width=True)
            if submitted and sel_vsp_id:
                sid = db.create_session(st.session_state.user_name, sel_filial_id, sel_vsp_id, op_date)
                st.session_state.current_session_id = sid
                st.session_state.step = 1
                st.rerun()

elif st.session_state.step == 1:
    if "current_session_id" not in st.session_state:
        st.error("Сессия не найдена")
        st.session_state.step = 0
        st.rerun()

    sid = st.session_state.current_session_id
    sdata = db.get_session_data(sid)
    if not sdata:
        st.error("Данные сессии отсутствуют")
        st.stop()

    template = db.get_checklist_template()
    if template.empty:
        st.warning("Шаблон пуст")
        st.stop()

    saved = sdata['answers']
    if "temp_answers" not in st.session_state:
        st.session_state.temp_answers = copy.deepcopy(saved)

    # Получаем названия филиала и ВСП для отображения
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        if db.use_postgres:
            cur.execute(f"""
                SELECT f.name, v.name
                FROM {db.schema}.checklist_sessions s
                JOIN {db.schema}.filials f ON s.filial_id = f.id
                JOIN {db.schema}.vsp v ON s.vsp_id = v.id
                WHERE s.id = %s
            """, (sid,))
            row = cur.fetchone()
            filial_name, vsp_name = row['name'], row['name_1'] if db.use_postgres else row[1]  # упростим
            # лучше так:
            # filial_name = row['name']
            # vsp_name = row['name_1'] но зависит от алиасов
            # перепишем запрос с алиасами
            cur.execute(f"""
                SELECT f.name as fname, v.name as vname
                FROM {db.schema}.checklist_sessions s
                JOIN {db.schema}.filials f ON s.filial_id = f.id
                JOIN {db.schema}.vsp v ON s.vsp_id = v.id
                WHERE s.id = %s
            """, (sid,))
            row = cur.fetchone()
            filial_name = row['fname']
            vsp_name = row['vname']
        else:
            cur.execute("""
                SELECT f.name, v.name
                FROM checklist_sessions s
                JOIN filials f ON s.filial_id = f.id
                JOIN vsp v ON s.vsp_id = v.id
                WHERE s.id = ?
            """, (sid,))
            row = cur.fetchone()
            filial_name = row[0]
            vsp_name = row[1]
        conn.close()
    except Exception as e:
        filial_name, vsp_name = "?", "?"

    st.subheader(f"📋 Чек-лист: {filial_name} / {vsp_name}")
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"**🏢 Филиал:** {filial_name}")
    col2.markdown(f"**🏪 ВСП:** {vsp_name}")
    col3.markdown(f"**📅 Дата:** {sdata['info']['operation_date']}")
    st.divider()

    st.markdown("### ✅ Список проверок")
    header = st.columns([1, 5, 2, 1])
    header[0].markdown("**№**")
    header[1].markdown("**Наименование проверки**")
    header[2].markdown("**Доп. информация**")
    header[3].markdown("**Выполнено**")
    st.markdown("---")

    for _, row in template.iterrows():
        item_id = row['id']
        order = row['item_order']
        desc = row['description']
        add_info = row['additional_info']
        current = st.session_state.temp_answers.get(item_id, saved.get(item_id, False))

        cols = st.columns([1, 5, 2, 1])
        cols[0].write(f"**{order}**")
        cols[1].markdown(desc)

        with cols[2]:
            if add_info and add_info.strip():
                # Используем popover с простым текстом (копирование через выделение)
                with st.popover("ℹ️ Показать пояснение", use_container_width=True):
                    st.markdown(f"**Пояснение к проверке:**")
                    st.code(add_info, language="text", line_numbers=False)
                    st.caption("💡 Выделите текст мышкой и нажмите Ctrl+C для копирования")
            else:
                st.markdown("—")

        with cols[3]:
            new_val = st.checkbox(" ", value=current, key=f"chk_{item_id}", label_visibility="collapsed")
            if new_val != current:
                st.session_state.temp_answers[item_id] = new_val
            st.markdown("🟢 Выполнено" if new_val else "⚪ Не выполнено")

        st.markdown("---")

    colA, colB, colC = st.columns([1, 1, 2])
    if colA.button("🔙 Назад", use_container_width=True):
        db.save_answers(sid, st.session_state.temp_answers)
        st.session_state.step = 0
        del st.session_state.current_session_id
        del st.session_state.temp_answers
        st.rerun()
    if colB.button("💾 Сохранить", use_container_width=True):
        db.save_answers(sid, st.session_state.temp_answers)
        st.success("✅ Сохранено")
        time.sleep(0.5)
        st.rerun()
    if colC.button("✅ ЗАВЕРШИТЬ", type="primary", use_container_width=True):
        db.save_answers(sid, st.session_state.temp_answers)
        st.success("🎉 Чек-лист успешно завершен!")
        st.balloons()
        st.session_state.step = 0
        del st.session_state.current_session_id
        del st.session_state.temp_answers
        time.sleep(2)
        st.rerun()