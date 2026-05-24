
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
            # Принудительно преобразуем id в int (для всей колонки)
            sessions['id'] = sessions['id'].astype(int)
            # Получаем общее количество проверок как нативный int
            total_checks = int(sessions["Всего проверок"].iloc[0])

            st.dataframe(
                sessions,
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
                        max_value=total_checks,  # явный int
                        format="%d/%d"
                    ),
                    "Дата и время начала": st.column_config.DatetimeColumn("Начало"),
                    "Дата и время завершения": st.column_config.DatetimeColumn("Завершение"),
                    "Всего проверок": None  # скрываем
                },
                hide_index=True
            )

            st.divider()
            st.subheader("🔍 Детальный просмотр")

            # Строим словарь описаний заранее, избегая numpy в format_func
            session_descriptions = {}
            for _, row in sessions.iterrows():
                sid = int(row['id'])
                emp = str(row['Сотрудник'])
                date_val = row['Дата проверки']
                if hasattr(date_val, 'strftime'):
                    date_str = date_val.strftime('%Y-%m-%d')
                else:
                    date_str = str(date_val)
                session_descriptions[sid] = f"Сессия #{sid} ({emp}, {date_str})"

            session_ids = list(session_descriptions.keys())
            selected_sid = st.selectbox(
                "Выберите ID сессии",
                session_ids,
                format_func=lambda x: session_descriptions[x]
            )

            if st.button("📋 Показать результаты", key="user_analytics_view"):
                data = db.get_session_data(selected_sid)
                if data:
                    info = data['info']
                    with st.expander(f"Результаты проверки #{selected_sid}", expanded=True):
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
            # Принудительно преобразуем id в int (на всякий случай)
            sessions['id'] = sessions['id'].astype(int)

            st.dataframe(
                sessions,
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
                        max_value=sessions["Всего проверок"].iloc[0] if not sessions.empty else 1,
                        format="%d/%d"
                    ),
                    "Дата и время начала": st.column_config.DatetimeColumn("Начало"),
                    "Дата и время завершения": st.column_config.DatetimeColumn("Завершение"),
                    "Всего проверок": None
                },
                hide_index=True
            )

            st.divider()
            st.subheader("🔍 Детальный просмотр")
            
            # Строим словарь описаний заранее, избегая numpy-типов в format_func
            session_descriptions = {}
            for _, row in sessions.iterrows():
                sid = int(row['id'])
                emp = row['Сотрудник']
                # Безопасно получаем дату как строку
                date_val = row['Дата проверки']
                if hasattr(date_val, 'strftime'):
                    date_str = date_val.strftime('%Y-%m-%d')
                else:
                    date_str = str(date_val)
                session_descriptions[sid] = f"Сессия #{sid} ({emp}, {date_str})"
            
            session_ids = list(session_descriptions.keys())
            selected_sid = st.selectbox(
                "Выберите ID сессии",
                session_ids,
                format_func=lambda x: session_descriptions[x]
            )

            if st.button("📋 Показать результаты", key="user_analytics_view"):
                data = db.get_session_data(selected_sid)
                if data:
                    info = data['info']
                    with st.expander(f"Результаты проверки #{selected_sid}", expanded=True):
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








st.subheader("🔍 Детальный просмотр")
# Явно преобразуем id в стандартный int
session_ids = [int(x) for x in sessions['id']]
# Для format_func тоже используем int
selected_sid = st.selectbox(
    "Выберите ID сессии",
    session_ids,
    format_func=lambda x: f"Сессия #{int(x)} ({sessions.loc[sessions['id'] == int(x), 'Сотрудник'].iloc[0]}, {sessions.loc[sessions['id'] == int(x), 'Дата проверки'].iloc[0]})"
)
Добавим отдельную вкладку «📊 Аналитика по филиалу» для обычного пользователя.
Она показывает все проверки его филиала (черновики и завершённые) с возможностью просмотра деталей любой сессии. Удаление чужих черновиков недоступно, а свои можно удалить в штатной «Истории проверок».

Что нужно изменить в коде

1. В списке вкладок добавить новую

Найдите место, где формируется tab_titles для пользователя:

```python
if st.session_state.auth_valid:
    tab_titles.append("📅 Нерабочие дни ВСП")
    tab_titles.append("📊 Визуализация")
```

Замените на:

```python
if st.session_state.auth_valid:
    tab_titles.append("📅 Нерабочие дни ВСП")
    tab_titles.append("📊 Аналитика по филиалу")
    tab_titles.append("📊 Визуализация")
```

2. После создания вкладок tab_non_working и tab_visualization_user нужно создать новую переменную

Найдите блок:

```python
if st.session_state.auth_valid:
    tab_non_working = tabs[idx]; idx += 1
    tab_visualization_user = tabs[idx]; idx += 1
```

Замените на:

```python
if st.session_state.auth_valid:
    tab_non_working = tabs[idx]; idx += 1
    tab_user_analytics = tabs[idx]; idx += 1
    tab_visualization_user = tabs[idx]; idx += 1
```

3. Инициализируйте tab_user_analytics как None для неавторизованного

До этого же блока (где else: tab_non_working = ...) дополните:

```python
else:
    tab_non_working = tab_user_analytics = tab_visualization_user = None
```

4. Добавьте саму вкладку

После блока tab_non_working (пользовательские нерабочие дни) и перед tab_visualization_user вставьте:

```python
# --- АНАЛИТИКА ПО ФИЛИАЛУ (пользователь) ---
if tab_user_analytics is not None:
    with tab_user_analytics:
        st.markdown("## 📊 Аналитика проверок вашего филиала")
        if st.session_state.get("last_filial_id") is None:
            # Попробуем определить филиал
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

        # Загружаем все сессии филиала (используем метод, добавленный ранее)
        sessions = db.get_filial_sessions(current_filial_id)
        if sessions.empty:
            st.info("В вашем филиале пока нет проверок.")
        else:
            st.success(f"Всего проверок: {len(sessions)}")
            # Показываем таблицу (без пагинации, так как объём небольшой)
            st.dataframe(
                sessions,
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
                        max_value=sessions["Всего проверок"].iloc[0] if not sessions.empty else 1,
                        format="%d/%d"
                    ),
                    "Дата и время начала": st.column_config.DatetimeColumn("Начало"),
                    "Дата и время завершения": st.column_config.DatetimeColumn("Завершение"),
                    "Всего проверок": None
                },
                hide_index=True
            )

            st.divider()
            st.subheader("🔍 Детальный просмотр")
            selected_sid = st.selectbox(
                "Выберите ID сессии",
                sessions['id'].tolist(),
                format_func=lambda x: f"Сессия #{x} ({sessions[sessions['id']==x]['Сотрудник'].iloc[0]}, {sessions[sessions['id']==x]['Дата проверки'].iloc[0]})"
            )
            if st.button("📋 Показать результаты", key="user_analytics_view"):
                data = db.get_session_data(selected_sid)
                if data:
                    info = data['info']
                    with st.expander(f"Результаты проверки #{selected_sid}", expanded=True):
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
```

Важное дополнение

Убедитесь, что метод get_filial_sessions уже присутствует в классе DatabaseManager (мы добавили его ранее). Если нет – добавьте:

```python
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
```

Итог

Теперь у пользователя появилась отдельная вкладка «Аналитика по филиалу», где он видит все проверки своего филиала, может отсортировать таблицу по столбцам и просмотреть детали любой сессии. История своих проверок и возможность удалять собственные черновики остаются в прежней вкладке «История проверок».
