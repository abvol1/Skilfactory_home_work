"""
Главный файл приложения Streamlit.
Содержит интерфейс для обычного пользователя (5 чекбоксов с увеличенной областью клика)
и вызывает админ-панель, если пользователь администратор.
Реализовано:
- Увеличенные чекбоксы через CSS
- Всплывающие инструкции (st.popover)
- Автоматический сброс чекбоксов после 12:00 нового дня
- Отображение прогресса и поздравление при 5/5
"""

import streamlit as st
from auth import authenticate, logout
from db.database import (
    set_checkbox_state,
    get_instruction,
    get_all_checkbox_states,
    init_db
)

# Инициализация базы данных (создание таблиц, если их нет)
init_db()

# Настройка страницы (широкий режим, иконка, заголовок)
st.set_page_config(
    page_title="Система отметок - 5 чекбоксов",
    page_icon="✅",
    layout="wide"
)

# ---------- Кастомный CSS для увеличения чекбоксов и красивого вида ----------
st.markdown("""
<style>
/* Увеличиваем размер чекбокса и область клика */
.stCheckbox {
    transform: scale(1.3);
    margin: 10px 0;
}
.stCheckbox > label {
    padding: 12px 0 12px 40px !important;
    font-size: 16px !important;
    cursor: pointer !important;
    width: 100% !important;
}
.stCheckbox > label > div {
    transform: scale(1.2);
    margin-right: 15px !important;
}
/* Стили для бейджей статуса */
.success-badge {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    padding: 8px 15px;
    border-radius: 20px;
    color: white;
    font-weight: bold;
    text-align: center;
}
.warning-badge {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    padding: 8px 15px;
    border-radius: 20px;
    color: white;
    font-weight: bold;
    text-align: center;
}
/* Увеличиваем кнопки */
.stButton > button {
    font-size: 16px !important;
    padding: 8px 20px !important;
}
/* Увеличиваем всплывающие окна инструкций */
div[data-testid="stPopover"] > div {
    min-width: 500px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- Аутентификация ----------
if not authenticate():
    st.stop()  # Если не авторизован, останавливаем выполнение

# ---------- Боковая панель (отображается всегда) ----------
with st.sidebar:
    # Отображаем информацию о пользователе
    st.markdown(f"""
    <div style='text-align: center; padding: 10px;'>
        <h3>👤 {st.session_state.username}</h3>
        <p>🏭 Филиал: {st.session_state.branch}</p>
        <p style='color: {"orange" if st.session_state.role == "admin" else "green"}'>
            🎫 {st.session_state.role.upper()}
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # Получаем текущие состояния чекбоксов (с учётом возможного сброса)
    states = get_all_checkbox_states(st.session_state.user_id)
    checked_count = sum(states.values())

    # Красивый индикатор прогресса в боковой панели
    if checked_count == 5:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                    padding: 15px; border-radius: 10px; text-align: center;'>
            <h2 style='color: white; margin: 0;'>🎉 ПОЛНОСТЬЮ ГОТОВО!</h2>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 15px; border-radius: 10px; text-align: center;'>
            <h3 style='color: white; margin: 0;'>{checked_count}/5</h3>
        </div>
        """, unsafe_allow_html=True)

    st.metric("Отмечено чекбоксов", f"{checked_count}/5")
    st.divider()

    # Кнопка выхода
    if st.button("🚪 Выйти", use_container_width=True):
        logout()

# ---------- Основная логика: админ или пользователь ----------
if st.session_state.role == "admin":
    # Если админ – показываем админ-панель
    from admin_panel import show_admin_panel
    show_admin_panel()
else:
    # ---------- Интерфейс обычного пользователя ----------
    st.title("📋 Мои соглашения")
    st.markdown("Отметьте чекбоксы, с которыми вы согласны. Нажмите **Инструкция** для подробностей.")

    # Получаем актуальные состояния (с учётом возможного сброса)
    states = get_all_checkbox_states(st.session_state.user_id)

    # Данные о 5 чекбоксах (ID, эмодзи, название, описание)
    checkboxes_info = [
        {"id": 1, "emoji": "📋", "title": "Условия использования", "description": "Правила использования сервиса"},
        {"id": 2, "emoji": "🔒", "title": "Конфиденциальность", "description": "Политика обработки данных"},
        {"id": 3, "emoji": "📢", "title": "Уведомления", "description": "Получение информационных сообщений"},
        {"id": 4, "emoji": "📊", "title": "Аналитика", "description": "Сбор анонимной статистики"},
        {"id": 5, "emoji": "🤝", "title": "Партнерские программы", "description": "Участие в партнерских программах"}
    ]

    # Перебираем все 5 чекбоксов и отображаем каждый в отдельной карточке
    for cb in checkboxes_info:
        checkbox_id = cb["id"]
        current_state = states[checkbox_id]

        # Цвет фона и левой границы в зависимости от статуса
        bg_color = "#e8f5e9" if current_state else "#fff3e0"
        border_color = "#4caf50" if current_state else "#ff9800"

        # Контейнер с фоновым цветом
        with st.container():
            st.markdown(f"""
            <div style='background: {bg_color}; 
                        padding: 15px; 
                        border-radius: 10px; 
                        border-left: 5px solid {border_color};
                        margin: 10px 0;'>
            </div>
            """, unsafe_allow_html=True)

            # Разбиваем на 4 колонки: название, чекбокс, статус, инструкция
            col1, col2, col3, col4 = st.columns([2.5, 2.5, 1.5, 1.5])

            with col1:
                # Название чекбокса с эмодзи и галочкой, если отмечен
                st.markdown(f"### {cb['emoji']} {cb['title']}" + (" ✅" if current_state else ""))
                st.caption(cb['description'])

            with col2:
                # Увеличенный чекбокс (за счёт CSS)
                new_state = st.checkbox(
                    "Согласен/Согласна",
                    value=current_state,
                    key=f"cb_{checkbox_id}_{st.session_state.user_id}",
                    label_visibility="visible"
                )
                # Если состояние изменилось – сохраняем в БД и перезагружаем страницу
                if new_state != current_state:
                    set_checkbox_state(
                        st.session_state.user_id,
                        checkbox_id,
                        new_state,
                        st.session_state.user_id
                    )
                    st.toast(f"{'✅ Отмечен' if new_state else '❌ Снят'} «{cb['title']}»",
                             icon="✅" if new_state else "❌")
                    st.rerun()

            with col3:
                # Бейдж статуса
                if current_state:
                    st.markdown('<div class="success-badge">✅ Отмечено</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="warning-badge">⭕ Не отмечено</div>', unsafe_allow_html=True)

            with col4:
                # Кнопка "Инструкция" – открывает popover с текстом
                instr = get_instruction(checkbox_id)
                with st.popover(f"📖 Инструкция", use_container_width=True):
                    st.markdown(f"### {instr['title']}")
                    st.markdown("---")
                    st.markdown(instr['text'])
                    st.info("Нажмите вне этого окна, чтобы закрыть")

        st.divider()  # Разделитель между чекбоксами

    # ---------- Прогресс-бар и поздравление ----------
    st.subheader("📊 Общий прогресс")
    progress = checked_count / 5
    st.progress(progress, text=f"Выполнено {checked_count} из 5")

    if checked_count == 5:
        st.balloons()
        st.success("🎉 Поздравляем! Вы приняли все условия!")
        st.markdown("""
        <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                    padding: 20px; 
                    border-radius: 10px; 
                    text-align: center;
                    margin-top: 20px;'>
            <h2 style='color: white; margin: 0;'>🎉 ПОЗДРАВЛЯЕМ! 🎉</h2>
            <p style='color: white; margin: 10px 0 0 0;'>Вы успешно приняли все условия</p>
        </div>
        """, unsafe_allow_html=True)

    # Дополнительная справка (можно раскрыть)
    with st.expander("ℹ️ Как это работает"):
        st.markdown("""
        **Правила работы:**
        - Чекбоксы меняются **сразу** при клике.
        - **Инструкция** открывается по кнопке и не влияет на состояние чекбокса.
        - **Сброс чекбоксов** происходит автоматически при смене дня **после 12:00**.
        - Если вы зайдёте утром следующего дня, чекбоксы останутся отмеченными до полудня.
        - Все ваши действия (отметка/снятие/сброс) записываются в логи и видны администратору.
        """)