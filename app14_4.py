
if tab_admin_non_working is not None:
    with tab_admin_non_working:
        st.markdown("## 📅 Отчет по нерабочим дням ВСП (администратор)")

        # ----------------------------------------------------------------
        # СНАЧАЛА ОБРАБАТЫВАЕМ НАЖАТИЯ КНОПОК УДАЛЕНИЯ (если они были)
        # ----------------------------------------------------------------
        # Просматриваем все возможные ключи вида "del_nw_<id>" в session_state
        keys_to_delete = [k for k in st.session_state.keys() if k.startswith("del_nw_")]
        for key in keys_to_delete:
            if st.session_state[key]:   # если кнопка была нажата
                record_id = int(key.split("_")[-1])   # извлекаем id
                db.admin_delete_non_working_day(record_id)
                st.success(f"✅ Запись с ID {record_id} удалена")
                # Удаляем флаг, чтобы не зациклиться
                del st.session_state[key]
                time.sleep(0.5)
                st.rerun()   # перезагружаем страницу, список обновится

        # --- ФИЛЬТРЫ ---
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filials_df = db.get_filials()
            if not filials_df.empty:
                filial_opts = ["Все"] + filials_df['name'].tolist()
                sel_fil = st.selectbox("Филиал", filial_opts, key="adm_nw_filial")
                filial_id_filter = None if sel_fil == "Все" else int(
                    filials_df[filials_df['name'] == sel_fil]['id'].iloc[0]
                )
            else:
                filial_id_filter = None
        with col2:
            vsp_df = (
                db.get_vsp_by_filial(filial_id_filter)
                if filial_id_filter is not None
                else db.get_all_vsp()
            )
            if not vsp_df.empty:
                vsp_opts = ["Все"] + vsp_df['name'].tolist()
                sel_vsp = st.selectbox("ВСП", vsp_opts, key="adm_nw_vsp")
                vsp_id_filter = None if sel_vsp == "Все" else int(
                    vsp_df[vsp_df['name'] == sel_vsp]['id'].iloc[0]
                )
            else:
                vsp_id_filter = None
        with col3:
            date_from_nw = st.date_input("Дата от", value=None, key="adm_nw_date_from")
        with col4:
            date_to_nw = st.date_input("Дата до", value=None, key="adm_nw_date_to")

        # --- ПОКАЗ ДАННЫХ ПО КНОПКЕ "Показать" ---
        if st.button("🔍 Показать", key="adm_nw_show"):
            nw_data = db.get_non_working_days(
                filial_id=filial_id_filter,
                vsp_id=vsp_id_filter,
                date_from=date_from_nw,
                date_to=date_to_nw
            )
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

                    # Кнопка удаления: запоминает факт нажатия в session_state
                    btn_key = f"del_nw_{int(row['id'])}"
                    if btn_key not in st.session_state:
                        st.session_state[btn_key] = False

                    if c5.button("🗑️", key=f"btn_{btn_key}"):
                        st.session_state[btn_key] = True
                        st.rerun()   # немедленный перезапуск, чтобы удаление сработало в начале скрипта

                st.markdown("---")

        st.divider()

        # --- МАССОВОЕ ДОБАВЛЕНИЕ ---
        with st.expander("⚙️ Массовое добавление выходного дня для филиала", expanded=False):
            st.markdown("Добавить нерабочий день сразу для **всех ВСП** выбранного филиала.")
            filials_df_mass = db.get_filials()
            if not filials_df_mass.empty:
                mass_filial_name = st.selectbox(
                    "🏢 Филиал",
                    filials_df_mass['name'].tolist(),
                    key="mass_nw_filial"
                )
                mass_filial_id = int(
                    filials_df_mass[filials_df_mass['name'] == mass_filial_name]['id'].iloc[0]
                )
                mass_date = st.date_input("📅 Дата выходного", key="mass_nw_date")
                mass_reason = st.selectbox("📌 Причина", NON_WORKING_REASONS, key="mass_nw_reason")

                if st.button("✅ Добавить выходной для всех ВСП филиала", type="primary"):
                    vsp_list = db.get_vsp_by_filial(mass_filial_id)
                    if vsp_list.empty:
                        st.warning("В филиале нет ВСП.")
                    else:
                        added = 0
                        skipped = 0
                        for _, v in vsp_list.iterrows():
                            vid = int(v['id'])
                            if db.non_working_day_exists(vid, mass_date):
                                skipped += 1
                            else:
                                db.add_non_working_day(
                                    "admin", mass_filial_id, vid, mass_date, mass_reason
                                )
                                added += 1
                        msg = f"✅ Добавлено: {added} ВСП"
                        if skipped:
                            msg += f" | ⚠️ Пропущено (уже есть запись): {skipped} ВСП"
                        st.success(msg)
            else:
                st.warning("Нет филиалов в базе.")
