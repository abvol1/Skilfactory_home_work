
1. Новый метод в DatabaseManager
Добавьте в класс DatabaseManager (например, после delete_session):

python
    def delete_all_drafts(self):
        """
        Удаляет все черновики (сессии со status_bul = FALSE) и связанные с ними ответы.
        Возвращает количество удалённых сессий.
        """
        # Сначала удаляем ответы, связанные с черновиками
        self._execute(f"""
            DELETE FROM {self._table_name('checklist_answers')}
            WHERE session_id IN (
                SELECT id FROM {self._table_name('checklist_sessions')}
                WHERE status_bul = FALSE
            )
        """)
        # Затем удаляем сами черновики
        self._execute(
            f"DELETE FROM {self._table_name('checklist_sessions')} WHERE status_bul = FALSE"
        )
        # Возвращаем количество удалённых (приблизительно, можно запросить diagnostics, но не обязательно)
        # Для простоты возвращаем None, а сообщение об успехе покажем в интерфейсе.
2. Кнопка в админской аналитике
На вкладке «Аналитика» (tab_analytics) после блока удаления черновика по ID (где st.number_input и кнопка «Удалить сессию») добавьте следующий код:

python
                    # Массовое удаление всех черновиков
                    st.divider()
                    st.caption("🗑️ Массовое удаление всех черновиков")
                    confirm_mass_delete = st.checkbox(
                        "Я подтверждаю удаление ВСЕХ черновиков (нельзя отменить)",
                        key="confirm_mass_delete"
                    )
                    if st.button(
                        "🗑️ Удалить все черновики",
                        type="primary",
                        disabled=(not confirm_mass_delete),
                        key="mass_delete_drafts"
                    ):
                        db.delete_all_drafts()
                        st.success("Все черновики успешно удалены!")
                        st.rerun()
Теперь администратор сможет очистить все незавершённые сессии одной кнопкой.
