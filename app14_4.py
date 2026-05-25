if tab_admin_non_working is not None:
    with tab_admin_non_working:
        st.markdown("## 📅 Отчет по нерабочим дням ВСП (администратор)")

        # ---------- Callback для удаления ----------
        def delete_nw_callback(record_id: int):
            db.admin_delete_non_working_day(record_id)
            st.session_state["delete_success"] = True
            st.session_state["deleted_id"] = record_id

        if st.session_state.get("delete_success"):
            st.success(f"✅ Запись с ID {st.session_state['deleted_id']} удалена")
            del st.session_state["delete_success"]
            del st.session_state["deleted_id"]
            time.sleep(0.8)
            st.rerun()

        # ---------- ШТУЧНОЕ ДОБАВЛЕНИЕ (новый блок) ----------
        with st.expander("➕ Добавить нерабочий день (штучно)", expanded=False):
            st.markdown("Добавить нерабочий день для конкретного ВСП (один день или период).")
            filials_df = db.get_filials()
            if not filials_df.empty:
                # Выбор филиала
                filial_opts = filials_df['name'].tolist()
                sel_filial_name = st.selectbox("🏢 Филиал", filial_opts, key="manual_nw_filial")
                filial_id_manual = int(filials_df[filials_df['name'] == sel_filial_name]['id'].iloc[0])

                # Выбор ВСП
                vsp_df = db.get_vsp_by_filial(filial_id_manual)
                if not vsp_df.empty:
                    vsp_opts = vsp_df['name'].tolist()
                    sel_vsp_name = st.selectbox("🏪 ВСП", vsp_opts, key="manual_nw_vsp")
                    vsp_id_manual = int(vsp_df[vsp_df['name'] == sel_vsp_name]['id'].iloc[0])

                    # Тип добавления
                    add_type = st.radio("Тип добавления", ["Один день", "Период"], key="manual_nw_type")
                    if add_type == "Один день":
                        manual_date = st.date_input("📅 Дата", value=datetime.date.today(), key="manual_nw_date")
                        date_start = date_end = manual_date
                    else:
                        col1, col2 = st.columns(2)
                        with col1:
                            date_start = st.date_input("📅 Дата начала", value=datetime.date.today(), key="manual_nw_start")
                        with col2:
                            date_end = st.date_input("📅 Дата окончания", value=datetime.date.today(), key="manual_nw_end")
                        if date_start > date_end:
                            st.error("Дата начала не может быть позже даты окончания")
                            date_start = date_end  # чтобы избежать ошибки, но кнопку показываем

                    manual_reason = st.selectbox("📌 Причина", NON_WORKING_REASONS, key="manual_nw_reason")

                    if st.button("✅ Добавить", type="primary", key="manual_nw_btn"):
                        if date_start > date_end:
                            st.error("Исправьте диапазон дат")
                        else:
                            added = 0
                            skipped = 0
                            from datetime import timedelta
                            current_date = date_start
                            while current_date <= date_end:
                                if db.non_working_day_exists(vsp_id_manual, current_date):
                                    skipped += 1
                                else:
                                    db.add_non_working_day("admin", filial_id_manual, vsp_id_manual, current_date, manual_reason)
                                    added += 1
                                current_date += timedelta(days=1)
                            msg = f"✅ Добавлено дней: {added}"
                            if skipped:
                                msg += f" | ⚠️ Пропущено (уже были): {skipped}"
                            st.success(msg)
                else:
                    st.warning("В этом филиале нет ВСП.")
            else:
                st.warning("Нет филиалов в базе.")

        # ---------- Фильтры и просмотр ----------
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filials_df = db.get_filials()
            if not filials_df.empty:
                filial_opts = ["Все"] + filials_df['name'].tolist()
                sel_fil = st.selectbox("Филиал", filial_opts, key="adm_nw_filial")
                filial_id_filter = None if sel_fil == "Все" else int(filials_df[filials_df['name'] == sel_fil]['id'].iloc[0])
            else:
                filial_id_filter = None
        with col2:
            vsp_df = db.get_vsp_by_filial(filial_id_filter) if filial_id_filter is not None else db.get_all_vsp()
            if not vsp_df.empty:
                vsp_opts = ["Все"] + vsp_df['name'].tolist()
                sel_vsp = st.selectbox("ВСП", vsp_opts, key="adm_nw_vsp")
                vsp_id_filter = None if sel_vsp == "Все" else int(vsp_df[vsp_df['name'] == sel_vsp]['id'].iloc[0])
            else:
                vsp_id_filter = None
        with col3:
            date_from_nw = st.date_input("Дата от", value=None, key="adm_nw_date_from")
        with col4:
            date_to_nw = st.date_input("Дата до", value=None, key="adm_nw_date_to")

        if st.button("🔍 Показать", key="adm_nw_show"):
            nw_data = db.get_non_working_days(filial_id=filial_id_filter, vsp_id=vsp_id_filter, date_from=date_from_nw, date_to=date_to_nw)
            if nw_data.empty:
                st.info("Нет данных по выбранным фильтрам.")
            else:
                st.success(f"Найдено записей: {len(nw_data)}")
                st.markdown("---")
                for _, row in nw_data.iterrows():
                    c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 3, 1])
                    c1.write(f"🏢 {row['filial']}")
                    c2.write(f"🏪 {row['vsp']}")
                    c3.write(f"📅 {row['date']}")
                    c4.write(f"📌 {row['reason']}")
                    c5.button("🗑️", key=f"del_nw_{row['id']}", on_click=delete_nw_callback, args=(int(row['id']),))
                st.markdown("---")

        st.divider()

        # ---------- Массовое добавление ----------
        with st.expander("⚙️ Массовое добавление выходного дня для филиала", expanded=False):
            st.markdown("Добавить нерабочий день сразу для **всех ВСП** выбранного филиала.")
            filials_df_mass = db.get_filials()
            if not filials_df_mass.empty:
                mass_filial_name = st.selectbox("🏢 Филиал", filials_df_mass['name'].tolist(), key="mass_nw_filial")
                mass_filial_id = int(filials_df_mass[filials_df_mass['name'] == mass_filial_name]['id'].iloc[0])
                mass_date = st.date_input("📅 Дата выходного", key="mass_nw_date")
                mass_reason = st.selectbox("📌 Причина", NON_WORKING_REASONS, key="mass_nw_reason")
                if st.button("✅ Добавить выходной для всех ВСП филиала", type="primary"):
                    vsp_list = db.get_vsp_by_filial(mass_filial_id)
                    if vsp_list.empty:
                        st.warning("В филиале нет ВСП.")
                    else:
                        added, skipped = 0, 0
                        for _, v in vsp_list.iterrows():
                            vid = int(v['id'])
                            if db.non_working_day_exists(vid, mass_date):
                                skipped += 1
                            else:
                                db.add_non_working_day("admin", mass_filial_id, vid, mass_date, mass_reason)
                                added += 1
                        msg = f"✅ Добавлено: {added} ВСП"
                        if skipped:
                            msg += f" | ⚠️ Пропущено (уже есть запись): {skipped} ВСП"
                        st.success(msg)
            else:
                st.warning("Нет филиалов в базе.")
