
Извините за неточность! Давайте я покажу точно куда вставить код.

Место для вставки кэширования:

Вставьте этот код сразу после инициализации БД, примерно на строке 238 (после db = DatabaseManager()):

```python
# =============================================================================
# ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ
# =============================================================================
st.markdown("""
<style>
    div[data-testid="stCheckbox"] label span { transform: scale(1.5); margin-right: 12px; }
    div[data-testid="stCheckbox"] label { font-size: 16px; padding: 5px 0; }
</style>
""", unsafe_allow_html=True)

db = DatabaseManager()

# ========== ВОТ СЮДА ВСТАВИТЬ ЭТОТ КОД ==========
@st.cache_data(ttl=300)
def get_cached_filials():
    """Кэшированный список филиалов"""
    return db.get_filials()

@st.cache_data(ttl=300) 
def get_cached_template():
    """Кэшированный шаблон чек-листа"""
    return db.get_checklist_template()

@st.cache_data(ttl=600)
def get_cached_export():
    """Кэшированные данные для экспорта"""
    return db.get_export_data()

@st.cache_data(ttl=300)
def get_cached_vsp_by_filial(filial_id):
    """Кэшированный список ВСП по филиалу"""
    return db.get_vsp_by_filial(filial_id)
# =================================================

# переменные состояния (все как раньше)
if "user_name" not in st.session_state: st.session_state.user_name = ""
# ... остальной код
```

Затем замените прямые вызовы:

1. В sidebar (строка ~355):

Было:

```python
tpl = db.get_checklist_template()
```

Стало:

```python
tpl = get_cached_template()
```

2. В sidebar для экспорта (строка ~370):

Было:

```python
exp_df = db.get_export_data()
```

Стало:

```python
exp_df = get_cached_export()
```

3. Везде где используется db.get_filials():

Было:

```python
filials_df = db.get_filials()
```

Стало:

```python
filials_df = get_cached_filials()
```

4. Для ВСП по филиалу:

Было:

```python
vsp_df = db.get_vsp_by_filial(filial_id)
```

Стало:

```python
vsp_df = get_cached_vsp_by_filial(filial_id)
```

Полный пример с заменой:

```python
# В sidebar (примерно строка 355):
with st.sidebar:
    if st.session_state.step != 1:
        # ... код ...
        
        if st.session_state.admin_authenticated:
            st.divider()
            st.subheader("⚙️ Управление чек-листом")
            
            # ЗАМЕНА ЗДЕСЬ:
            tpl = get_cached_template()  # вместо db.get_checklist_template()
            total_items = len(tpl)
            
            # ... остальной код ...
            
            st.divider()
            st.subheader("📊 Экспорт данных")
            
            # ЗАМЕНА ЗДЕСЬ:
            exp_df = get_cached_export()  # вместо db.get_export_data()
            if not exp_df.empty:
                # ... остальной код ...
```

Важно!

Кэширование сработает так:

· Первый раз - данные загрузятся из БД (будет небольшая задержка)
· Последующие разы в течение 5-10 минут - данные будут браться из кэша (мгновенно)
· Через 5-10 минут - кэш обновится

Это значительно ускорит загрузку, особенно при частых перезагрузках страницы!
