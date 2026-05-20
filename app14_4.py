# --- Блок возврата завершённой сессии в черновик ---
st.divider()
st.subheader("🔄 Вернуть завершённую сессию в черновик")

# Получаем все завершённые сессии
completed_df = db._to_df(f"""
    SELECT s.id, s.user_name, f.name filial_name, v.name vsp_name,
           s.operation_date, s.completed_at
    FROM {db.schema}.checklist_sessions s
    JOIN {db.schema}.filials f ON s.filial_id = f.id
    JOIN {db.schema}.vsp v ON s.vsp_id = v.id
    WHERE s.status_bul = TRUE
    ORDER BY s.completed_at DESC
""")

if completed_df.empty:
    st.info("Нет завершённых сессий.")
else:
    st.info(f"Всего завершённых сессий: **{len(completed_df)}**")

    # Формируем список для выбора
    options = []
    for _, row in completed_df.iterrows():
        label = (
            f"ID {row['id']} | {row['user_name']} | "
            f"{row['filial_name']} / {row['vsp_name']} | {row['operation_date']} | "
            f"Завершена {row['completed_at']}"
        )
        options.append((row['id'], label))

    selected_id = st.selectbox(
        "Выберите сессию для возврата в черновик:",
        options=[opt[0] for opt in options],
        format_func=lambda x: next(
            (opt[1] for opt in options if opt[0] == x), str(x)
        ),
        key="completed_select"
    )

    if selected_id and st.button("🔄 Вернуть в черновик", key="revert_to_draft"):
        db.update_session_status(selected_id, False)
        st.success(f"✅ Сессия #{selected_id} теперь черновик.")
        time.sleep(1)
        st.rerun()
