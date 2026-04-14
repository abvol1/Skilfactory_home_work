import streamlit as st
import pandas as pd
import sqlite3
import datetime
import hashlib
import json
from typing import List, Dict, Any, Optional
import copy
import os
import time  # Добавляем для паузы

# Попробуем импортировать psycopg2. Если его нет, работать будем только с SQLite.
try:
    import psycopg2
    from psycopg2 import sql
    from psycopg2.extras import RealDictCursor

    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("Psycopg2 не установлен. Работаем в режиме SQLite.")

# ==============================================================================
# 1. КОНФИГУРАЦИЯ ПРИЛОЖЕНИЯ (БЫСТРОЕ ПЕРЕКЛЮЧЕНИЕ МЕЖДУ БАЗАМИ)
# ==============================================================================

USE_POSTGRES = False  # <---------------- ПОМЕНЯЙТЕ НА TRUE, КОГДА БУДЕТЕ ВЫКЛАДЫВАТЬ НА РАБОТУ

# Данные для PostgreSQL (замените на свои рабочие, когда переключите USE_POSTGRES = True)
PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "checklist_db",
    "user": "postgres",
    "password": "password",
    "schema": "public"
}

# Путь к файлу SQLite (для домашней разработки)
SQLITE_PATH = "checklist_app.db"

# Флаг для принудительного пересоздания БД (установите True если нужно сбросить все данные)
FORCE_RECREATE_DB = False  # Поставьте False после первого успешного запуска


# ==============================================================================
# 2. СЛОЙ РАБОТЫ С БАЗОЙ ДАННЫХ (АБСТРАКЦИЯ)
# ==============================================================================

class DatabaseManager:
    """
    Класс-прослойка для работы с БД.
    Позволяет легко переключаться между SQLite и PostgreSQL без изменения основной логики кода.
    """

    def __init__(self):
        self.use_postgres = USE_POSTGRES and POSTGRES_AVAILABLE
        self.schema = PG_CONFIG.get('schema', 'public') if self.use_postgres else None

    def get_connection(self):
        """Возвращает объект соединения в зависимости от настроек."""
        if self.use_postgres:
            # Подключение к PostgreSQL
            conn = psycopg2.connect(
                host=PG_CONFIG['host'],
                port=PG_CONFIG['port'],
                dbname=PG_CONFIG['database'],
                user=PG_CONFIG['user'],
                password=PG_CONFIG['password']
            )
            # Устанавливаем схему поиска, если она указана и не public
            if self.schema and self.schema != 'public':
                with conn.cursor() as cur:
                    cur.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(self.schema)))
            return conn
        else:
            # Подключение к SQLite
            conn = sqlite3.connect(SQLITE_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory = sqlite3.Row  # Чтобы можно было обращаться к полям по именам как в словаре
            return conn

    def init_db(self):
        """
        Создает таблицы, если их нет.
        SQLite и PostgreSQL имеют небольшие различия в синтаксисе (AUTOINCREMENT vs SERIAL),
        поэтому для каждого типа БД своя логика создания.
        """
        # Если включен флаг пересоздания БД и это SQLite - удаляем старый файл
        if FORCE_RECREATE_DB and not self.use_postgres and os.path.exists(SQLITE_PATH):
            os.remove(SQLITE_PATH)
            print(f"🗑️ Старая база данных {SQLITE_PATH} удалена для пересоздания")

        conn = self.get_connection()
        cursor = conn.cursor()

        if self.use_postgres:
            # --- Схема PostgreSQL ---
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.schema or 'public'}.checklist_templates (
                    id SERIAL PRIMARY KEY,
                    section_name VARCHAR(255) NOT NULL,
                    item_order INTEGER NOT NULL,
                    description TEXT,
                    additional_info TEXT
                )
            """)
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.schema or 'public'}.filials (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL
                )
            """)
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.schema or 'public'}.vsp (
                    id SERIAL PRIMARY KEY,
                    filial_id INTEGER REFERENCES {self.schema or 'public'}.filials(id),
                    name VARCHAR(255) NOT NULL
                )
            """)
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.schema or 'public'}.checklist_sessions (
                    id SERIAL PRIMARY KEY,
                    user_name VARCHAR(255) NOT NULL,
                    filial_id INTEGER REFERENCES {self.schema or 'public'}.filials(id),
                    vsp_id INTEGER REFERENCES {self.schema or 'public'}.vsp(id),
                    operation_date DATE NOT NULL,
                    status VARCHAR(50) DEFAULT 'completed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.schema or 'public'}.checklist_answers (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER REFERENCES {self.schema or 'public'}.checklist_sessions(id) ON DELETE CASCADE,
                    template_item_id INTEGER REFERENCES {self.schema or 'public'}.checklist_templates(id),
                    is_completed BOOLEAN DEFAULT FALSE,
                    UNIQUE(session_id, template_item_id)
                )
            """)
            # Триггер для обновления updated_at (PostgreSQL)
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
                DROP TRIGGER IF EXISTS update_checklist_sessions_updated_at ON {self.schema or 'public'}.checklist_sessions;
                CREATE TRIGGER update_checklist_sessions_updated_at
                BEFORE UPDATE ON {self.schema or 'public'}.checklist_sessions
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """)
        else:
            # --- Схема SQLite (ИСПРАВЛЕННАЯ ВЕРСИЯ) ---
            # Включаем поддержку внешних ключей
            cursor.execute("PRAGMA foreign_keys = ON")

            # 1. Таблица шаблонов чек-листа
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checklist_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    section_name TEXT NOT NULL DEFAULT 'Основной',
                    item_order INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    additional_info TEXT
                )
            """)

            # 2. Таблица филиалов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS filials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)

            # 3. Таблица ВСП (с внешним ключом)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vsp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filial_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    FOREIGN KEY (filial_id) REFERENCES filials (id) ON DELETE CASCADE
                )
            """)

            # 4. Таблица сессий чек-листа (статус по умолчанию 'completed')
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
                    FOREIGN KEY (filial_id) REFERENCES filials (id),
                    FOREIGN KEY (vsp_id) REFERENCES vsp (id)
                )
            """)

            # 5. Таблица ответов на проверки
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checklist_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    template_item_id INTEGER NOT NULL,
                    is_completed INTEGER DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES checklist_sessions (id) ON DELETE CASCADE,
                    FOREIGN KEY (template_item_id) REFERENCES checklist_templates (id) ON DELETE CASCADE,
                    UNIQUE(session_id, template_item_id)
                )
            """)

            # 6. Триггер для автоматического обновления updated_at в SQLite
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS update_checklist_sessions_updated_at
                AFTER UPDATE ON checklist_sessions
                FOR EACH ROW
                BEGIN
                    UPDATE checklist_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
                END;
            """)

            # 7. Создаем индексы для ускорения поиска
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON checklist_sessions(user_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_answers_session ON checklist_answers(session_id)")

        conn.commit()
        conn.close()
        print(f"✅ База данных инициализирована. Режим: {'PostgreSQL' if self.use_postgres else 'SQLite'}")

        # Выводим информацию о структуре таблицы для проверки
        if not self.use_postgres:
            self._verify_tables_structure()

    def _verify_tables_structure(self):
        """Проверяет структуру таблиц SQLite (для отладки)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Проверяем наличие таблицы checklist_sessions и её поля user_name
        cursor.execute("PRAGMA table_info(checklist_sessions)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'user_name' not in column_names:
            print("❌ ОШИБКА: Поле 'user_name' отсутствует в таблице checklist_sessions!")
            print(f"   Доступные поля: {column_names}")

            # Пытаемся добавить поле, если таблица существует
            try:
                cursor.execute("ALTER TABLE checklist_sessions ADD COLUMN user_name TEXT")
                conn.commit()
                print("✅ Поле 'user_name' успешно добавлено в существующую таблицу")
            except sqlite3.OperationalError as e:
                print(f"⚠️ Не удалось добавить поле: {e}")
        else:
            print(f"✅ Структура таблицы checklist_sessions корректна: {column_names}")

        conn.close()

    # --------------------------------------------------------------------------
    # Методы для получения справочников (Филиалы, ВСП)
    # --------------------------------------------------------------------------
    def get_filials(self) -> pd.DataFrame:
        """Возвращает список всех филиалов"""
        conn = self.get_connection()
        query = "SELECT id, name FROM filials ORDER BY name"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_vsp_by_filial(self, filial_id: int) -> pd.DataFrame:
        """Возвращает список ВСП для конкретного филиала"""
        conn = self.get_connection()
        if self.use_postgres:
            query = "SELECT id, name FROM vsp WHERE filial_id = %s ORDER BY name"
            df = pd.read_sql_query(query, conn, params=(filial_id,))
        else:
            query = "SELECT id, name FROM vsp WHERE filial_id = ? ORDER BY name"
            df = pd.read_sql_query(query, conn, params=(filial_id,))
        conn.close()
        return df

    # --------------------------------------------------------------------------
    # Методы для шаблонов чек-листов (CRUD для администратора)
    # --------------------------------------------------------------------------
    def get_checklist_template(self) -> pd.DataFrame:
        """Возвращает шаблон чек-листа (все проверки)"""
        conn = self.get_connection()
        query = "SELECT id, item_order, description, additional_info FROM checklist_templates ORDER BY item_order"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def add_template_item(self, description: str, additional_info: str):
        """Добавляет новый пункт в шаблон чек-листа"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Определяем следующий порядковый номер
        cursor.execute("SELECT COALESCE(MAX(item_order), 0) + 1 FROM checklist_templates")
        next_order = cursor.fetchone()[0]

        if self.use_postgres:
            query = sql.SQL(
                "INSERT INTO {} (section_name, item_order, description, additional_info) VALUES (%s, %s, %s, %s)").format(
                sql.Identifier(self.schema + '.checklist_templates'))
        else:
            query = "INSERT INTO checklist_templates (section_name, item_order, description, additional_info) VALUES (?, ?, ?, ?)"

        cursor.execute(query, ('Основной', next_order, description, additional_info))
        conn.commit()
        conn.close()

    def update_template_item(self, item_id: int, description: str, additional_info: str):
        """Обновляет существующий пункт шаблона"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if self.use_postgres:
            query = sql.SQL("UPDATE {} SET description = %s, additional_info = %s WHERE id = %s").format(
                sql.Identifier(self.schema + '.checklist_templates'))
        else:
            query = "UPDATE checklist_templates SET description = ?, additional_info = ? WHERE id = ?"
        cursor.execute(query, (description, additional_info, item_id))
        conn.commit()
        conn.close()

    def delete_template_item(self, item_id: int):
        """Удаляет пункт из шаблона"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if self.use_postgres:
            query = sql.SQL("DELETE FROM {} WHERE id = %s").format(sql.Identifier(self.schema + '.checklist_templates'))
        else:
            query = "DELETE FROM checklist_templates WHERE id = ?"
        cursor.execute(query, (item_id,))
        conn.commit()
        conn.close()

    # --------------------------------------------------------------------------
    # Методы для сессий и ответов
    # --------------------------------------------------------------------------
    def create_session(self, user_name: str, filial_id: int, vsp_id: int, op_date) -> int:
        """Создает сессию и возвращает её ID (статус сразу completed)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if self.use_postgres:
            query = sql.SQL(
                "INSERT INTO {} (user_name, filial_id, vsp_id, operation_date, status) VALUES (%s, %s, %s, %s, 'completed') RETURNING id").format(
                sql.Identifier(self.schema + '.checklist_sessions'))
            cursor.execute(query, (user_name, filial_id, vsp_id, op_date))
            session_id = cursor.fetchone()[0]
        else:
            query = "INSERT INTO checklist_sessions (user_name, filial_id, vsp_id, operation_date, status) VALUES (?, ?, ?, ?, 'completed')"
            cursor.execute(query, (user_name, filial_id, vsp_id, op_date))
            session_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return session_id

    def get_session_data(self, session_id: int) -> Dict[str, Any]:
        """Получает информацию о сессии и заполненные ответы."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Получаем метаданные сессии
        if self.use_postgres:
            cursor.execute(f"SELECT * FROM {self.schema}.checklist_sessions WHERE id = %s", (session_id,))
        else:
            cursor.execute("SELECT * FROM checklist_sessions WHERE id = ?", (session_id,))

        row = cursor.fetchone()
        if not row:
            return None

        session_info = dict(row)

        # Получаем ответы
        if self.use_postgres:
            cursor.execute(
                f"SELECT template_item_id, is_completed FROM {self.schema}.checklist_answers WHERE session_id = %s",
                (session_id,))
        else:
            cursor.execute("SELECT template_item_id, is_completed FROM checklist_answers WHERE session_id = ?",
                           (session_id,))

        answers = {row['template_item_id']: bool(row['is_completed']) for row in cursor.fetchall()}
        conn.close()

        return {"info": session_info, "answers": answers}

    def save_answers(self, session_id: int, answers: Dict[int, bool]):
        """Сохраняет ответы (перезаписывает или вставляет новые)."""
        conn = self.get_connection()
        cursor = conn.cursor()

        for item_id, is_completed in answers.items():
            if self.use_postgres:
                query = sql.SQL("""
                    INSERT INTO {} (session_id, template_item_id, is_completed) 
                    VALUES (%s, %s, %s)
                    ON CONFLICT (session_id, template_item_id) 
                    DO UPDATE SET is_completed = EXCLUDED.is_completed
                """).format(sql.Identifier(self.schema + '.checklist_answers'))
                cursor.execute(query, (session_id, item_id, is_completed))
            else:
                query = """
                    INSERT OR REPLACE INTO checklist_answers (session_id, template_item_id, is_completed) 
                    VALUES (?, ?, ?)
                """
                cursor.execute(query, (session_id, item_id, 1 if is_completed else 0))

        # Обновляем время изменения сессии
        if self.use_postgres:
            cursor.execute(f"UPDATE {self.schema}.checklist_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                           (session_id,))
        else:
            cursor.execute("UPDATE checklist_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (session_id,))

        conn.commit()
        conn.close()

    # Удаляем метод finalize_session, так как сессии теперь сразу завершены
    # Удаляем метод get_user_drafts, так как черновики не используются


# ==============================================================================
# 3. ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ И СЕССИИ STREAMLIT
# ==============================================================================

# Настройка страницы (должна быть первой командой Streamlit)
st.set_page_config(
    page_title="Чек-лист ВСП",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📋"
)

# Создаем экземпляр менеджера БД
db = DatabaseManager()
db.init_db()


# Заполнение тестовыми данными (если таблицы пустые)
def seed_initial_data():
    """Заполняет БД начальными справочниками и шаблонами, если их нет."""
    # Проверяем наличие филиалов
    if len(db.get_filials()) == 0:
        conn = db.get_connection()
        cursor = conn.cursor()
        # Добавляем филиалы
        filials = ['Центральный офис', 'Филиал Север', 'Филиал Юг', 'Филиал Запад', 'Филиал Восток']
        for f in filials:
            if db.use_postgres:
                cursor.execute(f"INSERT INTO {db.schema}.filials (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                               (f,))
            else:
                cursor.execute("INSERT OR IGNORE INTO filials (name) VALUES (?)", (f,))
        conn.commit()

        # Получаем ID филиалов для ВСП
        df_f = db.get_filials()

        # Добавляем ВСП для каждого филиала
        vsp_counter = 1
        for _, row in df_f.iterrows():
            fid = row['id']
            for i in range(1, 4):  # По 3 ВСП на филиал
                vsp_name = f"ВСП {vsp_counter:04d}"
                if db.use_postgres:
                    cursor.execute(f"INSERT INTO {db.schema}.vsp (filial_id, name) VALUES (%s, %s)", (fid, vsp_name))
                else:
                    cursor.execute("INSERT INTO vsp (filial_id, name) VALUES (?, ?)", (fid, vsp_name))
                vsp_counter += 1
        conn.commit()
        conn.close()
        print("✅ Тестовые справочники (филиалы, ВСП) добавлены")

    # Проверяем наличие шаблона чек-листа
    template = db.get_checklist_template()
    if len(template) == 0:
        # Добавляем стандартные проверки (как на скриншоте)
        items = [
            ("Проверка 1: Наличие вывески по брендбуку",
             "Проверить цвет, шрифт, подсветку вывески. Она должна соответствовать корпоративному стилю."),
            ("Проверка 2: Чистота в клиентской зоне",
             "Осмотр пола, стен, мебели. Отсутствие пыли, мусора, следов эксплуатации."),
            ("Проверка 3: Работа системы кондиционирования",
             "Температура должна быть 22-24 градуса. Проверить работу всех сплит-систем."),
            ("Проверка 4: Наличие актуальных рекламных материалов",
             "Стенды должны быть заполнены актуальными буклетами и листовками."),
            ("Проверка 5: Работоспособность терминалов самообслуживания",
             "Проверить все терминалы на предмет зависаний и ошибок."),
            ("Проверка 6: Наличие питьевой воды и стаканчиков",
             "Кулер должен быть заправлен, наличие чистых стаканчиков."),
            ("Проверка 7: Внешний вид сотрудников", "Соответствие dress-code, наличие бейджей."),
        ]
        for desc, add_info in items:
            db.add_template_item(desc, add_info)
        print("✅ Тестовый шаблон чек-листа добавлен")


# Запускаем заполнение тестовыми данными
seed_initial_data()

# Имитация системы авторизации (в реальном проекте здесь был бы SSO)
if "user_name" not in st.session_state:
    st.session_state.user_name = "Иванов Иван Иванович"

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# ==============================================================================
# 4. ИНТЕРФЕЙС ПОЛЬЗОВАТЕЛЯ
# ==============================================================================

st.title("📋 Система контроля качества ВСП")
st.caption("Заполнение чек-листа операционной проверки")

# Боковая панель только для информации о пользователе
with st.sidebar:
    st.header(f"👤 {st.session_state.user_name}")

    # Кнопка "Выход" (имитация)
    if st.button("🚪 Сменить пользователя (сброс сессии)", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key != 'user_name':
                del st.session_state[key]
        st.rerun()

    st.divider()
    st.caption("ℹ️ Для заполнения чек-листа используйте форму справа")
    st.caption("📊 Для управления шаблоном активируйте режим администратора")

# --- Административная панель (в основной области, появляется только при активации) ---
admin_mode = st.checkbox("🔑 Режим администратора (ЕСЦ)")
st.session_state.is_admin = admin_mode

if st.session_state.is_admin:
    st.markdown("---")
    st.subheader("⚙️ Панель администратора - Управление шаблоном чек-листа")

    template_df = db.get_checklist_template()

    # Отображаем существующие пункты
    st.dataframe(
        template_df[['id', 'item_order', 'description']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": "ID",
            "item_order": "№",
            "description": "Наименование проверки"
        }
    )

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("➕ Добавить проверку"):
            new_desc = st.text_area("Наименование проверки", key="new_check_desc")
            new_info = st.text_area("Дополнительная информация (пояснение)", key="new_check_info")
            if st.button("Добавить в шаблон", use_container_width=True):
                if new_desc:
                    db.add_template_item(new_desc, new_info)
                    st.success("✅ Проверка добавлена")
                    st.rerun()
                else:
                    st.error("❌ Введите наименование проверки")

    with col2:
        with st.expander("✏️ Редактировать/Удалить"):
            item_ids = template_df['id'].tolist()
            if item_ids:
                selected_id = st.selectbox(
                    "Выберите ID проверки для редактирования",
                    item_ids,
                    format_func=lambda x: f"ID {x}"
                )
                if selected_id:
                    row = template_df[template_df['id'] == selected_id].iloc[0]
                    edit_desc = st.text_area("Наименование", value=row['description'], key="edit_desc")
                    edit_info = st.text_area("Пояснение",
                                             value=row['additional_info'] if row['additional_info'] else "",
                                             key="edit_info")

                    edit_col1, edit_col2 = st.columns(2)
                    with edit_col1:
                        if st.button("💾 Обновить", use_container_width=True):
                            db.update_template_item(selected_id, edit_desc, edit_info)
                            st.success("✅ Проверка обновлена")
                            st.rerun()
                    with edit_col2:
                        if st.button("🗑️ Удалить", type="secondary", use_container_width=True):
                            db.delete_template_item(selected_id)
                            st.warning("⚠️ Проверка удалена")
                            st.rerun()

    # Выгрузка результатов
    st.subheader("📊 Выгрузка результатов проверок")
    if st.button("📥 Скачать отчет в CSV", use_container_width=True):
        try:
            conn = db.get_connection()
            if db.use_postgres:
                query = f"""
                    SELECT 
                        s.id, s.user_name, f.name as filial, v.name as vsp, 
                        s.operation_date, s.status, s.created_at, s.updated_at,
                        COUNT(a.id) as completed_checks
                    FROM {db.schema}.checklist_sessions s
                    JOIN {db.schema}.filials f ON s.filial_id = f.id
                    JOIN {db.schema}.vsp v ON s.vsp_id = v.id
                    LEFT JOIN {db.schema}.checklist_answers a ON s.id = a.session_id AND a.is_completed = true
                    GROUP BY s.id, f.name, v.name
                    ORDER BY s.created_at DESC
                """
            else:
                query = """
                    SELECT 
                        s.id, s.user_name, f.name as filial, v.name as vsp, 
                        s.operation_date, s.status, s.created_at, s.updated_at,
                        COUNT(a.id) as completed_checks
                    FROM checklist_sessions s
                    JOIN filials f ON s.filial_id = f.id
                    JOIN vsp v ON s.vsp_id = v.id
                    LEFT JOIN checklist_answers a ON s.id = a.session_id AND a.is_completed = 1
                    GROUP BY s.id
                    ORDER BY s.created_at DESC
                """
            df_export = pd.read_sql_query(query, conn)
            conn.close()

            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Скачать CSV файл",
                csv,
                f"checklist_report_{datetime.date.today()}.csv",
                "text/csv",
                use_container_width=True
            )
            st.success(f"✅ Отчет готов. Найдено {len(df_export)} записей.")
        except Exception as e:
            st.error(f"❌ Ошибка при формировании отчета: {e}")

    st.markdown("---")

# ==============================================================================
# 5. ОСНОВНАЯ ЛОГИКА ОТОБРАЖЕНИЯ ОКОН
# ==============================================================================

# Определяем текущий шаг: 0 - модальное окно, 1 - чек-лист
if "step" not in st.session_state:
    st.session_state.step = 0

# --- ШАГ 0: МОДАЛЬНОЕ ОКНО РЕГИСТРАЦИИ СЕАНСА ---
if st.session_state.step == 0:
    # Используем колонки для центрирования формы
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form(key="session_form"):
            st.markdown("### 📝 Регистрация сеанса заполнения чек-листа")
            st.markdown("---")

            # 1. ФИЛИАЛ (выпадающий список)
            filials_df = db.get_filials()
            if not filials_df.empty:
                filial_names = filials_df['name'].tolist()
                filial_map = dict(zip(filials_df['name'], filials_df['id']))
                selected_filial_name = st.selectbox(
                    "🏢 Филиал",
                    filial_names,
                    key="filial_select"
                )
                selected_filial_id = filial_map[selected_filial_name]

                # 2. ВСП (зависимый выпадающий список)
                vsp_df = db.get_vsp_by_filial(selected_filial_id)
                if not vsp_df.empty:
                    vsp_names = vsp_df['name'].tolist()
                    vsp_map = dict(zip(vsp_df['name'], vsp_df['id']))
                    selected_vsp_name = st.selectbox(
                        "🏪 ВСП",
                        vsp_names,
                        key="vsp_select"
                    )
                    selected_vsp_id = vsp_map[selected_vsp_name]
                else:
                    st.warning("⚠️ В выбранном филиале нет ВСП. Обратитесь к администратору.")
                    selected_vsp_id = None
            else:
                st.error("❌ Справочник филиалов пуст. Обратитесь к администратору.")
                st.stop()

            # 3. ФИО пользователя
            st.text_input(
                "👤 ФИО сотрудника",
                value=st.session_state.user_name,
                disabled=True
            )

            # 4. Дата операционного дня
            op_date = st.date_input(
                "📅 Дата операционного дня",
                value=datetime.date.today(),
                format="DD.MM.YYYY"
            )

            st.markdown("---")

            # 5. КНОПКА ПРОДОЛЖИТЬ
            submitted = st.form_submit_button(
                "▶️ НАЧАТЬ ЗАПОЛНЕНИЕ",
                type="primary",
                use_container_width=True
            )

            if submitted:
                if selected_vsp_id:
                    try:
                        # Создаем новую сессию в БД
                        session_id = db.create_session(
                            user_name=st.session_state.user_name,
                            filial_id=selected_filial_id,
                            vsp_id=selected_vsp_id,
                            op_date=op_date
                        )
                        st.session_state.current_session_id = session_id
                        st.session_state.step = 1
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Ошибка создания сессии: {e}")
                else:
                    st.error("❌ Невозможно продолжить без выбора ВСП.")

# --- ШАГ 1: ФОРМА ЧЕК-ЛИСТА ---
elif st.session_state.step == 1:
    if "current_session_id" not in st.session_state:
        st.error("❌ Ошибка: сессия не найдена. Вернитесь к регистрации.")
        if st.button("🔙 Вернуться к регистрации"):
            st.session_state.step = 0
            st.rerun()
        st.stop()

    session_id = st.session_state.current_session_id

    try:
        session_data = db.get_session_data(session_id)
    except Exception as e:
        st.error(f"❌ Ошибка загрузки данных сессии: {e}")
        if st.button("🔙 Вернуться к регистрации"):
            st.session_state.step = 0
            st.rerun()
        st.stop()

    if not session_data:
        st.error("❌ Сессия не найдена в базе данных.")
        st.stop()

    # Загружаем шаблон чек-листа
    template_df = db.get_checklist_template()
    if template_df.empty:
        st.warning("⚠️ Шаблон чек-листа пуст. Администратор должен добавить проверки.")
        st.stop()

    # Загружаем сохраненные ответы
    saved_answers = session_data['answers']

    # Отображаем информацию о сеансе
    st.subheader(f"📋 Чек-лист операционной проверки")

    # Получаем названия филиала и ВСП
    try:
        conn = db.get_connection()
        if db.use_postgres:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT f.name as filial_name, v.name as vsp_name 
                FROM {db.schema}.checklist_sessions s
                JOIN {db.schema}.filials f ON s.filial_id = f.id
                JOIN {db.schema}.vsp v ON s.vsp_id = v.id
                WHERE s.id = %s
            """, (session_id,))
            row = cursor.fetchone()
        else:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT f.name as filial_name, v.name as vsp_name 
                FROM checklist_sessions s
                JOIN filials f ON s.filial_id = f.id
                JOIN vsp v ON s.vsp_id = v.id
                WHERE s.id = ?
            """, (session_id,))
            row = cursor.fetchone()
        conn.close()

        if row:
            filial_name = row['filial_name'] if not db.use_postgres else row[0]
            vsp_name = row['vsp_name'] if not db.use_postgres else row[1]
        else:
            filial_name = f"ID: {session_data['info']['filial_id']}"
            vsp_name = f"ID: {session_data['info']['vsp_id']}"
    except:
        filial_name = f"ID: {session_data['info']['filial_id']}"
        vsp_name = f"ID: {session_data['info']['vsp_id']}"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**🏢 Филиал:** {filial_name}")
    with col2:
        st.markdown(f"**🏪 ВСП:** {vsp_name}")
    with col3:
        st.markdown(f"**📅 Дата:** {session_data['info']['operation_date']}")

    st.divider()

    # Создаем контейнер для таблицы чек-листа
    st.markdown("### ✅ Список проверок")

    # Заголовок таблицы
    header_cols = st.columns([1, 6, 2])
    header_cols[0].markdown("**№ п/п**")
    header_cols[1].markdown("**Наименование проверки**")
    header_cols[2].markdown("**Отчет о выполнении**")

    st.markdown("---")

    # Временное хранилище ответов
    if "temp_answers" not in st.session_state:
        st.session_state.temp_answers = copy.deepcopy(saved_answers)

    # Отображаем строки чек-листа
    for index, row in template_df.iterrows():
        item_id = row['id']
        order = row['item_order']
        description = row['description']
        additional_info = row['additional_info']

        # Текущее состояние чекбокса
        current_val = st.session_state.temp_answers.get(item_id, saved_answers.get(item_id, False))

        cols = st.columns([1, 6, 2])

        # Колонка 1: Номер
        cols[0].write(f"**{order}**")

        # Колонка 2: Наименование с дополнительными функциями
        with cols[1]:
            st.markdown(f"{description}")

            # Кнопки действий
            action_cols = st.columns([1, 1, 10])

            # Кнопка копирования
            if action_cols[0].button("📋", key=f"copy_{item_id}", help="Скопировать текст проверки"):
                st.toast(f"Текст скопирован: {description[:50]}...", icon="📋")
                st.session_state[f"copy_text_{item_id}"] = description

            # Кнопка информации
            if additional_info:
                action_cols[1].button("ℹ️", key=f"info_{item_id}", help=additional_info)
            else:
                action_cols[1].button("ℹ️", key=f"info_{item_id}", help="Дополнительная информация отсутствует",
                                      disabled=True)

        # Колонка 3: Статус выполнения
        with cols[2]:
            new_val = st.checkbox(
                "Выполнено",
                value=current_val,
                key=f"check_{item_id}",
                label_visibility="collapsed"
            )

            if new_val != current_val:
                st.session_state.temp_answers[item_id] = new_val

            # Визуальный индикатор
            if current_val:
                st.markdown("🟢 **✓ Выполнено**")
            else:
                st.markdown("⚪ **○ Не выполнено**")

        st.markdown("---")

    # --- КНОПКИ УПРАВЛЕНИЯ ---
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("🔙 Назад к регистрации", use_container_width=True):
            try:
                db.save_answers(session_id, st.session_state.temp_answers)
                st.success("✅ Данные сохранены")
            except Exception as e:
                st.error(f"❌ Ошибка сохранения: {e}")
            st.session_state.step = 0
            if "current_session_id" in st.session_state:
                del st.session_state.current_session_id
            if "temp_answers" in st.session_state:
                del st.session_state.temp_answers
            st.rerun()

    with col2:
        if st.button("💾 Сохранить", use_container_width=True):
            try:
                db.save_answers(session_id, st.session_state.temp_answers)
                st.success("✅ Результаты проверки сохранены!", icon="💾")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Ошибка сохранения: {e}")

    with col3:
        if st.button("✅ ЗАВЕРШИТЬ ПРОВЕРКУ", type="primary", use_container_width=True):
            try:
                # Сохраняем ответы
                db.save_answers(session_id, st.session_state.temp_answers)
                st.success("🎉 Чек-лист успешно завершен!", icon="✅")
                st.balloons()

                # Очищаем состояние и возвращаемся на главную
                st.session_state.step = 0
                if "current_session_id" in st.session_state:
                    del st.session_state.current_session_id
                if "temp_answers" in st.session_state:
                    del st.session_state.temp_answers

                time.sleep(2)  # Небольшая пауза для просмотра сообщения
                st.rerun()
            except Exception as e:
                st.error(f"❌ Ошибка при завершении проверки: {e}")