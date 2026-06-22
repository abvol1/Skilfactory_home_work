
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
