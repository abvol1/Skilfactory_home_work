"""
Модуль аутентификации пользователя.
Использует session_state Streamlit для хранения статуса входа.
Добавлено поле "Номер филиала".
"""

import streamlit as st
from db.database import get_user_by_credentials


def authenticate():
    """
    Проверяет, авторизован ли пользователь.
    Если нет – показывает форму входа (логин, пароль, филиал).
    Возвращает True, если пользователь авторизован, иначе False.
    """
    # Инициализируем переменные session_state, если их ещё нет
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.user_id = None
        st.session_state.role = None
        st.session_state.branch = None

    # Если пользователь ещё не вошёл – показываем форму
    if not st.session_state.authenticated:
        # Немного CSS для красивого центрирования формы
        st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.title("🔐 Авторизация")

            with st.form("login_form"):
                username = st.text_input("👤 Логин")
                password = st.text_input("🔑 Пароль", type="password")
                branch = st.text_input("🏭 Номер филиала")
                submitted = st.form_submit_button("Войти", use_container_width=True)

                if submitted:
                    # Проверяем, что все поля заполнены
                    if not username or not password or not branch:
                        st.error("Заполните все поля")
                    else:
                        user = get_user_by_credentials(username, password, branch)
                        if user:
                            # Сохраняем данные в session_state
                            st.session_state.authenticated = True
                            st.session_state.username = user['username']
                            st.session_state.user_id = user['id']
                            st.session_state.role = user['role']
                            st.session_state.branch = user['branch']
                            st.rerun()   # Перезагружаем страницу, чтобы скрыть форму
                        else:
                            st.error("❌ Неверные данные или филиал")

            st.markdown('</div>', unsafe_allow_html=True)
            st.info("💡 Тестовые пользователи: user1/pass1/1, user2/pass2/2, user3/pass3/3")
            st.info("👑 Админ: admin/admin123/0")
        return False
    return True


def logout():
    """Очищает session_state и выполняет выход из системы."""
    for key in ["authenticated", "username", "user_id", "role", "branch"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()