
"""
ЧЕК-ЛИСТ ВСП (Streamlit + PostgreSQL)
=====================================
Перед запуском необходимо:
1) Подставить свои параметры подключения в PG_CONFIG.
2) Выполнить SQL-запросы для добавления колонки и таблицы альтернативных настроек
   (см. комментарий в самом начале кода).
3) Установить зависимости: streamlit pandas psycopg2-binary openpyxl
"""
import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
from typing import Dict, Any, Optional
import copy
import time

# =============================================================================
# ПЕРЕД ЗАПУСКОМ ВЫПОЛНИТЕ ВРУЧНУЮ В POSTGRESQL:
# =============================================================================
# 1. Добавить колонку check_name в таблицу filials (если её ещё нет):
#    ALTER TABLE public.filials ADD COLUMN IF NOT EXISTS check_name BOOLEAN NOT NULL DEFAULT FALSE;
#
# 2. Создать таблицу для альтернативных фильтров:
#    CREATE TABLE IF NOT EXISTS public.checklist_alt_templates (
#        id SERIAL PRIMARY KEY,
#        template_item_id INTEGER NOT NULL REFERENCES public.checklist_templates(id) ON DELETE CASCADE,
#        filial_id INTEGER NOT NULL REFERENCES public.filials(id) ON DELETE CASCADE,
#        alt_filter_value TEXT DEFAULT '',
#        alt_additional_info TEXT DEFAULT '',
#        alt_events_value TEXT DEFAULT '',
#        UNIQUE (template_item_id, filial_id)
#    );
# =============================================================================

# =============================================================================
# НАСТРОЙКА СТРАНИЦЫ STREAMLIT
# =============================================================================
st.set_page_config(
    page_title="Чек-лист ВСП",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📋"
)

# =============================================================================
# ПРОВЕРКА НАЛИЧИЯ OPENPYXL ДЛЯ ЭКСПОРТА В EXCEL (НЕОБЯЗАТЕЛЬНО)
# =============================================================================
try:
    from openpyxl import Workbook
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    st.warning("Для экспорта в Excel установите: pip install openpyxl")

# =============================================================================
# 1. КОНФИГУРАЦИЯ ПОДКЛЮЧЕНИЯ К POSTGRESQL – ЗАМЕНИТЕ НА СВОИ ДАННЫЕ
# =============================================================================
PG_CONFIG = {
    "host": "your_host",          # например, "localhost"
    "port": 5432,
    "database": "your_db",
    "user": "your_user",
    "password": "your_password",
    "schema": "public"             # или ваша схема
}

# Пароль для входа в режим администратора
ADMIN_PASSWORD = "admin123"

# =============================================================================
# 2. КЛАСС ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ
#    Содержит все методы для взаимодействия с PostgreSQL.
# =============================================================================
class DatabaseManager:
    """
    Управление подключением к PostgreSQL и выполнение запросов.
    Для простоты используется одно постоянное соединение на всё время жизни приложения.
    """

    def __init__(self):
        self.schema = PG_CONFIG['schema']          # схема (обычно public)
        self._connection = None                    # объект соединения
        self._cursor = None                        # курсор (использует RealDictCursor)

    def _get_connection(self):
        """Возвращает существующее соединение или создаёт новое (один раз)."""
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
        """Возвращает курсор, при необходимости создавая его."""
        if self._cursor is None:
            conn = self._get_connection()
            self._cursor = conn.cursor(cursor_factory=RealDictCursor)
        return self._cursor

    def _reset_cursor(self):
        """Сброс курсора при ошибке."""
        if self._cursor:
            self._cursor.close()
            self._cursor = None

    def _reset_connection(self):
        """Полный сброс соединения (закрывает курсор и соединение)."""
        self._reset_cursor()
        if self._connection:
            self._connection.close()
            self._connection = None

    def close(self):
        """Закрыть все ресурсы при завершении работы."""
        self._reset_connection()

    def _table_name(self, table: str) -> str:
        """Возвращает полное имя таблицы со схемой."""
        return f"{self.schema}.{table}"

    # -------------------------------------------------------------------------
    # Универсальные методы выполнения запросов
    # -------------------------------------------------------------------------
    def _execute(self, query: str, params=None, fetch_one=False, fetch_all=False, commit=True):
        """
        Выполняет SQL-запрос.
        - params: кортеж параметров для %s (защита от инъекций).
        - fetch_one / fetch_all: вернуть одну или все строки.
        - commit: выполнить commit (по умолчанию True).
        """
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
        """Выполняет SELECT и возвращает результат как DataFrame."""
        try:
            conn = self._get_connection()
            return pd.read_sql_query(query, conn, params=params or ())
        except Exception as e:
            self._reset_connection()
            raise e

    # -------------------------------------------------------------------------
    # МЕТОДЫ ДЛЯ РАБОТЫ С ДАННЫМИ
    # -------------------------------------------------------------------------

    # --- Филиалы и ВСП ---
    def get_filials(self) -> pd.DataFrame:
        """Возвращает DataFrame с id, name, check_name (флаг альтернативных настроек)."""
        return self._to_df(
            f"SELECT id, name, check_name FROM {self._table_name('filials')} ORDER BY name"
        )

    def set_filial_check(self, filial_id: int, check_value: bool):
        """Обновляет флаг check_name для филиала."""
        self._execute(
            f"UPDATE {self._table_name('filials')} SET check_name = %s WHERE id = %s",
            (check_value, int(filial_id))
        )

    def get_vsp_by_filial(self, filial_id: int) -> pd.DataFrame:
        """Возвращает список ВСП для заданного филиала."""
        return self._to_df(
            f"SELECT id, name FROM {self._table_name('vsp')} WHERE filial_id = %s ORDER BY name",
            (int(filial_id),)
        )

    # --- Шаблон чек-листа ---
    def get_checklist_template(self) -> pd.DataFrame:
        """Возвращает все пункты шаблона."""
        return self._to_df(
            f"SELECT id, item_order, description, additional_info, filter_value, events_value "
            f"FROM {self._table_name('checklist_templates')} ORDER BY item_order"
        )

    def add_template_item(self, description: str, additional_info: str,
                          filter_value: str = "", events_value: str = ""):
        """Добавляет новый пункт в шаблон (администратором)."""
        row = self._execute(
            f"SELECT COALESCE(MAX(item_order), 0) + 1 AS next_order "
            f"FROM {self._table_name('checklist_templates')}",
            fetch_one=True
        )
        next_order = row['next_order'] if row else 1
        self._execute(
            f"INSERT INTO {self._table_name('checklist_templates')} "
            f"(section_name, item_order, description, additional_info, filter_value, events_value) "
            f"VALUES (%s, %s, %s, %s, %s, %s)",
            ('Основной', next_order, description, additional_info, filter_value, events_value)
        )

    def update_template_item(self, item_id: int, description: str, additional_info: str,
                             filter_value: str = "", events_value: str = ""):
        """Обновляет существующий пункт шаблона."""
        self._execute(
            f"UPDATE {self._table_name('checklist_templates')} "
            f"SET description = %s, additional_info = %s, filter_value = %s, events_value = %s "
            f"WHERE id = %s",
            (description, additional_info, filter_value, events_value, item_id)
        )

    def delete_template_item(self, item_id: int):
        """Удаляет пункт шаблона и все связанные ответы + альтернативные записи."""
        self._execute(f"DELETE FROM {self._table_name('checklist_answers')} WHERE template_item_id = %s", (item_id,))
        self._execute(f"DELETE FROM {self._table_name('checklist_alt_templates')} WHERE template_item_id = %s", (item_id,))
        self._execute(f"DELETE FROM {self._table_name('checklist_templates')} WHERE id = %s", (item_id,))

    # --- Альтернативные настройки для филиалов ---
    def get_alt_template_for_filial(self, filial_id: int) -> pd.DataFrame:
        """Все альтернативные записи для филиала."""
        return self._to_df(
            f"SELECT template_item_id, alt_filter_value, alt_additional_info, alt_events_value "
            f"FROM {self._table_name('checklist_alt_templates')} WHERE filial_id = %s",
            (int(filial_id),)
        )

    def get_alt_template_item(self, filial_id: int, template_item_id: int) -> Optional[Dict]:
        """Возвращает словарь с альтернативными полями или None, если записи нет."""
        return self._execute(
            f"SELECT alt_filter_value, alt_additional_info, alt_events_value "
            f"FROM {self._table_name('checklist_alt_templates')} "
            f"WHERE filial_id = %s AND template_item_id = %s",
            (int(filial_id), int(template_item_id)),
            fetch_one=True
        )

    def upsert_alt_template(self, filial_id: int, template_item_id: int,
                            alt_filter: str, alt_info: str, alt_events: str):
        """Вставляет или обновляет альтернативные поля для пары (филиал, пункт)."""
        self._execute(
            f"INSERT INTO {self._table_name('checklist_alt_templates')} "
            f"(template_item_id, filial_id, alt_filter_value, alt_additional_info, alt_events_value) "
            f"VALUES (%s, %s, %s, %s, %s) "
            f"ON CONFLICT (template_item_id, filial_id) DO UPDATE SET "
            f"alt_filter_value = EXCLUDED.alt_filter_value, "
            f"alt_additional_info = EXCLUDED.alt_additional_info, "
            f"alt_events_value = EXCLUDED.alt_events_value",
            (int(template_item_id), int(filial_id), alt_filter, alt_info, alt_events)
        )

    # --- Сессии проверок ---
    def create_session(self, user_full_name: str, filial_id: int, vsp_id: int,
                       op_date, status='draft') -> int:
        """Создаёт новую сессию и возвращает её ID."""
        row = self._execute(
            f"INSERT INTO {self._table_name('checklist_sessions')} "
            f"(user_name, filial_id, vsp_id, operation_date, status) "
            f"VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (user_full_name, filial_id, vsp_id, op_date, status),
            fetch_one=True
        )
        return row['id']

    def check_user_by_name(self, name: str):
        """
        Проверяет существование пользователя по логину.
        Возвращает (True, full_name, filial_name) или (False, None, None).
        """
        df = self._to_df(
            f"""
            SELECT us.name, us.full_name, f.name AS filial_name
            FROM {self.schema}.users us
            LEFT JOIN {self.schema}.filials f ON us.name_filial::numeric = f.id
            WHERE LOWER(us.name) = LOWER(%s)
            """,
            (name,)
        )
        if not df.empty:
            return True, df.iloc[0]['full_name'], df.iloc[0].get('filial_name')
        return False, None, None

    def update_session_status(self, session_id: int, status: str):
        """Меняет статус сессии: 'draft' или 'completed'."""
        self._execute(
            f"UPDATE {self._table_name('checklist_sessions')} SET status = %s WHERE id = %s",
            (status, session_id)
        )

    def get_user_draft_sessions(self, full_name: str) -> pd.DataFrame:
        """Черновики пользователя (незавершённые сессии)."""
        return self._to_df(
            f"""
            SELECT s.id, s.operation_date, f.name AS filial_name, v.name AS vsp_name,
                   s.updated_at, COUNT(a.id) AS completed_count,
                   (SELECT COUNT(*) FROM {self.schema}.checklist_templates) AS total_count
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id = f.id
            JOIN {self.schema}.vsp v ON s.vsp_id = v.id
            LEFT JOIN {self.schema}.checklist_answers a ON s.id = a.session_id AND a.is_completed = true
            WHERE s.user_name = %s AND s.status = 'draft'
            GROUP BY s.id, f.name, v.name, s.operation_date, s.updated_at
            ORDER BY s.updated_at DESC
            """,
            (full_name,)
        )

    def get_last_user_session_data(self, full_name: str) -> Optional[Dict]:
        """Последняя завершённая сессия пользователя."""
        df = self._to_df(
            f"""
            SELECT f.id AS filial_id, f.name AS filial_name, v.id AS vsp_id, v.name AS vsp_name
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id = f.id
            JOIN {self.schema}.vsp v ON s.vsp_id = v.id
            WHERE s.user_name = %s AND s.status = 'completed'
            ORDER BY s.created_at DESC LIMIT 1
            """,
            (full_name,)
        )
        return df.iloc[0].to_dict() if not df.empty else None

    def get_last_user_any_session_data(self, full_name: str) -> Optional[Dict]:
        """Последняя любая сессия пользователя (черновик или завершённая)."""
        df = self._to_df(
            f"""
            SELECT f.id AS filial_id, f.name AS filial_name, v.id AS vsp_id, v.name AS vsp_name
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id = f.id
            JOIN {self.schema}.vsp v ON s.vsp_id = v.id
            WHERE s.user_name = %s
            ORDER BY s.created_at DESC LIMIT 1
            """,
            (full_name,)
        )
        return df.iloc[0].to_dict() if not df.empty else None

    def get_session_data(self, session_id: int) -> Optional[Dict]:
        """Полные данные сессии + ответы."""
        cur = self._get_cursor()
        cur.execute(f"SELECT * FROM {self._table_name('checklist_sessions')} WHERE id = %s", (session_id,))
        row = cur.fetchone()
        if not row:
            return None
        info = dict(row)
        cur.execute(
            f"SELECT template_item_id, is_completed FROM {self._table_name('checklist_answers')} WHERE session_id = %s",
            (session_id,)
        )
        rows = cur.fetchall()
        answers = {r['template_item_id']: r['is_completed'] for r in rows}
        return {"info": info, "answers": answers}

    def save_answers(self, session_id: int, answers: Dict[int, bool]):
        """Сохраняет ответы (UPSERT) и обновляет временную метку сессии."""
        cur = self._get_cursor()
        for item_id, comp in answers.items():
            cur.execute(
                f"INSERT INTO {self._table_name('checklist_answers')} (session_id, template_item_id, is_completed) "
                f"VALUES (%s, %s, %s) "
                f"ON CONFLICT (session_id, template_item_id) DO UPDATE SET is_completed = EXCLUDED.is_completed",
                (session_id, item_id, comp)
            )
        cur.execute(
            f"UPDATE {self._table_name('checklist_sessions')} SET updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (session_id,)
        )
        self._get_connection().commit()

    # --- Экспорт и отчёты ---
    def get_export_data(self) -> pd.DataFrame:
        """Сводные данные по всем сессиям для экспорта."""
        return self._to_df(f"""
            SELECT
                s.id AS session_id, s.user_name AS ФИО, f.name AS Филиал, v.name AS ВСП,
                s.operation_date AS Дата_проверки,
                CASE s.status WHEN 'completed' THEN 'Завершена' WHEN 'draft' THEN 'Черновик' ELSE s.status END AS Статус,
                s.created_at AS Дата_создания, s.updated_at AS Дата_обновления,
                COUNT(a.id) AS Выполнено_проверок,
                (SELECT COUNT(*) FROM {self.schema}.checklist_templates) AS Всего_проверок
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id = f.id
            JOIN {self.schema}.vsp v ON s.vsp_id = v.id
            LEFT JOIN {self.schema}.checklist_answers a ON s.id = a.session_id AND a.is_completed = true
            GROUP BY s.id, f.name, v.name, s.user_name, s.operation_date, s.status, s.created_at, s.updated_at
            ORDER BY s.created_at DESC
        """)

    def get_user_sessions(self, full_name: str) -> pd.DataFrame:
        """История проверок конкретного пользователя."""
        return self._to_df(f"""
            SELECT
                s.id, s.operation_date AS "Дата проверки", f.name AS "Филиал", v.name AS "ВСП",
                CASE s.status WHEN 'completed' THEN 'Завершена' WHEN 'draft' THEN 'Черновик' ELSE s.status END AS "Статус",
                s.created_at AS "Дата создания", s.updated_at AS "Дата обновления",
                COUNT(a.id) AS "Выполнено проверок",
                (SELECT COUNT(*) FROM {self.schema}.checklist_templates) AS "Всего проверок"
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id = f.id
            JOIN {self.schema}.vsp v ON s.vsp_id = v.id
            LEFT JOIN {self.schema}.checklist_answers a ON s.id = a.session_id AND a.is_completed = true
            WHERE s.user_name = %s
            GROUP BY s.id, f.name, v.name, s.operation_date, s.status, s.created_at, s.updated_at
            ORDER BY s.created_at DESC
        """, (full_name,))

    def get_admin_analytics(self, filial_id=None, vsp_id=None,
                            date_from=None, date_to=None) -> pd.DataFrame:
        """Детальная аналитика (для администратора) с фильтрами."""
        conds = []
        params = []
        if filial_id is not None:
            conds.append("s.filial_id = %s")
            params.append(int(filial_id))
        if vsp_id is not None:
            conds.append("s.vsp_id = %s")
            params.append(int(vsp_id))
        if date_from is not None:
            conds.append("s.operation_date >= %s")
            params.append(date_from)
        if date_to is not None:
            conds.append("s.operation_date <= %s")
            params.append(date_to)
        where = " AND ".join(conds) if conds else "1=1"

        sessions = self._to_df(f"""
            SELECT s.id AS session_id, s.user_name AS ФИО, f.name AS Филиал, v.name AS ВСП,
                   s.operation_date AS Дата, s.status AS Статус,
                   s.created_at AS Дата_создания, s.updated_at AS Дата_обновления
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id = f.id
            JOIN {self.schema}.vsp v ON s.vsp_id = v.id
            WHERE {where}
            ORDER BY s.operation_date DESC, f.name, v.name
        """, tuple(params) if params else None)

        if sessions.empty:
            return sessions

        template = self.get_checklist_template()
        if template.empty:
            return sessions

        # Собираем ответы для каждой сессии
        all_answers = []
        for sid in sessions['session_id']:
            data = self.get_session_data(sid)
            answers = data['answers'] if data else {}
            row = {'session_id': sid}
            for _, tpl in template.iterrows():
                row[f"check_{tpl['id']}"] = answers.get(tpl['id'], False)
            all_answers.append(row)
        ans_df = pd.DataFrame(all_answers)
        return sessions.merge(ans_df, on='session_id', how='left')


# =============================================================================
# 3. ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ И ПЕРЕМЕННЫХ СОСТОЯНИЯ
# =============================================================================
# CSS для крупных чекбоксов
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

# Единый экземпляр менеджера БД
db = DatabaseManager()

# Инициализация переменных состояния Streamlit
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
    st.session_state.step = 0                       # 0 – выбор параметров, 1 – заполнение чек-листа
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
    """
    Загружает последние использованные филиал и ВСП для текущего пользователя.
    Вызывается при старте, если пользователь авторизован.
    """
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

# =============================================================================
# 4. БОКОВАЯ ПАНЕЛЬ (SIDEBAR)
# =============================================================================
with st.sidebar:
    # Во время заполнения чек-листа показываем только краткую информацию
    if st.session_state.step != 1:
        st.header("👤 Информация")
        if st.session_state.auth_valid and st.session_state.user_full_name:
            st.markdown(f"**Пользователь:** {st.session_state.user_full_name}")
            st.caption(f"Логин: {st.session_state.user_name}")
            if st.button("🔄 Сменить пользователя", use_container_width=True):
                for key in ['user_name', 'user_full_name', 'auth_valid', 'last_filial_name', 'last_vsp_name',
                            'last_filial_id', 'last_vsp_id', 'selected_filial_id', 'selected_vsp_id',
                            'step', 'data_loaded', 'update_counter', 'current_session_id', 'temp_answers', 'resume_session_id']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        else:
            st.info("👋 Пользователь не выбран")

        st.divider()
        st.subheader("🔐 Администрирование")

        # Чекбокс для входа в админ-режим
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

        # Инструменты администратора (видны только после входа)
        if st.session_state.admin_authenticated:
            st.divider()
            st.subheader("⚙️ Управление чек-листом")
            tpl = db.get_checklist_template()
            if not tpl.empty:
                with st.expander("📋 Текущие проверки"):
                    for _, r in tpl.iterrows():
                        st.markdown(f"**{r['item_order']}.** {r['description']}")
            # Добавление новой проверки
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
            # Редактирование / удаление пункта
            with st.expander("✏️ Редактировать/Удалить"):
                if not tpl.empty:
                    sel_id = st.selectbox(
                        "Выберите проверку", tpl['id'].tolist(),
                        format_func=lambda x: f"ID {x} - {tpl[tpl['id']==x]['description'].iloc[0][:50]}"
                    )
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
                    if OPENPYXL_AVAILABLE:
                        path = "/tmp/export.xlsx"
                        with pd.ExcelWriter(path, engine='openpyxl') as writer:
                            exp_df.to_excel(writer, sheet_name='Отчет', index=False)
                        with open(path, 'rb') as f:
                            st.download_button("💾 Скачать", f.read(),
                                               f"checklist_{datetime.date.today()}.xlsx",
                                               use_container_width=True)
                    else:
                        st.error("Установите openpyxl")
            else:
                st.warning("Нет данных для экспорта")
    else:
        st.info("Идет заполнение чек-листа...")

# =============================================================================
# 5. ОСНОВНОЙ ИНТЕРФЕЙС (ВКЛАДКИ)
# =============================================================================
st.title("📋 Завершение операций по ВСП")
st.caption("")

# В зависимости от режима показываем разные вкладки
if st.session_state.admin_authenticated:
    tab_history, tab_main, tab_analytics, tab_alt = st.tabs([
        "📜 История проверок", "📝 Новая проверка", "📊 Аналитика", "🏢 Альт. настройки филиалов"
    ])
else:
    tab_history, tab_main = st.tabs(["📜 История проверок", "📝 Новая проверка"])
    tab_analytics = None
    tab_alt = None

# ===================== ВКЛАДКА "НОВАЯ ПРОВЕРКА" =====================
with tab_main:
    if st.session_state.step == 0:
        # --- Отображение черновиков пользователя (только за сегодня) ---
        if st.session_state.auth_valid and st.session_state.user_full_name:
            drafts = db.get_user_draft_sessions(st.session_state.user_full_name)
            if not drafts.empty:
                drafts = drafts[drafts['operation_date'] == datetime.date.today()]
        else:
            drafts = pd.DataFrame()

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Черновики
            if not drafts.empty:
                st.info(f"📌 У вас есть {len(drafts)} сохраненных черновиков")
                for _, d in drafts.iterrows():
                    with st.container():
                        a, b, c = st.columns([3, 2, 1])
                        a.markdown(f"**{d['filial_name']} / {d['vsp_name']}**")
                        a.caption(f"📅 {d['operation_date']}")
                        b.caption(f"✅ {d['completed_count']}/{d['total_count']}")
                        if c.button("📂 Продолжить", key=f"resume_{d['id']}", use_container_width=True):
                            st.session_state.current_session_id = d['id']
                            st.session_state.step = 1
                            st.rerun()
                        st.divider()

            # --- Авторизация и выбор параметров ---
            filials_df = db.get_filials()  # теперь есть поле check_name
            if not filials_df.empty:
                filial_names = filials_df['name'].tolist()
                filial_map = dict(zip(filials_df['name'], filials_df['id']))

                # Поле ввода логина
                login = st.text_input(
                    "👤 Учетная запись сотрудника",
                    value=st.session_state.user_name if not st.session_state.auth_valid else "",
                    placeholder="rf_ivanov_av           (либо go_ivanov_av) ",
                    disabled=st.session_state.auth_valid,
                    key=f"login_{st.session_state.update_counter}"
                )
                login_norm = login.lower().strip() if login else ""

                # Автоматическая проверка при вводе логина
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
                        # Загружаем последний ВСП
                        last = db.get_last_user_session_data(full)
                        if last:
                            if not st.session_state.last_vsp_name:
                                st.session_state.last_vsp_name = last['vsp_name']
                            st.session_state.last_vsp_id = last['vsp_id']
                            st.session_state.selected_vsp_id = last['vsp_id']
                            if not st.session_state.selected_filial_id:
                                st.session_state.selected_filial_id = last['filial_id']
                            st.session_state.last_filial_id = last['filial_id']
                            st.session_state.update_counter += 1
                        st.rerun()
                    else:
                        st.error(f"❌ Пользователь '{login_norm}' не найден!")

                # Информация об авторизованном пользователе
                if st.session_state.auth_valid:
                    st.info(f"👤 **Авторизован:** {st.session_state.user_full_name}")
                    st.caption(f"Логин: {st.session_state.user_name}")
                    if st.button("🔄 Сменить пользователя", key="change_btn", use_container_width=True):
                        for k in ['user_name','user_full_name','auth_valid','last_filial_name','last_vsp_name',
                                  'last_filial_id','last_vsp_id','selected_filial_id','selected_vsp_id',
                                  'step','data_loaded','update_counter','current_session_id','temp_answers','resume_session_id']:
                            if k in st.session_state:
                                del st.session_state[k]
                        st.rerun()
                    st.divider()

                    # Филиал (автоподстановка, только для отображения)
                    sel_filial_id = st.session_state.last_filial_id
                    if sel_filial_id is None:
                        st.error("Филиал не определен. Обратитесь к администратору")
                        st.stop()
                    st.markdown(f"**Филиал:** {st.session_state.last_filial_name}")

                    # Выбор ВСП
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
                        sel_vsp = st.selectbox(
                            "🏪 ВСП", vsp_names, index=vsp_idx,
                            key=f"vsp_{st.session_state.update_counter}"
                        )
                        sel_vsp_id = vsp_map[sel_vsp]
                        st.session_state.last_vsp_name = sel_vsp
                        st.session_state.last_vsp_id = sel_vsp_id
                        st.session_state.selected_vsp_id = sel_vsp_id
                    else:
                        sel_vsp_id = None
                        st.warning("Нет ВСП в выбранном филиале")

                    # Кнопка начала заполнения (создаёт новую сессию)
                    with st.form("new_session_form"):
                        op_date = st.date_input(
                            "📅 Дата", value=datetime.date.today(),
                            format="DD.MM.YYYY", disabled=True
                        )
                        submitted = st.form_submit_button(
                            "▶️ НАЧАТЬ ЗАПОЛНЕНИЕ", type="primary", use_container_width=True
                        )
                        if submitted and sel_vsp_id:
                            sid = db.create_session(
                                st.session_state.user_full_name,
                                sel_filial_id, sel_vsp_id, op_date, 'draft'
                            )
                            st.session_state.current_session_id = sid
                            st.session_state.step = 1
                            st.rerun()
                        elif submitted:
                            st.error("Выберите ВСП!")
            else:
                st.error("Нет филиалов в базе данных")

# ===================== ВКЛАДКА "ИСТОРИЯ ПРОВЕРОК" =====================
with tab_history:
    st.markdown("### 📜 История ваших проверок")
    if st.session_state.auth_valid and st.session_state.user_full_name:
        hist = db.get_user_sessions(st.session_state.user_full_name)
        if not hist.empty:
            st.dataframe(hist, use_container_width=True, height=400)
            sel_sess = st.selectbox(
                "Выберите сессию", hist['id'].tolist(),
                format_func=lambda x: f"Сессия #{x} - {hist[hist['id']==x]['Дата проверки'].iloc[0]}"
            )
            if st.button("📋 Показать результаты"):
                data = db.get_session_data(sel_sess)
                if data:
                    with st.expander(f"Результаты проверки #{sel_sess}", expanded=True):
                        st.markdown(f"**Дата:** {data['info']['operation_date']}")
                        st.markdown(f"**Статус:** {'✔️ Завершена' if data['info']['status']=='completed' else '📄 Черновик'}")
                        tpl = db.get_checklist_template()
                        ans = data['answers']
                        for _, r in tpl.iterrows():
                            st.markdown(f"{'✔️' if ans.get(r['id'], False) else '❌'} {r['description']}")
                else:
                    st.error("Не удалось загрузить данные")
        else:
            st.info("У вас пока нет завершённых проверок.")
    else:
        st.warning("Введите учётную запись, чтобы увидеть историю.")

# ===================== ВКЛАДКА "АНАЛИТИКА" (только для админа) =====================
if tab_analytics is not None:
    with tab_analytics:
        st.markdown("## 📊 Детальная аналитика по проверкам")
        st.caption("Просмотр всех сессий с фильтрацией и визуализацией статусов проверок (✔️/❌)")

        filials_df = db.get_filials()
        if not filials_df.empty:
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                filial_opts = ["Все"] + filials_df['name'].tolist()
                sel_filial_name = st.selectbox("Филиал", filial_opts, key="adm_filial")
                filial_id = None if sel_filial_name == "Все" else int(filials_df[filials_df['name']==sel_filial_name]['id'].iloc[0])
            with col_f2:
                if filial_id:
                    vsp_df = db.get_vsp_by_filial(filial_id)
                else:
                    vsp_df = db._to_df(f"SELECT id, name FROM {db._table_name('vsp')} ORDER BY name")
                vsp_opts = ["Все"] + vsp_df['name'].tolist() if not vsp_df.empty else ["Все"]
                sel_vsp_name = st.selectbox("ВСП", vsp_opts, key="adm_vsp")
                vsp_id = None if sel_vsp_name == "Все" else int(vsp_df[vsp_df['name']==sel_vsp_name]['id'].iloc[0])
            with col_f3:
                date_from = st.date_input("Дата от", value=None, key="adm_date_from")
            with col_f4:
                date_to = st.date_input("Дата до", value=None, key="adm_date_to")

            if st.button("🔍 Показать данные", use_container_width=True):
                with st.spinner("Загрузка..."):
                    analytics = db.get_admin_analytics(filial_id, vsp_id, date_from, date_to)
                if analytics.empty:
                    st.info("Нет данных по выбранным фильтрам")
                else:
                    st.success(f"Найдено {len(analytics)} сессий")
                    template = db.get_checklist_template()
                    # Преобразуем True/False в иконки
                    for _, tpl in template.iterrows():
                        col_name = f"check_{tpl['id']}"
                        if col_name in analytics.columns:
                            analytics[col_name] = analytics[col_name].apply(lambda x: "✔️" if x else "❌")
                    # Переименовываем колонки для читаемости
                    rename = {f"check_{tpl['id']}": f"{tpl['item_order']}. {tpl['description'][:50]}"
                              for _, tpl in template.iterrows()}
                    analytics.rename(columns=rename, inplace=True)
                    base_cols = ['ФИО', 'Филиал', 'ВСП', 'Дата', 'Статус']
                    display_cols = base_cols + [v for v in rename.values() if v in analytics.columns]
                    final_df = analytics[display_cols]
                    st.dataframe(final_df, use_container_width=True, height=500)
        else:
            st.warning("Нет филиалов в базе данных")

# ===================== ВКЛАДКА "АЛЬТ. НАСТРОЙКИ ФИЛИАЛОВ" (только для админа) =====================
if tab_alt is not None:
    with tab_alt:
        st.markdown("## 🏢 Альтернативные настройки для филиалов")
        st.caption("Включите опцию для филиала и задайте фильтры/описания, которые будут показаны вместо стандартных.")

        filials_df = db.get_filials()  # id, name, check_name
        if filials_df.empty:
            st.warning("Нет филиалов")
        else:
            # Выбор филиала из списка
            selected_filial = st.selectbox(
                "Выберите филиал для настройки",
                filials_df['name'].tolist(),
                key="alt_filial_select"
            )
            filial_row = filials_df[filials_df['name'] == selected_filial].iloc[0]
            filial_id = int(filial_row['id'])
            current_check = bool(filial_row['check_name'])

            template = db.get_checklist_template()
            if template.empty:
                st.info("Шаблон чек-листа пуст")
                st.stop()

            # Загружаем существующие альтернативные записи для этого филиала
            alt_df = db.get_alt_template_for_filial(filial_id)
            alt_dict = {}
            if not alt_df.empty:
                for _, row in alt_df.iterrows():
                    alt_dict[int(row['template_item_id'])] = {
                        'filter': row['alt_filter_value'],
                        'info': row['alt_additional_info'],
                        'events': row['alt_events_value']
                    }

            # Единая форма: флаг + все поля + кнопка сохранения
            with st.form("alt_full_form"):
                # Флаг использования альтернативных настроек
                new_check = st.checkbox(
                    "✅ Использовать альтернативные фильтры и описания для этого филиала",
                    value=current_check
                )

                st.divider()
                st.subheader("📝 Альтернативные значения для каждого пункта")
                st.caption("Оставьте поле пустым – будет использовано стандартное значение из шаблона.")

                alt_data = {}
                for _, tpl in template.iterrows():
                    item_id = int(tpl['id'])
                    desc = tpl['description']
                    std_filter = tpl['filter_value'] or ""
                    std_info = tpl['additional_info'] or ""
                    std_events = tpl['events_value'] or ""

                    # Значения по умолчанию — из уже сохранённых альт. записей, иначе стандартные
                    cur = alt_dict.get(item_id, {})
                    cur_filter = cur.get('filter', std_filter)
                    cur_info = cur.get('info', std_info)
                    cur_events = cur.get('events', std_events)

                    with st.expander(f"📌 {tpl['item_order']}. {desc}"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.caption("Стандартный фильтр:")
                            st.code(std_filter if std_filter else "—", language="text")
                            st.caption("Стандартное описание:")
                            st.code(std_info if std_info else "—", language="text")
                        with col_b:
                            st.caption("Стандартные мероприятия:")
                            st.code(std_events if std_events else "—", language="text")

                        st.markdown("**Альтернативные значения:**")
                        af = st.text_area("Фильтр", value=cur_filter, key=f"af_{item_id}")
                        ai = st.text_area("Описание", value=cur_info, key=f"ai_{item_id}")
                        ae = st.text_area("Мероприятия", value=cur_events, key=f"ae_{item_id}")
                        alt_data[item_id] = (af, ai, ae)

                submitted = st.form_submit_button("💾 Сохранить все настройки", type="primary")

            # Кнопка «Копировать стандартные значения» (вне формы, чтобы не сохранять настройки при её нажатии)
            if st.button("📋 Копировать стандартные значения для всех пунктов", key="copy_std_btn"):
                for _, tpl in template.iterrows():
                    item_id = int(tpl['id'])
                    std_filter = tpl['filter_value'] or ""
                    std_info = tpl['additional_info'] or ""
                    std_events = tpl['events_value'] or ""
                    db.upsert_alt_template(filial_id, item_id, std_filter, std_info, std_events)
                st.success("Стандартные значения скопированы!")
                st.rerun()

            # Обработка отправки формы
            if submitted:
                # Сохраняем флаг
                db.set_filial_check(filial_id, new_check)
                # Сохраняем все альтернативные поля
                for item_id, (af, ai, ae) in alt_data.items():
                    db.upsert_alt_template(filial_id, item_id, af, ai, ae)
                st.success("Все настройки сохранены!")
                st.rerun()

# =============================================================================
# 6. ШАГ 1: ЗАПОЛНЕНИЕ ЧЕК-ЛИСТА
# =============================================================================
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

    # Ответы, сохранённые ранее
    saved = sess['answers']
    if "temp_answers" not in st.session_state:
        st.session_state.temp_answers = copy.deepcopy(saved)

    # Получаем информацию о филиале и ВСП текущей сессии
    cur = db._get_cursor()
    cur.execute(f"""
        SELECT f.name AS filial_name, v.name AS vsp_name, s.filial_id
        FROM {db.schema}.checklist_sessions s
        JOIN {db.schema}.filials f ON s.filial_id = f.id
        JOIN {db.schema}.vsp v ON s.vsp_id = v.id
        WHERE s.id = %s
    """, (sid,))
    row = cur.fetchone()
    filial_name = row['filial_name'] if row else "?"
    vsp_name = row['vsp_name'] if row else "?"
    current_filial_id = int(row['filial_id']) if row else None

    # Определяем, нужно ли использовать альтернативные настройки для этого филиала
    use_alt = False
    if current_filial_id:
        filial_info = db._execute(
            f"SELECT check_name FROM {db._table_name('filials')} WHERE id = %s",
            (current_filial_id,), fetch_one=True
        )
        if filial_info and filial_info['check_name']:
            use_alt = True

    # Заголовок формы
    st.subheader(f"📋 Чек-лист: {filial_name} / {vsp_name}")
    status_text = "Черновик" if sess['info']['status'] == 'draft' else "Завершена"
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(f"**👤 Сотрудник:** {sess['info']['user_name']}")
    c2.markdown(f"**🏢 Филиал:** {filial_name}")
    c3.markdown(f"**🏪 ВСП:** {vsp_name}")
    c4.markdown(f"**📅 Дата:** {sess['info']['operation_date']}")
    c5.markdown(f"**📌 Статус:** {status_text}")
    st.divider()
    st.markdown("### ✔️ Список проверок")

    # Заголовки таблицы
    header = st.columns([1, 5, 2, 1])
    header[0].markdown("**№**")
    header[1].markdown("**Наименование проверки**")
    header[2].markdown('<div style="text-align: center; font-weight:900; font-style: italic; text-shadow: 0.8px 0 0 currentColor;">Доп. информация</div>', unsafe_allow_html=True)
    header[3].markdown("**Статус**")
    st.markdown("<hr style='margin:8px 0;border:1.5px solid #000000;'>", unsafe_allow_html=True)

    # Построение строк чек-листа
    for _, tpl in template.iterrows():
        item_id = tpl['id']
        order = tpl['item_order']
        desc = tpl['description']

        # Стандартные значения из шаблона
        std_filter = tpl['filter_value'] or "Не задан"
        std_info = tpl['additional_info'] or "Описание отсутствует"
        std_events = tpl['events_value'] or "Мероприятия не заданы"

        # Попытка получить альтернативные значения (только если use_alt == True)
        if use_alt and current_filial_id:
            alt = db.get_alt_template_item(current_filial_id, item_id)
        else:
            alt = None

        # Логика выбора: если запись существует, используем её поля;
        # если поле пустое – подставляем стандартное.
        if alt is not None:
            filter_text = alt['alt_filter_value'] if alt['alt_filter_value'] else std_filter
            add_info = alt['alt_additional_info'] if alt['alt_additional_info'] else std_info
            events_text = alt['alt_events_value'] if alt['alt_events_value'] else std_events
        else:
            filter_text = std_filter
            add_info = std_info
            events_text = std_events

        # Текущее состояние чекбокса (изменённое или из БД)
        current = st.session_state.temp_answers.get(item_id, saved.get(item_id, False))

        # Отрисовка строки
        cols = st.columns([1, 5, 2, 1])
        cols[0].write(f"**{order}**")
        cols[1].markdown(desc)

        # Popover с подробной информацией
        with cols[2]:
            with st.popover(f"ℹ️ Подробнее о проверке №{order}", use_container_width=True):
                t1, t2 = st.tabs(["🔍 Фильтр", "📌 Мероприятия"])
                with t1:
                    st.markdown("**Описание процедуры:**")
                    st.info(add_info)
                    if filter_text != "Не задан":
                        filter_display = filter_text
                        # Обработка макроса [Дата1] – пользователь может выбрать дату
                        if "[Дата1]" in filter_text:
                            default_date = datetime.date.today()
                            selected_date = st.date_input(
                                "📅Выберите дату", key=f"date_{item_id}",
                                value=default_date, format="DD.MM.YYYY"
                            )
                            date_str = selected_date.strftime("%d.%m.%y")
                            filter_display = filter_text.replace("[Дата1]", date_str)
                        filter_display = filter_display.replace("[РФ]", vsp_name)
                        st.code(filter_display, language="text")

                        # Кнопка копирования фильтра в буфер обмена
                        import streamlit.components.v1 as components
                        js_code = f"""
                        <div style="margin-top:8px">
                            <button id="copy_{item_id}" style="background:#4CAF50;color:white;padding:8px;border:none;border-radius:5px;width:100%">
                                📋 КОПИРОВАТЬ ФИЛЬТР
                            </button>
                            <div id="status_{item_id}" style="margin-top:5px;font-size:12px;text-align:center"></div>
                        </div>
                        <script>
                        (function(){{
                            var btn=document.getElementById("copy_{item_id}");
                            var statusDiv=document.getElementById("status_{item_id}");
                            var textToCopy={repr(filter_display)};
                            btn.addEventListener("click",function(){{
                                navigator.clipboard.writeText(textToCopy).then(function(){{
                                    statusDiv.innerHTML="✅ Скопировано!";statusDiv.style.color="green";
                                    setTimeout(function(){{statusDiv.innerHTML="";}},2000);
                                }},function(){{
                                    statusDiv.innerHTML="❌ Ошибка";statusDiv.style.color="red";
                                }});
                            }});
                        }})();
                        </script>
                        """
                        components.html(js_code, height=100)
                    else:
                        st.info("Фильтр не задан")
                with t2:
                    st.markdown("**Мероприятия:**")
                    st.info(events_text)

        # Чекбокс выполнения
        with cols[3]:
            new_val = st.checkbox(" ", value=current, key=f"chk_{item_id}", label_visibility="collapsed")
            if new_val != current:
                st.session_state.temp_answers[item_id] = new_val

        st.markdown("<hr style='margin:8px 0;border:1.5px solid #000000;'>", unsafe_allow_html=True)

    # Кнопки управления
    colA, colB, colC, colD = st.columns([1, 1, 1, 2])
    with colA:
        if st.button("🔙 Назад", use_container_width=True):
            db.save_answers(sid, st.session_state.temp_answers)
            db.update_session_status(sid, 'draft')
            st.session_state.step = 0
            for k in ['current_session_id', 'temp_answers', 'resume_session_id']:
                if k in st.session_state: del st.session_state[k]
            st.rerun()
    with colB:
        if st.button("💾 Сохранить черновик", use_container_width=True):
            db.save_answers(sid, st.session_state.temp_answers)
            db.update_session_status(sid, 'draft')
            st.success("✅ Черновик сохранён!")
            time.sleep(1)
            st.rerun()
    with colC:
        if st.button("📋 Предпросмотр", use_container_width=True):
            with st.expander("📄 Предпросмотр результатов", expanded=True):
                completed = sum(st.session_state.temp_answers.values())
                total = len(template)
                st.info(f"Выполнено {completed}/{total} проверок")
                for _, r in template.iterrows():
                    status = "✅" if st.session_state.temp_answers.get(r['id'], False) else "❌"
                    st.markdown(f"{status} {r['description']}")
    with colD:
        if st.button("✅ ЗАВЕРШИТЬ ПРОВЕРКУ", type="primary", use_container_width=True):
            completed = sum(st.session_state.temp_answers.values())
            total = len(template)
            if completed < total:
                st.toast(f"⚠️ Выполнено только {completed} из {total} проверок. Заполните все.", icon="❗")
            else:
                db.save_answers(sid, st.session_state.temp_answers)
                db.update_session_status(sid, 'completed')
                st.success("🎉 Отлично! Чек-лист успешно завершён!")
                st.balloons()
                st.session_state.step = 0
                for k in ['current_session_id', 'temp_answers', 'resume_session_id']:
                    if k in st.session_state: del st.session_state[k]
                time.sleep(2)
                st.rerun()
