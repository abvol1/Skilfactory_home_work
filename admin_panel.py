"""
Административная панель.
Доступна только пользователям с ролью 'admin'.
Позволяет:
- Просматривать статусы всех пользователей (с филиалами)
- Редактировать инструкции для каждого чекбокса
- Добавлять новых пользователей
- Просматривать логи действий (включая сбросы по дате)
"""

import streamlit as st
import pandas as pd
from db.database import (
    get_all_users_status,
    update_instruction,
    get_all_logs,
    add_new_user,
    get_instruction
)


def show_admin_panel():
    """Главная функция отображения админ-панели (вызывается из main.py)."""
    st.title("🔧 Административная панель")

    # Создаём вкладки
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Статус пользователей",
        "✏️ Инструкции",
        "➕ Добавить пользователя",
        "📜 Логи"
    ])

    # ---------- Вкладка 1: Статус пользователей ----------
    with tab1:
        st.subheader("Все пользователи и состояние чекбоксов")
        users_data = get_all_users_status()
        if users_data:
            df = pd.DataFrame(users_data)
            # Для красивого отображения заменяем True/False на ✅/❌
            display_df = df.copy()
            for i in range(1, 6):
                display_df[f"checkbox_{i}"] = display_df[f"checkbox_{i}"].map({True: "✅", False: "❌"})
            st.dataframe(
                display_df[["username", "branch", "checkbox_1", "checkbox_2", "checkbox_3", "checkbox_4", "checkbox_5"]],
                use_container_width=True,
                column_config={
                    "username": "Пользователь",
                    "branch": "Филиал",
                    "checkbox_1": "📋",
                    "checkbox_2": "🔒",
                    "checkbox_3": "📢",
                    "checkbox_4": "📊",
                    "checkbox_5": "🤝",
                },
                hide_index=True
            )
        else:
            st.info("Нет обычных пользователей")

    # ---------- Вкладка 2: Редактирование инструкций ----------
    with tab2:
        st.subheader("Редактирование инструкций для чекбоксов")
        checkbox_id = st.selectbox(
            "Выберите чекбокс",
            [1, 2, 3, 4, 5],
            format_func=lambda x: f"Чекбокс {x}"
        )
        current = get_instruction(checkbox_id)
        new_title = st.text_input("Заголовок", value=current['title'])
        new_text = st.text_area("Текст инструкции (поддерживается Markdown)",
                                value=current['text'], height=300)
        if st.button("💾 Сохранить инструкцию"):
            update_instruction(checkbox_id, new_title, new_text, st.session_state.user_id)
            st.success("Инструкция сохранена")
            st.rerun()

    # ---------- Вкладка 3: Добавление пользователя ----------
    with tab3:
        st.subheader("Добавление нового пользователя")
        with st.form("add_user_form"):
            username = st.text_input("Логин")
            password = st.text_input("Пароль", type="password")
            branch = st.text_input("Номер филиала")
            submitted = st.form_submit_button("Создать пользователя")
            if submitted:
                if not username or not password or not branch:
                    st.error("Заполните все поля")
                else:
                    if add_new_user(username, password, branch):
                        st.success(f"Пользователь {username} создан")
                        st.rerun()
                    else:
                        st.error("Пользователь с таким логином уже существует")

    # ---------- Вкладка 4: Логи ----------
    with tab4:
        st.subheader("История действий пользователей")
        limit = st.slider("Количество записей", 10, 500, 100)
        logs = get_all_logs(limit)
        if logs:
            df_logs = pd.DataFrame(logs)
            # Заменяем коды действий на читаемые
            df_logs["action"] = df_logs["action"].map({
                "check": "✅ Отметил",
                "uncheck": "❌ Снял",
                "reset": "🔄 Сброс дня"
            })
            df_logs["timestamp"] = pd.to_datetime(df_logs["timestamp"])
            st.dataframe(
                df_logs[["username", "branch", "checkbox_id", "action", "timestamp", "performer_name"]],
                use_container_width=True,
                column_config={
                    "username": "Пользователь",
                    "branch": "Филиал",
                    "checkbox_id": "Чекбокс",
                    "action": "Действие",
                    "timestamp": "Время",
                    "performer_name": "Кто выполнил"
                },
                hide_index=True
            )
        else:
            st.info("Логов пока нет")