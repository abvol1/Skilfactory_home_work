"""
Модуль для работы с базой данных.
Поддерживает SQLite (для разработки) и PostgreSQL (для продакшена до 500+ пользователей).
Реализовано:
- Авторизация с филиалом
- Единая строка состояния (5 чекбоксов) на пользователя
- Логирование всех действий (отметка/снятие/сброс)
- Автоматический сброс чекбоксов при смене дня, но только после 12:00
"""

import os
import sqlite3
from datetime import datetime, date, time
from config import DATABASE_PATH, ADMIN_USERNAME, ADMIN_PASSWORD

# Определяем тип базы данных из переменной окружения
DB_TYPE = os.getenv("DB_TYPE", "sqlite")

# Условный импорт для PostgreSQL (если не используется SQLite)
if DB_TYPE == "postgres":
    import psycopg2


def get_db():
    """
    Возвращает соединение с базой данных в зависимости от DB_TYPE.
    Для SQLite используется sqlite3.connect с check_same_thread=False,
    чтобы несколько потоков (Streamlit) могли работать с одной БД.
    Для PostgreSQL – psycopg2.connect с параметрами из config.
    """
    if DB_TYPE == "postgres":
        return psycopg2.connect(
            host=os.getenv("PG_HOST", "localhost"),
            port=os.getenv("PG_PORT", "5432"),
            database=os.getenv("PG_DATABASE", "app_db"),
            user=os.getenv("PG_USER", "app_user"),
            password=os.getenv("PG_PASSWORD", "app_password")
        )
    else:
        # SQLite: check_same_thread=False необходимо для работы с Streamlit
        return sqlite3.connect(DATABASE_PATH, check_same_thread=False)


def execute_query(sql, params=None, fetch_one=False, fetch_all=False):
    """
    Универсальная функция для выполнения SQL-запросов.
    Автоматически открывает и закрывает соединение.
    Параметры:
        sql - строка SQL-запроса
        params - кортеж параметров для подстановки (опционально)
        fetch_one - вернуть одну запись
        fetch_all - вернуть все записи
    Возвращает:
        результат выборки (если fetch_one/fetch_all) или None
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        result = None
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()

        conn.commit()      # Фиксируем изменения
        return result
    except Exception as e:
        conn.rollback()    # Откат при ошибке
        raise e
    finally:
        conn.close()       # Всегда закрываем соединение


def init_db():
    """
    Инициализация базы данных: создание таблиц, добавление администратора,
    тестовых пользователей и инструкций для 5 чекбоксов.
    Вызывается один раз при запуске приложения.
    """
    conn = get_db()
    cursor = conn.cursor()

    # ---------- Создание таблиц (в зависимости от типа БД) ----------
    if DB_TYPE == "postgres":
        # PostgreSQL синтаксис (SERIAL, BOOLEAN, TIMESTAMP, DATE)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT,
                branch TEXT,
                last_reset_date DATE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkbox_states (
                user_id INTEGER,
                checkbox_id INTEGER,
                is_checked BOOLEAN,
                last_updated TIMESTAMP,
                updated_by INTEGER,
                PRIMARY KEY (user_id, checkbox_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkbox_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                checkbox_id INTEGER,
                action TEXT,
                timestamp TIMESTAMP,
                performed_by INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS instructions (
                checkbox_id INTEGER PRIMARY KEY,
                title TEXT,
                text TEXT,
                updated_at TIMESTAMP,
                updated_by INTEGER
            )
        ''')
    else:
        # SQLite синтаксис (AUTOINCREMENT, INTEGER, TEXT)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT,
                branch TEXT,
                last_reset_date TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkbox_states (
                user_id INTEGER,
                checkbox_id INTEGER,
                is_checked INTEGER,
                last_updated TEXT,
                updated_by INTEGER,
                PRIMARY KEY (user_id, checkbox_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkbox_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                checkbox_id INTEGER,
                action TEXT,
                timestamp TEXT,
                performed_by INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS instructions (
                checkbox_id INTEGER PRIMARY KEY,
                title TEXT,
                text TEXT,
                updated_at TEXT,
                updated_by INTEGER
            )
        ''')

    conn.commit()

    # ---------- Добавление колонок branch и last_reset_date (для старых БД) ----------
    # Это нужно, если база уже существовала без этих полей
    try:
        if DB_TYPE == "sqlite":
            cursor.execute("ALTER TABLE users ADD COLUMN branch TEXT")
            cursor.execute("ALTER TABLE users ADD COLUMN last_reset_date TEXT")
        else:
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS branch TEXT")
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_reset_date DATE")
        conn.commit()
    except:
        pass  # Колонки уже есть – игнорируем ошибку

    # ---------- Создание администратора, если его нет ----------
    admin = execute_query(
        "SELECT * FROM users WHERE username=?",
        (ADMIN_USERNAME,),
        fetch_one=True
    )
    if not admin:
        execute_query(
            "INSERT INTO users (username, password, role, branch, last_reset_date) VALUES (?, ?, ?, ?, ?)",
            (ADMIN_USERNAME, ADMIN_PASSWORD, 'admin', '0', None)
        )
        # Получаем ID созданного администратора
        admin_id = execute_query(
            "SELECT id FROM users WHERE username=?",
            (ADMIN_USERNAME,),
            fetch_one=True
        )[0]
    else:
        admin_id = admin[0]

    # ---------- Создание тестовых пользователей (логин/пароль/филиал) ----------
    test_users = [
        ('user1', 'pass1', 'user', '1'),
        ('user2', 'pass2', 'user', '2'),
        ('user3', 'pass3', 'user', '3')
    ]
    for username, password, role, branch in test_users:
        existing = execute_query(
            "SELECT * FROM users WHERE username=?",
            (username,),
            fetch_one=True
        )
        if not existing:
            execute_query(
                "INSERT INTO users (username, password, role, branch, last_reset_date) VALUES (?, ?, ?, ?, ?)",
                (username, password, role, branch, None)
            )

    # ---------- Инструкции для 5 чекбоксов (по умолчанию) ----------
    default_instructions = [
        (1, "📋 Чекбокс 1: Согласие с условиями",
         "### ✅ Условия использования\n\nПожалуйста, подтвердите, что вы ознакомились и согласны с условиями использования сервиса."),
        (2, "🔒 Чекбокс 2: Конфиденциальность",
         "### 🔒 Политика конфиденциальности\n\nВы соглашаетесь на обработку персональных данных."),
        (3, "📢 Чекбокс 3: Рассылка уведомлений",
         "### 📢 Подписка на уведомления\n\nВы соглашаетесь получать уведомления о важных событиях."),
        (4, "📊 Чекбокс 4: Аналитика",
         "### 📊 Сбор аналитики\n\nВы разрешаете сбор анонимной аналитики."),
        (5, "🤝 Чекбокс 5: Партнерские программы",
         "### 🤝 Партнерские программы\n\nВы соглашаетесь на участие в партнерских программах.")
    ]
    now = datetime.now().isoformat() if DB_TYPE == "sqlite" else datetime.now()
    for cb_id, title, text in default_instructions:
        existing = execute_query(
            "SELECT * FROM instructions WHERE checkbox_id=?",
            (cb_id,),
            fetch_one=True
        )
        if not existing:
            execute_query(
                "INSERT INTO instructions (checkbox_id, title, text, updated_at, updated_by) VALUES (?, ?, ?, ?, ?)",
                (cb_id, title, text, now, admin_id)
            )

    conn.close()


# ---------- Функции для работы с пользователями ----------

def get_user_by_credentials(username, password, branch):
    """
    Аутентификация пользователя по логину, паролю и номеру филиала.
    Возвращает словарь с данными пользователя или None.
    """
    user = execute_query(
        "SELECT id, username, password, role, branch FROM users WHERE username=? AND password=? AND branch=?",
        (username, password, branch),
        fetch_one=True
    )
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'password': user[2],
            'role': user[3],
            'branch': user[4]
        }
    return None


def get_user_by_id(user_id):
    """Возвращает данные пользователя по его ID."""
    user = execute_query(
        "SELECT id, username, password, role, branch FROM users WHERE id=?",
        (user_id,),
        fetch_one=True
    )
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'password': user[2],
            'role': user[3],
            'branch': user[4]
        }
    return None


def add_new_user(username, password, branch):
    """
    Добавляет нового обычного пользователя (role='user').
    Возвращает True при успехе, False если пользователь уже существует.
    """
    try:
        execute_query(
            "INSERT INTO users (username, password, role, branch, last_reset_date) VALUES (?, ?, ?, ?, ?)",
            (username, password, 'user', branch, None)
        )
        return True
    except Exception:
        return False


# ---------- Функция сброса чекбоксов по дате и времени ----------

def check_and_reset_daily(user_id):
    """
    Проверяет, нужно ли сбросить все чекбоксы пользователя.
    Условия сброса:
      1. Дата последнего сброса (last_reset_date) не равна сегодняшней дате.
      2. Текущее системное время >= 12:00 (полдень).
    Если оба условия выполнены – сбрасываем все чекбоксы в False,
    логируем действие с action='reset' и обновляем last_reset_date на сегодня.
    """
    # Получаем текущую дату и время
    today_date = date.today()
    current_time = datetime.now().time()
    # Время полудня
    noon = time(12, 0)

    # Запрашиваем дату последнего сброса для данного пользователя
    user = execute_query(
        "SELECT last_reset_date FROM users WHERE id=?",
        (user_id,),
        fetch_one=True
    )
    if not user:
        return False

    last_reset_str = user[0]  # может быть None или строка/дата
    last_reset_date = None
    if last_reset_str:
        if DB_TYPE == "sqlite":
            # В SQLite дата хранится как ISO-строка, преобразуем
            last_reset_date = date.fromisoformat(last_reset_str)
        else:
            # В PostgreSQL это уже объект date
            last_reset_date = last_reset_str

    # Условие 1: смена дня (сегодня != дата последнего сброса)
    day_changed = (last_reset_date != today_date)

    # Условие 2: текущее время >= 12:00
    after_noon = (current_time >= noon)

    if day_changed and after_noon:
        # Сбрасываем все чекбоксы пользователя в 0 (False)
        now_iso = datetime.now().isoformat()
        if DB_TYPE == "sqlite":
            execute_query(
                "UPDATE checkbox_states SET is_checked=0, last_updated=?, updated_by=? WHERE user_id=?",
                (now_iso, user_id, user_id)
            )
        else:
            execute_query(
                "UPDATE checkbox_states SET is_checked=False, last_updated=?, updated_by=? WHERE user_id=?",
                (datetime.now(), user_id, user_id)
            )

        # Логируем событие сброса (checkbox_id = 0 означает сброс всех)
        execute_query(
            "INSERT INTO checkbox_logs (user_id, checkbox_id, action, timestamp, performed_by) VALUES (?, ?, ?, ?, ?)",
            (user_id, 0, 'reset', now_iso, user_id)
        )

        # Обновляем дату последнего сброса на сегодня
        if DB_TYPE == "sqlite":
            execute_query(
                "UPDATE users SET last_reset_date=? WHERE id=?",
                (today_date.isoformat(), user_id)
            )
        else:
            execute_query(
                "UPDATE users SET last_reset_date=? WHERE id=?",
                (today_date, user_id)
            )
        return True
    return False


# ---------- Функции для работы с чекбоксами ----------

def get_checkbox_state(user_id, checkbox_id):
    """
    Возвращает состояние одного чекбокса (True/False).
    Перед этим проверяет необходимость сброса по дате.
    """
    check_and_reset_daily(user_id)  # возможно, сбросит все чекбоксы
    state = execute_query(
        "SELECT is_checked FROM checkbox_states WHERE user_id=? AND checkbox_id=?",
        (user_id, checkbox_id),
        fetch_one=True
    )
    return bool(state[0]) if state else False


def get_all_checkbox_states(user_id):
    """
    Возвращает словарь {checkbox_id: is_checked} для всех 5 чекбоксов.
    Перед этим проверяет необходимость сброса.
    """
    check_and_reset_daily(user_id)
    states = execute_query(
        "SELECT checkbox_id, is_checked FROM checkbox_states WHERE user_id=?",
        (user_id,),
        fetch_all=True
    )
    result = {}
    if states:
        for row in states:
            # В SQLite is_checked может быть 0/1, приводим к bool
            result[row[0]] = bool(row[1])
    # Заполняем недостающие чекбоксы (если пользователь ни разу не отмечал)
    for i in range(1, 6):
        if i not in result:
            result[i] = False
    return result


def set_checkbox_state(user_id, checkbox_id, is_checked, performed_by):
    """
    Устанавливает состояние одного чекбокса (отмечен/снят).
    Записывает действие в лог. Перед этим проверяет сброс по дате.
    """
    check_and_reset_daily(user_id)

    now = datetime.now().isoformat() if DB_TYPE == "sqlite" else datetime.now()
    # Приводим к формату, понятному БД
    is_checked_val = 1 if is_checked else 0 if DB_TYPE == "sqlite" else is_checked

    # INSERT OR REPLACE – если записи нет, создаётся; если есть – обновляется
    execute_query(
        '''INSERT OR REPLACE INTO checkbox_states 
           (user_id, checkbox_id, is_checked, last_updated, updated_by) 
           VALUES (?, ?, ?, ?, ?)''',
        (user_id, checkbox_id, is_checked_val, now, performed_by)
    )

    # Логируем действие: 'check' или 'uncheck'
    action = 'check' if is_checked else 'uncheck'
    execute_query(
        "INSERT INTO checkbox_logs (user_id, checkbox_id, action, timestamp, performed_by) VALUES (?, ?, ?, ?, ?)",
        (user_id, checkbox_id, action, now, performed_by)
    )


# ---------- Функции для инструкций ----------

def get_instruction(checkbox_id):
    """Возвращает словарь с заголовком и текстом инструкции для чекбокса."""
    instr = execute_query(
        "SELECT title, text FROM instructions WHERE checkbox_id=?",
        (checkbox_id,),
        fetch_one=True
    )
    if instr:
        return {'title': instr[0], 'text': instr[1]}
    return {'title': f'Чекбокс {checkbox_id}', 'text': 'Инструкция отсутствует'}


def update_instruction(checkbox_id, title, text, updated_by):
    """Обновляет инструкцию для указанного чекбокса."""
    now = datetime.now().isoformat() if DB_TYPE == "sqlite" else datetime.now()
    execute_query(
        "INSERT OR REPLACE INTO instructions (checkbox_id, title, text, updated_at, updated_by) VALUES (?, ?, ?, ?, ?)",
        (checkbox_id, title, text, now, updated_by)
    )


# ---------- Функции для администратора ----------

def get_all_users_status():
    """
    Возвращает список всех пользователей (role='user') с состоянием их 5 чекбоксов.
    Используется в админ-панели для отображения таблицы.
    """
    users = execute_query(
        "SELECT id, username, branch FROM users WHERE role='user'",
        fetch_all=True
    )
    result = []
    if users:
        for user_id, username, branch in users:
            states = execute_query(
                "SELECT checkbox_id, is_checked FROM checkbox_states WHERE user_id=?",
                (user_id,),
                fetch_all=True
            )
            checkbox_status = {}
            if states:
                for row in states:
                    checkbox_status[row[0]] = bool(row[1])
            for i in range(1, 6):
                if i not in checkbox_status:
                    checkbox_status[i] = False
            result.append({
                "username": username,
                "branch": branch,
                "user_id": user_id,
                "checkbox_1": checkbox_status[1],
                "checkbox_2": checkbox_status[2],
                "checkbox_3": checkbox_status[3],
                "checkbox_4": checkbox_status[4],
                "checkbox_5": checkbox_status[5]
            })
    return result


def get_all_logs(limit=100):
    """
    Возвращает последние 'limit' записей из логов с именами пользователей.
    Используется в админ-панели.
    """
    logs = execute_query('''
        SELECT l.id, l.user_id, u.username, u.branch, l.checkbox_id, l.action, l.timestamp, l.performed_by, p.username as performer_name
        FROM checkbox_logs l
        LEFT JOIN users u ON l.user_id = u.id
        LEFT JOIN users p ON l.performed_by = p.id
        ORDER BY l.id DESC LIMIT ?
    ''', (limit,), fetch_all=True)

    result = []
    if logs:
        for log in logs:
            result.append({
                'id': log[0],
                'user_id': log[1],
                'username': log[2],
                'branch': log[3],
                'checkbox_id': log[4],
                'action': log[5],
                'timestamp': log[6],
                'performed_by': log[7],
                'performer_name': log[8]
            })
    return result