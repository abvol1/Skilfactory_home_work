
📍 Куда именно вставить код диагностики

Вам нужно найти в вашем коде существующий блок админ-панели и заменить его.

1️⃣ Сначала найдите в своем коде где начинается админ-панель

Ищите что-то похожее на:

```python
# ВАШ СУЩЕСТВУЮЩИЙ КОД (пример)
if st.session_state.get('role') == 'admin':
    st.title("Админ-панель")
    # ... много кода админки
    # ... загрузка данных
    # ... отображение интерфейса
```

2️⃣ Замените НАЧАЛО этого блока

БЫЛО (ваш код):

```python
if st.session_state.get('role') == 'admin':
    st.title("Админ-панель")
    # ... ваш код
```

СТАЛО (с диагностикой):

```python
if st.session_state.get('role') == 'admin':
    
    # ⏱️ ПРОСТАЯ ДИАГНОСТИКА
    st.toast("🟢 ШАГ 1: Загрузка админ-панели...")
    time.sleep(0.5)
    
    # Проверка 1: session_state
    st.toast(f"🟢 ШАГ 2: SessionState OK. Ключей: {len(st.session_state)}")
    time.sleep(0.5)
    
    # Проверка 2: подключение к БД
    try:
        test_conn = db._get_connection()
        st.toast("🟢 ШАГ 3: Подключение к БД OK")
        time.sleep(0.5)
    except Exception as e:
        st.error(f"❌ БД не доступна: {e}")
        st.stop()
    
    # Проверка 3: загрузка данных
    try:
        # Загружаем по частям с уведомлениями
        st.toast("🟡 ШАГ 4: Загрузка пользователей...")
        users = db.get_all_users()
        st.toast(f"🟢 Загружено {len(users)} пользователей")
        time.sleep(0.5)
        
        st.toast("🟡 ШАГ 5: Загрузка сессий...")
        sessions = db.get_all_sessions()
        st.toast(f"🟢 Загружено {len(sessions)} сессий")
        time.sleep(0.5)
        
        st.toast("🟡 ШАГ 6: Загрузка статистики...")
        stats = db.get_admin_stats()
        st.toast("🟢 Статистика загружена")
        time.sleep(0.5)
        
    except Exception as e:
        st.error(f"❌ Ошибка загрузки: {e}")
        st.stop()
    
    st.toast("✅ ВСЕ ЗАГРУЖЕНО! Отрисовка интерфейса...")
    time.sleep(0.5)
    
    # ДАЛЬШЕ ВАШ КОД АДМИН-ПАНЕЛИ (который был до этого)
    st.title("Админ-панель")
    # ... остальной ваш код админки
```

3️⃣ Весь ваш существующий код админки ОСТАВЛЯЕМ без изменений

Весь код, который был у вас внутри if st.session_state.get('role') == 'admin': остается как есть, просто мы добавили диагностику в начало.

🔍 Пример полной замены

Допустим, у вас было так:

```python
if st.session_state.get('role') == 'admin':
    st.title("🔐 Админ-панель")
    
    menu = st.sidebar.selectbox(
        "Меню",
        ["Пользователи", "Сессии", "Статистика"]
    )
    
    if menu == "Пользователи":
        users = db.get_all_users()
        st.dataframe(users)
    elif menu == "Сессии":
        sessions = db.get_all_sessions()
        st.dataframe(sessions)
    else:
        stats = db.get_admin_stats()
        st.metric("Всего сессий", stats['total'])
```

После вставки диагностики будет так:

```python
if st.session_state.get('role') == 'admin':
    
    # ⏱️ ПРОСТАЯ ДИАГНОСТИКА
    st.toast("🟢 ШАГ 1: Загрузка админ-панели...")
    time.sleep(0.5)
    
    st.toast(f"🟢 ШАГ 2: SessionState OK. Ключей: {len(st.session_state)}")
    time.sleep(0.5)
    
    try:
        test_conn = db._get_connection()
        st.toast("🟢 ШАГ 3: Подключение к БД OK")
        time.sleep(0.5)
    except Exception as e:
        st.error(f"❌ БД не доступна: {e}")
        st.stop()
    
    try:
        st.toast("🟡 ШАГ 4: Загрузка пользователей...")
        users = db.get_all_users()
        st.toast(f"🟢 Загружено {len(users)} пользователей")
        time.sleep(0.5)
        
        st.toast("🟡 ШАГ 5: Загрузка сессий...")
        sessions = db.get_all_sessions()
        st.toast(f"🟢 Загружено {len(sessions)} сессий")
        time.sleep(0.5)
        
        st.toast("🟡 ШАГ 6: Загрузка статистики...")
        stats = db.get_admin_stats()
        st.toast("🟢 Статистика загружена")
        time.sleep(0.5)
        
    except Exception as e:
        st.error(f"❌ Ошибка загрузки: {e}")
        st.stop()
    
    st.toast("✅ ВСЕ ЗАГРУЖЕНО! Отрисовка интерфейса...")
    time.sleep(0.5)
    
    # ===== ВАШ СУЩЕСТВУЮЩИЙ КОД =====
    st.title("🔐 Админ-панель")
    
    menu = st.sidebar.selectbox(
        "Меню",
        ["Пользователи", "Сессии", "Статистика"]
    )
    
    if menu == "Пользователи":
        # users уже загружены выше
        st.dataframe(users)
    elif menu == "Сессии":
        # sessions уже загружены выше
        st.dataframe(sessions)
    else:
        # stats уже загружены выше
        st.metric("Всего сессий", stats['total'])
```

⚠️ Важно!

1. Не забудьте импортировать time в начале файла (если еще нет):

```python
import time
```

2. Если у вас нет функций db.get_all_users(), db.get_all_sessions(), db.get_admin_stats() - замените на ваши реальные функции загрузки данных
3. Смотрите в какой момент останавливается выполнение - какое последнее сообщение вы видите

📌 Если после вставки кода ничего не работает - просто уберите диагностику и скажите мне, какие функции у вас есть в админ-панели, я подстрою код под них.


















Отличный вопрос! Давайте разберем, почему в первой вкладке кнопка работает, а во второй - нет.

🔍 Анализ проблемы

Посмотрите внимательно на ID элементов в коде:

Вкладка "Фильтр" (работает):

```javascript
// ID кнопки
id="copy_{item_id}"           // например: copy_123

// ID статуса  
id="status_{item_id}"         // например: status_123

// В JavaScript:
var btn = document.getElementById("copy_{item_id}");
var statusDiv = document.getElementById("status_{item_id}");
```

Вкладка "Дополнительный фильтр" (НЕ работает):

```javascript
// ID кнопки
id="copy2_{item_id}"          // например: copy2_123

// ID статуса
id="status_{item_id}"         // например: status_123   ⚠️ ТАКОЙ ЖЕ!

// В JavaScript:
var btn = document.getElementById("copy_2{item_id}");  // ❌ ОШИБКА!
// Должно быть: "copy2_{item_id}", а написано "copy_2{item_id}"
```

🐛 Ошибки в коде второй вкладки:

1. Несоответствие ID: В HTML кнопка имеет id="copy2_{item_id}", а в JavaScript ищется "copy_2{item_id}" (без подчеркивания)
2. Статус-бар имеет такой же ID, как в первой вкладке - конфликт

✅ Исправленный код для вкладки "Дополнительный фильтр":

```python
with t2:
    st.markdown("**Описание процедуры:**"); st.info(chosen_info)
    if chosen_events != "Не задан":
        filter_display = chosen_events
        today = datetime.date.today()

        if "[Дата1]" in filter_display:
            st.date_input("📅 Дата (автоматически сегодня)", value=today, disabled=True, key=f"date2_{item_id}", format="DD.MM.YYYY")
            filter_display = filter_display.replace("[Дата1]", today.strftime("%d.%m.%y"))
        if "[Дата1 гггг-мм-дд]" in filter_display:
            filter_display = filter_display.replace("[Дата1 гггг-мм-дд]", today.strftime("%Y-%m-%d"))
        if "[Дата1 дд.мм.гггг]" in filter_display:
            filter_display = filter_display.replace("[Дата1 дд.мм.гггг]", today.strftime("%d.%m.%Y"))
        filter_display = filter_display.replace("[РФ]", vsp_name)
        filter_display = filter_display.replace("[РФ1]", vsp_name[:3])
        st.code(filter_display, language="text")
        
        import streamlit.components.v1 as components
        js = f"""<div style="margin-top:8px">
            <button id="copy2_{item_id}" style="background:#4CAF50;color:white;padding:8px;border:none;border-radius:5px;width:100%">📋 КОПИРОВАТЬ ФИЛЬТР</button>
            <div id="status2_{item_id}" style="margin-top:5px;font-size:12px;text-align:center"></div>
        </div>
        <script>
        (function(){{
            var btn = document.getElementById("copy2_{item_id}");
            var statusDiv = document.getElementById("status2_{item_id}");
            var textToCopy = {repr(filter_display)};
            btn.addEventListener("click", function(){{
                navigator.clipboard.writeText(textToCopy)
                    .then(function(){{
                        statusDiv.innerHTML = "✅ Скопировано!";
                        statusDiv.style.color = "green";
                        setTimeout(function(){{ statusDiv.innerHTML = ""; }}, 2000);
                    }})
                    .catch(function(){{
                        statusDiv.innerHTML = "❌ Ошибка";
                        statusDiv.style.color = "red";
                    }});
            }});
        }})();
        </script>"""
        components.html(js, height=100)
    else:
        st.info("Фильтр не задан")
```

📝 Что было исправлено:

1. ID статуса: status_{item_id} → status2_{item_id} (чтобы не конфликтовать с первой вкладкой)
2. JavaScript селектор: "copy_2{item_id}" → "copy2_{item_id}" (исправлена опечатка)
3. Улучшена читаемость кода для отладки

🎯 Альтернатива - если хотите просто убрать кнопку:

Если вы все же хотите удалить кнопку, вот гарантированно работающий вариант:

```python
with t2:
    st.markdown("**Описание процедуры:**"); st.info(chosen_info)
    if chosen_events != "Не задан":
        filter_display = chosen_events
        today = datetime.date.today()

        if "[Дата1]" in filter_display:
            st.date_input("📅 Дата (автоматически сегодня)", value=today, disabled=True, key=f"date2_{item_id}", format="DD.MM.YYYY")
            filter_display = filter_display.replace("[Дата1]", today.strftime("%d.%m.%y"))
        if "[Дата1 гггг-мм-дд]" in filter_display:
            filter_display = filter_display.replace("[Дата1 гггг-мм-дд]", today.strftime("%Y-%m-%d"))
        if "[Дата1 дд.мм.гггг]" in filter_display:
            filter_display = filter_display.replace("[Дата1 дд.мм.гггг]", today.strftime("%d.%m.%Y"))
        filter_display = filter_display.replace("[РФ]", vsp_name)
        filter_display = filter_display.replace("[РФ1]", vsp_name[:3])
        
        # Показываем только текст фильтра, без кнопки
        st.code(filter_display, language="text")
        # ВСЕ! Никакого JavaScript, никаких кнопок
    else:
        st.info("Фильтр не задан")
```

Этот вариант точно не упадет, потому что мы удаляем весь проблемный код.










"""
ЧЕК-ЛИСТ ВСП (Streamlit + PostgreSQL)
=====================================
Финальная версия:
  - Запрет создания черновика любым пользователем конкретного ВСП (если за сегодня уже есть черновик/завершенный по данному ВСП, то никкто в этом ВСП не сможет больше начать заполнение чек листа повторно)
  - Пользователь видит/удаляет нерабочие дни только своего ВСП (не зависимо от того он ли эти записи сделал).
  - Админ управляет шаблоном (вставка, удаление, перемещение).
  - Визуализация: 
       * пользователь – «бублик» по своему филиалу (легко определить  какое ВСП по своему Филиалу не заполнило Чек-лист),
       * админ – по выбранному филиалу + сводка по всем филиалам (легко определить какой Филиал, какое ВСП не заполнило Чек-лист).
  - Админ может во вкладке Чек-боксы (Филиалы)  отмечать те Филиалы, такие как Липецк, которые были мигрированы  (если чек-бокс установлен то пользователю подгружаются другие фильтры)
  - Удаление черновиков:
      * пользователь может удалить свой черновик,
      * админ может выбрать нужные ему черновики (сразу несколько) и удалить
  - Дата [Дата1] всегда сегодня и не редактируется.
  - Админ может массового добавлять выходные дни по всем ВСП Филиала.
  - Админ может штучного удалять нерабочие  ВСП под админом
  - Добавлена Витрина под админом
  - Добавлена возмжность возврата сессии из Завершено в Черновик !!!
  - Скорректировал выпдающие списки с Филиалами привел их к виду ( пример :было Самарский филиал стало 013 - Самарский филиал)
  - Добавил в панеле админа возможность редактировать ФИО (но так как база с пользователями постоянно обновляется то это редактированое поле актуально только до следующего обновления БД с пользователями)
  - Добавлена вкладка Аналитика для сотрудника ВСП
  - Добавлена возмжность админу добавлять выходные как штучно так и за период по ВСП.
  - Добавлена возможность во вкладке Аналитика для сотрудника ВСП выборка по дате
  - Добавляем возможность заглушки (если ФИЛИАЛ еще не входит в пилотный проект)
  - Добавляем возможность автоматического подтягивания номера ВСП из таблицы USERS
  - Корректируем данные в "Истории проверок" делаем фильтрацию по ФИО +ФИЛИАЛ (что бы пользователь видил только свои проверки)
  - Добавлена возможность автоматического "подтягивания логина" в авторизацию (СКК)
  - Добавлена возможность подмены Даты в фильтр в разных форматах
  - Добавлена возможность массового добавления суббот на все ВСП всех филиалов, а также массового удаления ВСП (можно выбрать в мультиселекте) но по одному РФ
  - Корректировка автологирования (тезки) (скк)
  - В фильтр добавлена возможность подмены  [РФ1] на номер РФ
  - Убрал возможность просмотра пользователем всех выходных по его РФ и нет теперь у пользователя возможности удалять выходные (так как это перегружает помять и приложение падает)
  - Добавил вместо Мероприятия  второй дополнительный фильтр
"""

import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
from typing import Dict, Any, Optional
import copy
import time
import numpy as np
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# НАСТРОЙКА СТРАНИЦЫ
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Чек-лист ВСП/РФ",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="✔️"
)

#----------------------------- ЭТОТ БЛОК ОТВЕЧАЕТ ЗА АВТОМАТИЧЕСКОЕ ЛОГИРОВАНИЕ !!!-------------------------------
load_dotenv()

from raisa_streamlit_oauth import protect_application, get_jwt_token

protect_application()

token = get_jwt_token()

st.session_state["email"] = token.get("email", "unknown") 

# -------------------------------------------------------------------------------------------------------------------
# КОНФИГУРАЦИЯ БД (замените на свои параметры)
# -----------------------------------------------------------------------------
PG_CONFIG = {
    "host": "",
    "port": 5432,
    "database": "",
    "user": "",
    "password": "",
    "schema": ""
}

ADMIN_PASSWORD = "admin123"

NON_WORKING_REASONS = [
    "Ремонтные работы",
    "Праздничный день",
    "Выходной день",
    "Технические причины",
    "Другое"
]

# =============================================================================
# КЛАСС ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ
# =============================================================================
class DatabaseManager:
    def __init__(self):
        self.schema = PG_CONFIG['schema']
        self._connection = None
        self._cursor = None

    # --- соединение/курсор ---
    def _get_connection(self):
        if self._connection is None:
            self._connection = psycopg2.connect(
                host=PG_CONFIG['host'], port=PG_CONFIG['port'],
                dbname=PG_CONFIG['database'], user=PG_CONFIG['user'],
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

    def _table_name(self, table: str) -> str:
        return f"{self.schema}.{table}"

    def _execute(self, query, params=None, fetch_one=False, fetch_all=False, commit=True):

        if params:
           # Преобразуем numpy.int64 и numpy.int32 в обычный int
           params = tuple(
              int(p) if hasattr(p, 'dtype') and 'int' in str(p.dtype) else p
              for p in params
           )


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

    def _to_df(self, query, params=None):
        try:
            conn = self._get_connection()
            return pd.read_sql_query(query, conn, params=params or ())
        except Exception as e:
            self._reset_connection()
            raise e

    # -------------------------------------------------------------------------
    # ФИЛИАЛЫ И ВСП
    # -------------------------------------------------------------------------
    def get_filials(self):
        return self._to_df(f"SELECT id, name, check_name FROM {self._table_name('filials')} ORDER BY name")


    # ---- ДОБАВИТЬ ЭТОТ БЛОК ДЛЯ ВОЗМОЖНОСТИ БЛОКИРОВОК ПО ФИЛИАЛАМ (ПИЛОТ/НЕ ПИЛОТ)----
    def get_filial_blocked_status(self, filial_id: int) -> bool:
        filial_id = int(filial_id)
        row = self._execute(
            f"SELECT blocked FROM {self._table_name('filials')} WHERE id = %s",
            (filial_id,), fetch_one=True
        )
        return row['blocked'] if row else False

    def set_filial_blocked(self, filial_id: int, blocked: bool):
        filial_id = int(filial_id)
        self._execute(
            f"UPDATE {self._table_name('filials')} SET blocked = %s WHERE id = %s",
            (blocked, filial_id)
        )


        

    def set_filial_check(self, filial_id, check_value):
        self._execute(f"UPDATE {self._table_name('filials')} SET check_name=%s WHERE id=%s", (check_value, int(filial_id)))

    def get_vsp_by_filial(self, filial_id):
        return self._to_df(f"SELECT id, name, name_vsp FROM {self._table_name('vsp')} WHERE filial_id=%s ORDER BY name", (int(filial_id),))

    def get_all_vsp(self):
        return self._to_df(f"SELECT id, name, name_vsp FROM {self._table_name('vsp')} ORDER BY name")

    def delete_non_working_day_by_vsp_date(self, vsp_id, date):
        """Удаляет запись о нерабочем дне для конкретного ВСП на конкретную дату (если есть)."""
        self._execute(
            f"DELETE FROM {self._table_name('vsp_non_working_days')} WHERE vsp_id = %s AND date = %s",
            (vsp_id, date)
        )


    def delete_saturdays_for_vsp_list(self, vsp_ids, date_from, date_to):
        """
        Удаляет нерабочие дни (субботы) для списка ВСП в указанном диапазоне дат.
        vsp_ids: список целых чисел (ID ВСП)
        Возвращает общее количество удалённых записей.
        """
        if not vsp_ids:
            return 0
    
        # Приводим все ID к int и сохраняем как список
        vsp_ids = [int(vid) for vid in vsp_ids]
    
        # Параметры: (список, дата_от, дата_до)
        params = (vsp_ids, date_from, date_to)
    
        count_query = f"""
            SELECT COUNT(*) as cnt 
            FROM {self._table_name('vsp_non_working_days')}
            WHERE vsp_id = ANY(%s) 
              AND date BETWEEN %s AND %s 
              AND EXTRACT(DOW FROM date) = 6
        """
        count_row = self._execute(count_query, params, fetch_one=True)
        count = count_row['cnt'] if count_row else 0
    
        if count:
            delete_query = f"""
                DELETE FROM {self._table_name('vsp_non_working_days')}
                WHERE vsp_id = ANY(%s) 
                  AND date BETWEEN %s AND %s 
                  AND EXTRACT(DOW FROM date) = 6
            """
            self._execute(delete_query, params)
    
        return count



    # -------------------------------------------------------------------------
    # ФИЛИАЛЫ (ЗАГЛУШКИ ДЛЯ ФИЛИЛАЛ КОТОРЫЕ ЕЩЕ НЕ В ПИЛОТЕ)
    # -------------------------------------------------------------------------

    def set_filial_blocked(self, filial_id: int, blocked: bool):
        filial_id = int(filial_id)
        self._execute(
            f"UPDATE {self._table_name('filials')} SET blocked = %s WHERE id = %s",
            (blocked, filial_id)
        )

    def set_filial_blocked(self, filial_id: int, blocked: bool):
        self._execute(
            f"UPDATE {self._table_name('filials')} SET blocked = %s WHERE id = %s",
            (blocked, filial_id)
        )


    # -------------------------------------------------------------------------
    # ШАБЛОН ЧЕК-ЛИСТА (управление порядком)
    # -------------------------------------------------------------------------
    def get_checklist_template(self):
        return self._to_df(
            f"SELECT id, item_order, description, additional_info, filter_value, events_value, "
            f"alt_filter_value, alt_additional_info, alt_events_value "
            f"FROM {self._table_name('checklist_templates')} ORDER BY item_order"
        )

    def add_template_item(self, description, additional_info, filter_value="", events_value="",
                          alt_filter="", alt_info="", alt_events="", position=None):
        max_row = self._execute(f"SELECT COALESCE(MAX(item_order),0) max_o FROM {self._table_name('checklist_templates')}", fetch_one=True)
        max_order = max_row['max_o']
        if position is None or position > max_order:
            next_order = max_order + 1
        else:
            self._execute(f"UPDATE {self._table_name('checklist_templates')} SET item_order=item_order+1 WHERE item_order>=%s", (position,))
            next_order = position
        self._execute(
            f"INSERT INTO {self._table_name('checklist_templates')} (section_name,item_order,description,additional_info,filter_value,events_value,alt_filter_value,alt_additional_info,alt_events_value) "
            f"VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            ('Основной', next_order, description, additional_info, filter_value, events_value, alt_filter, alt_info, alt_events)
        )

    def update_template_item(self, item_id, description, additional_info, filter_value="", events_value="",
                             alt_filter="", alt_info="", alt_events=""):
        self._execute(
            f"UPDATE {self._table_name('checklist_templates')} SET description=%s,additional_info=%s,filter_value=%s,events_value=%s,alt_filter_value=%s,alt_additional_info=%s,alt_events_value=%s WHERE id=%s",
            (description, additional_info, filter_value, events_value, alt_filter, alt_info, alt_events, item_id)
        )

    def delete_template_item(self, item_id):
        self._execute(f"DELETE FROM {self._table_name('checklist_answers')} WHERE template_item_id=%s", (item_id,))
        self._execute(f"DELETE FROM {self._table_name('checklist_templates')} WHERE id=%s", (item_id,))
        self._execute(f"""
            UPDATE {self._table_name('checklist_templates')} AS t
            SET item_order = t2.new_order
            FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY item_order) new_order FROM {self._table_name('checklist_templates')}) t2
            WHERE t.id = t2.id
        """)

    def move_template_item(self, item_id, direction):
        row = self._execute(f"SELECT item_order FROM {self._table_name('checklist_templates')} WHERE id=%s", (item_id,), fetch_one=True)
        if not row: return
        current = row['item_order']
        if direction == 'up' and current > 1:
            target = current - 1
        elif direction == 'down':
            max_row = self._execute(f"SELECT MAX(item_order) max_o FROM {self._table_name('checklist_templates')}", fetch_one=True)
            max_order = max_row['max_o']
            if current < max_order:
                target = current + 1
            else:
                return
        else:
            return
        neighbor = self._execute(f"SELECT id FROM {self._table_name('checklist_templates')} WHERE item_order=%s", (target,), fetch_one=True)
        if not neighbor: return
        self._execute(f"UPDATE {self._table_name('checklist_templates')} SET item_order=%s WHERE id=%s", (target, item_id))
        self._execute(f"UPDATE {self._table_name('checklist_templates')} SET item_order=%s WHERE id=%s", (current, neighbor['id']))

    def move_to_position(self, item_id, new_position):
        row = self._execute(f"SELECT item_order FROM {self._table_name('checklist_templates')} WHERE id=%s", (item_id,), fetch_one=True)
        if not row: return
        old_pos = row['item_order']
        max_row = self._execute(f"SELECT MAX(item_order) max_o FROM {self._table_name('checklist_templates')}", fetch_one=True)
        max_order = max_row['max_o']
        if new_position < 1 or new_position > max_order or new_position == old_pos: return
        if new_position < old_pos:
            self._execute(f"UPDATE {self._table_name('checklist_templates')} SET item_order=item_order+1 WHERE item_order>=%s AND item_order<%s", (new_position, old_pos))
        else:
            self._execute(f"UPDATE {self._table_name('checklist_templates')} SET item_order=item_order-1 WHERE item_order>%s AND item_order<=%s", (old_pos, new_position))
        self._execute(f"UPDATE {self._table_name('checklist_templates')} SET item_order=%s WHERE id=%s", (new_position, item_id))

    # -------------------------------------------------------------------------
    # СЕССИИ
    # -------------------------------------------------------------------------
    def create_session(self, user_full_name, filial_id, vsp_id, op_date, status_bul=False):
        row = self._execute(
            f"INSERT INTO {self._table_name('checklist_sessions')} (user_name,filial_id,vsp_id,operation_date,status_bul) VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (user_full_name, filial_id, vsp_id, op_date, status_bul), fetch_one=True
        )
        return row['id']

    def get_today_draft_session_id(self, user_name: str) -> Optional[int]:
        today = datetime.date.today()
        row = self._execute(
            f"SELECT id FROM {self._table_name('checklist_sessions')} WHERE user_name=%s AND operation_date=%s AND status_bul=FALSE LIMIT 1",
            (user_name, today), fetch_one=True
        )
        return row['id'] if row else None

    def session_exists_for_vsp_date(self, vsp_id, operation_date):
        """Проверяет, есть ли уже любая сессия для данного ВСП на указанную дату."""
        row = self._execute(
             f"SELECT id FROM {self._table_name('checklist_sessions')} "
             f"WHERE vsp_id = %s AND operation_date = %s LIMIT 1",
             (vsp_id, operation_date),
             fetch_one=True
         )
        return row is not None




         

    def check_user_by_name(self, name: str):
        query = f"""
            SELECT 
                us.name, 
                us.full_name, 
                f.name AS filial_name, 
                f.id AS filial_id,
                us.name_vsp,
                v.id AS vsp_id
            FROM {self.schema}.users us
            LEFT JOIN {self.schema}.filials f ON us.name_filial::numeric = f.id
            LEFT JOIN {self.schema}.vsp v ON us.name_vsp = v.name
            WHERE LOWER(us.name) = LOWER(%s)
        """
        df = self._to_df(query, (name,))
        if not df.empty:
            row = df.iloc[0]
            filial_id = int(row['filial_id']) if row.get('filial_id') is not None else None
            vsp_id = int(row['vsp_id']) if row.get('vsp_id') is not None else None
            return (
                True,
                row['full_name'],
                row.get('filial_name'),
                filial_id,
                row.get('name_vsp'),
                vsp_id
           )
        return False, None, None, None, None, None

    #------------------------------ЭТА ЧАСТЬ КОДА ТАК ЖЕ ОТВЕЧАЕТ ЗА АВТОМАТИЧЕСКОЕ ЛОГИРОВАНИЕ-------------------------------------
    def get_user_logins_by_email(self, email: str):
            query = f"""
                SELECT DISTINCT
                    us.name,
                    us.full_name,
                    su.email
                FROM {self.schema}.sed_users su
                JOIN {self.schema}.users us
                    ON LOWER(TRIM(us.full_name)) = LOWER(TRIM(su.full_name))
                WHERE LOWER(TRIM(su.email)) = LOWER(TRIM(%s))
                ORDER BY us.name
            """

            df = self._to_df(query, (email,))

            return [
                {
                    "name": row["name"],
                    "full_name": row["full_name"],
                    "email": row["email"],
                }
                for _, row in df.iterrows()
            ]
    #--------------------------------------------------------------------------------------------------------------------------------------------

    def update_user_full_name(self, login, new_full_name):
         """Обновляет full_name пользователя по его логину."""
         self._execute(
              f"UPDATE {self._table_name('users')} SET full_name = %s WHERE LOWER(name) = LOWER(%s)",
              (new_full_name, login)
         )


    def get_filial_sessions(self, filial_id: int):
        return self._to_df(f"""
            SELECT s.id, s.user_name "Сотрудник", s.operation_date "Дата проверки",
                   v.name "ВСП",
                   CASE s.status_bul WHEN TRUE THEN 'Завершена' ELSE 'Черновик' END "Статус",
                   s.created_at "Дата и время начала", s.completed_at "Дата и время завершения",
                   COUNT(a.id) "Выполнено проверок",
                   (SELECT COUNT(*) FROM {self.schema}.checklist_templates) "Всего проверок"
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.vsp v ON s.vsp_id = v.id
            LEFT JOIN {self.schema}.checklist_answers a ON s.id = a.session_id AND a.is_completed = true
            WHERE s.filial_id = %s
            GROUP BY s.id, v.name, s.user_name, s.operation_date, s.status_bul, s.created_at, s.completed_at
            ORDER BY s.created_at DESC
        """, (int(filial_id),))
    

    

    def update_session_status(self, session_id, completed):
        if completed:
            self._execute(f"UPDATE {self._table_name('checklist_sessions')} SET status_bul=TRUE, completed_at=CURRENT_TIMESTAMP WHERE id=%s", (session_id,))
        else:
            self._execute(f"UPDATE {self._table_name('checklist_sessions')} SET status_bul=FALSE, completed_at=NULL WHERE id=%s", (session_id,))

    def delete_session(self, session_id):
        self._execute(f"DELETE FROM {self._table_name('checklist_answers')} WHERE session_id=%s", (session_id,))
        self._execute(f"DELETE FROM {self._table_name('checklist_sessions')} WHERE id=%s", (session_id,))

    def delete_all_drafts(self):
        """Удаляет ВСЕ черновики и связанные ответы."""
        self._execute(f"DELETE FROM {self._table_name('checklist_answers')} WHERE session_id IN (SELECT id FROM {self._table_name('checklist_sessions')} WHERE status_bul=FALSE)")
        self._execute(f"DELETE FROM {self._table_name('checklist_sessions')} WHERE status_bul=FALSE")

    def get_user_draft_sessions(self, full_name: str):
        return self._to_df(f"""
            SELECT s.id, s.operation_date, f.name filial_name, v.name vsp_name,
                   s.created_at, COUNT(a.id) completed_count,
                   (SELECT COUNT(*) FROM {self.schema}.checklist_templates) total_count
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id=f.id
            JOIN {self.schema}.vsp v ON s.vsp_id=v.id
            LEFT JOIN {self.schema}.checklist_answers a ON s.id=a.session_id AND a.is_completed=true
            WHERE s.user_name=%s AND s.status_bul=FALSE
            GROUP BY s.id, f.name, v.name, s.operation_date, s.created_at
            ORDER BY s.created_at DESC
        """, (full_name,))

    def get_last_user_session_data(self, full_name: str):
        df = self._to_df(f"""
            SELECT f.id filial_id, f.name filial_name, v.id vsp_id, v.name vsp_name
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id=f.id
            JOIN {self.schema}.vsp v ON s.vsp_id=v.id
            WHERE s.user_name=%s AND s.status_bul=TRUE
            ORDER BY s.created_at DESC LIMIT 1
        """, (full_name,))
        return df.iloc[0].to_dict() if not df.empty else None

    def get_last_user_any_session_data(self, full_name: str):
        df = self._to_df(f"""
            SELECT f.id filial_id, f.name filial_name, v.id vsp_id, v.name vsp_name
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id=f.id
            JOIN {self.schema}.vsp v ON s.vsp_id=v.id
            WHERE s.user_name=%s
            ORDER BY s.created_at DESC LIMIT 1
        """, (full_name,))
        return df.iloc[0].to_dict() if not df.empty else None

    def get_session_data(self, session_id):
        cur = self._get_cursor()
        cur.execute(f"SELECT * FROM {self._table_name('checklist_sessions')} WHERE id=%s", (session_id,))
        row = cur.fetchone()
        if not row:
            return None
        info = dict(row)
        cur.execute(f"SELECT template_item_id, is_completed FROM {self._table_name('checklist_answers')} WHERE session_id=%s", (session_id,))
        answers = {r['template_item_id']: r['is_completed'] for r in cur.fetchall()}
        return {"info": info, "answers": answers}

    def save_answers(self, session_id, answers):
        cur = self._get_cursor()
        for item_id, comp in answers.items():
            cur.execute(
                f"INSERT INTO {self._table_name('checklist_answers')} (session_id,template_item_id,is_completed) VALUES (%s,%s,%s) ON CONFLICT (session_id,template_item_id) DO UPDATE SET is_completed=EXCLUDED.is_completed",
                (session_id, item_id, comp)
            )
        self._get_connection().commit()

    # -------------------------------------------------------------------------
    # НЕРАБОЧИЕ ДНИ
    # -------------------------------------------------------------------------
    def add_non_working_day(self, user_name, filial_id, vsp_id, day, reason):
        self._execute(
            f"INSERT INTO {self._table_name('vsp_non_working_days')} (user_name,filial_id,vsp_id,date,reason) VALUES (%s,%s,%s,%s,%s)",
            (user_name, filial_id, vsp_id, day, reason)
        )

    def delete_non_working_day(self, record_id, vsp_id, filial_id):
        self._execute(
            f"DELETE FROM {self._table_name('vsp_non_working_days')} WHERE id=%s AND vsp_id=%s AND filial_id=%s",
            (record_id, vsp_id, filial_id)
        )

    def get_non_working_days(self, filial_id=None, vsp_id=None, date_from=None, date_to=None):
        conds = []; params = []
        if filial_id is not None: conds.append("nwd.filial_id=%s"); params.append(filial_id)
        if vsp_id is not None: conds.append("nwd.vsp_id=%s"); params.append(vsp_id)
        if date_from is not None: conds.append("nwd.date>=%s"); params.append(date_from)
        if date_to is not None: conds.append("nwd.date<=%s"); params.append(date_to)
        where = " AND ".join(conds) if conds else "1=1"
        return self._to_df(f"""
            SELECT nwd.id, nwd.user_name, f.name filial, v.name vsp, nwd.date, nwd.reason, nwd.created_at
            FROM {self._table_name('vsp_non_working_days')} nwd
            JOIN {self._table_name('filials')} f ON nwd.filial_id=f.id
            JOIN {self._table_name('vsp')} v ON nwd.vsp_id=v.id
            WHERE {where} ORDER BY nwd.date DESC, nwd.created_at DESC
        """, tuple(params))


    def admin_delete_non_working_day(self,record_id):
        """Удаление нерабочего дня по id"""
        self._execute(f"DELETE FROM {self._table_name('vsp_non_working_days')} where id=%s",(record_id,)
        )


    def delete_non_working_days_by_ids(self, ids):
        """Удаляет записи о нерабочих днях по списку id. Возвращает количество удалённых."""
        if not ids:
            return 0
        ids = [int(i) for i in ids]
        self._execute(
            f"DELETE FROM {self._table_name('vsp_non_working_days')} WHERE id = ANY(%s)",
            (ids,)
        )
        return len(ids)


    # -------------------------------------------------------------------------
    # ЭКСПОРТ / ОТЧЁТЫ
    # -------------------------------------------------------------------------
    def get_export_data(self):
        return self._to_df(f"""
            SELECT s.id session_id, s.user_name ФИО, f.name Филиал, v.name ВСП,
                   s.operation_date Дата_проверки,
                   CASE s.status_bul WHEN TRUE THEN 'Завершена' ELSE 'Черновик' END Статус,
                   s.created_at "Дата и время начала", s.completed_at "Дата и время завершения",
                   COUNT(a.id) Выполнено_проверок,
                   (SELECT COUNT(*) FROM {self.schema}.checklist_templates) Всего_проверок
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id=f.id
            JOIN {self.schema}.vsp v ON s.vsp_id=v.id
            LEFT JOIN {self.schema}.checklist_answers a ON s.id=a.session_id AND a.is_completed=true
            GROUP BY s.id, f.name, v.name, s.user_name, s.operation_date, s.status_bul, s.created_at, s.completed_at
            ORDER BY s.created_at DESC
        """)

    def get_user_sessions(self, full_name, filial_id):
        return self._to_df(f"""
            SELECT s.id, s.operation_date "Дата проверки", f.name "Филиал", v.name "ВСП",
                   CASE s.status_bul WHEN TRUE THEN 'Завершена' ELSE 'Черновик' END "Статус",
                   s.created_at "Дата и время начала", s.completed_at "Дата и время завершения",
                   COUNT(a.id) "Выполнено проверок",
                   (SELECT COUNT(*) FROM {self.schema}.checklist_templates) "Всего проверок"
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id=f.id
            JOIN {self.schema}.vsp v ON s.vsp_id=v.id
            LEFT JOIN {self.schema}.checklist_answers a ON s.id=a.session_id AND a.is_completed=true
            WHERE s.user_name=%s AND s.filial_id=%s
            GROUP BY s.id, f.name, v.name, s.user_name, s.operation_date, s.status_bul, s.created_at, s.completed_at
            ORDER BY s.created_at DESC
        """, (full_name, filial_id))

    def get_admin_analytics(self, filial_id=None, vsp_id=None, date_from=None, date_to=None):
        conds = []; params = []
        if filial_id is not None: conds.append("s.filial_id=%s"); params.append(int(filial_id))
        if vsp_id is not None: conds.append("s.vsp_id=%s"); params.append(int(vsp_id))
        if date_from is not None: conds.append("s.operation_date>=%s"); params.append(date_from)
        if date_to is not None: conds.append("s.operation_date<=%s"); params.append(date_to)
        where = " AND ".join(conds) if conds else "1=1"
        sessions = self._to_df(f"""
            SELECT s.id session_id, s.user_name ФИО, f.name Филиал, v.name ВСП,
                   s.created_at Дата, s.status_bul Статус,
                   s.completed_at "Дата и время завершения"
            FROM {self.schema}.checklist_sessions s
            JOIN {self.schema}.filials f ON s.filial_id=f.id
            JOIN {self.schema}.vsp v ON s.vsp_id=v.id
            WHERE {where}
            ORDER BY s.created_at DESC, f.name, v.name
        """, tuple(params))
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
        return sessions.merge(pd.DataFrame(all_answers), on='session_id', how='left')

    # -------------------------------------------------------------------------
    # ВИЗУАЛИЗАЦИЯ
    # -------------------------------------------------------------------------
    def get_vsp_status_for_date(self, filial_id, target_date):
        vsp_list = self.get_vsp_by_filial(filial_id)
        if vsp_list.empty:
            return pd.DataFrame(columns=["ВСП", "Статус"])
        nw_ids = set(self._to_df(f"SELECT vsp_id FROM {self._table_name('vsp_non_working_days')} WHERE date=%s AND filial_id=%s", (target_date, filial_id))['vsp_id'])
        comp_ids = set(self._to_df(f"SELECT vsp_id FROM {self._table_name('checklist_sessions')} WHERE operation_date=%s AND filial_id=%s AND status_bul=TRUE", (target_date, filial_id))['vsp_id'])
        result = []
        for _, v in vsp_list.iterrows():
            vid, vname = v['id'], v['name']
            if vid in nw_ids: status = "Выходной"
            elif vid in comp_ids: status = "Заполнен"
            else: status = "Не заполнен"
            result.append({"ВСП": vname, "Статус": status})
        return pd.DataFrame(result)

    def get_filial_status_for_date(self, target_date):
        filials = self.get_filials()
        if filials.empty:
            return pd.DataFrame(columns=["Филиал","Статус","Всего ВСП","Активных ВСП","Заполнено ВСП"])
        result = []
        for _, f in filials.iterrows():
            fid, fname = int(f['id']), f['name']
            vsp_list = self.get_vsp_by_filial(fid)
            nw_ids = set(self._to_df(f"SELECT vsp_id FROM {self._table_name('vsp_non_working_days')} WHERE date=%s AND filial_id=%s", (target_date, fid))['vsp_id'])
            comp_ids = set(self._to_df(f"SELECT vsp_id FROM {self._table_name('checklist_sessions')} WHERE operation_date=%s AND filial_id=%s AND status_bul=TRUE", (target_date, fid))['vsp_id'])
            total_vsp = len(vsp_list)
            active_vsp = total_vsp - len([v for v in vsp_list['id'] if v in nw_ids])
            completed_vsp = len([v for v in vsp_list['id'] if v in comp_ids])
            if active_vsp == 0: status = "Все выходные"
            elif completed_vsp == active_vsp: status = "Заполнен"
            elif completed_vsp > 0: status = "Частично"
            else: status = "Не заполнен"
            result.append({"Филиал": fname, "Статус": status, "Всего ВСП": total_vsp, "Активных ВСП": active_vsp, "Заполнено ВСП": completed_vsp})
        return pd.DataFrame(result)



    def non_working_day_exists(self, vsp_id, date):
        """Проверяет, есть ли уже запись о нерабочем дне для данного ВСП на дату."""
        row = self._execute(
             f"SELECT 1 FROM {self._table_name('vsp_non_working_days')} WHERE vsp_id=%s AND date=%s",
             (vsp_id, date),
             fetch_one=True
        )
        return row is not None


# =============================================================================
# ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ
# =============================================================================
st.markdown("""
<style>
    div[data-testid="stCheckbox"] label span { transform: scale(1.5); margin-right: 12px; }
    div[data-testid="stCheckbox"] label { font-size: 16px; padding: 5px 0; }
</style>
""", unsafe_allow_html=True)

db = DatabaseManager()

# переменные состояния (все как раньше)
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "user_full_name" not in st.session_state: st.session_state.user_full_name = ""
if "auth_valid" not in st.session_state: st.session_state.auth_valid = False
if "manual_login_mode" not in st.session_state: st.session_state.manual_login_mode = False
if "last_filial_name" not in st.session_state: st.session_state.last_filial_name = None
if "last_vsp_name" not in st.session_state: st.session_state.last_vsp_name = None
if "last_filial_id" not in st.session_state: st.session_state.last_filial_id = None
if "last_vsp_id" not in st.session_state: st.session_state.last_vsp_id = None
if "admin_authenticated" not in st.session_state: st.session_state.admin_authenticated = False
if "step" not in st.session_state: st.session_state.step = 0
if "selected_filial_id" not in st.session_state: st.session_state.selected_filial_id = None
if "selected_vsp_id" not in st.session_state: st.session_state.selected_vsp_id = None
if "resume_session_id" not in st.session_state: st.session_state.resume_session_id = None
if "data_loaded" not in st.session_state: st.session_state.data_loaded = False
if "update_counter" not in st.session_state: st.session_state.update_counter = 0
if "user_filial_blocked" not in st.session_state:st.session_state.user_filial_blocked = False

def load_last_user_data():
    if (st.session_state.user_full_name and not st.session_state.data_loaded and st.session_state.auth_valid):
        last_data = db.get_last_user_session_data(st.session_state.user_full_name)
        if not last_data:
            last_data = db.get_last_user_any_session_data(st.session_state.user_full_name)
        if last_data:
            if not st.session_state.last_filial_name: st.session_state.last_filial_name = last_data['filial_name']
            st.session_state.last_vsp_name = last_data['vsp_name']
            st.session_state.last_vsp_id = last_data['vsp_id']
            if st.session_state.selected_vsp_id is None: st.session_state.selected_vsp_id = last_data['vsp_id']
            if st.session_state.selected_filial_id is None: st.session_state.selected_filial_id = last_data['filial_id']
            if st.session_state.last_filial_id is None: st.session_state.last_filial_id = last_data['filial_id']
            st.session_state.update_counter += 1
        st.session_state.data_loaded = True

load_last_user_data()

# =============================================================================
# БОКОВАЯ ПАНЕЛЬ (как в предыдущей версии, полностью)
# =============================================================================
with st.sidebar:
    if st.session_state.step != 1:
        st.header("👤 Информация")
        if st.session_state.auth_valid and st.session_state.user_full_name:
            st.markdown(f"**Пользователь:** {st.session_state.user_full_name}")
            st.caption(f"Логин: {st.session_state.user_name}")
            if st.button("🔄 Сменить пользователя", use_container_width=True):
                for key in ['user_name','user_full_name','auth_valid','last_filial_name','last_vsp_name','last_filial_id','last_vsp_id','selected_filial_id','selected_vsp_id','step','data_loaded','update_counter','current_session_id','temp_answers','resume_session_id']:
                    if key in st.session_state: del st.session_state[key]
                st.session_state["manual_login_mode"] = True
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
                        st.success("✅ Режим администратора активирован!"); time.sleep(0.5); st.rerun()
                    else:
                        st.error("❌ Неверный пароль!")
            else:
                st.success("✅ Режим администратора активен")
                if st.button("Выйти", use_container_width=True):
                    st.session_state.admin_authenticated = False; st.rerun()
        else:
            if st.session_state.admin_authenticated:
                st.session_state.admin_authenticated = False; st.rerun()

        if st.session_state.admin_authenticated:
            st.divider()
            st.subheader("⚙️ Управление чек-листом")
            tpl = db.get_checklist_template()
            total_items = len(tpl)

            if not tpl.empty:
                with st.expander("📋 Текущие проверки"):
                    for _, r in tpl.iterrows():
                        st.markdown(f"**{r['item_order']}.** {r['description']}")

            with st.expander("➕ Добавить проверку"):
                new_desc = st.text_area("Наименование", height=68)
                new_info = st.text_area("Описание", height=68)
                new_filter = st.text_area("🔍 Фильтр (стандартный)")
                new_events = st.text_area("📌 Фильтр2 (стандартные)", height=68)
                new_alt_filter = st.text_area("🔍 Альт. фильтр")
                new_alt_info = st.text_area("📝 Альт. описание", height=68)
                new_alt_events = st.text_area("📌 Альт. Фильтр2", height=68)

                pos_options = list(range(1, total_items + 2))
                pos_labels = [f"Перед пунктом {p} (сдвинуть)" if p <= total_items else "В конец списка" for p in pos_options]
                sel_label = st.selectbox("Вставить на позицию", pos_labels, index=pos_labels.index("В конец списка"))
                insert_position = None if sel_label == "В конец списка" else int(sel_label.split()[2])

                if st.button("➕ Добавить", use_container_width=True, type="primary"):
                    if new_desc:
                        db.add_template_item(new_desc, new_info, new_filter, new_events,
                                             new_alt_filter, new_alt_info, new_alt_events, position=insert_position)
                        st.success("✅ Добавлено!"); st.rerun()

            with st.expander("✏️ Редактировать/Удалить/Переместить"):
                if not tpl.empty:
                    sel_id = st.selectbox("Выберите проверку", tpl['id'].tolist(),
                                          format_func=lambda x: f"ID {x} - {tpl[tpl['id']==x]['description'].iloc[0][:50]}")
                    row = tpl[tpl['id'] == sel_id].iloc[0]
                    current_order = row['item_order']
                    st.caption(f"Текущий порядковый номер: {current_order}")

                    e_desc = st.text_area("Наименование", value=row['description'])
                    e_info = st.text_area("Описание", value=row['additional_info'] or "")
                    e_filter = st.text_area("Фильтр (стандартный)", value=row['filter_value'] or "")
                    e_events = st.text_area("Фильтр2 (стандартные)", value=row['events_value'] or "")
                    e_alt_filter = st.text_area("Альт. фильтр", value=row['alt_filter_value'] or "")
                    e_alt_info = st.text_area("Альт. описание", value=row['alt_additional_info'] or "")
                    e_alt_events = st.text_area("Альт. фильтр2", value=row['alt_events_value'] or "")

                    c1, c2, c3, c4 = st.columns(4)
                    if c1.button("💾 Обновить", use_container_width=True):
                        db.update_template_item(sel_id, e_desc, e_info, e_filter, e_events,
                                                e_alt_filter, e_alt_info, e_alt_events)
                        st.success("Обновлено!"); st.rerun()
                    if c2.button("🗑️ Удалить", use_container_width=True):
                        db.delete_template_item(sel_id)
                        st.success("Удалено! Нумерация обновлена."); st.rerun()

                    max_order = tpl['item_order'].max()
                    if c3.button("⬆️ Вверх", use_container_width=True, disabled=(current_order == 1)):
                        db.move_template_item(sel_id, 'up'); st.rerun()
                    if c4.button("⬇️ Вниз", use_container_width=True, disabled=(current_order == max_order)):
                        db.move_template_item(sel_id, 'down'); st.rerun()

                    st.caption("Или переместить на конкретную позицию:")
                    all_positions = list(range(1, max_order + 1))
                    allowed_positions = [p for p in all_positions if p != current_order]
                    if allowed_positions:
                        target_pos = st.selectbox("Выберите новую позицию", allowed_positions,
                                                  format_func=lambda x: f"Позиция {x}", key=f"move_pos_{sel_id}")
                        if st.button("📌 Переместить", key=f"move_btn_{sel_id}"):
                            db.move_to_position(sel_id, target_pos); st.rerun()
                    else:
                        st.info("Это единственный пункт, перемещение невозможно.")

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
                            st.download_button("💾 Скачать", f.read(), f"checklist_{datetime.date.today()}.xlsx", use_container_width=True)
                    else:
                        st.error("Установите openpyxl")
            else:
                st.warning("Нет данных для экспорта")
                
#===========================ДОБАВЛЕНА ВОЗМОЖНОСТЬ РЕДАКТИРОВАНИЯ ПОЛЬЗОВАТЕЛЯ (СТАРОЕ ИМЯ НА НОВОЕ)=================================================
            st.divider()
            with st.expander("...", expanded=False):
                user_login = st.text_input("Логин сотрудника", placeholder="rf_ivanov_av", key="edit_user_login")
                # Загружаем текущее ФИО, если логин введён
                current_full_name = ""
                if user_login:
                    exists, full, _ = db.check_user_by_name(user_login.strip())
                    if exists:
                        current_full_name = full
                        st.info(f"Текущее ФИО: **{current_full_name}**")
                    else:
                        st.error("Пользователь не найден")
    
                new_full_name = st.text_input("Новое ФИО", value=current_full_name if current_full_name else "", key="new_full_name")
    
                if st.button("💾 Обновить ФИО", use_container_width=True):
                    if not user_login.strip():
                        st.error("Введите логин")
                    elif not new_full_name.strip():
                        st.error("Введите новое ФИО")
                    else:
                        exists, _, _ = db.check_user_by_name(user_login.strip())
                        if not exists:
                            st.error("Пользователь не существует")
                        else:
                            try:
                                db.update_user_full_name(user_login.strip(), new_full_name.strip())
                                st.success(f"ФИО для {user_login} обновлено на «{new_full_name}»!")
                                # Очистим поле логина, чтобы избежать повторного обновления
                                st.session_state["edit_user_login"] = ""
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Успешно обновлено!!")

#========================================================================================================================================================
    else:
        st.info("Идет заполнение чек-листа...")

# =============================================================================
# ОСНОВНОЙ ИНТЕРФЕЙС – ВКЛАДКИ
# =============================================================================
st.title("📋 Завершение операций по ВСП/РФ")
#ВСТАВЛЯЕМ ЗАГЛУШКУ (ПИЛОТ/НЕ ПИЛОТ)
if st.session_state.auth_valid and st.session_state.user_filial_blocked:
    st.error("⛔ Доступ временно ограничен")
    st.warning(
        "На данный филиал пилотный проект не распространяется.\n\n"
        "Пожалуйста, ожидайте дополнительной информации от руководителя."
    )
    st.stop()
tab_titles = ["📝 Новая проверка","📜 История проверок"]
if st.session_state.admin_authenticated:
    tab_titles.append("📊 Аналитика")
    tab_titles.append("🏢 Филиалы (чекбоксы)")
    tab_titles.append("📅 Нерабочие дни (отчет)")
    tab_titles.append("📊 Визуализация (админ)")
    tab_titles.append("📈 Витрины (админ)")
elif st.session_state.auth_valid:
    tab_titles.append("📅 Нерабочие дни ВСП")
    tab_titles.append("📊 Аналитика по филиалу")
    tab_titles.append("📊 Визуализация")

tabs = st.tabs(tab_titles)

idx = 0
tab_main = tabs[idx]; idx += 1
tab_history = tabs[idx]; idx += 1

tab_non_working = None
tab_user_analytics = None
tab_visualization_user = None

tab_analytics = None
tab_filial_check = None
tab_admin_non_working = None
tab_visualization_admin = None
tab_views_admin = None

if st.session_state.admin_authenticated:
    tab_analytics = tabs[idx]; idx += 1
    tab_filial_check = tabs[idx]; idx += 1
    tab_admin_non_working = tabs[idx]; idx += 1
    tab_visualization_admin = tabs[idx]; idx += 1
    tab_views_admin = tabs[idx]; idx += 1

elif st.session_state.auth_valid:
    tab_non_working = tabs[idx]; idx += 1
    tab_user_analytics = tabs[idx]; idx += 1
    tab_visualization_user = tabs[idx]; idx += 1

# --- НОВАЯ ПРОВЕРКА ---
with tab_main:
    if st.session_state.step == 0:
        if st.session_state.auth_valid and st.session_state.user_full_name:
            drafts = db.get_user_draft_sessions(st.session_state.user_full_name)
            today_drafts = drafts[drafts['operation_date'] == datetime.date.today()] if not drafts.empty else pd.DataFrame()
        else:
            today_drafts = pd.DataFrame()

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if not today_drafts.empty:
                st.info(f"📌 У вас есть незавершённый черновик за сегодня.")
                for _, d in today_drafts.iterrows():
                    a, b, c1, c2 = st.columns([2.5, 1.5, 1, 1])
                    a.markdown(f"**{d['filial_name']} / {d['vsp_name']}**")
                    b.caption(f"✅ {d['completed_count']}/{d['total_count']}")
                    if c1.button("📂 Продолжить", key=f"resume_{d['id']}", use_container_width=True):
                        # Получаем filial_id из черновика (он есть в данных d)
                        # У вас в d уже есть колонка filial_name, но нет filial_id.
                        # Проще сделать дополнительный запрос к БД, либо добавить filial_id в df get_user_draft_sessions.
                        # Для простоты – сделаем запрос:
                        sess_data = db.get_session_data(d['id'])
                        if sess_data and sess_data['info'].get('filial_id'):
                            if db.get_filial_blocked_status(sess_data['info']['filial_id']):
                                st.error("Ваш филиал заблокирован. Продолжение невозможно.")
                            else:
                                st.session_state.current_session_id = d['id']; st.session_state.step = 1;
                                st.rerun()
                        else:
                            st.session_state.current_session_id = d['id']; st.session_state.step = 1; st.rerun()
                    if c2.button("🗑️ Удалить", key=f"delete_{d['id']}", use_container_width=True):
                        db.delete_session(int(d['id']))
                        st.success("Черновик удалён"); time.sleep(0.5); st.rerun()
                st.divider()

            filials_df = db.get_filials()
            if not filials_df.empty:
                filial_names = filials_df['name'].tolist()
                filial_map = dict(zip(filials_df['name'], filials_df['id']))

                #----------------------------- ЭТОТ БЛОК ОТВЕЧАЕТ ЗА АВТОМАТИЧЕСКОЕ ЛОГИРОВАНИЕ !!!-------------------------------
                login = ""

                # Если пользователь еще не авторизован
                if not st.session_state.get("auth_valid", False):

                    if st.session_state.get("manual_login_mode", False):
                        user_logins = []
                    else:
                        user_logins = db.get_user_logins_by_email(st.session_state["email"])

                    # Вариант 1: найден ровно один логин
                    if len(user_logins) == 1:
                        login = user_logins[0]["name"]

                    # Вариант 2: найдено несколько тёзок — показываем список
                    elif len(user_logins) > 1:
                        st.warning("👤 Найдено несколько учетных записей.")

                        selected_user = st.selectbox(
                            "Пожалуйста, выберите свою учетную запись из списка:",
                            options=user_logins,
                            format_func=lambda x: f'{x["name"]} — {x["full_name"]}',
                            key=f'login_select_{st.session_state.get("update_counter", 0)}'
                        )

                        if st.button(
                                "➡️ Войти",
                                key=f"confirm_selected_login_{st.session_state.get('update_counter', 0)}",
                                use_container_width=True
                        ):
                            login = selected_user["name"]

                    # Вариант 3: Ручной ввод
                    else:
                        with st.form(key=f"manual_login_form_{st.session_state.get('update_counter', 0)}"):   #СДВИНУТЬ НА 8
                            entered_login = st.text_input(
                                "👤 Учетная запись сотрудника",
                                value="",
                                placeholder="rf_ivanov_av",
                                key=f"login_{st.session_state.get('update_counter', 0)}"
                            )

                            submitted = st.form_submit_button(
                                "➡️ Войти",
                                use_container_width=True
                            )

                        if submitted:                                                                          #СДВИНУТЬ НА 8    
                            login = entered_login                                                              #СДВИНУТЬ НА 8 

                    login_norm = login.lower().strip() if login else ""

                    if login_norm:
                        exists, full, fil, filial_id, default_vsp_name, default_vsp_id = db.check_user_by_name(
                            login_norm)

                        if exists:
                            st.session_state.user_name = login_norm
                            st.session_state.user_full_name = full
                            st.session_state.auth_valid = True
                            st.session_state["manual_login_mode"] = False

                            st.session_state.default_vsp_name = default_vsp_name
                            st.session_state.default_vsp_id = default_vsp_id

                            if filial_id is not None:
                                st.session_state.user_filial_blocked = db.get_filial_blocked_status(filial_id)
                                st.session_state.last_filial_id = filial_id
                            else:
                                st.session_state.user_filial_blocked = False

                            if fil:
                                st.session_state.last_filial_name = fil
                                st.session_state.selected_filial_id = filial_id

                            st.success(f"✅ Добро пожаловать, {full}!")
                            st.rerun()

                        else:
                            st.error(f"❌ Пользователь '{login_norm}' не найден!")

                if st.session_state.auth_valid:
                    st.info(f"👤 **Авторизован:** {st.session_state.user_full_name}")
                    st.caption(f"Логин: {st.session_state.user_name}")
                    if st.button("🔄 Сменить пользователя", key="change_btn", use_container_width=True):
                        for k in ['user_name', 'user_full_name', 'auth_valid', 'last_filial_name', 'last_vsp_name',
                                  'last_filial_id', 'last_vsp_id', 'selected_filial_id', 'selected_vsp_id', 'step',
                                  'data_loaded', 'update_counter', 'current_session_id', 'temp_answers',
                                  'resume_session_id']:
                            if k in st.session_state: del st.session_state[k]
                        st.session_state["manual_login_mode"] = True
                        st.rerun()
                    st.divider()

                    sel_filial_id = st.session_state.last_filial_id
                    if sel_filial_id is None:
                        st.error("Филиал не определен.")
                        st.stop()

                    st.markdown(f"**Филиал:** {st.session_state.last_filial_name}")

                    vsp_df = db.get_vsp_by_filial(sel_filial_id)

                    if not vsp_df.empty:
                        vsp_names = vsp_df['name'].tolist()
                        vsp_map = dict(zip(vsp_df['name'], vsp_df['id']))

                        vsp_display_map = {
                            row["name"]: f'{row["name"]} ({row["name_vsp"]})'
                            for _, row in vsp_df.iterrows()
                        }

                        default_vsp_name = st.session_state.get('default_vsp_name')
                        default_vsp_id = st.session_state.get('default_vsp_id')

                        use_default = st.checkbox(
                            "🔒 Использовать моё ВСП",
                            value=(default_vsp_name is not None and default_vsp_name in vsp_names),
                            key="use_my_vsp"
                        )

                        if use_default and default_vsp_name and default_vsp_name in vsp_names:
                            selected_vsp_name = default_vsp_name
                            selected_vsp_id = default_vsp_id

                            st.info(
                                f"🏪 Ваше ВСП: **{default_vsp_name}**"
                            )

                        else:
                            default_idx = 0

                            if (
                                    'last_vsp_name' in st.session_state
                                    and st.session_state.last_vsp_name in vsp_names
                            ):
                                default_idx = vsp_names.index(st.session_state.last_vsp_name)

                            elif default_vsp_name and default_vsp_name in vsp_names:
                                default_idx = vsp_names.index(default_vsp_name)

                            selected_vsp_name = st.selectbox(
                                "🏪 ВСП",
                                vsp_names,
                                index=default_idx,
                                key="vsp_select",
                                format_func=lambda x: vsp_display_map.get(x, x)
                            )

                            selected_vsp_id = vsp_map[selected_vsp_name]

                        # Обратная совместимость
                        sel_vsp = selected_vsp_name
                        sel_vsp_id = selected_vsp_id

                        st.session_state.last_vsp_name = selected_vsp_name
                        st.session_state.last_vsp_id = selected_vsp_id
                        st.session_state.selected_vsp_id = selected_vsp_id

                    else:
                        sel_vsp_id = None
                        sel_vsp = None
                        st.warning("Нет ВСП в выбранном филиале")

                    existing_draft_id = db.get_today_draft_session_id(st.session_state.user_full_name)
                    new_session_allowed = existing_draft_id is None
                    if not new_session_allowed:
                        st.warning("⚠️ У вас уже есть незавершённый черновик за сегодня. Завершите или удалите его.")

                    with st.form("new_session_form"):
                        op_date = st.date_input("📅 Дата", value=datetime.date.today(), format="DD.MM.YYYY",
                                                disabled=True)
                        submitted = st.form_submit_button(
                            "▶️ НАЧАТЬ ЗАПОЛНЕНИЕ",
                            type="primary",
                            use_container_width=True,
                            disabled=(not new_session_allowed)
                            # отключаем кнопку, если у пользователя уже есть черновик за сегодня
                        )
                        if submitted and sel_vsp_id is not None:
                            # 1. Проверка блокировки филиала
                            if st.session_state.user_filial_blocked:
                                st.error("Ваш филиал временно заблокирован...")
                            # 2. Проверка, нет ли уже сессии для этого ВСП на сегодня
                            elif db.session_exists_for_vsp_date(sel_vsp_id, op_date):
                                st.error(f"❌ Для ВСП «{sel_vsp}» на {op_date} уже существует проверка...")
                            # 3. Проверка, нет ли у пользователя черновика за сегодня
                            elif db.get_today_draft_session_id(st.session_state.user_full_name) is not None:
                                st.error("У вас уже есть незавершённый черновик за сегодня...")
                            else:
                                # ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ – можно удалять выходной и создавать сессию
                                if op_date.weekday() == 5:  # 5 = суббота
                                    db.delete_non_working_day_by_vsp_date(sel_vsp_id, op_date)
                                    # опционально: st.toast("Выходной снят, можете заполнять", icon="✅")
                                sid = db.create_session(
                                    st.session_state.user_full_name,
                                    sel_filial_id,
                                    sel_vsp_id,
                                    op_date,
                                    False
                                )
                                st.session_state.current_session_id = sid
                                st.session_state.step = 1
                                st.rerun()

# --- ИСТОРИЯ ПРОВЕРОК ---
with tab_history:
    st.markdown("### 📜 История ваших проверок")
    if st.session_state.auth_valid and st.session_state.user_full_name:
        if st.session_state.get('last_filial_id') is not None:
            hist = db.get_user_sessions(st.session_state.user_full_name, st.session_state.last_filial_id)
        else:
            st.warning("Филиал не определён. История недоступна.")
            hist = pd.DataFrame()  # пустой DataFrame
        if not hist.empty:
            st.dataframe(hist, use_container_width=True, height=400)
            sel_sess = st.selectbox("Выберите сессию", hist['id'].tolist(),
                                    format_func=lambda x: f"Сессия #{x} - {hist[hist['id']==x]['Дата проверки'].iloc[0]}")
            if st.button("📋 Показать результаты"):
                data = db.get_session_data(sel_sess)
                if data:
                    info = data['info']
                    with st.expander(f"Результаты проверки #{sel_sess}", expanded=True):
                        st.markdown(f"**Дата:** {info['operation_date']}")
                        st.markdown(f"**Статус:** {'✔️ Завершена' if info['status_bul'] else '📄 Черновик'}")
                        if info['status_bul'] and info.get('completed_at'):
                            st.markdown(f"**Время завершения:** {info['completed_at']}")
                        tpl = db.get_checklist_template()
                        ans = data['answers']
                        for _, r in tpl.iterrows():
                            st.markdown(f"{'✔️' if ans.get(r['id'], False) else '❌'} {r['description']}")
                else:
                    st.error("Не удалось загрузить данные")

            st.divider()
            st.caption("Удалить черновик по ID")
            col_d1, col_d2 = st.columns([2, 1])
            with col_d1:
                del_hist_id = st.number_input("ID сессии", min_value=1, step=1, key="hist_del")
            with col_d2:
                if st.button("🗑️ Удалить", key="hist_del_btn"):
                    sess_data = db.get_session_data(del_hist_id)
                    if sess_data and not sess_data['info']['status_bul']:
                        if sess_data['info']['user_name'] == st.session_state.user_full_name:
                            db.delete_session(del_hist_id); st.success("Черновик удалён"); st.rerun()
                        else:
                            st.error("Вы можете удалять только свои черновики")
                    else:
                        st.error("Это не черновик или сессия не найдена")
        else:
            st.info("У вас пока нет завершённых проверок.")
    else:
        st.warning("Введите учётную запись, чтобы увидеть историю.")

# --- НЕРАБОЧИЕ ДНИ ВСП ---
if tab_non_working is not None:
    with tab_non_working:
        st.markdown("## 📅 Внесение нерабочих дней ВСП")
        st.caption("Укажите дату и причину. Удалить можно только запись для выбранного ВСП.")
        if st.session_state.get("last_filial_id") is None:
            exists, full, fil = db.check_user_by_name(st.session_state.user_name)
            if exists and fil:
                filials_df = db.get_filials()
                if not filials_df.empty:
                    fid_row = filials_df[filials_df['name'] == fil]
                    if not fid_row.empty:
                        st.session_state.last_filial_id = int(fid_row['id'].iloc[0])
                        st.session_state.last_filial_name = fil
            if st.session_state.get("last_filial_id") is None:
                st.error("Не удалось определить ваш филиал."); st.stop()

        current_filial_id = st.session_state.last_filial_id
        current_filial_name = st.session_state.last_filial_name
        st.markdown(f"**Филиал:** {current_filial_name}")

        vsp_df = db.get_vsp_by_filial(current_filial_id)
        if vsp_df.empty:
            st.warning("В этом филиале нет ВСП.")
        else:
            vsp_names = vsp_df['name'].tolist()
            vsp_map = dict(zip(vsp_df['name'], vsp_df['id']))
            default_vsp = st.session_state.last_vsp_name if st.session_state.last_vsp_name in vsp_names else vsp_names[0]
            default_vsp_idx = vsp_names.index(default_vsp)

            sel_vsp_nw = st.selectbox("🏪 ВСП", vsp_names, index=default_vsp_idx, key="nw_vsp")
            sel_vsp_id_nw = vsp_map[sel_vsp_nw]

            nw_date = st.date_input("📅 Дата нерабочего дня", value=datetime.date.today(), key="nw_date")
            nw_reason = st.selectbox("📌 Причина", NON_WORKING_REASONS, key="nw_reason")

            if st.button("💾 Добавить нерабочий день", type="primary", use_container_width=True):
                db.add_non_working_day(st.session_state.user_full_name, current_filial_id, sel_vsp_id_nw, nw_date, nw_reason)
                st.success(f"✅ Нерабочий день {nw_date} для ВСП «{sel_vsp_nw}» сохранён!"); time.sleep(1); st.rerun()

            # st.divider()
            # st.markdown("### 📋 Ранее добавленные нерабочие дни")
            # show_all = st.checkbox("Показать все ВСП филиала", value=False, key="nw_show_all")
            # filter_vsp = None if show_all else sel_vsp_id_nw
            # nw_df = db.get_non_working_days(filial_id=current_filial_id, vsp_id=filter_vsp)
            # if nw_df.empty:
            #     st.info("Нет записей о нерабочих днях.")
            # else:
            #     st.markdown("---")
            #     for _, row in nw_df.iterrows():
            #         col1, col2, col3, col4 = st.columns([3, 2, 3, 1])
            #         col1.write(f"🏪 {row['vsp']}")
            #         col2.write(f"📅 {row['date']}")
            #         col3.write(f"📌 {row['reason']}")
            #         if not show_all:
            #             if col4.button("🗑️", key=f"del_nw_{row['id']}", help="Удалить"):
            #                 db.delete_non_working_day(int(row['id']), sel_vsp_id_nw, current_filial_id)
            #                 st.success("Запись удалена"); time.sleep(0.5); st.rerun()
            #     st.markdown("---")


# --- АНАЛИТИКА ПО ФИЛИАЛУ (пользователь) ---
if tab_user_analytics is not None:
    with tab_user_analytics:
        st.markdown("## 📊 Аналитика проверок вашего филиала")
        if st.session_state.get("last_filial_id") is None:
            exists, full, fil = db.check_user_by_name(st.session_state.user_name)
            if exists and fil:
                filials_df = db.get_filials()
                if not filials_df.empty:
                    fid_row = filials_df[filials_df['name'] == fil]
                    if not fid_row.empty:
                        st.session_state.last_filial_id = int(fid_row['id'].iloc[0])
                        st.session_state.last_filial_name = fil
            if st.session_state.get("last_filial_id") is None:
                st.error("Не удалось определить ваш филиал."); st.stop()

        current_filial_id = st.session_state.last_filial_id
        current_filial_name = st.session_state.last_filial_name
        st.info(f"🏢 Филиал: **{current_filial_name}**")

        sessions = db.get_filial_sessions(current_filial_id)
        if sessions.empty:
            st.info("В вашем филиале пока нет проверок.")
        else:
            # Фильтр по дате (без кнопки сброса)
            st.markdown("### 📅 Фильтр по дате проверки")
            col1, col2 = st.columns(2)
            with col1:
                date_from = st.date_input("Дата от", value=None, key="user_analytics_date_from")
            with col2:
                date_to = st.date_input("Дата до", value=None, key="user_analytics_date_to")

            # Применяем фильтр
            sessions_filtered = sessions.copy()
            if date_from is not None:
                sessions_filtered = sessions_filtered[sessions_filtered["Дата проверки"] >= date_from]
            if date_to is not None:
                sessions_filtered = sessions_filtered[sessions_filtered["Дата проверки"] <= date_to]

            if sessions_filtered.empty:
                st.warning("Нет данных за выбранный период.")
            else:
                # Принудительно преобразуем id в int
                sessions_filtered['id'] = sessions_filtered['id'].astype(int)
                total_checks = int(sessions_filtered["Всего проверок"].iloc[0])

                st.dataframe(
                    sessions_filtered,
                    use_container_width=True,
                    height=500,
                    column_config={
                        "id": "ID сессии",
                        "Сотрудник": "Сотрудник",
                        "Дата проверки": st.column_config.DateColumn("Дата"),
                        "ВСП": "ВСП",
                        "Статус": "Статус",
                        "Выполнено проверок": st.column_config.ProgressColumn(
                            "Выполнено",
                            min_value=0,
                            max_value=total_checks,
                            #format="%d/%d"
                          
                        ),
                        "Дата и время начала": st.column_config.DatetimeColumn("Начало"),
                        "Дата и время завершения": st.column_config.DatetimeColumn("Завершение"),
                        "Всего проверок": None
                    },
                    hide_index=True
                )



# --- ВИЗУАЛИЗАЦИЯ (ПОЛЬЗОВАТЕЛЬ) ---
if tab_visualization_user is not None:
    with tab_visualization_user:
        st.markdown("## 📊 Статус заполнения чек-листов по вашему филиалу")
        st.caption("🟢 Зелёный — заполнен, 🔴 Красный — не заполнен (ВСП с выходным не участвуют).")
        if st.session_state.get("last_filial_id") is None:
            exists, full, fil = db.check_user_by_name(st.session_state.user_name)
            if exists and fil:
                filials_df = db.get_filials()
                if not filials_df.empty:
                    fid_row = filials_df[filials_df['name'] == fil]
                    if not fid_row.empty:
                        st.session_state.last_filial_id = int(fid_row['id'].iloc[0])
                        st.session_state.last_filial_name = fil
            if st.session_state.get("last_filial_id") is None:
                st.error("Не удалось определить ваш филиал."); st.stop()
        current_filial_id = st.session_state.last_filial_id
        current_filial_name = st.session_state.last_filial_name
        st.info(f"🏢 Ваш филиал: **{current_filial_name}**")

        vis_date_user = st.date_input("📅 Дата", value=datetime.date.today(), key="vis_date_user")
        if st.button("🔍 Показать статус", key="vis_btn_user", use_container_width=True):
            with st.spinner("Собираем данные..."):
                status_df = db.get_vsp_status_for_date(current_filial_id, vis_date_user)
            if status_df.empty:
                st.info("Нет ВСП в вашем филиале.")
            else:
                filtered_df = status_df[status_df['Статус'] != 'Выходной']
                total_active = len(filtered_df)
                if total_active == 0:
                    st.info("На выбранную дату все ВСП филиала — нерабочие.")
                else:
                    filled = int((filtered_df['Статус'] == 'Заполнен').sum())
                    not_filled = total_active - filled
                    st.subheader("🍩 Соотношение заполненных и незаполненных ВСП")
                    import plotly.graph_objects as go
                    fig = go.Figure(data=[go.Pie(labels=["Заполнено","Не заполнено"], values=[filled, not_filled],
                                                 marker=dict(colors=["#28a745","#dc3545"]),
                                                 textinfo='label+percent', textfont=dict(size=16), hole=0.4)])
                    fig.update_layout(showlegend=True, legend=dict(font=dict(size=16)), margin=dict(t=20,b=20,l=20,r=20), height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    col_a, col_b = st.columns(2)
                    col_a.metric("✅ Заполнено", f"{filled} из {total_active}", delta=f"{filled / total_active * 100:.0f} %")
                    col_b.metric("❌ Не заполнено", f"{not_filled} из {total_active}", delta=f"{not_filled / total_active * 100:.0f} %", delta_color="inverse")
                st.subheader("📋 Детализация по ВСП вашего филиала")
                def highlight_status(row):
                    if row['Статус'] == 'Заполнен': return ['background-color:#d4edda;color:#155724']*len(row)
                    elif row['Статус'] == 'Выходной': return ['background-color:#fff3cd;color:#856404']*len(row)
                    else: return ['background-color:#f8d7da;color:#721c24']*len(row)
                status_order = {"Не заполнен":0, "Заполнен":1, "Выходной":2}
                status_df['_sort'] = status_df['Статус'].map(status_order)
                status_df = status_df.sort_values('_sort').drop(columns=['_sort'])
                st.dataframe(status_df.style.apply(highlight_status, axis=1), use_container_width=True, height=400)


# --- АНАЛИТИКА (админ, с кнопкой «Удалить все черновики») ---
if tab_analytics is not None:
    with tab_analytics:
        st.markdown("## 📊 Детальная аналитика по проверкам")
        filials_df = db.get_filials()
        if not filials_df.empty:
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                filial_opts = ["Все"] + sorted((filials_df['id'].astype(str).str.zfill(3)+' - '+filials_df['name']).tolist())
                sel_filial_name = st.selectbox("Филиал", filial_opts, key="adm_filial")
                filial_id = None if sel_filial_name == "Все" else int(sel_filial_name.split()[0])
            with col_f2:
                vsp_df = db.get_vsp_by_filial(filial_id) if filial_id is not None else db.get_all_vsp()
                vsp_opts = (["Все"] + (vsp_df["name"] + " - " + vsp_df["name_vsp"]).tolist()) if not vsp_df.empty else ["Все"]
                sel_vsp_name = st.selectbox("ВСП", vsp_opts, key="adm_vsp")
                vsp_id = None if sel_vsp_name == "Все" else int(vsp_df[vsp_df['name'] == sel_vsp_name]['id'].iloc[0])
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
                    for _, tpl in template.iterrows():
                        col_name = f"check_{tpl['id']}"
                        if col_name in analytics.columns:
                            analytics[col_name] = analytics[col_name].apply(lambda x: "✔️" if x else "❌")
                    rename = {f"check_{tpl['id']}": f"{tpl['item_order']}. {tpl['description'][:50]}" for _, tpl in template.iterrows()}
                    analytics.rename(columns=rename, inplace=True)
                    analytics['Статус'] = analytics['Статус'].apply(lambda x: 'Завершена' if x else 'Черновик')
                    base_cols = ['ФИО','Филиал','ВСП','Дата','Статус','Дата и время завершения']
                    display_cols = base_cols + [v for v in rename.values() if v in analytics.columns]
                    st.dataframe(analytics[display_cols], use_container_width=True, height=500)

            # --- Блок удаления черновиков (с выбором через multiselect) ---
            st.divider()
            st.subheader("🗑️ Удаление черновиков")

            # Получаем список всех черновиков с основной информацией
            drafts_df = db._to_df(f"""
                SELECT s.id, s.user_name, f.name filial_name, v.name vsp_name,
                       s.operation_date, s.created_at
                FROM {db.schema}.checklist_sessions s
                JOIN {db.schema}.filials f ON s.filial_id = f.id
                JOIN {db.schema}.vsp v ON s.vsp_id = v.id
                WHERE s.status_bul = FALSE
                ORDER BY s.created_at DESC
            """)

            if drafts_df.empty:
                st.info("Нет черновиков для удаления.")
            else:
                st.info(f"Всего черновиков в базе: **{len(drafts_df)}**")

                # Формируем список опций для multiselect: (id, читаемая строка)
                options = []
                for _, row in drafts_df.iterrows():
                    label = (
                        f"ID {row['id']} | {row['user_name']} | "
                        f"{row['filial_name']} / {row['vsp_name']} | {row['operation_date']}"
                    )
                    options.append((row['id'], label))

                # Выбор черновиков через выпадающий список с множественным выбором
                selected_ids = st.multiselect(
                    "Выберите черновики для удаления:",
                    options=[opt[0] for opt in options],
                    format_func=lambda x: next(
                        (opt[1] for opt in options if opt[0] == x), str(x)
                    ),
                    key="draft_multiselect"
                )

            if selected_ids:
                st.write(f"Выбрано черновиков: **{len(selected_ids)}**")

                # Подтверждение удаления (защита от случайного нажатия)
                confirm_selected = st.checkbox(
                    "Я подтверждаю удаление выбранных черновиков (нельзя отменить)",
                    key="confirm_selected_delete"
                )

                if st.button(
                    "🗑️ Удалить выбранные черновики",
                    type="primary",
                    disabled=(not confirm_selected),
                    key="delete_selected_drafts"
                ):
                    for sid in selected_ids:
                        db.delete_session(int(sid))
                    st.success(f"Успешно удалено черновиков: {len(selected_ids)}")
                    time.sleep(1)
                    st.rerun()
            else:
                    st.caption("👆 Выберите хотя бы один черновик из списка выше.")

#Делаем возможность вернуть из ЗАВЕРЕШЕННОГО состояния в ЧЕРНОВИК==========================================================


    # --- Блок возврата завершённой сессии в черновик ---
            st.divider()
            st.subheader("🔄 Вернуть завершённую сессию в черновик")

            # Получаем все завершённые сессии
            completed_df = db._to_df(f"""
                SELECT s.id, s.user_name, f.name filial_name, v.name vsp_name,
                       s.operation_date, s.completed_at
                FROM {db.schema}.checklist_sessions s
                JOIN {db.schema}.filials f ON s.filial_id = f.id
                JOIN {db.schema}.vsp v ON s.vsp_id = v.id
                WHERE s.status_bul = TRUE
                ORDER BY s.completed_at DESC
            """)

            if completed_df.empty:
                st.info("Нет завершённых сессий.")
            else:
                st.info(f"Всего завершённых сессий: **{len(completed_df)}**")

                # Формируем список для выбора
                options = [("","-Выберите сессию (достаточно указать ФИО)-")]
                for _, row in completed_df.iterrows():
                    label = (
                        f"ID {row['id']} | {row['user_name']} | "
                        f"{row['filial_name']} / {row['vsp_name']} | {row['operation_date']} | "
                        f"Завершена {row['completed_at']}"
                    )
                    options.append((row['id'], label))

                selected_id = st.selectbox(
                    "Выберите сессию для возврата в черновик:",
                    options=[opt[0] for opt in options],
                    format_func=lambda x: next(
                        (opt[1] for opt in options if opt[0] == x), str(x)
                    ),
                    index=0,
                    key="completed_select"
                )

                if selected_id != "" and st.button("🔄 Вернуть в черновик", key="revert_to_draft"):
                    db.update_session_status(selected_id, False)
                    st.success(f"✅ Сессия #{selected_id} теперь черновик.")
                    time.sleep(1)
                    st.rerun()


            



# --- ФИЛИАЛЫ (ЧЕКБОКСЫ) ---
if tab_filial_check is not None:
    with tab_filial_check:
        st.markdown("## 🏢 Настройка филиалов")
        st.caption("**Первый чекбокс** – для альтернативных фильтров (миграция).\n"
                   "**Второй (🔒)** – временная блокировка доступа для филиала.")
        filials_df = db.get_filials()
        if filials_df.empty:
            st.warning("Нет филиалов")
        else:
            with st.form("filial_settings_form"):
                # Заголовки таблицы
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.markdown("**Филиал**")
                col2.markdown("**Альт. фильтр**")
                col3.markdown("**🔒 Блокировка**")
                st.divider()

                new_checks = {}
                new_blocked = {}
                for _, frow in filials_df.iterrows():
                    fid = int(frow['id'])
                    fname = frow['name']
                    current_check = bool(frow['check_name'])
                    current_blocked = db.get_filial_blocked_status(fid)

                    cols = st.columns([3, 1, 1])
                    with cols[0]:
                        st.write(fname)
                    with cols[1]:
                        new_checks[fid] = st.checkbox(" ", value=current_check, key=f"fchk_{fid}", label_visibility="collapsed")
                    with cols[2]:
                        new_blocked[fid] = st.checkbox(" ", value=current_blocked, key=f"fblock_{fid}", label_visibility="collapsed")

                if st.form_submit_button("💾 Сохранить настройки"):
                    for fid, val in new_checks.items():
                        db.set_filial_check(fid, val)
                    for fid, blocked in new_blocked.items():
                        db.set_filial_blocked(fid, blocked)
                    st.success("Настройки сохранены!")
                    st.rerun()

# --- НЕРАБОЧИЕ ДНИ (ОТЧЕТ) ---
if tab_admin_non_working is not None:
    with tab_admin_non_working:
        st.markdown("## 📅 Отчет по нерабочим дням ВСП (администратор)")

        # ---------- Фильтры ----------
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filials_df = db.get_filials()
            if not filials_df.empty:
                filial_opts = ["Все"] + filials_df['name'].tolist()
                sel_fil = st.selectbox("Филиал", filial_opts, key="adm_nw_filial_table")
                filial_id_filter = None if sel_fil == "Все" else int(filials_df[filials_df['name'] == sel_fil]['id'].iloc[0])
            else:
                filial_id_filter = None
        with col2:
            vsp_df = db.get_vsp_by_filial(filial_id_filter) if filial_id_filter is not None else db.get_all_vsp()
            if not vsp_df.empty:
                vsp_opts = ["Все"] + vsp_df['name'].tolist()
                sel_vsp = st.selectbox("ВСП", vsp_opts, key="adm_nw_vsp_table")
                vsp_id_filter = None if sel_vsp == "Все" else int(vsp_df[vsp_df['name'] == sel_vsp]['id'].iloc[0])
            else:
                vsp_id_filter = None
        with col3:
            date_from_nw = st.date_input("Дата от", value=None, key="adm_nw_date_from_table")
        with col4:
            date_to_nw = st.date_input("Дата до", value=None, key="adm_nw_date_to_table")

        if st.button("🔍 Показать", key="adm_nw_show_table"):
            with st.spinner("Загрузка данных..."):
                nw_data = db.get_non_working_days(
                    filial_id=filial_id_filter,
                    vsp_id=vsp_id_filter,
                    date_from=date_from_nw,
                    date_to=date_to_nw
                )
            if nw_data.empty:
                st.info("Нет данных по выбранным фильтрам.")
                st.session_state['nw_data'] = None
            else:
                st.success(f"Найдено записей: {len(nw_data)}")
                # Добавляем колонку для выбора (будет редактироваться)
                nw_data['Выбрать для удаления'] = False
                # Оставляем только нужные колонки для отображения
                display_df = nw_data[['id', 'filial', 'vsp', 'date', 'reason', 'Выбрать для удаления']].copy()
                st.session_state['nw_data'] = display_df

        # Отображаем таблицу, если данные есть
        if st.session_state.get('nw_data') is not None and not st.session_state['nw_data'].empty:
            edited_df = st.data_editor(
                st.session_state['nw_data'],
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True),
                    "filial": st.column_config.TextColumn("Филиал", disabled=True),
                    "vsp": st.column_config.TextColumn("ВСП", disabled=True),
                    "date": st.column_config.DateColumn("Дата", disabled=True),
                    "reason": st.column_config.TextColumn("Причина", disabled=True),
                    "Выбрать для удаления": st.column_config.CheckboxColumn("Удалить", default=False),
                },
                hide_index=True,
                use_container_width=True,
                height=400
            )

            # Кнопка массового удаления
            col_btn1, col_btn2 = st.columns([1, 4])
            with col_btn1:
                if st.button("🗑️ Удалить выбранные", type="primary"):
                    ids_to_delete = edited_df[edited_df['Выбрать для удаления'] == True]['id'].tolist()
                    if not ids_to_delete:
                        st.warning("Не выбрано ни одной записи для удаления.")
                    else:
                        with st.spinner(f"Удаление {len(ids_to_delete)} записей..."):
                            deleted_count = db.delete_non_working_days_by_ids(ids_to_delete)
                            st.success(f"✅ Удалено записей: {deleted_count}")
                            # Очищаем сохранённые данные, чтобы при следующем нажатии "Показать" они обновились
                            st.session_state['nw_data'] = None
                            st.rerun()
            with col_btn2:
                # Дополнительная кнопка сброса
                if st.button("🔄 Сбросить и показать заново"):
                    st.session_state['nw_data'] = None
                    st.rerun()

        # ---------- Массовое добавление ----------
        with st.expander("➕ Массовое добавление выходного дня для филиала", expanded=False):
            st.markdown("Добавить нерабочий день сразу для **всех ВСП** выбранного филиала.")
            filials_df_mass = db.get_filials()
            if not filials_df_mass.empty:
                mass_filial_name = st.selectbox("🏢 Филиал", filials_df_mass['name'].tolist(), key="mass_nw_filial")
                mass_filial_id = int(filials_df_mass[filials_df_mass['name'] == mass_filial_name]['id'].iloc[0])
                mass_date = st.date_input("📅 Дата выходного", key="mass_nw_date")
                mass_reason = st.selectbox("📌 Причина", NON_WORKING_REASONS, key="mass_nw_reason")
                if st.button("✅ Добавить выходной для всех ВСП филиала", type="primary"):
                    vsp_list = db.get_vsp_by_filial(mass_filial_id)
                    if vsp_list.empty:
                        st.warning("В филиале нет ВСП.")
                    else:
                        added, skipped = 0, 0
                        for _, v in vsp_list.iterrows():
                            vid = int(v['id'])
                            if db.non_working_day_exists(vid, mass_date):
                                skipped += 1
                            else:
                                db.add_non_working_day("admin", mass_filial_id, vid, mass_date, mass_reason)
                                added += 1
                        msg = f"✅ Добавлено: {added} ВСП"
                        if skipped:
                            msg += f" | ⚠️ Пропущено (уже есть запись): {skipped} ВСП"
                        st.success(msg)
            else:
                st.warning("Нет филиалов в базе.")

        # ---------- ШТУЧНОЕ ДОБАВЛЕНИЕ (новый блок) ----------
        with st.expander("➕ Добавить нерабочий день (штучно)", expanded=False):
            st.markdown("Добавить нерабочий день для конкретного ВСП (один день или период).")
            filials_df = db.get_filials()
            if not filials_df.empty:
                # Выбор филиала
                filial_opts = filials_df['name'].tolist()
                sel_filial_name = st.selectbox("🏢 Филиал", filial_opts, key="manual_nw_filial")
                filial_id_manual = int(filials_df[filials_df['name'] == sel_filial_name]['id'].iloc[0])

                # Выбор ВСП
                vsp_df = db.get_vsp_by_filial(filial_id_manual)
                if not vsp_df.empty:
                    vsp_opts = vsp_df['name'].tolist()
                    sel_vsp_name = st.selectbox("🏪 ВСП", vsp_opts, key="manual_nw_vsp")
                    vsp_id_manual = int(vsp_df[vsp_df['name'] == sel_vsp_name]['id'].iloc[0])

                    # Тип добавления
                    add_type = st.radio("Тип добавления", ["Один день", "Период"], key="manual_nw_type")
                    if add_type == "Один день":
                        manual_date = st.date_input("📅 Дата", value=datetime.date.today(), key="manual_nw_date")
                        date_start = date_end = manual_date
                    else:
                        col1, col2 = st.columns(2)
                        with col1:
                            date_start = st.date_input("📅 Дата начала", value=datetime.date.today(), key="manual_nw_start")
                        with col2:
                            date_end = st.date_input("📅 Дата окончания", value=datetime.date.today(), key="manual_nw_end")
                        if date_start > date_end:
                            st.error("Дата начала не может быть позже даты окончания")
                            date_start = date_end  # чтобы избежать ошибки, но кнопку показываем

                    manual_reason = st.selectbox("📌 Причина", NON_WORKING_REASONS, key="manual_nw_reason")

                    if st.button("✅ Добавить", type="primary", key="manual_nw_btn"):
                        if date_start > date_end:
                            st.error("Исправьте диапазон дат")
                        else:
                            added = 0
                            skipped = 0
                            from datetime import timedelta
                            current_date = date_start
                            while current_date <= date_end:
                                if db.non_working_day_exists(vsp_id_manual, current_date):
                                    skipped += 1
                                else:
                                    db.add_non_working_day("admin", filial_id_manual, vsp_id_manual, current_date, manual_reason)
                                    added += 1
                                current_date += timedelta(days=1)
                            msg = f"✅ Добавлено дней: {added}"
                            if skipped:
                                msg += f" | ⚠️ Пропущено (уже были): {skipped}"
                            st.success(msg)
                else:
                    st.warning("В этом филиале нет ВСП.")
            else:
                st.warning("Нет филиалов в базе.")

        # ---------- ДОБАВЛЕНИЕ суббот массовое (ПО ВСЕМ РФ) ----------
        with st.expander("➕ Добавить выходные на все субботы (для всех ВСП)", expanded=False):
            st.markdown("Создаст нерабочие дни для **всех ВСП** на все субботы в указанном диапазоне.")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Начало", value=datetime.date.today(), key="sat_start")
            with col2:
                end_date = st.date_input("Конец", value=datetime.date.today() + datetime.timedelta(days=365), key="sat_end")
    
            if st.button("✅ Добавить выходные на субботы"):
                if start_date > end_date:
                    st.error("Дата начала не может быть позже окончания")
                else:
                    # Получаем все ВСП с их filial_id
                    all_vsp = db._to_df(f"SELECT id, filial_id, name FROM {db.schema}.vsp")
                    if all_vsp.empty:
                        st.warning("Нет ВСП в базе")
                    else:
                        added = 0
                        skipped = 0
                        current = start_date
                        while current <= end_date:
                            if current.weekday() == 5:  # суббота
                                for _, row in all_vsp.iterrows():
                                    vsp_id = int(row['id'])
                                    filial_id = int(row['filial_id'])
                                    if db.non_working_day_exists(vsp_id, current):
                                        skipped += 1
                                    else:
                                        db.add_non_working_day("admin", filial_id, vsp_id, current, "Суббота (выходной)")
                                        added += 1
                            current += datetime.timedelta(days=1)
                        st.success(f"✅ Добавлено: {added} записей. Пропущено (уже были): {skipped}")
                        st.rerun()

                        
        # ---------- Удаление суббот массовое (ПО ОДНОМУ РФ И НО ПО НЕСКОЛЬКИМ ВЫБРАННЫМ ВСП) ----------
        with st.expander("🗑️ Массовое удаление суббот для нескольких ВСП", expanded=False):
            st.markdown("Выберите филиал, затем **одно или несколько ВСП** для удаления всех нерабочих суббот за период.")
    
            filials_df = db.get_filials()
            if not filials_df.empty:
                selected_filial_name = st.selectbox("🏢 Филиал", filials_df['name'].tolist(), key="del_multi_filial")
                filial_id = int(filials_df[filials_df['name'] == selected_filial_name]['id'].iloc[0])
        
                vsp_df = db.get_vsp_by_filial(filial_id)
                if not vsp_df.empty:
                    # Создаём список (ID, название) для мультиселекта
                    vsp_options = {row['id']: row['name'] for _, row in vsp_df.iterrows()}
                    selected_vsp_ids = st.multiselect(
                        "🏪 Выберите ВСП (можно несколько)",
                        options=list(vsp_options.keys()),
                        format_func=lambda x: vsp_options[x],
                        key="del_multi_vsp"
                    )
                else:
                    st.warning("В филиале нет ВСП")
                    selected_vsp_ids = []
        
                if selected_vsp_ids:
                    col3, col4 = st.columns(2)
                    with col3:
                        date_from_del = st.date_input("📅 Дата от", value=datetime.date(2026, 1, 1), key="multi_date_from")
                    with col4:
                        date_to_del = st.date_input("📅 Дата до", value=datetime.date.today(), key="multi_date_to")
            
                    # Показываем выбранные ВСП для наглядности
                    st.write(f"Выбрано ВСП: {', '.join([vsp_options[vid] for vid in selected_vsp_ids])}")
            
                    confirm = st.checkbox("⚠️ Я подтверждаю удаление всех суббот для выбранных ВСП за указанный период", key="confirm_multi")
            
                    if st.button("🗑️ Удалить субботы для выбранных ВСП", type="primary", disabled=not confirm):
                        if date_from_del > date_to_del:
                            st.error("Дата от не может быть позже даты до")
                        else:
                            deleted = db.delete_saturdays_for_vsp_list(selected_vsp_ids, date_from_del, date_to_del)
                            if deleted:
                                st.success(f"✅ Удалено нерабочих суббот: {deleted}")
                                st.rerun()
                            else:
                                st.info("Нет нерабочих суббот за выбранный период у выбранных ВСП.")
                elif selected_vsp_ids is not None:
                   st.info("Выберите хотя бы одно ВСП.")
            else:
                st.warning("Нет филиалов в базе")

                

# --- ВИЗУАЛИЗАЦИЯ (АДМИН) ---
if tab_visualization_admin is not None:
    with tab_visualization_admin:
        st.markdown("## 📊 Статус заполнения чек-листов (администратор)")
        col1, col2 = st.columns(2)
        with col1:
            filials_df = db.get_filials()
            if filials_df.empty: st.error("Нет филиалов в базе"); st.stop()
            filial_names = filials_df['name'].tolist()
            sel_filial_name = st.selectbox("🏢 Филиал", filial_names, key="vis_admin_filial")
            filial_id_vis = int(filials_df[filials_df['name'] == sel_filial_name]['id'].iloc[0])
        with col2:
            vis_date_admin = st.date_input("📅 Дата", value=datetime.date.today(), key="vis_date_admin")

        if st.button("🔍 Показать статус", key="vis_btn_admin", use_container_width=True):
            with st.spinner("Собираем данные..."):
                status_df = db.get_vsp_status_for_date(filial_id_vis, vis_date_admin)
            if status_df.empty:
                st.info("Нет ВСП в выбранном филиале.")
            else:
                filtered_df = status_df[status_df['Статус'] != 'Выходной']
                total_active = len(filtered_df)
                if total_active == 0:
                    st.info("На выбранную дату все ВСП филиала — нерабочие.")
                else:
                    filled = int((filtered_df['Статус'] == 'Заполнен').sum())
                    not_filled = total_active - filled
                    st.subheader("🍩 Соотношение заполненных и незаполненных ВСП")
                    import plotly.graph_objects as go
                    fig = go.Figure(data=[go.Pie(labels=["Заполнено","Не заполнено"], values=[filled, not_filled],
                                                 marker=dict(colors=["#28a745","#dc3545"]),
                                                 textinfo='label+percent', textfont=dict(size=16), hole=0.4)])
                    fig.update_layout(showlegend=True, legend=dict(font=dict(size=16)), margin=dict(t=20,b=20,l=20,r=20), height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    col_a, col_b = st.columns(2)
                    col_a.metric("✅ Заполнено", f"{filled} из {total_active}", delta=f"{filled / total_active * 100:.0f} %")
                    col_b.metric("❌ Не заполнено", f"{not_filled} из {total_active}", delta=f"{not_filled / total_active * 100:.0f} %", delta_color="inverse")
                st.subheader("📋 Детализация по ВСП")
                def highlight_status(row):
                    if row['Статус'] == 'Заполнен': return ['background-color:#d4edda;color:#155724']*len(row)
                    elif row['Статус'] == 'Выходной': return ['background-color:#fff3cd;color:#856404']*len(row)
                    else: return ['background-color:#f8d7da;color:#721c24']*len(row)
                status_order = {"Не заполнен":0, "Заполнен":1, "Выходной":2}
                status_df['_sort'] = status_df['Статус'].map(status_order)
                status_df = status_df.sort_values('_sort').drop(columns=['_sort'])
                st.dataframe(status_df.style.apply(highlight_status, axis=1), use_container_width=True, height=400)

                # Сводка по всем филиалам
                st.divider(); st.subheader("🏢 Сводка по всем филиалам")
                filial_status_df = db.get_filial_status_for_date(vis_date_admin)
                if not filial_status_df.empty:
                    status_counts = filial_status_df['Статус'].value_counts()
                    status_colors = {"Заполнен":"#28a745","Частично":"#fd7e14","Не заполнен":"#dc3545","Все выходные":"#6c757d"}
                    labels, values, colors = [], [], []
                    for s, c in status_colors.items():
                        if s in status_counts:
                            labels.append(s); values.append(status_counts[s]); colors.append(c)
                    if labels:
                        fig_filial = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors),
                                                             textinfo='label+percent', textfont=dict(size=16), hole=0.4)])
                        fig_filial.update_layout(showlegend=True, legend=dict(font=dict(size=14)), margin=dict(t=20,b=20,l=20,r=20), height=400)
                        st.plotly_chart(fig_filial, use_container_width=True)
                        total_filials = len(filial_status_df)
                        filled_f = int((filial_status_df['Статус'] == 'Заполнен').sum())
                        partial_f = int((filial_status_df['Статус'] == 'Частично').sum())
                        empty_f = int((filial_status_df['Статус'] == 'Не заполнен').sum())
                        c1, c2, c3 = st.columns(3)
                        c1.metric("🟢 Заполнено", filled_f, f"{filled_f/total_filials*100:.0f} %")
                        c2.metric("🟠 Частично", partial_f, f"{partial_f/total_filials*100:.0f} %")
                        c3.metric("🔴 Не заполнено", empty_f, f"{empty_f/total_filials*100:.0f} %", delta_color="inverse")
                    with st.expander("📋 Таблица по филиалам"):
                        def highlight_filial(row):
                            if row['Статус'] == 'Заполнен': return ['background-color:#d4edda']*len(row)
                            elif row['Статус'] == 'Частично': return ['background-color:#ffe5cc']*len(row)
                            elif row['Статус'] == 'Не заполнен': return ['background-color:#f8d7da']*len(row)
                            else: return ['background-color:#e2e3e5']*len(row)
                        sort_order = {"Не заполнен":0,"Частично":1,"Заполнен":2,"Все выходные":3}
                        filial_status_df['_sort'] = filial_status_df['Статус'].map(sort_order)
                        filial_status_df = filial_status_df.sort_values('_sort').drop(columns=['_sort'])
                        st.dataframe(filial_status_df.style.apply(highlight_filial, axis=1), use_container_width=True, height=400)

# --- ВИТРИНЫ (АДМИН) ---
if tab_views_admin is not None:
    with tab_views_admin:

        st.markdown("## 📈 Аналитические витрины (администратор)")
        filials_df = db.get_filials()
        if not filials_df.empty:
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                filial_opts = ["Все"] + sorted((filials_df['id'].astype(str).str.zfill(3)+' - '+filials_df['name']).tolist())
                sel_filial_name = st.selectbox("Филиал", filial_opts, key="adm_vw_filial")
                filial_id = None if sel_filial_name == "Все" else int(sel_filial_name.split()[0])
            with col_f2:
                vsp_df = db.get_vsp_by_filial(filial_id) if filial_id is not None else db.get_all_vsp()
                vsp_opts = (["Все"] + (vsp_df["name"] + " - " + vsp_df["name_vsp"]).tolist())  if not vsp_df.empty else ["Все"]
                sel_vsp_name = st.selectbox("ВСП", vsp_opts, key="adm_vw_vsp")
                vsp_id = None if sel_vsp_name == "Все" else int(vsp_df[vsp_df['name'] == sel_vsp_name]['id'].iloc[0])
            with col_f3:
                date_from = st.date_input("Дата от", value=None, key="adm_vw_date_from")
            with col_f4:
                date_to = st.date_input("Дата до", value=None, key="adm_vw_date_to")      
        st.markdown("### ВИТРИНА ЗАВЕРШЕНИЯ ОПЕРАЦИЙ РФ/ВСП")
        st.markdown("_Сводный отчет по состоянию исполнения контролей за день._")
        view1 = f'''
        with cs_czo as (
        select vsp_id, min(value::int)::bool czo_check, "date"
        from checklist_rf.incomplete_checks_czo
        group by 1, 3
        ),
        
        cs_rf as (
        select vsp.id vsp_id, max(status_bul::int)::bool vsp_check, operation_date
        from checklist_rf.checklist_sessions cs
        join checklist_rf.vsp vsp on cs.vsp_id = vsp.id
        group by 1, 3
        ),
        
        cal as(
        select date
        from public.calendar cal
        where "date" between {"'"+str(date_from)+"'" if date_from is not None else "'2026-05-01'"} and {"'"+str(date_to)+"'" if date_to is not None else 'current_date'}
        )
        
        select substring(vsp.name, 1, 3) "РФ", vsp.name "ВСП", cal.date "Дата ОД", cs_rf.vsp_check "Результат", coalesce(case when cs_czo.czo_check = true then false when cs_czo.czo_check = false then true else null end, true) "Контроль ЕСЦ"
        from checklist_rf.vsp vsp
        cross join cal
        left join cs_rf on vsp.id = cs_rf.vsp_id and cal.date = cs_rf.operation_date
        left join cs_czo on vsp.id = cs_czo.vsp_id and cal.date = cs_czo.date
        where (cs_rf.vsp_check is not null or cs_czo.czo_check is not null)
        {'' if filial_id is None else ' and vsp.filial_id = '+str(filial_id)}
        {'' if vsp_id is None else ' and vsp.id = '+str(vsp_id)}
        order by 1,2,3;
        '''
        view1 = db._to_df(view1)
        # column_config={col: st.column_config.Column(width=120) for col in view1.columns}
        view1['Ст.'] = np.where(
            view1['Результат'] == True,
            view1['Контроль ЕСЦ'],
            None
        )
        # view1.rename('')
        view1['Ст.'] = view1['Ст.'].apply(lambda x: "✔️" if x else ("⚠️" if x is None else "❌"))
        view1[['Результат', 'Контроль ЕСЦ']] = view1[['Результат', 'Контроль ЕСЦ']].applymap(lambda x: "V" if x else (' ' if x is None else "X"))
        st.dataframe(view1, hide_index=True)

        st.markdown("### ОТЧЕТ “ЗАВЕРШЕНИЕ ОПЕРАЦИЙ” ПО РФ")
        st.markdown("_Сводный за месяц рейтинг по всем РФ в двух измерениях - количество ВСП с ошибками и количество операционных дней с ошибками._")
        view2 = f'''
        with cal as(
        select EXTRACT(YEAR FROM cal.date) AS year, TRIM(TO_CHAR(cal.date, 'Month')) AS month, date_trunc('month',date) date, date date_count, work_day
        from public.calendar cal
        where "date" between {"'"+str(date_from)+"'" if date_from is not None else "'2026-05-01'"} and {"'"+str(date_to)+"'" if date_to is not None else 'current_date'}
        ),
        
        cs_rf as(
        select distinct vsp.id vsp_id, operation_date::date
        from checklist_rf.checklist_sessions cs
        join checklist_rf.vsp vsp on cs.vsp_id = vsp.id
        where cs.user_name not in ('Посанчукова Анна Сергеевна')
        and cs.status_bul = True
        ),
        
        cs_cso as(
        select distinct "date"::date operation_date, vsp_id
        from checklist_rf.incomplete_checks_czo
        where value = true
        ),
        
        semi_res as(
        select
        	year,
        	month,
        	cal.date_count,
        	cal.work_day,
        	LPAD(CAST(f.id AS TEXT), 3, '0') rf,
        	v."name" vsp,
        	cs_cso.vsp_id cs_cso,
        	cs_rf.vsp_id cs_rf,
        	cs_cso.operation_date cs_cso_operation_date
        from checklist_rf.filials f
        cross join cal
        left join checklist_rf.vsp v on f.id = v.filial_id
        left join cs_cso on v.id = cs_cso.vsp_id and cs_cso.operation_date = cal.date_count
        left join cs_rf on v.id = cs_rf.vsp_id and cs_rf.operation_date = cal.date_count
        left join checklist_rf.vsp_non_working_days nwd on v.id = nwd.vsp_id and cal.date_count = nwd."date"
        where nwd.reason is null
        {'' if filial_id is None else ' and v.filial_id = '+str(filial_id)}
        {'' if vsp_id is None else ' and v.id = '+str(vsp_id)}
        --and (cs_cso.vsp_id is not null or cs_rf.vsp_id is not null)
        ),
        
        err_vsp_view as (
        select year, month, rf, count(distinct vsp) vsp_cnt, count(distinct cs_cso) err_cnt
        from semi_res
        group by 1,2,3
        order by 1,2,3
        ),
        
        err_days_view as(
        select
                year, month, rf,
                COUNT(distinct cs_cso_operation_date) AS err_days_cnt,
                COUNT(distinct date_count) FILTER (WHERE work_day IS true or cs_cso is not null) AS total_days
            FROM semi_res
            group by 1,2,3
        )
        
        select distinct ev.year::TEXT "Год", ev.month "Месяц", ev.rf "РФ",
        ev.err_cnt::TEXT||'/'||ev.vsp_cnt::TEXT "Количество ВСП с ошибками", DENSE_RANK() over (partition by ev.year, ev.month order by ev.err_cnt::FLOAT/ev.vsp_cnt) "Рейтинг",
        ed.err_days_cnt::TEXT||'/'||ed.total_days::TEXT "Количество дней с ошибками", DENSE_RANK() over (partition by ev.year, ev.month order by ed.err_days_cnt::FLOAT/ed.total_days) "Рeйтинг"
        from err_vsp_view ev
        left join err_days_view ed on ev.year = ed.year and ev.month = ed.month and ev.rf = ed.rf
        order by 1,2,3;
        '''
        view2 = db._to_df(view2)
        def highlight_columns(row, columns_to_highlight):
            styles = [''] * len(row)
            for col in columns_to_highlight:
                if col in row.index:
                    col_idx = row.index.get_loc(col)
                    # Пример правила: если значение 1 или 2 → зеленый
                    if row[col] in (1, 2):
                        styles[col_idx] = 'background-color:#d4edda;color:#155724'
                    else:
                        styles[col_idx] = 'background-color:#f8d7da;color:#721c24'
            return styles
            
        st.dataframe(
            view2.style.apply(lambda row: highlight_columns(row, ['Рейтинг', 'Рeйтинг']), axis=1),
            hide_index=True
        )
        # st.write(view2.to_html(index=False, escape=False), unsafe_allow_html=True)

        st.markdown("### ОТЧЕТ “ЗАВЕРШЕНИЕ ОПЕРАЦИЙ” ПО ВСП")
        st.markdown("_Сводный за месяц рейтинг по всем ВСП. Красная зона - ВСП требуют повышенного внимания._")
        view3 = f'''
        with cal as(
        select EXTRACT(YEAR FROM cal.date) AS year, TRIM(TO_CHAR(cal.date, 'Month')) AS month, date_trunc('month',date) date, date date_count, work_day
        from public.calendar cal
        where "date" between {"'"+str(date_from)+"'" if date_from is not None else "'2026-05-01'"} and {"'"+str(date_to)+"'" if date_to is not None else 'current_date'}
        ),
        
        cs_rf as(
        select distinct vsp.id vsp_id, operation_date::date
        from checklist_rf.checklist_sessions cs
        join checklist_rf.vsp vsp on cs.vsp_id = vsp.id
        -- where cs.user_name not in ()
        and cs.status_bul = True
        ),
        
        cs_cso as(
        select distinct "date"::date operation_date, vsp_id
        from checklist_rf.incomplete_checks_czo
        where value = true
        ),
        
        semi_res as(
        select
        	year,
        	month,
        	cal.date_count,
        	cal.work_day,
        	LPAD(CAST(f.id AS TEXT), 3, '0') rf,
        	v."name" vsp,
        	cs_cso.vsp_id cs_cso,
        	cs_rf.vsp_id cs_rf,
        	cs_cso.operation_date cs_cso_operation_date
        from checklist_rf.filials f
        cross join cal
        left join checklist_rf.vsp v on f.id = v.filial_id
        left join cs_cso on v.id = cs_cso.vsp_id and cs_cso.operation_date = cal.date_count
        left join cs_rf on v.id = cs_rf.vsp_id and cs_rf.operation_date = cal.date_count
        left join checklist_rf.vsp_non_working_days nwd on v.id = nwd.vsp_id and cal.date_count = nwd."date"
        where nwd.reason is null
        {'' if filial_id is None else ' and v.filial_id = '+str(filial_id)}
        {'' if vsp_id is None else ' and v.id = '+str(vsp_id)}
        ),
        
        err_days_view as(
        select
                year::TEXT, month, rf, vsp,
                COUNT(distinct cs_cso_operation_date) AS err_days_cnt,
                COUNT(distinct date_count) FILTER (WHERE work_day IS true or cs_cso is not null) AS total_days
        FROM semi_res
        group by 1,2,3,4
        )
        
        select year::TEXT "Год", month "Месяц",vsp "ВСП", err_days_cnt::TEXT||'/'||total_days::TEXT "Количество дней с ошибками", DENSE_RANK() over (partition by year, month order by err_days_cnt::FLOAT/total_days) "Рейтинг"
        from err_days_view;
        '''
        view3 = db._to_df(view3)
        st.dataframe(
            view3.style.apply(lambda row: highlight_columns(row, ['Рейтинг']), axis=1),
            hide_index=True
        )

        st.markdown("### ДЕТАЛЬНЫЙ ОТЧЕТ ПО ЗАВЕРШЕНИЮ ОПЕРАЦИЙ")
        st.markdown("_Реестр контролей, в которых были допущены ошибки для проработки с исполнителями._")
        view4 = f'''
        with cs_cso as(
        SELECT distinct cc.vsp_id, cc."date"::date date, ct.item_order::text||'. '||ct.description description
        FROM checklist_rf.incomplete_checks_czo cc
        left join checklist_rf.checklist_templates ct on cc.template_id = ct.id
        where value = true and cc.date between {"'"+str(date_from)+"'" if date_from is not None else "'2026-05-01'"} and {"'"+str(date_to)+"'" if date_to is not None else 'current_date'}
        ),
        
        cs_rf as(
        select vsp.id vsp_id, vsp.name vsp, LPAD(CAST(vsp.filial_id AS TEXT), 3, '0') rf, operation_date, user_name
        from checklist_rf.checklist_sessions cs
        join checklist_rf.vsp vsp on cs.vsp_id = vsp.id
        where cs.status_bul = True
        {'' if filial_id is None else ' and vsp.filial_id = '+str(filial_id)}
        {'' if vsp_id is None else ' and vsp.id = '+str(vsp_id)}
        )
        
        select distinct cs_rf.rf "РФ", cs_rf.vsp "ВСП", cs_rf.operation_date "Дата ОД", cs_rf.user_name "Исполнитель", cs_cso.description "Контроль"
        from cs_rf
        join cs_cso on cs_rf.operation_date = cs_cso.date and cs_cso.vsp_id = cs_rf.vsp_id
        order by 1,2,3,4,5;
        '''
        view4 = db._to_df(view4)
        st.dataframe(view4, hide_index=True)
                    

# =============================================================================
# ШАГ 1: ЗАПОЛНЕНИЕ ЧЕК-ЛИСТА (без изменений в логике)
# =============================================================================
if st.session_state.step == 1:
    if "current_session_id" not in st.session_state:
        st.error("Сессия не найдена"); st.session_state.step = 0; st.rerun()
    sid = st.session_state.current_session_id
    sess = db.get_session_data(sid)
    if not sess:
        st.error("Данные сессии отсутствуют"); st.stop()
    template = db.get_checklist_template()
    if template.empty:
        st.warning("Шаблон пуст"); st.stop()
    saved = sess['answers']
    if "temp_answers" not in st.session_state:
        st.session_state.temp_answers = copy.deepcopy(saved)
    cur = db._get_cursor()
    cur.execute(f"SELECT f.name filial_name, v.name vsp_name, s.filial_id, f.check_name FROM {db.schema}.checklist_sessions s JOIN {db.schema}.filials f ON s.filial_id=f.id JOIN {db.schema}.vsp v ON s.vsp_id=v.id WHERE s.id=%s", (sid,))
    row = cur.fetchone()
    filial_name = row['filial_name'] if row else "?"
    vsp_name = row['vsp_name'] if row else "?"
    check_name_value = row['check_name'] if row else False
    use_alt = bool(check_name_value) if check_name_value is not None else False

    st.subheader(f"📋 Чек-лист: {filial_name} / {vsp_name}")
    status_text = "Завершена" if sess['info']['status_bul'] else "Черновик"
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(f"**👤 Сотрудник:** {sess['info']['user_name']}")
    c2.markdown(f"**🏢 Филиал:** {filial_name}")
    c3.markdown(f"**🏪 ВСП:** {vsp_name}")
    c4.markdown(f"**📅 Дата:** {sess['info']['operation_date']}")
    c5.markdown(f"**📌 Статус:** {status_text}")
    if sess['info']['status_bul'] and sess['info'].get('completed_at'):
        st.caption(f"⏱️ Завершено: {sess['info']['completed_at']}")
    st.divider(); st.markdown("### ✔️ Список проверок")

    header = st.columns([1,5,2,1])
    header[0].markdown("**№**"); header[1].markdown("**Наименование проверки**")
    header[2].markdown('<div style="text-align:center;font-weight:900;">Доп. информация</div>', unsafe_allow_html=True)
    header[3].markdown("**Статус**")
    st.markdown("<hr style='margin:8px 0;border:1.5px solid #000000;'>", unsafe_allow_html=True)

    for _, tpl in template.iterrows():
        item_id = tpl['id']; order = tpl['item_order']; desc = tpl['description']
        std_filter = tpl['filter_value'] or "Не задан"
        std_info = tpl['additional_info'] or "Описание отсутствует"
        std_events = tpl['events_value'] or "Фильтр2 не задан"
        alt_filter = tpl['alt_filter_value'] or ""
        alt_info = tpl['alt_additional_info'] or ""
        alt_events = tpl['alt_events_value'] or ""
        chosen_filter = alt_filter if (use_alt and alt_filter) else std_filter
        chosen_info = alt_info if (use_alt and alt_info) else std_info
        chosen_events = alt_events if (use_alt and alt_events) else std_events
        current = st.session_state.temp_answers.get(item_id, saved.get(item_id, False))

        cols = st.columns([1,5,2,1])
        cols[0].write(f"**{order}**"); cols[1].markdown(desc)
        with cols[2]:
            with st.popover(f"ℹ️ Подробнее о проверке №{order}", use_container_width=True):
                t1, t2 = st.tabs(["🔍 Фильтр","📌 Дополнительный фильтр"])
                with t1:
                    st.markdown("**Описание процедуры:**"); st.info(chosen_info)
                    if chosen_filter != "Не задан":
                        filter_display = chosen_filter
                        today = datetime.date.today()
     
                        # Старый формат (для обратной совместимости)
                        if "[Дата1]" in filter_display:
                                st.date_input("📅 Дата (автоматически сегодня)", value=today, disabled=True, key=f"date_{item_id}", format="DD.MM.YYYY")
                                filter_display = filter_display.replace("[Дата1]", today.strftime("%d.%m.%y"))
                        # Новый формат: гггг-мм-дд
                        if "[Дата1 гггг-мм-дд]" in filter_display:
                                filter_display = filter_display.replace("[Дата1 гггг-мм-дд]", today.strftime("%Y-%m-%d"))
                        # Новый формат: дд.мм.гггг
                        if "[Дата1 дд.мм.гггг]" in filter_display:
                                filter_display = filter_display.replace("[Дата1 дд.мм.гггг]", today.strftime("%d.%m.%Y"))
                        filter_display = filter_display.replace("[РФ]", vsp_name)
                        filter_display = filter_display.replace("[РФ1]", vsp_name[:3])
                        st.code(filter_display, language="text")
                        import streamlit.components.v1 as components
                        js = f"""<div style="margin-top:8px"><button id="copy_{item_id}" style="background:#4CAF50;color:white;padding:8px;border:none;border-radius:5px;width:100%">📋 КОПИРОВАТЬ ФИЛЬТР</button><div id="status_{item_id}" style="margin-top:5px;font-size:12px;text-align:center"></div></div>
                        <script>(function(){{var btn=document.getElementById("copy_{item_id}");var statusDiv=document.getElementById("status_{item_id}");var textToCopy={repr(filter_display)};btn.addEventListener("click",function(){{navigator.clipboard.writeText(textToCopy).then(function(){{statusDiv.innerHTML="✅ Скопировано!";statusDiv.style.color="green";setTimeout(function(){{statusDiv.innerHTML="";}},2000);}},function(){{statusDiv.innerHTML="❌ Ошибка";statusDiv.style.color="red";}});}});}})();</script>"""
                        components.html(js, height=100)
                    else:
                        st.info("Фильтр не задан")
                with t2:
                    st.markdown("**Описание процедуры:**"); st.info(chosen_info)
                    if chosen_events != "Не задан":
                        filter_display = chosen_events
                        today = datetime.date.today()
     
                        # Старый формат (для обратной совместимости)
                        if "[Дата1]" in filter_display:
                                st.date_input("📅 Дата (автоматически сегодня)", value=today, disabled=True, key=f"date2_{item_id}", format="DD.MM.YYYY")
                                filter_display = filter_display.replace("[Дата1]", today.strftime("%d.%m.%y"))
                        # Новый формат: гггг-мм-дд
                        if "[Дата1 гггг-мм-дд]" in filter_display:
                                filter_display = filter_display.replace("[Дата1 гггг-мм-дд]", today.strftime("%Y-%m-%d"))
                        # Новый формат: дд.мм.гггг
                        if "[Дата1 дд.мм.гггг]" in filter_display:
                                filter_display = filter_display.replace("[Дата1 дд.мм.гггг]", today.strftime("%d.%m.%Y"))
                        filter_display = filter_display.replace("[РФ]", vsp_name)
                        filter_display = filter_display.replace("[РФ1]", vsp_name[:3])
                        st.code(filter_display, language="text")
                        import streamlit.components.v1 as components
                        js = f"""<div style="margin-top:8px"><button id="copy2_{item_id}" style="background:#4CAF50;color:white;padding:8px;border:none;border-radius:5px;width:100%">📋 КОПИРОВАТЬ ФИЛЬТР</button><div id="status_{item_id}" style="margin-top:5px;font-size:12px;text-align:center"></div></div>
                        <script>(function(){{var btn=document.getElementById("copy_{item_id}");var statusDiv=document.getElementById("status2_{item_id}");var textToCopy={repr(filter_display)};btn.addEventListener("click",function(){{navigator.clipboard.writeText(textToCopy).then(function(){{statusDiv.innerHTML="✅ Скопировано!";statusDiv.style.color="green";setTimeout(function(){{statusDiv.innerHTML="";}},2000);}},function(){{statusDiv.innerHTML="❌ Ошибка";statusDiv.style.color="red";}});}});}})();</script>"""
                        components.html(js, height=100)
                    else:
                        st.info("Фильтр не задан")
        with cols[3]:
            new_val = st.checkbox(" ", value=current, key=f"chk_{item_id}", label_visibility="collapsed")
            if new_val != current: st.session_state.temp_answers[item_id] = new_val
        st.markdown("<hr style='margin:8px 0;border:1.5px solid #000000;'>", unsafe_allow_html=True)

    colA, colB, colC, colD = st.columns([1,1,1,2])
    if colA.button("🔙 Назад", use_container_width=True):
        db.save_answers(sid, st.session_state.temp_answers)
        db.update_session_status(sid, False)
        st.session_state.step = 0
        for k in ['current_session_id','temp_answers','resume_session_id']:
            if k in st.session_state: del st.session_state[k]
        st.rerun()
    if colB.button("💾 Сохранить черновик", use_container_width=True):
        db.save_answers(sid, st.session_state.temp_answers)
        db.update_session_status(sid, False)
        st.success("✅ Черновик сохранён!"); time.sleep(1); st.rerun()
    if colC.button("📋 Предпросмотр", use_container_width=True):
        with st.expander("📄 Предпросмотр результатов", expanded=True):
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
            db.update_session_status(sid, True)
            st.success("🎉 Отлично! Чек-лист успешно завершён!")
            st.balloons()
            st.session_state.step = 0
            for k in ['current_session_id','temp_answers','resume_session_id']:
                if k in st.session_state: del st.session_state[k]
            time.sleep(2); st.rerun()
