
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
