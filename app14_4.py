
def update_user_full_name(self, login, new_full_name):
    """Обновляет full_name пользователя по его логину."""
    self._execute(
        f"UPDATE {self._table_name('users')} SET full_name = %s WHERE LOWER(name) = LOWER(%s)",
        (new_full_name, login)
    )



st.divider()
st.subheader("👤 Редактировать пользователя")
with st.expander("✏️ Изменить ФИО сотрудника", expanded=False):
    user_login = st.text_input("Логин сотрудника", placeholder="rf_ivanov_av", key="edit_user_login")
    # Загружаем текущее ФИО, если логин введён
    current_full_name = ""
    if user_login:
        exists, full, _ = db.check_user_by_name(user_login.strip())
        if exists:
            current_full_name = full
            st.info(f"Текущее ФИО: **{current_full_name}**")
        else:
            st.error("Пользователь не найден")
    
    new_full_name = st.text_input("Новое ФИО", value=current_full_name if current_full_name else "", key="new_full_name")
    
    if st.button("💾 Обновить ФИО", use_container_width=True):
        if not user_login.strip():
            st.error("Введите логин")
        elif not new_full_name.strip():
            st.error("Введите новое ФИО")
        else:
            exists, _, _ = db.check_user_by_name(user_login.strip())
            if not exists:
                st.error("Пользователь не существует")
            else:
                db.update_user_full_name(user_login.strip(), new_full_name.strip())
                st.success(f"ФИО для {user_login} обновлено на «{new_full_name}»!")
                # Очистим поле логина, чтобы избежать повторного обновления
                st.session_state["edit_user_login"] = ""
                time.sleep(1)
                st.rerun()
