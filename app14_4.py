
Проблема: в истории операций видны чужие записи при совпадении ФИО

У вас разные пользователи из разных филиалов, но с одинаковым ФИО. Сейчас выборка идёт только по user_name (ФИО), без учёта филиала. Нужно добавить фильтр по filial_id.

Что меняем

1. Метод get_user_sessions в классе DatabaseManager – добавим параметр filial_id и условие в SQL.
2. Вызов этого метода во вкладке «История проверок» – передадим st.session_state.last_filial_id.

---

1. Исправляем метод get_user_sessions

Было:

```python
def get_user_sessions(self, full_name):
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
        WHERE s.user_name=%s
        GROUP BY s.id, f.name, v.name, s.user_name, s.operation_date, s.status_bul, s.created_at, s.completed_at
        ORDER BY s.created_at DESC
    """, (full_name,))
```

Стало:

```python
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
```

---

2. Исправляем вызов во вкладке «История проверок»

Найдите во вкладке tab_history строку:

```python
hist = db.get_user_sessions(st.session_state.user_full_name)
```

Замените её на:

```python
if st.session_state.get('last_filial_id') is not None:
    hist = db.get_user_sessions(st.session_state.user_full_name, st.session_state.last_filial_id)
else:
    st.warning("Филиал не определён. История недоступна.")
    hist = pd.DataFrame()  # пустой DataFrame
```

---

3. Дополнительная защита (необязательно, но полезно)

Если у пользователя почему-то нет last_filial_id (например, он не прошёл авторизацию), покажите сообщение и не грузите историю.

Вот полный фрагмент tab_history с исправлением:

```python
with tab_history:
    st.markdown("### 📜 История ваших проверок")
    if st.session_state.auth_valid and st.session_state.user_full_name:
        filial_id = st.session_state.get('last_filial_id')
        if filial_id is not None:
            hist = db.get_user_sessions(st.session_state.user_full_name, filial_id)
            if not hist.empty:
                st.dataframe(hist, use_container_width=True, height=400)
                # ... остальной код (выбор сессии, удаление черновиков)
            else:
                st.info("У вас пока нет завершённых проверок.")
        else:
            st.error("Не удалось определить ваш филиал. Обратитесь к администратору.")
    else:
        st.warning("Введите учётную запись, чтобы увидеть историю.")
```

---

Что это даст

· Теперь в историю попадают только сессии, созданные пользователем с таким же ФИО и с таким же filial_id.
· Пользователи из разных филиалов с одинаковыми ФИО не будут видеть чужие записи.

---

Примечание

Если в будущем понадобится также фильтровать черновики (вкладка «Новая проверка» – список незавершённых черновиков), то аналогично нужно исправить метод get_user_draft_sessions. Но по условию задачи требуется только история операций.









Реализация: выходные по субботам для всех ВСП, но с возможностью их удаления при заполнении

Мы сделаем три вещи:

1. Метод для удаления выходного дня по ВСП и дате (если существует).
2. При создании новой проверки в субботу – автоматически удаляем выходной для этого ВСП, чтобы сотрудник мог заполнить чек-лист.
3. В админ-панели – кнопка для массового добавления выходных на все субботы для всех ВСП всех филиалов (на заданный период).

---

1. Добавляем метод в DatabaseManager

Вставьте этот метод в класс DatabaseManager (например, после admin_delete_non_working_day):

```python
def delete_non_working_day_by_vsp_date(self, vsp_id, date):
    """Удаляет запись о нерабочем дне для конкретного ВСП на конкретную дату (если есть)."""
    self._execute(
        f"DELETE FROM {self._table_name('vsp_non_working_days')} WHERE vsp_id = %s AND date = %s",
        (vsp_id, date)
    )
```

---

2. Модифицируем создание новой проверки (вкладка «Новая проверка»)

Найдите код, где после всех проверок вызывается db.create_session. Примерно так:

```python
if submitted and sel_vsp_id is not None:
    # ... существующие проверки (блокировка, существующая сессия, черновик)
    if db.session_exists_for_vsp_date(sel_vsp_id, op_date):
        st.error(...)
    else:
        draft_id = db.get_today_draft_session_id(...)
        if draft_id:
            st.error(...)
        else:
            # ЗДЕСЬ ДОБАВИТЬ НОВЫЙ КОД
            sid = db.create_session(...)
```

Добавьте перед sid = db.create_session(...) следующий блок:

```python
# Если дата – суббота, удаляем запись о нерабочем дне для этого ВСП
if op_date.weekday() == 5:  # 5 = суббота (понедельник=0, воскресенье=6)
    db.delete_non_working_day_by_vsp_date(sel_vsp_id, op_date)
    # Можно добавить необязательное уведомление:
    # st.toast("Выходной день снят, можете заполнять чек-лист", icon="✅")
```

Теперь, если в субботу для данного ВСП был установлен выходной (администратором), при попытке начать заполнение он автоматически удалится, и пользователь сможет создать новую сессию.

---

3. Добавляем в админ-панель массовое создание выходных на субботы

Откройте вкладку «📅 Нерабочие дни (отчет)» (для администратора) и вставьте новый блок с st.expander. Например, после существующего блока массового добавления или в конце.

```python
with st.expander("➕ Массовое добавление выходных на субботы для всех ВСП", expanded=False):
    st.markdown("Добавить нерабочие дни для **всех ВСП всех филиалов** на все субботы в указанном диапазоне.")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Начало диапазона", value=datetime.date.today(), key="sat_start")
    with col2:
        end_date = st.date_input("Конец диапазона", value=datetime.date.today() + datetime.timedelta(days=365), key="sat_end")
    
    if st.button("✅ Добавить выходные на субботы для всех ВСП"):
        if start_date > end_date:
            st.error("Дата начала не может быть позже даты окончания")
        else:
            all_vsp = db.get_all_vsp()
            if all_vsp.empty:
                st.warning("Нет ВСП в базе данных")
            else:
                added = 0
                skipped = 0
                current_date = start_date
                while current_date <= end_date:
                    if current_date.weekday() == 5:  # суббота
                        for _, v in all_vsp.iterrows():
                            vsp_id = int(v['id'])
                            if db.non_working_day_exists(vsp_id, current_date):
                                skipped += 1
                            else:
                                db.add_non_working_day("admin", None, vsp_id, current_date, "Суббота (выходной)")
                                added += 1
                    current_date += datetime.timedelta(days=1)
                st.success(f"✅ Добавлено: {added} записей. Пропущено (уже были): {skipped}")
                st.rerun()
```

Этот блок позволяет администратору одним кликом установить выходные на все субботы (например, на год вперёд) для абсолютно всех ВСП из всех филиалов.

---

Что в итоге?

· Администратор запускает массовое добавление – у всех ВСП на субботы появляются выходные.
· Сотрудник в субботу пытается начать заполнение – система удаляет выходной для его ВСП именно на эту дату и позволяет создать проверку.
· Если другой сотрудник этого же ВСП попытается заполнить в ту же субботу позже – выходного уже нет, он тоже сможет заполнить (но это не страшно, так как по логике у вас может быть только один черновик/завершённая сессия на ВСП в день, что уже реализовано).

Таким образом, выходные по умолчанию есть, но если сотрудник решает работать в субботу – система не мешает.

---

Примечание

Если вы хотите, чтобы удаление выходного происходило только при начале заполнения, а не при любом действии – код уже делает именно это. Никакие другие операции (просмотр истории, аналитика) не удаляют выходные.

Если же администратор хочет принудительно не давать заполнять в субботу, он просто не использует массовое добавление и не даёт прав на удаление (но удаление происходит автоматически, так что выходной всё равно будет снят при попытке заполнения). Это соответствует вашему требованию.

  
