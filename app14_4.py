
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Hello World</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            text-align: center;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h2>Hello World!</h2>
    <button onclick="onSayHello()">Сказать привет</button>

    <script>
        // ====== ГЛАВНОЕ: сообщаем Р7, что плагин готов ======
        window.Asc.plugin.init = function() {
            console.log("Плагин загружен!");
            // Отправляем сигнал о готовности — спинер исчезнет!
            window.Asc.plugin.onReady();
        };

        // ====== Функция для кнопки ======
        function onSayHello() {
            // Показываем уведомление в интерфейсе Р7
            window.Asc.plugin.infoMessage("Привет из плагина!");
            // Или можно использовать обычный alert:
            // alert("Привет, мир из Р7-Офис!");
        }
    </script>
</body>
</html>









# ==================== ВАРИАНТ С МУЛЬТИСЕЛЕКТОМ (ТОЛЬКО СВОЕ ВСП) ====================
st.divider()
st.markdown("### 🗑️ Управление черновиками")

# Получаем все черновики
all_drafts = sessions_filtered[sessions_filtered["Статус"] == "Черновик"].copy()

if not all_drafts.empty:
    # === ОГРАНИЧЕНИЕ: ТОЛЬКО ЧЕРНОВИКИ СВОЕГО ВСП ===
    # Получаем ВСП пользователя из сессии
    user_vsp = st.session_state.last_vsp_name
    
    # Фильтруем черновики только по ВСП пользователя
    drafts_by_user_vsp = all_drafts[all_drafts["ВСП"] == user_vsp].copy()
    
    if not drafts_by_user_vsp.empty:
        st.info(f"📋 Найдено черновиков по вашему ВСП **'{user_vsp}'**: {len(drafts_by_user_vsp)}")
        
        # Создаем список для мультиселекта
        options = []
        for _, row in drafts_by_user_vsp.iterrows():
            label = f"ID {row['id']} | {row['Сотрудник']} | {row['Дата проверки']} | {row['Выполнено проверок']}/{row['Всего проверок']}"
            options.append((row['id'], label))
        
        # Мультиселект для выбора черновиков
        selected_ids = st.multiselect(
            "Выберите черновики для удаления:",
            options=[opt[0] for opt in options],
            format_func=lambda x: next((opt[1] for opt in options if opt[0] == x), str(x)),
            key="drafts_multiselect"
        )
        
        if selected_ids:
            st.write(f"Выбрано черновиков: **{len(selected_ids)}**")
            
            # Показываем предупреждение если есть чужие черновики
            selected_drafts = drafts_by_user_vsp[drafts_by_user_vsp['id'].isin(selected_ids)]
            other_users = selected_drafts[selected_drafts['Сотрудник'] != st.session_state.user_full_name]
            
            if not other_users.empty:
                st.warning(f"⚠️ Вы выбрали черновики других сотрудников: {', '.join(other_users['Сотрудник'].unique())}")
            
            # Подтверждение
            confirm = st.checkbox("✅ Подтверждаю удаление выбранных черновиков", key="confirm_multiselect")
            
            if st.button("🗑️ Удалить выбранные черновики", type="primary", disabled=not confirm):
                deleted_count = 0
                for sid in selected_ids:
                    try:
                        db.delete_session(int(sid))
                        deleted_count += 1
                    except Exception as e:
                        st.error(f"Ошибка при удалении сессии {sid}: {e}")
                
                if deleted_count > 0:
                    st.success(f"✅ Удалено черновиков: {deleted_count}")
                    time.sleep(1)
                    st.rerun()
        else:
            st.caption("👆 Выберите черновики из списка выше")
    else:
        st.info(f"✅ У вас нет черновиков по вашему ВСП **'{user_vsp}'**")
else:
    st.info("В вашем филиале нет черновиков для удаления.")
# ==================== КОНЕЦ БЛОКА ====================








# ==================== ВАРИАНТ С МУЛЬТИСЕЛЕКТОМ ====================
st.divider()
st.markdown("### 🗑️ Управление черновиками по ВСП")

# Получаем все черновики
all_drafts = sessions_filtered[sessions_filtered["Статус"] == "Черновик"].copy()

if not all_drafts.empty:
    # Выбор ВСП
    vsp_options = all_drafts["ВСП"].unique().tolist()
    selected_vsp = st.selectbox(
        "Выберите ВСП для управления черновиками",
        options=vsp_options,
        key="delete_drafts_vsp_select"
    )
    
    # Фильтруем черновики по выбранному ВСП
    drafts_by_vsp = all_drafts[all_drafts["ВСП"] == selected_vsp].copy()
    
    if not drafts_by_vsp.empty:
        st.info(f"Найдено черновиков по ВСП '{selected_vsp}': {len(drafts_by_vsp)}")
        
        # Создаем список для мультиселекта
        options = []
        for _, row in drafts_by_vsp.iterrows():
            label = f"ID {row['id']} | {row['Сотрудник']} | {row['Дата проверки']} | {row['Выполнено проверок']}/{row['Всего проверок']}"
            options.append((row['id'], label))
        
        # Мультиселект для выбора черновиков
        selected_ids = st.multiselect(
            "Выберите черновики для удаления:",
            options=[opt[0] for opt in options],
            format_func=lambda x: next((opt[1] for opt in options if opt[0] == x), str(x)),
            key="drafts_multiselect"
        )
        
        if selected_ids:
            st.write(f"Выбрано черновиков: **{len(selected_ids)}**")
            
            # Подтверждение
            confirm = st.checkbox("✅ Подтверждаю удаление выбранных черновиков", key="confirm_multiselect")
            
            if st.button("🗑️ Удалить выбранные черновики", type="primary", disabled=not confirm):
                deleted_count = 0
                for sid in selected_ids:
                    try:
                        db.delete_session(int(sid))
                        deleted_count += 1
                    except Exception as e:
                        st.error(f"Ошибка при удалении сессии {sid}: {e}")
                
                if deleted_count > 0:
                    st.success(f"✅ Удалено черновиков: {deleted_count}")
                    time.sleep(1)
                    st.rerun()
        else:
            st.caption("👆 Выберите черновики из списка выше")
    else:
        st.info(f"Нет черновиков по ВСП '{selected_vsp}'")
else:
    st.info("В вашем филиале нет черновиков для удаления.")
# ==================== КОНЕЦ БЛОКА ====================












# --- АНАЛИТИКА ПО ФИЛИАЛУ (пользователь) ---
if tab_user_analytics is not None:
    with tab_user_analytics:
        st.markdown("## 📊 Аналитика проверок вашего филиала")
        # ... код определения филиала ...

        sessions = db.get_filial_sessions(current_filial_id)
        if sessions.empty:
            st.info("В вашем филиале пока нет проверок.")
        else:
            # Фильтр по дате
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
                sessions_filtered['id'] = sessions_filtered['id'].astype(int)
                total_checks = int(sessions_filtered["Всего проверок"].iloc[0])

                # ==================== ВСТАВИТЬ СЮДА ====================
                # БЛОК УДАЛЕНИЯ ЧЕРНОВИКОВ С ТАБЛИЦЕЙ И СЕЛЕКТБОКСАМИ
                st.divider()
                st.markdown("### 🗑️ Управление черновиками по ВСП")
                
                # Получаем все черновики
                all_drafts = sessions_filtered[sessions_filtered["Статус"] == "Черновик"]
                
                if not all_drafts.empty:
                    # Выбор ВСП
                    vsp_options = all_drafts["ВСП"].unique().tolist()
                    selected_vsp = st.selectbox(
                        "Выберите ВСП для управления черновиками",
                        options=vsp_options,
                        key="delete_drafts_vsp_select"
                    )
                    
                    # Фильтруем черновики по выбранному ВСП
                    drafts_by_vsp = all_drafts[all_drafts["ВСП"] == selected_vsp].copy()
                    
                    if not drafts_by_vsp.empty:
                        st.info(f"Найдено черновиков по ВСП '{selected_vsp}': {len(drafts_by_vsp)}")
                        
                        # Создаем таблицу для редактирования с чекбоксами
                        drafts_by_vsp['Удалить'] = False
                        
                        edited_drafts = st.data_editor(
                            drafts_by_vsp[['id', 'Сотрудник', 'Дата проверки', 'Выполнено проверок', 'Всего проверок', 'Удалить']],
                            column_config={
                                "id": st.column_config.NumberColumn("ID", disabled=True),
                                "Сотрудник": st.column_config.TextColumn("Сотрудник", disabled=True),
                                "Дата проверки": st.column_config.DateColumn("Дата", disabled=True),
                                "Выполнено проверок": st.column_config.NumberColumn("Выполнено", disabled=True),
                                "Всего проверок": st.column_config.NumberColumn("Всего", disabled=True),
                                "Удалить": st.column_config.CheckboxColumn(
                                    "🗑️ Удалить",
                                    help="Отметьте черновики для удаления"
                                )
                            },
                            hide_index=True,
                            use_container_width=True,
                            height=300,
                            key="drafts_editor"
                        )
                        
                        # Кнопка удаления отмеченных
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            if st.button("🗑️ Удалить отмеченные", type="primary", use_container_width=True):
                                ids_to_delete = edited_drafts[edited_drafts['Удалить'] == True]['id'].tolist()
                                if ids_to_delete:
                                    # Подтверждение
                                    st.warning(f"Вы собираетесь удалить {len(ids_to_delete)} черновиков(а)")
                                    confirm = st.checkbox("✅ Подтверждаю удаление", key="confirm_drafts_delete")
                                    if confirm:
                                        for sid in ids_to_delete:
                                            db.delete_session(int(sid))
                                        st.success(f"✅ Удалено черновиков: {len(ids_to_delete)}")
                                        time.sleep(1)
                                        st.rerun()
                                else:
                                    st.warning("Не выбрано ни одного черновика для удаления")
                        
                        with col2:
                            if st.button("🔄 Сбросить выделение", use_container_width=True):
                                st.rerun()
                        
                        with col3:
                            st.caption("💡 Отметьте нужные черновики галочками и нажмите 'Удалить отмеченные'")
                    else:
                        st.info(f"Нет черновиков по ВСП '{selected_vsp}'")
                else:
                    st.info("В вашем филиале нет черновиков для удаления.")
                # ==================== КОНЕЦ ВСТАВКИ ====================

                st.divider()
                st.markdown("### 📋 Список всех проверок")
                
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
                        ),
                        "Дата и время начала": st.column_config.DatetimeColumn("Начало"),
                        "Дата и время завершения": st.column_config.DatetimeColumn("Завершение"),
                        "Всего проверок": None
                    },
                    hide_index=True
                )
