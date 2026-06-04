
Извините за путаницу! Вернём как было, но добавим выбор ВСП с чекбоксом.

Мы не трогаем существующую форму авторизации (логин, ФИО, филиал, дата, кнопка).
Изменим только блок выбора ВСП – там, где раньше был st.selectbox или пустота, добавим чекбокс и выпадающий список.

Что нужно сделать по шагам:

1. Убедитесь, что метод check_user_by_name возвращает vsp_name и vsp_id (как я уже давал).

Если ещё не добавили – добавьте, это важно.

2. В коде вкладки «Новая проверка» найдите место, где сейчас отображается выбор ВСП (или где вы его хотите разместить). Обычно это после вывода филиала и перед датой.

В вашем исходном коде (который вы мне показали в первом сообщении) там был такой блок:

```python
vsp_df = db.get_vsp_by_filial(sel_filial_id)
if not vsp_df.empty:
    vsp_names = vsp_df['name'].tolist()
    vsp_map = dict(zip(vsp_df['name'], vsp_df['id']))
    vsp_idx = 0
    if (st.session_state.last_vsp_name and st.session_state.last_vsp_name in vsp_names):
        vsp_idx = vsp_names.index(st.session_state.last_vsp_name)
    elif st.session_state.last_vsp_id is not None:
        for i, (name, vid) in enumerate(vsp_map.items()):
            if vid == st.session_state.last_vsp_id:
                vsp_idx = i; st.session_state.last_vsp_name = name; break
    sel_vsp = st.selectbox("🏪 ВСП", vsp_names, index=vsp_idx, key=f"vsp_{st.session_state.update_counter}")
    sel_vsp_id = vsp_map[sel_vsp]
    st.session_state.last_vsp_name = sel_vsp
    st.session_state.last_vsp_id = sel_vsp_id
    st.session_state.selected_vsp_id = sel_vsp_id
else:
    sel_vsp_id = None
    st.warning("Нет ВСП в выбранном филиале")
```

Этот блок нужно заменить на новый, где появится чекбокс «Использовать моё ВСП» и выпадающий список.

3. Новый блок (полностью заменяет старый):

```python
vsp_df = db.get_vsp_by_filial(sel_filial_id)
if not vsp_df.empty:
    vsp_names = vsp_df['name'].tolist()
    vsp_map = dict(zip(vsp_df['name'], vsp_df['id']))
    
    # Получаем привязанное к пользователю ВСП (если есть)
    default_vsp_name = st.session_state.get('default_vsp_name')
    default_vsp_id = st.session_state.get('default_vsp_id')
    
    # Чекбокс: использовать своё ВСП (по умолчанию True, если есть своё ВСП)
    use_default = st.checkbox("🔒 Использовать моё ВСП", 
                              value=(default_vsp_name is not None and default_vsp_name in vsp_names),
                              key="use_my_vsp")
    
    if use_default and default_vsp_name and default_vsp_name in vsp_names:
        # Автоматически ставим привязанное ВСП
        selected_vsp_name = default_vsp_name
        selected_vsp_id = default_vsp_id
        st.info(f"🏪 Ваше ВСП: **{selected_vsp_name}**")
    else:
        # Выпадающий список со всеми ВСП
        # Индекс по умолчанию – если было предыдущее выбранное ВСП или привязанное
        default_idx = 0
        if 'last_vsp_name' in st.session_state and st.session_state.last_vsp_name in vsp_names:
            default_idx = vsp_names.index(st.session_state.last_vsp_name)
        elif default_vsp_name and default_vsp_name in vsp_names:
            default_idx = vsp_names.index(default_vsp_name)
        selected_vsp_name = st.selectbox("🏪 ВСП", vsp_names, index=default_idx, key="vsp_select")
        selected_vsp_id = vsp_map[selected_vsp_name]
    
    # Сохраняем выбранное ВСП в сессию
    st.session_state.last_vsp_name = selected_vsp_name
    st.session_state.last_vsp_id = selected_vsp_id
    st.session_state.selected_vsp_id = selected_vsp_id
    sel_vsp_id = selected_vsp_id
else:
    sel_vsp_id = None
    st.warning("Нет ВСП в выбранном филиале")
```

4. В блоке авторизации (где вы вводите логин) нужно добавить сохранение default_vsp_name и default_vsp_id.

Найдите строки, где вы вызываете db.check_user_by_name и сохраняете st.session_state.user_full_name и т.д. Дополните:

```python
exists, full, fil, filial_id, default_vsp_name, default_vsp_id = db.check_user_by_name(login_norm)
if exists:
    st.session_state.user_name = login_norm
    st.session_state.user_full_name = full
    st.session_state.auth_valid = True
    st.session_state.default_vsp_name = default_vsp_name   # добавьте
    st.session_state.default_vsp_id = default_vsp_id       # добавьте
    # ... остальное как было
```

5. Ничего больше не трогайте: дата, филиал, кнопка «Начать заполнение» остаются без изменений.

Что получится в итоге:

· Пользователь вводит логин → подтягивается его ФИО, филиал и его родное ВСП.
· Чекбокс «Использовать моё ВСП» включён по умолчанию – отображается его ВСП (только текст, без выбора).
· Если снять чекбокс – появляется выпадающий список со всеми ВСП филиала, и можно выбрать другое.
· Дата и кнопка работают как раньше.

Если после замены кода форма всё равно выглядит не так (нет филиала, даты и т.д.) – значит, вы случайно удалили что-то ещё. Верните обратно ваш старый код и вставьте только этот новый блок вместо старого if not vsp_df.empty. Остальные элементы (например, st.markdown(f"**Филиал:** {st.session_state.last_filial_name}") и st.date_input) должны остаться нетронутыми.

Если нужна более точная помощь – покажите фрагмент вашего текущего кода (строк 750–850), и я скажу, что именно заменить.
