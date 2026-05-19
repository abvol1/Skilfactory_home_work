if tab_analytics is not None:
    with tab_analytics:
        st.markdown("## 📊 Детальная аналитика по проверкам")

        # ---------- Обработка удаления черновика (если была нажата кнопка) ----------
        if st.session_state.get("delete_draft_id") is not None:
            draft_id = st.session_state["delete_draft_id"]
            # Проверяем, что это действительно черновик
            session_data = db.get_session_data(draft_id)
            if session_data and not session_data['info']['status_bul']:
                db.delete_session(draft_id)
                st.success(f"✅ Черновик сессии #{draft_id} удалён")
            else:
                st.error(f"❌ Сессия #{draft_id} не является черновиком или не найдена")
            # Очищаем флаг и перезагружаем
            st.session_state["delete_draft_id"] = None
            time.sleep(0.8)
            st.rerun()

        # ---------- Фильтры ----------
        filials_df = db.get_filials()
        if not filials_df.empty:
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                filial_opts = ["Все"] + filials_df['name'].tolist()
                sel_filial_name = st.selectbox("Филиал", filial_opts, key="adm_filial")
                filial_id = None if sel_filial_name == "Все" else int(
                    filials_df[filials_df['name'] == sel_filial_name]['id'].iloc[0]
                )
            with col_f2:
                vsp_df = db.get_vsp_by_filial(filial_id) if filial_id is not None else db.get_all_vsp()
                vsp_opts = ["Все"] + vsp_df['name'].tolist() if not vsp_df.empty else ["Все"]
                sel_vsp_name = st.selectbox("ВСП", vsp_opts, key="adm_vsp")
                vsp_id = None if sel_vsp_name == "Все" else int(
                    vsp_df[vsp_df['name'] == sel_vsp_name]['id'].iloc[0]
                )
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
                    st.success(f"Найдено сессий: {len(analytics)}")

                    # Преобразуем статус в читаемый вид
                    analytics['Статус'] = analytics['Статус'].apply(
                        lambda x: 'Черновик' if not x else 'Завершена'
                    )

                    # Для каждой строки выводим информацию и кнопку удаления (только для черновиков)
                    st.markdown("---")
                    for idx, row in analytics.iterrows():
                        c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 2, 2, 2, 1])
                        c1.write(f"**{row['ФИО']}**")
                        c2.write(f"{row['Филиал']}")
                        c3.write(f"{row['ВСП']}")
                        c4.write(f"{row['Дата']}")
                        c5.write(f"{row['Статус']}")

                        if row['Статус'] == 'Черновик':
                            # Кнопка удаления – вызывает колбэк, который устанавливает delete_draft_id
                            if c6.button("🗑️", key=f"del_draft_{row['session_id']}"):
                                st.session_state["delete_draft_id"] = row['session_id']
                                st.rerun()
                        else:
                            c6.write("")  # пустое место для завершённых

                    st.markdown("---")

                    # Также оставим возможность просмотра детализации по отдельной сессии
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
        else:
            st.warning("Нет филиалов в базе данных")

        # ---------- Блок удаления ВСЕХ черновиков (оставляем без изменений) ----------
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
            st.success("Все черновики успешно удалены!")
            time.sleep(1)
            st.rerun()
