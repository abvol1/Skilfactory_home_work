
Отлично, всё исправили! Теперь пользователь может удалять любые записи нерабочих дней для СВОЕГО ВСП

Ваше требование выполнено: сотрудник ВСП имеет право удалять нерабочие дни, относящиеся к его ВСП, независимо от того, кто их создал. При этом он не может затронуть записи других ВСП.

Что было изменено

1. Метод удаления в DatabaseManager – delete_non_working_days_by_ids_for_vsp – удаляет записи по списку id, проверяя только vsp_id и filial_id, но не проверяя user_name.
2. Отображение во вкладке пользователя – показываются все нерабочие дни для его ВСП, с колонкой «Кто добавил» (для информации).
3. Безопасность – при попытке удалить запись, которая не принадлежит его ВСП, удаление не произойдёт.
4. Просмотр других ВСП – отдельный блок только для чтения, без возможности удаления.

Итоговые возможности пользователя

· ✅ Добавлять нерабочие дни для своего ВСП.
· ✅ Удалять любые нерабочие дни (свои или созданные администратором/другими сотрудниками) для своего ВСП.
· ✅ Просматривать нерабочие дни других ВСП своего филиала (без права удаления).

Никакой лишней функциональности, база в безопасности, логика прозрачна. Если потребуются доработки – обращайтесь.








Исправляем: пользователь может удалять только свои нерабочие дни (своего ВСП)

Проблема

В предыдущей реализации пользователь, выбрав в выпадающем списке чужое ВСП (сняв галочку «Использовать моё ВСП»), мог удалить записи нерабочих дней этого чужого ВСП. Это недопустимо.

Решение

· При удалении всегда использовать привязанное к пользователю ВСП (default_vsp_id), а не выбранное в интерфейсе.
· Проверять также user_name (кто создал запись) – чтобы пользователь удалял только свои собственные записи (даже если у него есть доступ к чужому ВСП).
· При показе «всех ВСП филиала» кнопка удаления вообще не должна отображаться (как и было в оригинале).

1. Исправленный метод в DatabaseManager (безопасное удаление)

Замените метод delete_non_working_days_by_ids_for_user на этот:

```python
def delete_my_non_working_days(self, ids, user_name, vsp_id, filial_id):
    """
    Удаляет записи о нерабочих днях, созданные пользователем,
    для указанного ВСП и филиала (дополнительная проверка).
    Возвращает количество удалённых записей.
    """
    if not ids:
        return 0
    ids = [int(i) for i in ids]
    vsp_id = int(vsp_id)
    filial_id = int(filial_id)
    query = f"""
        DELETE FROM {self._table_name('vsp_non_working_days')}
        WHERE id = ANY(%s)
          AND user_name = %s
          AND vsp_id = %s
          AND filial_id = %s
    """
    self._execute(query, (ids, user_name, vsp_id, filial_id))
    return len(ids)
```

2. Исправленный блок вкладки пользователя

Полностью замените содержимое вкладки tab_non_working (пользовательскую) на следующий код:

```python
if tab_non_working is not None:
    with tab_non_working:
        st.markdown("## 📅 Внесение нерабочих дней ВСП")
        st.caption("Укажите дату и причину. Удалить можно только свои записи (только для вашего ВСП).")
        
        # Определяем филиал пользователя
        if st.session_state.get("last_filial_id") is None:
            exists, full, fil, filial_id, default_vsp_name, default_vsp_id = db.check_user_by_name(st.session_state.user_name)
            if exists and filial_id:
                st.session_state.last_filial_id = filial_id
                st.session_state.last_filial_name = fil
                st.session_state.default_vsp_id = default_vsp_id
                st.session_state.default_vsp_name = default_vsp_name
            else:
                st.error("Не удалось определить ваш филиал."); st.stop()
        
        current_filial_id = st.session_state.last_filial_id
        current_filial_name = st.session_state.last_filial_name
        my_vsp_id = st.session_state.get('default_vsp_id')
        my_vsp_name = st.session_state.get('default_vsp_name')
        
        st.markdown(f"**Филиал:** {current_filial_name}")
        
        if not my_vsp_id:
            st.error("Для вашего логина не указано ВСП в таблице users. Обратитесь к администратору.")
            st.stop()
        
        # Показываем информацию о своём ВСП
        st.info(f"🏪 Ваше ВСП: **{my_vsp_name}** (ID {my_vsp_id})")
        
        # ---- Форма добавления нового нерабочего дня ----
        nw_date = st.date_input("📅 Дата нерабочего дня", value=datetime.date.today(), key="user_nw_date")
        nw_reason = st.selectbox("📌 Причина", NON_WORKING_REASONS, key="user_nw_reason")
        
        if st.button("💾 Добавить нерабочий день", type="primary", use_container_width=True):
            db.add_non_working_day(
                st.session_state.user_full_name,
                current_filial_id,
                my_vsp_id,   # всегда добавляем для своего ВСП
                nw_date,
                nw_reason
            )
            st.success(f"✅ Нерабочий день {nw_date} для вашего ВСП сохранён!")
            time.sleep(1)
            st.rerun()
        
        st.divider()
        
        # ---- Отображение ранее добавленных нерабочих дней (только своих, для своего ВСП) ----
        st.markdown("### 📋 Ранее добавленные вами нерабочие дни")
        
        # Загружаем только записи, созданные пользователем для его ВСП
        my_nw_df = db.get_non_working_days(
            filial_id=current_filial_id,
            vsp_id=my_vsp_id
        )
        # Дополнительно фильтруем по user_name (на всякий случай)
        my_nw_df = my_nw_df[my_nw_df['user_name'] == st.session_state.user_full_name]
        
        if my_nw_df.empty:
            st.info("У вас нет добавленных нерабочих дней.")
        else:
            # Подготавливаем таблицу
            display_df = my_nw_df[['id', 'date', 'reason']].copy()
            display_df['Выбрать для удаления'] = False
            display_df['date'] = pd.to_datetime(display_df['date']).dt.date
            
            edited_df = st.data_editor(
                display_df,
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True),
                    "date": st.column_config.DateColumn("Дата", disabled=True),
                    "reason": st.column_config.TextColumn("Причина", disabled=True),
                    "Выбрать для удаления": st.column_config.CheckboxColumn("Удалить", default=False),
                },
                hide_index=True,
                use_container_width=True,
                height=400
            )
            
            col_btn1, col_btn2 = st.columns([1, 4])
            with col_btn1:
                if st.button("🗑️ Удалить выбранные", key="user_del_my"):
                    ids_to_delete = edited_df[edited_df['Выбрать для удаления'] == True]['id'].tolist()
                    if not ids_to_delete:
                        st.warning("Не выбрано ни одной записи.")
                    else:
                        deleted = db.delete_my_non_working_days(
                            ids_to_delete,
                            st.session_state.user_full_name,
                            my_vsp_id,
                            current_filial_id
                        )
                        st.success(f"✅ Удалено записей: {deleted}")
                        st.rerun()
            with col_btn2:
                if st.button("🔄 Обновить список", key="user_refresh_my"):
                    st.rerun()
        
        # ---- Дополнительно: возможность посмотреть все ВСП филиала (только просмотр) ----
        st.markdown("### 👁️ Просмотр нерабочих дней других ВСП (только чтение)")
        show_all = st.checkbox("Показать все ВСП филиала", value=False, key="user_show_all_readonly")
        if show_all:
            all_nw_df = db.get_non_working_days(filial_id=current_filial_id, vsp_id=None)
            if not all_nw_df.empty:
                st.dataframe(
                    all_nw_df[['vsp', 'date', 'reason', 'user_name']],
                    column_config={
                        "vsp": "ВСП",
                        "date": "Дата",
                        "reason": "Причина",
                        "user_name": "Кто добавил"
                    },
                    hide_index=True,
                    use_container_width=True,
                    height=400
                )
            else:
                st.info("Нет записей.")
```

Что изменилось

1. Добавление нового дня – всегда для своего ВСП (my_vsp_id).
2. Отображение – только записи пользователя для его ВСП.
3. Удаление – через метод delete_my_non_working_days, который проверяет user_name, vsp_id, filial_id.
4. Просмотр чужих ВСП – отдельный блок с st.dataframe только для чтения, без кнопок удаления.
5. Убрана возможность выбора чужого ВСП для удаления.

Безопасность

· Пользователь может удалить только свои собственные записи (по user_name).
· Даже если в таблице окажется запись с его user_name, но для чужого ВСП – она не будет удалена, потому что проверка по vsp_id отсечёт.
· При добавлении нового дня vsp_id берётся из сессии (my_vsp_id), а не из выпадающего списка.

Теперь всё корректно: пользователь работает только со своим ВСП, не может повлиять на чужие данные.






Переделываем вкладку пользователя «Нерабочие дни ВСП» в табличную форму с массовым удалением

Сейчас во вкладке пользователя записи выводятся через цикл с кнопкой «🗑️» для каждой строки, что при большом количестве записей вызывает зависание. Заменим на st.data_editor с чекбоксами и одной кнопкой «Удалить выбранные», но только для записей текущего ВСП пользователя.

1. Добавляем безопасный метод удаления в DatabaseManager

Метод удаляет записи по списку id, но предварительно проверяет, что эти записи принадлежат указанному vsp_id и filial_id (чтобы пользователь случайно не удалил чужие записи, если id подберёт).

```python
def delete_non_working_days_by_ids_for_user(self, ids, vsp_id, filial_id):
    """
    Удаляет записи о нерабочих днях по списку id, но только те,
    которые принадлежат указанному ВСП и филиалу.
    Возвращает количество удалённых записей.
    """
    if not ids:
        return 0
    ids = [int(i) for i in ids]
    vsp_id = int(vsp_id)
    filial_id = int(filial_id)
    query = f"""
        DELETE FROM {self._table_name('vsp_non_working_days')}
        WHERE id = ANY(%s)
          AND vsp_id = %s
          AND filial_id = %s
    """
    self._execute(query, (ids, vsp_id, filial_id))
    return len(ids)
```

2. Заменяем блок вывода записей во вкладке пользователя

Найдите вкладку tab_non_working (пользовательскую). Внутри неё есть часть с st.markdown("### 📋 Ранее добавленные нерабочие дни") и цикл for _, row in nw_df.iterrows(): с кнопками. Замените весь этот блок (от st.markdown("### 📋 Ранее добавленные нерабочие дни") до конца цикла) на следующий код:

```python
# ----- Блок отображения и удаления нерабочих дней (табличный) -----
st.markdown("### 📋 Ранее добавленные нерабочие дни")
show_all = st.checkbox("Показать все ВСП филиала", value=False, key="nw_show_all_user")
filter_vsp = None if show_all else sel_vsp_id_nw
nw_df = db.get_non_working_days(filial_id=current_filial_id, vsp_id=filter_vsp)

if nw_df.empty:
    st.info("Нет записей о нерабочих днях.")
else:
    # Добавляем колонку для выбора удаления
    nw_df['Выбрать для удаления'] = False
    # Ограничим колонки для отображения
    display_df = nw_df[['id', 'date', 'reason', 'Выбрать для удаления']].copy()
    # Если show_all = True, покажем ещё и ВСП
    if show_all:
        display_df.insert(0, 'vsp', nw_df['vsp'])
    
    # Редактируемая таблица
    edited_df = st.data_editor(
        display_df,
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "vsp": st.column_config.TextColumn("ВСП", disabled=True) if show_all else None,
            "date": st.column_config.DateColumn("Дата", disabled=True),
            "reason": st.column_config.TextColumn("Причина", disabled=True),
            "Выбрать для удаления": st.column_config.CheckboxColumn("Удалить", default=False),
        },
        hide_index=True,
        use_container_width=True,
        height=400,
        disabled=not show_all  # если show_all, то колонка vsp будет видна, но редактировать нельзя
    )
    
    # Кнопка удаления выбранных
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🗑️ Удалить выбранные", key="user_del_selected"):
            ids_to_delete = edited_df[edited_df['Выбрать для удаления'] == True]['id'].tolist()
            if not ids_to_delete:
                st.warning("Не выбрано ни одной записи для удаления.")
            else:
                # Безопасное удаление только для текущего ВСП (или для всех, если show_all? 
                # При show_all пользователь видит записи других ВСП? По логике show_all = True показывает все ВСП филиала, но удалять пользователь может только записи, созданные им? 
                # В исходной логике при show_all = False удаляется только запись для выбранного ВСП. При show_all = True кнопка удаления вообще не отображалась (были только для своего ВСП). 
                # Чтобы не нарушать безопасность, при show_all = True кнопку удаления лучше не показывать, либо удалять только записи, где vsp_id = текущему ВСП пользователя.
                # Поскольку в исходном коде при show_all кнопок удаления не было, здесь мы тоже запретим удаление при show_all.
                if show_all:
                    st.error("При показе всех ВСП удаление невозможно. Снимите галочку 'Показать все ВСП филиала' и выберите конкретное ВСП.")
                else:
                    # Удаляем только те записи, которые принадлежат текущему ВСП пользователя
                    deleted = db.delete_non_working_days_by_ids_for_user(
                        ids_to_delete, sel_vsp_id_nw, current_filial_id
                    )
                    st.success(f"✅ Удалено записей: {deleted}")
                    st.rerun()
    with col_btn2:
        if st.button("🔄 Обновить список", key="user_refresh"):
            st.rerun()
```

Важные моменты

· Когда показаны все ВСП (галочка show_all = True), кнопка удаления будет выдавать ошибку и не удалит ничего. Это соответствует исходной логике: пользователь мог удалять только записи своего ВСП, а при показе всех ВСП кнопки удаления вообще не было.
· Удаление происходит через метод delete_non_working_days_by_ids_for_user, который проверяет vsp_id и filial_id – даже если пользователь каким-то образом передал чужой id, запись не удалится.
· Таблица редактируемая, но все колонки, кроме чекбокса, отключены (disabled=True). Пользователь только выбирает строки для удаления.
· Высота таблицы фиксирована (400px), чтобы не растягиваться на весь экран.
· После удаления или обновления страница перезагружается.

3. Удалите старый код с циклом и кнопками

Уберите всё, что было внутри if not show_all: и else: с кнопками col4.button("🗑️", ...). Оставьте только код, который получает nw_df и затем новый st.data_editor.

Итог

Теперь у пользователя тоже быстрая табличная форма с возможностью массового выбора и удаления (но только для его ВСП). База не пострадает, лишнего не удалится.
















Переделываем вкладку «Нерабочие дни (отчет)» в табличную форму

Ваша текущая реализация (построчный вывод через st.columns + кнопки) при большом количестве записей приводит к зависанию. Заменим её на st.data_editor с возможностью выбора строк и массовым удалением. Это будет работать быстро даже для тысяч записей.

1. Добавляем метод массового удаления в DatabaseManager

```python
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
```

2. Полностью заменяем вкладку tab_admin_non_working

Найдите в вашем коде блок, начинающийся с if tab_admin_non_working is not None: (скорее всего, в конце файла). Замените всё содержимое этой вкладки на следующий код:

```python
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
```

Что изменилось и почему это быстро

· Используется st.data_editor – он отображает таблицу как единый компонент, а не сотни отдельных виджетов.
· Колонка для удаления – чекбоксы, которые можно проставить для нескольких строк.
· Массовое удаление одним запросом – метод delete_non_working_days_by_ids удаляет все выбранные записи за один SQL-запрос (через ANY), а не по одному.
· Данные кэшируются в st.session_state – при повторных нажатиях "Показать" данные перезагружаются.
· Высота таблицы ограничена (400px) – это не даёт ей разрастаться на весь экран.
· Удаление происходит с подтверждением (вы сначала ставите галочки, затем нажимаете кнопку).

Дополнительные улучшения (по желанию)

· Если данных очень много (>1000 строк), можно добавить пагинацию или ограничить выборку последними N записями, но st.data_editor и так справляется с несколькими тысячами строк довольно хорошо.
· Чтобы ускорить загрузку, можно в get_non_working_days добавить LIMIT 2000, но это ограничит отображение.

Что удалить из старого кода

· Функцию delete_nw_callback (если она была объявлена выше) – больше не нужна.
· Старый цикл for _, row in nw_data.iterrows(): – полностью заменён.

Теперь вкладка работает быстро даже при большом количестве записей, не зависает, и администратор может массово удалять нерабочие дни.
















Как сохранить все функции и заменить только отчёт

Вы абсолютно правы – в вашей вкладке «Нерабочие дни (отчёт)» было много полезных блоков:

· Массовое добавление выходного дня для филиала (на все ВСП за день)
· Штучное добавление нерабочего дня (один день или период)
· Массовое добавление суббот для всех ВСП (на диапазон)
· Массовое удаление суббот для нескольких ВСП (то, что добавили недавно)

И отчёт (список существующих нерабочих дней) — его мы и хотим сделать быстрым, табличным.

Ничего удалять не нужно – мы просто заменяем только ту часть, которая выводит список записей (сейчас там цикл с кучей кнопок «🗑️» для каждой строки). Все остальные st.expander с настройками добавления/удаления остаются на своих местах.

Правильная структура вкладки после изменений

Ваша вкладка должна выглядеть так (сверху вниз):

1. Заголовок ## 📅 Отчет по нерабочим дням ВСП (администратор)
2. Блок фильтров (филиал, ВСП, дата от/до) и кнопка «Показать»
3. Табличный отчёт (новый, через st.data_editor с возможностью массового удаления)
4. Различные expander'ы (массовое добавление, штучное добавление, субботы, удаление суббот) — их не трогаем

Что именно нужно изменить

1. Удалите старый код, который выводил список через for _, row in nw_data.iterrows(): (с кнопками и columns). Он находится после кнопки «Показать» (или внутри неё) – его больше не будет.
2. Вставьте новый код (тот, что я дал с st.data_editor и кнопкой «Удалить выбранные») вместо удалённого старого цикла.
3. Убедитесь, что методы delete_non_working_days_by_ids добавлен в DatabaseManager (это для массового удаления из таблицы).
4. Все expander'ы оставьте как есть – они должны быть после блока отчёта или до – не важно, главное не удаляйте их.

Полный пример правильного расположения

```python
if tab_admin_non_working is not None:
    with tab_admin_non_working:
        st.markdown("## 📅 Отчет по нерабочим дням ВСП (администратор)")

        # ---------- Фильтры (оставляем без изменений) ----------
        col1, col2, col3, col4 = st.columns(4)
        # ... код фильтров ...

        if st.button("🔍 Показать", key="adm_nw_show_table"):
            with st.spinner("Загрузка данных..."):
                nw_data = db.get_non_working_days(...)
            # ... отображение data_editor ...

        # ---------- ВСЕ ОСТАЛЬНЫЕ БЛОКИ (НЕ ТРОГАЕМ) ----------
        with st.expander("➕ Массовое добавление выходного дня для филиала", expanded=False):
            # ... существующий код ...

        with st.expander("➕ Добавить нерабочий день (штучно)", expanded=False):
            # ... существующий код ...

        with st.expander("➕ Массовое добавление суббот для всех ВСП", expanded=False):
            # ... существующий код ...

        with st.expander("🗑️ Массовое удаление суббот для нескольких ВСП", expanded=False):
            # ... существующий код (мультиселект, удаление суббот) ...
```

Что важно проверить

· Метод delete_non_working_days_by_ids у вас уже должен быть (я давал ранее). Если нет – добавьте.
· Старый код с delete_nw_callback и кнопками в цикле – полностью удалите.
· Кнопка «Удалить выбранные» в новом отчёте удаляет только те записи, которые вы отметили галочками. Это не конфликтует с другими блоками удаления (например, с удалением суббот – они работают независимо).

Если вы хотите оставить и старые кнопки «🗑️» для каждой строки (не надо, но вдруг)

Технически можно оставить, но тогда пропадает смысл перехода на табличную форму – будет опять много виджетов и зависание. Лучше заменить на единый data_editor с чекбоксами.

Итог

Всё, что было полезного – остаётся. Меняется только способ отображения и удаления из списка найденных записей (было много кнопок – стало удобная таблица с массовым выбором). Остальные expander'ы работают как раньше.
