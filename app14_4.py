
if st.button("🔍 Показать данные", use_container_width=True):
    # Сбрасываем страницу при новом поиске
    st.session_state.analytics_page = 1
    with st.spinner("Загрузка..."):
        analytics = db.get_admin_analytics(filial_id, vsp_id, date_from, date_to)

    if analytics.empty:
        st.info("Нет данных по выбранным фильтрам")
    else:
        # Сохраняем в кэш для пагинации и сортировки
        st.session_state.analytics_data = analytics
        st.session_state.analytics_total = len(analytics)
        # Сортировка по умолчанию – без изменений
        st.session_state.analytics_sort_order = "Без сортировки"

# Если данные уже есть в кэше (после поиска или удаления)
if "analytics_data" in st.session_state and not st.session_state.analytics_data.empty:
    analytics = st.session_state.analytics_data
    total_sessions = st.session_state.analytics_total
    st.success(f"Найдено сессий: {total_sessions}")

    # Преобразуем статус
    analytics['Статус'] = analytics['Статус'].apply(
        lambda x: 'Черновик' if not x else 'Завершена'
    )

    # ---------- СОРТИРОВКА ПО СТАТУСУ ----------
    sort_options = ["Без сортировки", "Сначала завершённые", "Сначала черновики"]
    current_sort = st.session_state.get("analytics_sort_order", "Без сортировки")
    sort_index = sort_options.index(current_sort) if current_sort in sort_options else 0
    selected_sort = st.selectbox(
        "Сортировка по статусу",
        sort_options,
        index=sort_index,
        key="analytics_sort_select"
    )
    # Если сортировка изменилась, обновляем порядок данных и сбрасываем на первую страницу
    if selected_sort != st.session_state.analytics_sort_order:
        st.session_state.analytics_sort_order = selected_sort
        st.session_state.analytics_page = 1
        # Перестраиваем данные в кэше согласно выбранной сортировке
        if selected_sort == "Сначала завершённые":
            # Сортировка: Завершена < Черновик (алфавитный порядок подходит, т.к. "Завершена" < "Черновик")
            analytics = analytics.sort_values(by="Статус", ascending=True)
        elif selected_sort == "Сначала черновики":
            analytics = analytics.sort_values(by="Статус", ascending=False)
        else:  # Без сортировки – возвращаем исходный порядок из БД
            analytics = st.session_state.analytics_data
        # Обновляем кэш с отсортированными данными
        st.session_state.analytics_data = analytics

    # ---------- ПАГИНАЦИЯ ----------
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

    # Построчный вывод текущей страницы
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
