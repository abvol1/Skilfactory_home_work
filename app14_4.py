import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import datetime
from typing import Dict, Any, Optional
import copy
import time

st.set_page_config(page_title="Чек-лист ВСП", layout="wide", initial_sidebar_state="expanded", page_icon="📋")

# Проверка openpyxl для Excel
try:
    from openpyxl import Workbook
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    st.warning("Для экспорта в Excel установите: pip install openpyxl")

# ==============================================================================
# 1. КОНФИГУРАЦИЯ POSTGRESQL
# ==============================================================================
PG_CONFIG = {
    "host": "localhost",      # ЗАМЕНИТЕ НА ВАШ ХОСТ
    "port": 5432,
    "database": "checklist_db",
    "user": "postgres",
    "password": "password",
    "schema": "public"
}
ADMIN_PASSWORD = "admin123"

# ==============================================================================
# 2. КЛАСС РАБОТЫ С БД (ТОЛЬКО POSTGRESQL)
# ==============================================================================
class DatabaseManager:
    def __init__(self):
        self.schema = PG_CONFIG['schema']
        self._connection = None
        self._cursor = None

    def _get_connection(self):
        if self._connection is None:
            self._connection = psycopg2.connect(
                host=PG_CONFIG['host'],
                port=PG_CONFIG['port'],
                dbname=PG_CONFIG['database'],
                user=PG_CONFIG['user'],
                password=PG_CONFIG['password']
            )
        return self._connection

    def _get_cursor(self):
        if self._cursor is None:
            self._cursor = self._get_connection().cursor(cursor_factory=RealDictCursor)
        return self._cursor

    def _reset_cursor(self):
        if self._cursor:
            self._cursor.close()
            self._cursor = None

    def _reset_connection(self):
        self._reset_cursor()
        if self._connection:
            self._connection.close()
            self._connection = None

    def close(self):
        self._reset_connection()

    def _execute(self, query: str, params=None, fetch_one=False, fetch_all=False, commit=True):
        try:
            cur = self._get_cursor()
            cur.execute(query, params or ())
            result = None
            if fetch_one:
                result = cur.fetchone()
            elif fetch_all:
                result = cur.fetchall()
            if commit:
                self._get_connection().commit()
            return result
        except Exception as e:
            self._reset_cursor()
            self._reset_connection()
            raise e

    def _to_df(self, query: str, params=None) -> pd.DataFrame:
        try:
            return pd.read_sql_query(query, self._get_connection(), params=params or ())
        except Exception as e:
            self._reset_connection()
            raise e

    def init_db(self):
        conn = self._get_connection()
        cur = self._get_cursor()
        # Создание таблиц
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.schema}.users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                name_filial VARCHAR(255)
            )
        """)
        cur.execute(f"""
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
        # Добавляем колонки, если их нет (для старых БД)
        cur.execute(f"""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name='checklist_templates' AND table_schema='{self.schema}'
        """)
        existing = [row['column_name'] for row in cur.fetchall()]
        if 'filter_value' not in existing:
            cur.execute(f"ALTER TABLE {self.schema}.checklist_templates ADD COLUMN filter_value TEXT")
        if 'events_value' not in existing:
            cur.execute(f"ALTER TABLE {self.schema}.checklist_templates ADD COLUMN events_value TEXT")

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.schema}.filials (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL
            )
        """)
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.schema}.vsp (
                id SERIAL PRIMARY KEY,
                filial_id INTEGER REFERENCES {self.schema}.filials(id),
                name VARCHAR(255) NOT NULL
            )
        """)
        cur.execute(f"""
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
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.schema}.checklist_answers (
                id SERIAL PRIMARY KEY,
                session_id INTEGER REFERENCES {self.schema}.checklist_sessions(id) ON DELETE CASCADE,
                template_item_id INTEGER REFERENCES {self.schema}.checklist_templates(id),
                is_completed BOOLEAN DEFAULT FALSE,
                UNIQUE(session_id, template_item_id)
            )
        """)
        conn.commit()
        self._migrate_existing_sessions()
        self._add_sample_users()

    def _migrate_existing_sessions(self):
        """Обновляем старые сессии: заменяем логин на ФИО"""
        try:
            cur = self._get_cursor()
            cur.execute(f"""
                UPDATE {self.schema}.checklist_sessions s
                SET user_name = u.full_name
                FROM {self.schema}.users u
                WHERE s.user_name = u.name
            """)
            self._get_connection().commit()
        except Exception as e:
            print(f"Миграция не требуется или ошибка: {e}")

    def _add_sample_users(self):
        cur = self._get_cursor()
        cur.execute(f"SELECT COUNT(*) as cnt FROM {self.schema}.users")
        count = cur.fetchone()['cnt']
        if count == 0:
            users = [
                ('go_ivanov_av', 'Иванов Александр Владимирович', 'Центральный офис'),
                ('go_petrov_iv', 'Петров Игорь Викторович', 'Филиал Север'),
                ('go_sidorov_nn', 'Сидоров Николай Николаевич', 'Филиал Юг'),
                ('test_user', 'Тестовый Пользователь', 'Центральный офис'),
            ]
            for name, full_name, filial in users:
                cur.execute(f"INSERT INTO {self.schema}.users (name, full_name, name_filial) VALUES (%s, %s, %s)",
                            (name, full_name, filial))
            self._get_connection().commit()

    # ----- Основные методы -----
    def get_filials(self) -> pd.DataFrame:
        return self._to_df(f"SELECT id, name FROM {self.schema}.filials ORDER BY name")

    def get_vsp_by_filial(self, filial_id: int) -> pd.DataFrame:
        return self._to_df(f"SELECT id, name FROM {self.schema}.vsp WHERE filial_id = %s ORDER BY name", (filial_id,))

    def get_all_vsp(self) -> pd.DataFrame:
        return self._to_df(f"SELECT id, name, filial_id FROM {self.schema}.vsp ORDER BY name")

    def get_checklist_template(self) -> pd.DataFrame:
        return self._to_df(f"SELECT id, item_order, description, additional_info, filter_value, events_value FROM {self.schema}.checklist_templates ORDER BY item_order")

    def add_template_item(self, description: str, additional_info: str, filter_value: str = "", events_value: str = ""):
        row = self._execute(f"SELECT COALESCE(MAX(item_order), 0) + 1 as next_order FROM {self.schema}.checklist_templates", fetch_one=True)
        next_order = row['next_order'] if row else 1
        self._execute(f"""
            INSERT INTO {self.schema}.checklist_templates (section_name, item_order, description, additional_info, filter_value, events_value)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, ('Основной', next_order, description, additional_info, filter_value, events_value))

    def update_template_item(self, item_id: int, description: str, additional_info: str, filter_value: str = "", events_value: str = ""):
        self._execute(f"""
            UPDATE {self.schema}.checklist_templates
            SET description = %s, additional_info = %s, filter_value = %s, events_value = %s
            WHERE id = %s
        """, (description, additional_info, filter_value, events_value, item_id))

    def delete_template_item(self, item_id: int):
        self._execute(f"DELETE FROM {self.schema}.checklist_answers WHERE template_item_id = %s", (item_id,))
        self._execute(f"DELETE FROM {self.schema}.checklist_templates WHERE id = %s", (item_id,))

    def create_session(self, user_full_name: str, filial_id: int, vsp_id: int, op_date, status='draft') -> int:
        cur = self._get_cursor()
        cur.execute(f"""
            INSERT INTO {self.schema}.checklist_sessions (user_name, filial_id, vsp_id, operation_date, status)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (user_full_name, filial_id, vsp_id, op_date, status))
        self._get_connection().commit()
        return cur.fetchone()['id']

    def check_user_by_name(self, name: str):
        try:
            df = self._to_df(f"SELECT full_name, name_filial FROM {self.schema}.users WHERE LOWER(name) = LOWER(%s)", (name,))
            if not df.empty:
                return True, df.iloc[0]['full_name'], df.iloc[0].get('name_filial', None)
            return False, None, None
        except Exception:
            return False, None, None

    def update_session_status(self, session_id: int, status: str):
        self._execute(f"UPDATE {self.schema}.checklist_sessions SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s", (status, session_id))

    def get_user_draft_sessions(self, full_name: str) -> pd.DataFrame:
        return self._to_df(f"""
            SELECT s.id, s.operation_date, f.name as filial_name, v.name as vsp_name, 
                   s.updated_at, COUNT(a.id) as completed_count,
                   (SELECT COUNT(*) FROM {self.schema}.checklist_templates) as total_count
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id = f.id
            JOIN {self.schema}.vsp v ON s.vsp_id = v.id
            LEFT JOIN {self.schema}.checklist_answers a ON s.id = a.session_id AND a.is_completed = true
            WHERE s.user_name = %s AND s.status = 'draft'
            GROUP BY s.id, f.name, v.name, s.operation_date, s.updated_at
            ORDER BY s.updated_at DESC
        """, (full_name,))

    def get_last_user_session_data(self, full_name: str) -> Optional[Dict]:
        df = self._to_df(f"""
            SELECT f.id as filial_id, f.name as filial_name, v.id as vsp_id, v.name as vsp_name
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id = f.id
            JOIN {self.schema}.vsp v ON s.vsp_id = v.id
            WHERE s.user_name = %s AND s.status = 'completed'
            ORDER BY s.created_at DESC LIMIT 1
        """, (full_name,))
        return df.iloc[0].to_dict() if not df.empty else None

    def get_last_user_any_session_data(self, full_name: str) -> Optional[Dict]:
        df = self._to_df(f"""
            SELECT f.id as filial_id, f.name as filial_name, v.id as vsp_id, v.name as vsp_name
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id = f.id
            JOIN {self.schema}.vsp v ON s.vsp_id = v.id
            WHERE s.user_name = %s
            ORDER BY s.created_at DESC LIMIT 1
        """, (full_name,))
        return df.iloc[0].to_dict() if not df.empty else None

    def get_session_data(self, session_id: int) -> Optional[Dict]:
        cur = self._get_cursor()
        cur.execute(f"SELECT * FROM {self.schema}.checklist_sessions WHERE id = %s", (session_id,))
        row = cur.fetchone()
        if not row:
            return None
        session_info = dict(row)
        cur.execute(f"SELECT template_item_id, is_completed FROM {self.schema}.checklist_answers WHERE session_id = %s", (session_id,))
        answers = {row['template_item_id']: row['is_completed'] for row in cur.fetchall()}
        return {"info": session_info, "answers": answers}

    def save_answers(self, session_id: int, answers: Dict[int, bool]):
        cur = self._get_cursor()
        for item_id, is_completed in answers.items():
            cur.execute(f"""
                INSERT INTO {self.schema}.checklist_answers (session_id, template_item_id, is_completed)
                VALUES (%s, %s, %s)
                ON CONFLICT (session_id, template_item_id) DO UPDATE SET is_completed = EXCLUDED.is_completed
            """, (session_id, item_id, is_completed))
        cur.execute(f"UPDATE {self.schema}.checklist_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = %s", (session_id,))
        self._get_connection().commit()

    def get_export_data(self) -> pd.DataFrame:
        return self._to_df(f"""
            SELECT s.id as session_id, s.user_name as ФИО, f.name as Филиал, v.name as ВСП,
                   s.operation_date as Дата_проверки,
                   CASE s.status WHEN 'completed' THEN 'Завершена' WHEN 'draft' THEN 'Черновик' ELSE s.status END as Статус,
                   s.created_at as Дата_создания, s.updated_at as Дата_обновления,
                   COUNT(a.id) as Выполнено_проверок,
                   (SELECT COUNT(*) FROM {self.schema}.checklist_templates) as Всего_проверок
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id = f.id
            JOIN {self.schema}.vsp v ON s.vsp_id = v.id
            LEFT JOIN {self.schema}.checklist_answers a ON s.id = a.session_id AND a.is_completed = true
            GROUP BY s.id, f.name, v.name, s.user_name, s.operation_date, s.status, s.created_at, s.updated_at
            ORDER BY s.created_at DESC
        """)

    def get_user_sessions(self, full_name: str) -> pd.DataFrame:
        return self._to_df(f"""
            SELECT s.id, s.operation_date as "Дата проверки", f.name as "Филиал", v.name as "ВСП",
                   CASE s.status WHEN 'completed' THEN 'Завершена' WHEN 'draft' THEN 'Черновик' ELSE s.status END as "Статус",
                   s.created_at as "Дата создания", s.updated_at as "Дата обновления",
                   COUNT(a.id) as "Выполнено проверок",
                   (SELECT COUNT(*) FROM {self.schema}.checklist_templates) as "Всего проверок"
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id = f.id
            JOIN {self.schema}.vsp v ON s.vsp_id = v.id
            LEFT JOIN {self.schema}.checklist_answers a ON s.id = a.session_id AND a.is_completed = true
            WHERE s.user_name = %s
            GROUP BY s.id, f.name, v.name, s.operation_date, s.status, s.created_at, s.updated_at
            ORDER BY s.created_at DESC
        """, (full_name,))

    def get_admin_analytics(self, filial_id: int = None, vsp_id: int = None,
                            date_from: datetime.date = None, date_to: datetime.date = None) -> pd.DataFrame:
        conditions = []
        params = []
        if filial_id:
            conditions.append("s.filial_id = %s")
            params.append(filial_id)
        if vsp_id:
            conditions.append("s.vsp_id = %s")
            params.append(vsp_id)
        if date_from:
            conditions.append("s.operation_date >= %s")
            params.append(date_from)
        if date_to:
            conditions.append("s.operation_date <= %s")
            params.append(date_to)
        where_clause = " AND ".join(conditions) if conditions else "1=1"

        sessions = self._to_df(f"""
            SELECT s.id as session_id, s.user_name as ФИО, f.name as Филиал, v.name as ВСП,
                   s.operation_date as Дата, s.status as Статус,
                   s.created_at as Дата_создания, s.updated_at as Дата_обновления
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id = f.id
            JOIN {self.schema}.vsp v ON s.vsp_id = v.id
            WHERE {where_clause}
            ORDER BY s.operation_date DESC, f.name, v.name
        """, tuple(params) if params else None)

        if sessions.empty:
            return sessions

        template = self.get_checklist_template()
        if template.empty:
            return sessions

        all_answers = []
        for sid in sessions['session_id']:
            data = self.get_session_data(sid)
            answers = data['answers'] if data else {}
            row = {'session_id': sid}
            for _, tpl in template.iterrows():
                row[f"check_{tpl['id']}"] = answers.get(tpl['id'], False)
            all_answers.append(row)
        answers_df = pd.DataFrame(all_answers)
        result = sessions.merge(answers_df, on='session_id', how='left')
        return result

# ==============================================================================
# 3. ИНИЦИАЛИЗАЦИЯ
# ==============================================================================
st.markdown("""
<style>
    div[data-testid="stCheckbox"] label span { transform: scale(1.5); margin-right: 12px; }
    div[data-testid="stCheckbox"] label { font-size: 16px; padding: 5px 0; }
</style>
""", unsafe_allow_html=True)

db = DatabaseManager()
db.init_db()

def seed_initial_data():
    if len(db.get_filials()) == 0:
        cur = db._get_cursor()
        filials = ['Центральный офис', 'Филиал Север', 'Филиал Юг', 'Филиал Запад', 'Филиал Восток']
        for f in filials:
            cur.execute(f"INSERT INTO {db.schema}.filials (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (f,))
        db._get_connection().commit()
        df_f = db.get_filials()
        vsp_counter = 1
        for _, row in df_f.iterrows():
            fid = row['id']
            for i in range(3):
                vsp_name = f"ВСП {vsp_counter:04d}"
                cur.execute(f"INSERT INTO {db.schema}.vsp (filial_id, name) VALUES (%s, %s)", (fid, vsp_name))
                vsp_counter += 1
        db._get_connection().commit()

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

# Инициализация session_state
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
    if st.session_state.user_full_name and not st.session_state.data_loaded and st.session_state.auth_valid:
        last_data = db.get_last_user_session_data(st.session_state.user_full_name)
        if not last_data:
            last_data = db.get_last_user_any_session_data(st.session_state.user_full_name)
        if last_data:
            if not st.session_state.last_filial_name:
                st.session_state.last_filial_name = last_data['filial_name']
            st.session_state.last_vsp_name = last_data['vsp_name']
            st.session_state.last_vsp_id = last_data['vsp_id']
            if not st.session_state.selected_vsp_id:
                st.session_state.selected_vsp_id = last_data['vsp_id']
            if not st.session_state.selected_filial_id:
                st.session_state.selected_filial_id = last_data['filial_id']
            if not st.session_state.last_filial_id:
                st.session_state.last_filial_id = last_data['filial_id']
            st.session_state.update_counter += 1
        st.session_state.data_loaded = True

load_last_user_data()

# ==============================================================================
# 4. БОКОВАЯ ПАНЕЛЬ
# ==============================================================================
with st.sidebar:
    st.header("👤 Информация")
    if st.session_state.auth_valid and st.session_state.user_full_name:
        st.markdown(f"**Пользователь:** {st.session_state.user_full_name}")
        st.caption(f"Логин: {st.session_state.user_name}")
        if st.button("🔄 Сменить пользователя", use_container_width=True):
            for key in ['user_name','user_full_name','auth_valid','last_filial_name','last_vsp_name',
                        'last_filial_id','last_vsp_id','selected_filial_id','selected_vsp_id',
                        'step','data_loaded','update_counter','current_session_id','temp_answers','resume_session_id']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    else:
        st.info("👋 Пользователь не выбран")

    st.divider()
    st.subheader("🔐 Администрирование")
    admin_access = st.checkbox("Вход в режим администратора", key="admin_checkbox")
    if admin_access:
        if not st.session_state.admin_authenticated:
            pwd = st.text_input("Введите пароль:", type="password", key="admin_password")
            if st.button("Войти", type="primary", use_container_width=True):
                if pwd == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                    st.success("✅ Режим администратора активирован!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Неверный пароль!")
        else:
            st.success("✅ Режим администратора активен")
            if st.button("Выйти", use_container_width=True):
                st.session_state.admin_authenticated = False
                st.rerun()
    else:
        if st.session_state.admin_authenticated:
            st.session_state.admin_authenticated = False
            st.rerun()

    if st.session_state.admin_authenticated:
        st.divider()
        st.subheader("⚙️ Управление чек-листом")
        tpl = db.get_checklist_template()
        if not tpl.empty:
            with st.expander("📋 Текущие проверки"):
                for _, r in tpl.iterrows():
                    st.markdown(f"**{r['item_order']}.** {r['description']}")
        with st.expander("➕ Добавить проверку"):
            new_desc = st.text_area("Наименование", height=68)
            new_info = st.text_area("Описание", height=68)
            new_filter = st.text_area("🔍 Фильтр")
            new_events = st.text_area("📌 Мероприятия", height=68)
            if st.button("➕ Добавить", use_container_width=True, type="primary"):
                if new_desc:
                    db.add_template_item(new_desc, new_info, new_filter, new_events)
                    st.success("✅ Добавлено!")
                    st.rerun()
                else:
                    st.error("Введите наименование!")
        with st.expander("✏️ Редактировать/Удалить"):
            if not tpl.empty:
                sel_id = st.selectbox("Выберите проверку", tpl['id'].tolist(),
                                      format_func=lambda x: f"ID {x} - {tpl[tpl['id']==x]['description'].iloc[0][:50]}")
                row = tpl[tpl['id'] == sel_id].iloc[0]
                e_desc = st.text_area("Наименование", value=row['description'])
                e_info = st.text_area("Описание", value=row['additional_info'] or "")
                e_filter = st.text_area("Фильтр", value=row['filter_value'] or "")
                e_events = st.text_area("Мероприятия", value=row['events_value'] or "")
                c1, c2 = st.columns(2)
                if c1.button("💾 Обновить", use_container_width=True):
                    db.update_template_item(sel_id, e_desc, e_info, e_filter, e_events)
                    st.success("Обновлено!")
                    st.rerun()
                if c2.button("🗑️ Удалить", use_container_width=True):
                    db.delete_template_item(sel_id)
                    st.success("Удалено!")
                    st.rerun()

        st.divider()
        st.subheader("📊 Экспорт данных")
        exp_df = db.get_export_data()
        if not exp_df.empty:
            if st.button("📊 Экспорт в Excel", use_container_width=True):
                if not OPENPYXL_AVAILABLE:
                    st.error("Установите openpyxl")
                else:
                    path = "/tmp/export.xlsx"
                    with pd.ExcelWriter(path, engine='openpyxl') as writer:
                        exp_df.to_excel(writer, sheet_name='Отчет', index=False)
                    with open(path, 'rb') as f:
                        st.download_button("💾 Скачать", f.read(), f"checklist_{datetime.date.today()}.xlsx", use_container_width=True)
        else:
            st.warning("Нет данных")

# ==============================================================================
# 5. ОСНОВНОЙ ИНТЕРФЕЙС (ВКЛАДКИ)
# ==============================================================================
st.title("📋 Чек-лист операционной проверки ВСП")
st.caption("Заполнение данных о пользователе чек-листа операционной проверки")

if st.session_state.admin_authenticated:
    tab_history, tab_main, tab_analytics = st.tabs(["📜 История проверок", "📝 Новая проверка", "📊 Аналитика"])
else:
    tab_history, tab_main = st.tabs(["📜 История проверок", "📝 Новая проверка"])
    tab_analytics = None

# ---------- Вкладка Новая проверка ----------
with tab_main:
    if st.session_state.step == 0:
        if st.session_state.auth_valid and st.session_state.user_full_name:
            drafts = db.get_user_draft_sessions(st.session_state.user_full_name)
            if not drafts.empty:
                drafts = drafts[drafts['operation_date'] == datetime.date.today()]
        else:
            drafts = pd.DataFrame()

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if not drafts.empty:
                st.info(f"📌 У вас есть {len(drafts)} сохраненных черновиков")
                for _, d in drafts.iterrows():
                    with st.container():
                        a,b,c = st.columns([3,2,1])
                        a.markdown(f"**{d['filial_name']} / {d['vsp_name']}**")
                        a.caption(f"📅 {d['operation_date']}")
                        b.caption(f"✅ {d['completed_count']}/{d['total_count']}")
                        if c.button("📂 Продолжить", key=f"resume_{d['id']}", use_container_width=True):
                            st.session_state.current_session_id = d['id']
                            st.session_state.step = 1
                            st.rerun()
                        st.divider()

            filials_df = db.get_filials()
            if not filials_df.empty:
                filial_names = filials_df['name'].tolist()
                filial_map = dict(zip(filials_df['name'], filials_df['id']))

                login = st.text_input("👤 Учетная запись сотрудника",
                                      value=st.session_state.user_name if not st.session_state.auth_valid else "",
                                      placeholder="go_ivanov_av",
                                      disabled=st.session_state.auth_valid,
                                      key=f"login_{st.session_state.update_counter}")
                login_norm = login.lower().strip() if login else ""

                if login_norm and login_norm != st.session_state.user_name and not st.session_state.auth_valid:
                    exists, full, fil = db.check_user_by_name(login_norm)
                    if exists:
                        st.session_state.user_name = login_norm
                        st.session_state.user_full_name = full
                        st.session_state.auth_valid = True
                        if fil and fil in filial_names:
                            st.session_state.last_filial_name = fil
                            st.session_state.selected_filial_id = filial_map[fil]
                            st.session_state.last_filial_id = filial_map[fil]
                            st.session_state.update_counter += 1
                        st.success(f"✅ Добро пожаловать, {full}!")
                        last = db.get_last_user_session_data(full)
                        if last:
                            if not st.session_state.last_filial_name:
                                st.session_state.last_filial_name = last['filial_name']
                            st.session_state.last_vsp_name = last['vsp_name']
                            st.session_state.last_vsp_id = last['vsp_id']
                            if not st.session_state.selected_vsp_id:
                                st.session_state.selected_vsp_id = last['vsp_id']
                            if not st.session_state.selected_filial_id:
                                st.session_state.selected_filial_id = last['filial_id']
                            st.session_state.update_counter += 1
                        st.rerun()
                    else:
                        st.error(f"❌ Пользователь '{login_norm}' не найден!")

                if st.session_state.auth_valid:
                    st.info(f"👤 **Авторизован:** {st.session_state.user_full_name}")
                    st.caption(f"Логин: {st.session_state.user_name}")
                    if st.button("🔄 Сменить пользователя", key="change_btn", use_container_width=True):
                        for key in ['user_name','user_full_name','auth_valid','last_filial_name','last_vsp_name',
                                    'last_filial_id','last_vsp_id','selected_filial_id','selected_vsp_id',
                                    'step','data_loaded','update_counter','current_session_id','temp_answers','resume_session_id']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()
                    st.divider()

                if st.session_state.auth_valid:
                    cur_idx = 0
                    if st.session_state.last_filial_name and st.session_state.last_filial_name in filial_names:
                        cur_idx = filial_names.index(st.session_state.last_filial_name)
                    sel_filial = st.selectbox("🏢 Филиал", filial_names, index=cur_idx,
                                              key=f"filial_{st.session_state.update_counter}")
                    sel_filial_id = filial_map[sel_filial]
                    st.session_state.last_filial_name = sel_filial
                    st.session_state.last_filial_id = sel_filial_id

                    if st.session_state.selected_filial_id != sel_filial_id:
                        st.session_state.selected_filial_id = sel_filial_id
                        st.session_state.selected_vsp_id = None
                        st.session_state.last_vsp_name = None
                        st.session_state.last_vsp_id = None
                        st.rerun()

                    vsp_df = db.get_vsp_by_filial(sel_filial_id)
                    if not vsp_df.empty:
                        vsp_names = vsp_df['name'].tolist()
                        vsp_map = dict(zip(vsp_df['name'], vsp_df['id']))
                        vsp_idx = 0
                        if st.session_state.last_vsp_name and st.session_state.last_vsp_name in vsp_names:
                            vsp_idx = vsp_names.index(st.session_state.last_vsp_name)
                        elif st.session_state.last_vsp_id:
                            for i, (name, vid) in enumerate(vsp_map.items()):
                                if vid == st.session_state.last_vsp_id:
                                    vsp_idx = i
                                    st.session_state.last_vsp_name = name
                                    break
                        sel_vsp = st.selectbox("🏪 ВСП", vsp_names, index=vsp_idx,
                                               key=f"vsp_{st.session_state.update_counter}")
                        sel_vsp_id = vsp_map[sel_vsp]
                        st.session_state.last_vsp_name = sel_vsp
                        st.session_state.last_vsp_id = sel_vsp_id
                        st.session_state.selected_vsp_id = sel_vsp_id
                    else:
                        st.warning("Нет ВСП")
                        sel_vsp_id = None

                    with st.form("new_session_form"):
                        op_date = st.date_input("📅 Дата", value=datetime.date.today(), format="DD.MM.YYYY", disabled=True)
                        submitted = st.form_submit_button("▶️ НАЧАТЬ ЗАПОЛНЕНИЕ", type="primary", use_container_width=True)
                        if submitted and sel_vsp_id:
                            sid = db.create_session(st.session_state.user_full_name, sel_filial_id, sel_vsp_id, op_date, 'draft')
                            st.session_state.current_session_id = sid
                            st.session_state.step = 1
                            st.rerun()
                        elif submitted:
                            st.error("Выберите ВСП!")
            else:
                st.error("Нет филиалов")

# ---------- Вкладка История проверок ----------
with tab_history:
    st.markdown("### 📜 История ваших проверок")
    if st.session_state.auth_valid and st.session_state.user_full_name:
        hist = db.get_user_sessions(st.session_state.user_full_name)
        if not hist.empty:
            st.dataframe(hist, use_container_width=True, height=400)
            sel_sess = st.selectbox("Выберите сессию", hist['id'].tolist(),
                                     format_func=lambda x: f"Сессия #{x} - {hist[hist['id']==x]['Дата проверки'].iloc[0]}")
            if st.button("📋 Показать результаты"):
                data = db.get_session_data(sel_sess)
                if data:
                    with st.expander(f"Результаты проверки #{sel_sess}", expanded=True):
                        st.markdown(f"**Дата:** {data['info']['operation_date']}")
                        st.markdown(f"**Статус:** {'✔️ Завершена' if data['info']['status']=='completed' else '📄 Черновик'}")
                        tpl = db.get_checklist_template()
                        ans = data['answers']
                        for _, r in tpl.iterrows():
                            st.markdown(f"{'✅' if ans.get(r['id'], False) else '❌'} {r['description']}")
                else:
                    st.error("Не удалось загрузить")
        else:
            st.info("Нет завершённых проверок")
    else:
        st.warning("Введите учётную запись")

# ---------- Вкладка Аналитика (только для админа) ----------
if tab_analytics is not None:
    with tab_analytics:
        st.markdown("## 📊 Детальная аналитика по проверкам")
        st.caption("Фильтрация по филиалу, ВСП, датам. Статусы проверок: ✅ выполнено, ❌ не выполнено")

        filials_df = db.get_filials()
        if not filials_df.empty:
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                filial_opts = ["Все"] + filials_df['name'].tolist()
                sel_filial_name = st.selectbox("Филиал", filial_opts, key="adm_filial")
                filial_id = None if sel_filial_name == "Все" else filials_df[filials_df['name']==sel_filial_name]['id'].iloc[0]
            with col_f2:
                if filial_id:
                    vsp_df = db.get_vsp_by_filial(filial_id)
                else:
                    vsp_df = db.get_all_vsp()
                vsp_opts = ["Все"] + vsp_df['name'].tolist() if not vsp_df.empty else ["Все"]
                sel_vsp_name = st.selectbox("ВСП", vsp_opts, key="adm_vsp")
                vsp_id = None if sel_vsp_name == "Все" else vsp_df[vsp_df['name']==sel_vsp_name]['id'].iloc[0]
            with col_f3:
                date_from = st.date_input("Дата от", value=None, key="adm_date_from")
            with col_f4:
                date_to = st.date_input("Дата до", value=None, key="adm_date_to")

            if st.button("🔍 Показать данные", use_container_width=True):
                with st.spinner("Загрузка..."):
                    analytics = db.get_admin_analytics(filial_id, vsp_id, date_from, date_to)
                if analytics.empty:
                    st.info("Нет данных по фильтрам")
                else:
                    st.success(f"Найдено {len(analytics)} сессий")
                    template = db.get_checklist_template()
                    # Преобразуем булевы в иконки
                    for _, tpl in template.iterrows():
                        col_name = f"check_{tpl['id']}"
                        if col_name in analytics.columns:
                            analytics[col_name] = analytics[col_name].apply(lambda x: "✅" if x else "❌")
                    # Переименовываем колонки
                    rename = {f"check_{tpl['id']}": f"{tpl['item_order']}. {tpl['description'][:50]}" for _, tpl in template.iterrows()}
                    analytics.rename(columns=rename, inplace=True)
                    # Выбираем колонки для отображения
                    base_cols = ['ФИО', 'Филиал', 'ВСП', 'Дата', 'Статус']
                    display_cols = base_cols + [v for v in rename.values() if v in analytics.columns]
                    final_df = analytics[display_cols]
                    st.dataframe(final_df, use_container_width=True, height=500)

                    if st.button("📥 Экспорт аналитики в Excel", key="export_analytics"):
                        if not OPENPYXL_AVAILABLE:
                            st.error("Установите openpyxl")
                        else:
                            path = "/tmp/analytics.xlsx"
                            with pd.ExcelWriter(path, engine='openpyxl') as writer:
                                final_df.to_excel(writer, sheet_name='Аналитика', index=False)
                            with open(path, 'rb') as f:
                                st.download_button("💾 Скачать аналитику", f.read(),
                                                   f"analytics_{datetime.date.today()}.xlsx", use_container_width=True)
        else:
            st.warning("Нет филиалов в БД")

# ---------- Шаг 1: Заполнение чек-листа ----------
if st.session_state.step == 1:
    if "current_session_id" not in st.session_state:
        st.error("Сессия не найдена")
        st.session_state.step = 0
        st.rerun()

    sid = st.session_state.current_session_id
    sess = db.get_session_data(sid)
    if not sess:
        st.error("Данные сессии отсутствуют")
        st.stop()

    template = db.get_checklist_template()
    if template.empty:
        st.warning("Шаблон пуст")
        st.stop()

    saved = sess['answers']
    if "temp_answers" not in st.session_state:
        st.session_state.temp_answers = copy.deepcopy(saved)

    # Получаем филиал и ВСП
    cur = db._get_cursor()
    cur.execute(f"""
        SELECT f.name as filial_name, v.name as vsp_name
        FROM {db.schema}.checklist_sessions s
        JOIN {db.schema}.filials f ON s.filial_id = f.id
        JOIN {db.schema}.vsp v ON s.vsp_id = v.id
        WHERE s.id = %s
    """, (sid,))
    row = cur.fetchone()
    filial_name = row['filial_name'] if row else "?"
    vsp_name = row['vsp_name'] if row else "?"

    st.subheader(f"📋 Чек-лист: {filial_name} / {vsp_name}")
    status_text = "Черновик" if sess['info']['status'] == 'draft' else "Завершена"
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.markdown(f"**👤 Сотрудник:** {sess['info']['user_name']}")
    c2.markdown(f"**🏢 Филиал:** {filial_name}")
    c3.markdown(f"**🏪 ВСП:** {vsp_name}")
    c4.markdown(f"**📅 Дата:** {sess['info']['operation_date']}")
    c5.markdown(f"**📌 Статус:** {status_text}")
    st.divider()
    st.markdown("### ✅ Список проверок")

    header = st.columns([1,5,2,1])
    header[0].markdown("**№**")
    header[1].markdown("**Наименование проверки**")
    header[2].markdown("**Доп. информация**")
    header[3].markdown("**Статус**")
    st.markdown("---")

    for _, row in template.iterrows():
        item_id = row['id']
        order = row['item_order']
        desc = row['description']
        add_info = row['additional_info']
        filter_text = row['filter_value'] if row['filter_value'] else "Не задан"
        events_text = row['events_value'] if row['events_value'] else "Не заданы"
        current = st.session_state.temp_answers.get(item_id, saved.get(item_id, False))

        cols = st.columns([1,5,2,1])
        cols[0].write(f"**{order}**")
        cols[1].markdown(desc)

        with cols[2]:
            with st.popover(f"ℹ️ Подробнее о проверке №{order}", use_container_width=True):
                t1,t2,t3 = st.tabs(["📝 Описание", "🔍 Фильтр", "📌 Мероприятия"])
                with t1:
                    st.markdown("**Описание процедуры:**")
                    st.info(add_info if add_info else "Описание отсутствует")
                with t2:
                    st.markdown("**Фильтр:**")
                    if filter_text != "Не задан":
                        filter_disp = filter_text
                        if "[Дата1]" in filter_text:
                            default_date = datetime.date.today() - datetime.timedelta(days=1)
                            sel_date = st.date_input("📅 Выберите дату", key=f"date_{item_id}", value=default_date)
                            filter_disp = filter_text.replace("[Дата1]", sel_date.strftime("%d.%m.%y"))
                        filter_disp = filter_disp.replace("[РФ]", vsp_name)
                        st.code(filter_disp, language="text")
                        # JS кнопка копирования
                        import streamlit.components.v1 as components
                        js = f"""
                        <div style="margin-top:8px"><button id="copy_{item_id}" style="background:#4CAF50;color:white;padding:8px;border:none;border-radius:5px;width:100%">📋 КОПИРОВАТЬ ФИЛЬТР</button>
                        <div id="status_{item_id}" style="margin-top:5px;font-size:12px;text-align:center"></div>
                        <script>
                        (function(){{
                            var btn=document.getElementById("copy_{item_id}");
                            var statusDiv=document.getElementById("status_{item_id}");
                            var txt={repr(filter_disp)};
                            btn.addEventListener("click",function(){{
                                navigator.clipboard.writeText(txt).then(function(){{
                                    statusDiv.innerHTML="✅ Скопировано!";statusDiv.style.color="green";
                                    setTimeout(function(){{statusDiv.innerHTML="";}},2000);
                                }},function(){{
                                    statusDiv.innerHTML="❌ Ошибка";statusDiv.style.color="red";
                                }});
                            }});
                        }})();
                        </script>
                        """
                        components.html(js, height=100)
                    else:
                        st.info("Фильтр не задан")
                with t3:
                    st.markdown("**Мероприятия:**")
                    st.info(events_text if events_text != "Не заданы" else "Мероприятия не заданы")

        with cols[3]:
            new_val = st.checkbox(" ", value=current, key=f"chk_{item_id}", label_visibility="collapsed")
            if new_val != current:
                st.session_state.temp_answers[item_id] = new_val

        st.markdown("<hr style='margin:2px 0;border:0.5px solid #e0e0e0;'>", unsafe_allow_html=True)

    colA, colB, colC, colD = st.columns([1,1,1,2])
    if colA.button("🔙 Назад", use_container_width=True):
        db.save_answers(sid, st.session_state.temp_answers)
        db.update_session_status(sid, 'draft')
        st.session_state.step = 0
        for k in ['current_session_id','temp_answers','resume_session_id']:
            if k in st.session_state: del st.session_state[k]
        st.rerun()

    if colB.button("💾 Сохранить черновик", use_container_width=True):
        db.save_answers(sid, st.session_state.temp_answers)
        db.update_session_status(sid, 'draft')
        st.success("✅ Черновик сохранён!")
        time.sleep(1)
        st.rerun()

    if colC.button("📋 Предпросмотр", use_container_width=True):
        with st.expander("📄 Предпросмотр", expanded=True):
            completed = sum(st.session_state.temp_answers.values())
            total = len(template)
            st.info(f"Выполнено {completed}/{total} проверок")
            for _, r in template.iterrows():
                status = "✅" if st.session_state.temp_answers.get(r['id'], False) else "❌"
                st.markdown(f"{status} {r['description']}")

    if colD.button("✅ ЗАВЕРШИТЬ ПРОВЕРКУ", type="primary", use_container_width=True):
        completed = sum(st.session_state.temp_answers.values())
        total = len(template)
        if completed < total:
            st.toast(f"⚠️ Выполнено только {completed} из {total} проверок. Заполните все.", icon="❗")
        else:
            db.save_answers(sid, st.session_state.temp_answers)
            db.update_session_status(sid, 'completed')
            st.success("🎉 Отлично! Чек-лист завершён!")
            st.balloons()
            st.session_state.step = 0
            for k in ['current_session_id','temp_answers','resume_session_id']:
                if k in st.session_state: del st.session_state[k]
            time.sleep(2)
            st.rerun()
