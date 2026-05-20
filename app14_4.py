if tab_analytics is not None:
    with tab_analytics:
        st.markdown("## 📊 Детальная аналитика по проверкам")

        # ---------- Callback для удаления черновика ----------
        def delete_draft_callback(session_id: int):
            session_data = db.get_session_data(session_id)
            if session_data and not session_data['info']['status_bul']:
                db.delete_session(session_id)
                st.session_state["draft_deleted"] = True
                st.session_state["deleted_draft_id"] = session_id
                st.session_state.analytics_page = 1
            else:
                st.session_state["draft_delete_error"] = True
                st.session_state["error_draft_id"] = session_id

        if st.session_state.get("draft_deleted"):
            st.success(f"✅ Черновик сессии #{st.session_state['deleted_draft_id']} удалён")
            del st.session_state["draft_deleted"]
            del st.session_state["deleted_draft_id"]
            # После удаления данные нужно обновить, сбросим кэш фильтров
            st.session_state["analytics_filters_changed"] = True
            time.sleep(0.8)
            st.rerun()

        if st.session_state.get("draft_delete_error"):
            st.error(f"❌ Сессия #{st.session_state['error_draft_id']} не является черновиком или не найдена")
            del st.session_state["draft_delete_error"]
            del st.session_state["error_draft_id"]

        # ---------- Фильтры ----------
        filials_df = db.get_filials()
        if not filials_df.empty:
            # Инициализация состояния фильтров
            if "analytics_filial" not in st.session_state:
                st.session_state.analytics_filial = "Все"
                st.session_state.analytics_vsp = "Все"
                st.session_state.analytics_date_from = None
                st.session_state.analytics_date_to = None
                st.session_state.analytics_filters_changed = True

            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                filial_opts = ["Все"] + filials_df['name'].tolist()
                sel_filial_name = st.selectbox("Филиал", filial_opts, key="analytics_filial")
            with col_f2:
                # Определим ID филиала для загрузки списка ВСП
                if sel_filial_name != "Все":
                    filial_id_for_vsp = int(filials_df[filials_df['name'] == sel_filial_name]['id'].iloc[0])
                    vsp_df = db.get_vsp_by_filial(filial_id_for_vsp)
                else:
                    vsp_df = db.get_all_vsp()
                vsp_opts = ["Все"] + vsp_df['name'].tolist() if not vsp_df.empty else ["Все"]
                sel_vsp_name = st.selectbox("ВСП", vsp_opts, key="analytics_vsp")
            with col_f3:
                date_from = st.date_input("Дата от", value=st.session_state.analytics_date_from, key="analytics_date_from")
            with col_f4:
                date_to = st.date_input("Дата до", value=st.session_state.analytics_date_to, key="analytics_date_to")

            # Проверяем, изменились ли фильтры по сравнению с прошлым запуском
            current_filters = (sel_filial_name, sel_vsp_name, date_from, date_to)
            last_filters = st.session_state.get("last_analytics_filters", None)
            if current_filters != last_filters:
                st.session_state.analytics_filters_changed = True
                st.session_state.last_analytics_filters = current_filters

            # Автоматическая загрузка данных, если фильтры изменились или данных ещё нет
            if st.session_state.analytics_filters_changed or "analytics_data" not in st.session_state:
                # Загрузка данных
                filial_id = None if sel_filial_name == "Все" else int(
                    filials_df[filials_df['name'] == sel_filial_name]['id'].iloc[0]
                )
                vsp_id = None if sel_vsp_name == "Все" else int(
                    vsp_df[vsp_df['name'] == sel_vsp_name]['id'].iloc[0]
                )
                with st.spinner("Загрузка данных..."):
                    analytics = db.get_admin_analytics(filial_id, vsp_id, date_from, date_to)
                st.session_state.analytics_data = analytics
                st.session_state.analytics_total = len(analytics)
                st.session_state.analytics_sort_order = "Без сортировки"
                st.session_state.analytics_page = 1
                st.session_state.analytics_filters_changed = False

        # ---------- Отображение данных ----------
        if "analytics_data" in st.session_state and not st.session_state.analytics_data.empty:
            analytics = st.session_state.analytics_data.copy()
            total_sessions = st.session_state.analytics_total
            st.success(f"Найдено сессий: {total_sessions}")

            # Преобразуем статус
            analytics['Статус'] = analytics['Статус'].apply(
                lambda x: 'Черновик' if not x else 'Завершена'
            )

            # ---------- Сортировка ----------
            sort_options = ["Без сортировки", "Сначала завершённые", "Сначала черновики"]
            current_sort = st.session_state.get("analytics_sort_order", "Без сортировки")
            sort_index = sort_options.index(current_sort) if current_sort in sort_options else 0
            selected_sort = st.selectbox(
                "Сортировка по статусу",
                sort_options,
                index=sort_index,
                key="analytics_sort_select"
            )
            if selected_sort != st.session_state.analytics_sort_order:
                st.session_state.analytics_sort_order = selected_sort
                st.session_state.analytics_page = 1
                # Применяем сортировку к кэшированным данным
                if selected_sort == "Сначала завершённые":
                    analytics = analytics.sort_values(by="Статус", ascending=True)
                elif selected_sort == "Сначала черновики":
                    analytics = analytics.sort_values(by="Статус", ascending=False)
                # обновляем кэш
                st.session_state.analytics_data = analytics
            else:
                # Если сортировка не менялась, но данные из кэша, используем их
                pass  # analytics уже скопирован

            # ---------- Пагинация ----------
            items_per_page = 20
            total_pages = max(1, (total_sessions + items_per_page - 1) // items_per_page)
            if "analytics_page" not in st.session_state:
                st.session_state.analytics_page = 1
            if st.session_state.analytics_page > total_pages:
                st.session_state.analytics_page = total_pages

            col_nav1, col_nav2, col_nav3, col_nav4, col_nav5 = st.columns([1, 1, 1.5, 1, 1])
            with col_nav1:
                if st.button("◀️ Назад", disabled=(st.session_state.analytics_page == 1)):
                    st.session_state.analytics_page -= 1
                    st.rerun()
            with col_nav2:
                st.write(f"**{st.session_state.analytics_page}** / {total_pages}")
            with col_nav3:
                new_page = st.selectbox(
                    "Перейти",
                    list(range(1, total_pages + 1)),
                    index=st.session_state.analytics_page - 1,
                    key="analytics_page_select",
                    label_visibility="collapsed"
                )
                if new_page != st.session_state.analytics_page:
                    st.session_state.analytics_page = new_page
                    st.rerun()
            with col_nav4:
                if st.button("Вперед ▶️", disabled=(st.session_state.analytics_page == total_pages)):
                    st.session_state.analytics_page += 1
                    st.rerun()
            with col_nav5:
                start_idx = (st.session_state.analytics_page - 1) * items_per_page
                end_idx = min(start_idx + items_per_page, total_sessions)
                st.write(f"Записи {start_idx+1}–{end_idx} из {total_sessions}")

            page_data = analytics.iloc[start_idx:end_idx]
            st.markdown("---")

            for _, row in page_data.iterrows():
                c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 2, 2, 1])
                c1.write(f"**{row['ФИО']}**")
                c2.write(f"{row['Филиал']}")
                c3.write(f"{row['ВСП']}")
                c4.write(f"{row['Дата']}")
                c5.write(f"{row['Статус']}")
                if row['Статус'] == 'Черновик':
                    c6.button(
                        "🗑️",
                        key=f"del_draft_{row['session_id']}",
                        on_click=delete_draft_callback,
                        args=(row['session_id'],)
                    )
                else:
                    c6.write("")
            st.markdown("---")

            # Детальный просмотр по сессии
            with st.expander("🔍 Детальный просмотр по сессии"):
                session_ids = analytics['session_id'].tolist()
                if session_ids:
                    selected_sid = st.selectbox(
                        "Выберите ID сессии",
                        session_ids,
                        format_func=lambda x: f"Сессия #{x}"
                    )
                    if st.button("Показать детали"):
                        data = db.get_session_data(selected_sid)
                        if data:
                            info = data['info']
                            answers = data['answers']
                            template = db.get_checklist_template()
                            st.markdown(f"**Дата:** {info['operation_date']}")
                            st.markdown(f"**Статус:** {'✔️ Завершена' if info['status_bul'] else '📄 Черновик'}")
                            if info['status_bul'] and info.get('completed_at'):
                                st.markdown(f"**Время завершения:** {info['completed_at']}")
                            st.markdown("**Выполненные проверки:**")
                            for _, tpl in template.iterrows():
                                done = answers.get(tpl['id'], False)
                                st.markdown(f"{'✔️' if done else '❌'} {tpl['description']}")
                        else:
                            st.error("Не удалось загрузить данные")
        elif "analytics_data" in st.session_state and st.session_state.analytics_data.empty:
            st.info("Нет данных по выбранным фильтрам.")
        else:
            # Данные ещё не загружены, показываем подсказку
            st.info("Выберите фильтры – данные загрузятся автоматически.")

        # ---------- Блок удаления ВСЕХ черновиков ----------
        st.divider()
        st.subheader("🗑️ Удаление всех черновиков")
        draft_count = db._execute(
            f"SELECT COUNT(*) AS cnt FROM {db._table_name('checklist_sessions')} WHERE status_bul = FALSE",
            fetch_one=True
        )['cnt']
        st.info(f"Сейчас в базе **{draft_count}** черновиков.")
        confirm_mass_delete = st.checkbox(
            "Я подтверждаю удаление ВСЕХ черновиков (нельзя отменить)",
            key="confirm_mass_delete"
        )
        if st.button("🗑️ Удалить все черновики", type="primary", disabled=(not confirm_mass_delete), key="mass_delete_drafts"):
            db.delete_all_drafts()
            st.session_state.analytics_filters_changed = True  # принудительно обновим данные
            st.success("Все черновики успешно удалены!")
            time.sleep(1)
            st.rerun()
