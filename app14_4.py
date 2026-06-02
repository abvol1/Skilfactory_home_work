
Ошибка: can't adapt type 'numpy.int64'

Это происходит, потому что вы передаёте в SQL-запрос значение типа numpy.int64 (извлечённое из pandas.DataFrame), а psycopg2 не умеет автоматически преобразовывать такие типы в PostgreSQL.

Решение: везде, где вы получаете filial_id из DataFrame, явно приводите его к стандартному int.

Конкретные места в вашем коде, которые нужно исправить

1. Метод check_user_by_name (после исправления)

```python
def check_user_by_name(self, name: str):
    df = self._to_df(...)
    if not df.empty:
        row = df.iloc[0]
        filial_id = row.get('filial_id')
        # ПРИВЕДЕНИЕ:
        if filial_id is not None:
            filial_id = int(filial_id)   # <-- добавить эту строку
        return True, row['full_name'], row.get('filial_name'), filial_id
    return False, None, None, None
```

2. В блоке авторизации (где вызывается check_user_by_name)

```python
exists, full, fil, filial_id = db.check_user_by_name(login_norm)
if exists:
    # Убедиться, что filial_id – это int (на всякий случай)
    if filial_id is not None:
        filial_id = int(filial_id)
    st.session_state.last_filial_id = filial_id
    # ...
```

3. В методе get_filial_blocked_status (чтобы защитить его от numpy.int64)

```python
def get_filial_blocked_status(self, filial_id: int) -> bool:
    # Привести к int, если вдруг передали numpy.int64
    filial_id = int(filial_id)
    row = self._execute(
        f"SELECT blocked FROM {self._table_name('filials')} WHERE id = %s",
        (filial_id,), fetch_one=True
    )
    return row['blocked'] if row else False
```

Аналогично в set_filial_blocked:

```python
def set_filial_blocked(self, filial_id: int, blocked: bool):
    filial_id = int(filial_id)
    self._execute(
        f"UPDATE {self._table_name('filials')} SET blocked = %s WHERE id = %s",
        (blocked, filial_id)
    )
```

4. При обновлении статуса блокировки после st.title

```python
if st.session_state.auth_valid and st.session_state.last_filial_id is not None:
    fid = int(st.session_state.last_filial_id)   # привести
    st.session_state.user_filial_blocked = db.get_filial_blocked_status(fid)
```

5. В форме создания новой проверки (перед db.create_session)

```python
if submitted and sel_vsp_id is not None:
    # Обновляем статус блокировки
    current_filial_id = int(sel_filial_id)   # привести
    st.session_state.user_filial_blocked = db.get_filial_blocked_status(current_filial_id)
    if st.session_state.user_filial_blocked:
        st.error("Ваш филиал временно заблокирован...")
```

Универсальный способ – написать функцию-обёртку

Чтобы не добавлять int() в каждом месте, можно модифицировать метод _execute, чтобы он автоматически конвертировал numpy.int64 в int:

```python
def _execute(self, query, params=None, fetch_one=False, fetch_all=False, commit=True):
    if params:
        # Преобразуем numpy.int64 и numpy.int32 в обычный int
        params = tuple(
            int(p) if hasattr(p, 'dtype') and 'int' in str(p.dtype) else p
            for p in params
        )
    # ... остальной код
```

Но проще и нагляднее явно приводить типы там, где вы передаёте значения из DataFrame.

Что делать прямо сейчас

1. Найдите в своём коде все вызовы db.get_filial_blocked_status(...) и db.set_filial_blocked(...).
2. Убедитесь, что аргумент filial_id обёрнут в int().
3. Исправьте метод check_user_by_name, как показано выше.
4. Перезапустите приложение.

После этих правок ошибка can't adapt type 'numpy.int64' исчезнет, и блокировка филиалов будет работать корректно.







Конкретные правки в вашем коде

Ниже перечислены 4 блока, которые нужно изменить, чтобы заглушка (блокировка филиала) заработала корректно.

---

1. Исправить метод check_user_by_name – возвращать filial_id

Где: Класс DatabaseManager, метод check_user_by_name (строки примерно 160–170 в вашем файле).

Было:

```python
def check_user_by_name(self, name: str):
    df = self._to_df(
        f"SELECT us.name, us.full_name, f.name AS filial_name FROM {self.schema}.users us LEFT JOIN {self.schema}.filials f ON us.name_filial::numeric = f.id WHERE LOWER(us.name)=LOWER(%s)",
        (name,)
    )
    if not df.empty:
        return True, df.iloc[0]['full_name'], df.iloc[0].get('filial_name')
    return False, None, None
```

Стало:

```python
def check_user_by_name(self, name: str):
    df = self._to_df(
        f"SELECT us.name, us.full_name, f.name AS filial_name, f.id AS filial_id FROM {self.schema}.users us LEFT JOIN {self.schema}.filials f ON us.name_filial::numeric = f.id WHERE LOWER(us.name)=LOWER(%s)",
        (name,)
    )
    if not df.empty:
        row = df.iloc[0]
        return True, row['full_name'], row.get('filial_name'), row.get('filial_id')
    return False, None, None, None
```

---

2. Исправить блок авторизации (вкладка «Новая проверка»)

Где: Внутри tab_main (секция с st.text_input("👤 Учетная запись сотрудника")). Строки примерно 760–780.

Было:

```python
if (login_norm and login_norm != st.session_state.user_name and not st.session_state.auth_valid):
    exists, full, fil = db.check_user_by_name(login_norm)
    if exists:
        st.session_state.user_name = login_norm
        st.session_state.user_full_name = full
        st.session_state.auth_valid = True

        filial_id_for_block = filial_map.get(fil)  # fil - название филиала из check_user_by_name
        if filial_id_for_block:
            st.session_state.user_filial_blocked = db.get_filial_blocked_status(filial_id_for_block)
        else:
            st.session_state.user_filial_blocked = False

        if fil and fil in filial_names:
            st.session_state.last_filial_name = fil
            st.session_state.selected_filial_id = filial_map[fil]
            st.session_state.last_filial_id = filial_map[fil]
            st.session_state.update_counter += 1
        st.success(f"✅ Добро пожаловать, {full}!"); st.rerun()
```

Стало:

```python
if (login_norm and login_norm != st.session_state.user_name and not st.session_state.auth_valid):
    exists, full, fil, filial_id = db.check_user_by_name(login_norm)   # теперь 4 значения
    if exists:
        st.session_state.user_name = login_norm
        st.session_state.user_full_name = full
        st.session_state.auth_valid = True

        # Блокировка определяется по ID, а не по названию
        if filial_id is not None:
            st.session_state.user_filial_blocked = db.get_filial_blocked_status(filial_id)
            st.session_state.last_filial_id = filial_id
        else:
            st.session_state.user_filial_blocked = False

        # Заполняем остальные данные
        if fil and fil in filial_names:
            st.session_state.last_filial_name = fil
            st.session_state.selected_filial_id = filial_id
            # st.session_state.last_filial_id уже установлен выше
            st.session_state.update_counter += 1
        st.success(f"✅ Добро пожаловать, {full}!"); st.rerun()
```

---

3. Добавить принудительное обновление статуса блокировки перед каждой проверкой

Где: Сразу после st.title("📋 Завершение операций по ВСП/РФ") (строка примерно 700), перед созданием вкладок.

Вставьте этот код:

```python
# Обновляем статус блокировки для текущего пользователя
if st.session_state.auth_valid and st.session_state.last_filial_id is not None:
    st.session_state.user_filial_blocked = db.get_filial_blocked_status(st.session_state.last_filial_id)
```

Это гарантирует, что если админ изменил блокировку во время сессии пользователя, статус обновится при любом действии (переходе между вкладками, нажатии кнопки).

---

4. Заблокировать возможность продолжать черновик, если филиал заблокирован

Где: Вкладка «Новая проверка», блок с today_drafts (строки примерно 740–750), внутри кнопки Продолжить.

Было:

```python
if c1.button("📂 Продолжить", key=f"resume_{d['id']}", use_container_width=True):
    st.session_state.current_session_id = d['id']; st.session_state.step = 1; st.rerun()
```

Стало:

```python
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
            st.session_state.current_session_id = d['id']; st.session_state.step = 1; st.rerun()
    else:
        st.session_state.current_session_id = d['id']; st.session_state.step = 1; st.rerun()
```

Альтернатива (проще): изменить метод get_user_draft_sessions, чтобы он возвращал также filial_id. Тогда не нужно делать лишний запрос.

---

5. (Дополнительно) Добавить проверку блокировки перед созданием новой сессии

Где: Там же, внутри формы with st.form("new_session_form"), перед вызовом db.create_session.

Сейчас у вас уже есть проверка:

```python
if st.session_state.user_filial_blocked:
    st.error("Ваш филиал временно заблокирован для заполнения чек-листов.")
```

Но чтобы она работала с обновлённым статусом, добавьте перед этим строку (можно в начале блока if submitted):

```python
if submitted and sel_vsp_id is not None:
    # Обновляем статус блокировки перед проверкой
    st.session_state.user_filial_blocked = db.get_filial_blocked_status(sel_filial_id)
    if st.session_state.user_filial_blocked:
        st.error("Ваш филиал временно заблокирован для заполнения чек-листов.")
    # ... остальные проверки
```

---

Итог: что делать по шагам

1. Скопируйте исправленный метод check_user_by_name в класс DatabaseManager.
2. Найдите в коде блок авторизации (где st.text_input("👤 Учетная запись сотрудника")) – замените его на новый.
3. Добавьте строчку обновления user_filial_blocked после st.title(...).
4. Измените логику кнопки «Продолжить» для черновиков.
5. При желании – добавьте обновление статуса перед созданием новой сессии.

После этих правок административная галочка блокировки будет работать мгновенно для всех пользователей, включая тех, кто уже авторизован.






















Вы правы, у вас уже есть чекбоксы во вкладке «Филиалы (чекбоксы)» для других целей (скорее всего, для check_name – пометки о миграции).
Мы не будем их трогать – просто добавим второй столбец чекбоксов «Блокировать» в той же самой форме. Это не сломает существующую логику, а только расширит функционал.

Как это будет выглядеть

В таблице филиалов появятся два чекбокса в строке:

Филиал Чекбокс (миграция) 🔒 Блокировать
Липецк ☑️ (старый) ☐ (новый)
... ... ...

При сохранении обновляются оба поля.

Что нужно изменить в коде

1. Добавить столбец blocked в таблицу filials (если ещё не сделали)

```sql
ALTER TABLE checklist_rf.filials ADD COLUMN IF NOT EXISTS blocked BOOLEAN DEFAULT FALSE;
```

2. Добавить методы в DatabaseManager

```python
def get_filial_blocked_status(self, filial_id: int) -> bool:
    row = self._execute(
        f"SELECT blocked FROM {self._table_name('filials')} WHERE id = %s",
        (filial_id,), fetch_one=True
    )
    return row['blocked'] if row else False

def set_filial_blocked(self, filial_id: int, blocked: bool):
    self._execute(
        f"UPDATE {self._table_name('filials')} SET blocked = %s WHERE id = %s",
        (blocked, filial_id)
    )
```

3. Изменить вкладку «Филиалы (чекбоксы)» – добавить колонку «Блокировать»

Найдите текущий блок:

```python
if tab_filial_check is not None:
    with tab_filial_check:
        st.markdown("## 🏢 Настройка филиалов для альтернативных фильтров")
        filials_df = db.get_filials()
        ...
        with st.form("filial_checks_form"):
            st.markdown("**Отметьте нужные филиалы:**")
            new_checks = {}
            for _, frow in filials_df.iterrows():
                fid = int(frow['id']); fname = frow['name']; current = bool(frow['check_name'])
                new_checks[fid] = st.checkbox(fname, value=current, key=f"fchk_{fid}")
            if st.form_submit_button("💾 Сохранить чекбоксы"):
                ...
```

Замените на следующий код (добавляем второй чекбокс в каждой строке и сохраняем оба):

```python
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
```

4. Добавить проверку блокировки при авторизации

В том месте, где пользователь успешно авторизуется (после st.session_state.auth_valid = True), добавьте:

```python
filial_id_for_block = filial_map.get(fil)  # fil - название филиала из check_user_by_name
if filial_id_for_block:
    st.session_state.user_filial_blocked = db.get_filial_blocked_status(filial_id_for_block)
else:
    st.session_state.user_filial_blocked = False
```

А также инициализацию в начале (с другими session_state):

```python
if "user_filial_blocked" not in st.session_state:
    st.session_state.user_filial_blocked = False
```

5. Показать заглушку

Сразу после st.title(...) вставьте:

```python
if st.session_state.auth_valid and st.session_state.user_filial_blocked:
    st.error("⛔ Доступ временно ограничен")
    st.warning(
        "На данный филиал пилотный проект не распространяется.\n\n"
        "Пожалуйста, ожидайте дополнительной информации от руководителя."
    )
    st.stop()
```

6. Дополнительно: блокировка кнопки «Начать заполнение»

В tab_main внутри обработки формы (где if submitted) добавьте:

```python
if st.session_state.user_filial_blocked:
    st.error("Ваш филиал временно заблокирован для заполнения чек-листов.")
```

Итог

· Старые чекбоксы check_name (миграция) остаются и работают как прежде.
· Появился новый столбец «Блокировка», независимый от старого.
· Админ может включить блокировку для любого филиала – пользователи этого филиала увидят сообщение и не смогут заполнять чек-листы.

Если нужно, могу прислать полный готовый файл с уже интегрированными изменениями.
