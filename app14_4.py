
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
