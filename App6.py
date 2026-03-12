# Импортируем необходимые библиотеки
import streamlit as st  # для создания веб-интерфейса
import pandas as pd  # для работы с табличными данными
import matplotlib.pyplot as plt  # для построения графиков
import plotly.express as px  # для интерактивных графиков
import numpy as np  # для работы с числами

# ===== НАСТРОЙКА СТРАНИЦЫ =====
st.set_page_config(
    page_title="CSV Анализатор",
    page_icon="📊",
    layout="wide"
)

# ===== ЗАГОЛОВОК =====
st.title("Aнализ произвольного CSV-файла")
st.markdown("---")


# ===== ФУНКЦИЯ ДЛЯ ЗАГРУЗКИ ДАННЫХ =====
@st.cache_data
def load_data(file, delimiter=','):
    """Загружает CSV файл с указанным разделителем"""
    try:
        return pd.read_csv(file, delimiter=delimiter)
    except Exception as e:
        st.error(f"Ошибка чтения файла: {e}")
        return None


# ===== БОКОВАЯ ПАНЕЛЬ =====
with st.sidebar:
    st.header("📁 Загрузка данных")

    # Создаем поле для загрузки файла
    uploaded_file = st.file_uploader("Выберите CSV файл", type=['csv'])

    # Инициализируем переменную df в session state, если её нет
    if 'df' not in st.session_state:
        st.session_state.df = None

    # Если пользователь загрузил новый файл
    if uploaded_file is not None:
        # Поле для ввода разделителя
        delimiter = st.text_input("Разделитель", value=",")

        # Кнопка загрузки
        if st.button("Загрузить файл"):
            with st.spinner("Загрузка..."):
                df = load_data(uploaded_file, delimiter)
                if df is not None:
                    st.session_state.df = df
                    st.success(f"✅ Загружено: {len(df)} строк, {len(df.columns)} столбцов")
                else:
                    st.error("❌ Ошибка загрузки файла")

    # Показываем информацию о загруженных данных
    if st.session_state.df is not None:
        st.info(f"Текущий файл: {uploaded_file.name if uploaded_file else 'загружен'}")
        if st.button("Очистить данные"):
            st.session_state.df = None
            st.rerun()

# ===== ОСНОВНАЯ ЧАСТЬ =====
if st.session_state.df is not None:
    df = st.session_state.df

    # ===== ВКЛАДКИ =====
    tab1, tab2, tab3 = st.tabs(["📋 Данные", "📊 Статистика", "📈 Графики"])

    # ===== ВКЛАДКА 1: ПРОСМОТР ДАННЫХ =====
    with tab1:
        st.subheader("Просмотр данных")

        # Ползунок для выбора количества строк
        n_rows = st.slider("Количество строк", min_value=1, max_value=len(df), value=min(10, len(df)))

        # Показываем таблицу
        st.dataframe(df.head(n_rows), use_container_width=True)

        # Показываем основную информацию о данных
        with st.expander("Информация о данных"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Типы данных:**")
                dtypes_df = pd.DataFrame({
                    'Столбец': df.dtypes.index,
                    'Тип': df.dtypes.values.astype(str)
                })
                st.dataframe(dtypes_df, use_container_width=True)
            with col2:
                st.write("**Пропущенные значения:**")
                missing_df = pd.DataFrame({
                    'Столбец': df.columns,
                    'Пропущено': df.isna().sum().values,
                    'Процент': (df.isna().sum().values / len(df) * 100).round(2)
                })
                missing_df = missing_df[missing_df['Пропущено'] > 0]
                if len(missing_df) > 0:
                    st.dataframe(missing_df, use_container_width=True)
                else:
                    st.write("Пропущенных значений нет")

    # ===== ВКЛАДКА 2: СТАТИСТИКА =====
    with tab2:
        st.subheader("Статистический анализ")

        # Выбираем только числовые столбцы
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if numeric_cols:
            # Выпадающий список для выбора столбца
            selected_col = st.selectbox("Выберите столбец для анализа", numeric_cols)

            if selected_col:
                # Получаем данные столбца (убираем NaN)
                col_data = df[selected_col].dropna()

                if len(col_data) > 0:
                    # Создаем 3 колонки для метрик
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Среднее", f"{col_data.mean():.2f}")

                    with col2:
                        st.metric("Медиана", f"{col_data.median():.2f}")

                    with col3:
                        st.metric("Ст. отклонение", f"{col_data.std():.2f}")

                    # Дополнительные метрики
                    col4, col5, col6 = st.columns(3)
                    with col4:
                        st.metric("Минимум", f"{col_data.min():.2f}")
                    with col5:
                        st.metric("Максимум", f"{col_data.max():.2f}")
                    with col6:
                        st.metric("Количество", len(col_data))

                    # Гистограмма
                    st.subheader("Гистограмма распределения")
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.hist(col_data, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
                    ax.set_xlabel(selected_col)
                    ax.set_ylabel('Частота')
                    ax.set_title(f'Распределение: {selected_col}')
                    ax.grid(True, alpha=0.3)
                    st.pyplot(fig)
                    plt.close()  # Закрываем фигуру для освобождения памяти
                else:
                    st.warning(f"В столбце {selected_col} нет данных")
        else:
            st.warning("В файле нет числовых столбцов для статистического анализа")

    # ===== ВКЛАДКА 3: ГРАФИКИ =====
    with tab3:
        st.subheader("Построение графиков")

        # Получаем списки столбцов по типам
        all_cols = df.columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if len(all_cols) >= 1:
            # Выбор типа графика
            chart_type = st.selectbox(
                "Тип графика",
                ["Линейный", "Точечный (рассеяние)", "Столбчатый", "Круговая"]
            )

            # Выбор столбцов в зависимости от типа графика
            if chart_type == "Круговая":
                # Для круговой диаграммы нужен один столбец
                pie_col = st.selectbox("Выберите столбец", all_cols)

                if pie_col:
                    # Считаем частоты значений
                    value_counts = df[pie_col].value_counts().reset_index()
                    value_counts.columns = [pie_col, 'count']

                    # Берем топ-10 для читаемости
                    if len(value_counts) > 10:
                        value_counts = value_counts.head(10)
                        st.info("Показаны топ-10 значений")

                    # Строим круговую диаграмму
                    fig = px.pie(value_counts, values='count', names=pie_col,
                                 title=f'Распределение: {pie_col}')
                    st.plotly_chart(fig, use_container_width=True)

            else:
                # Для остальных графиков нужны две оси
                col1, col2 = st.columns(2)

                with col1:
                    x_col = st.selectbox("Ось X", all_cols, key="x_col")

                with col2:
                    if chart_type in ["Линейный", "Точечный (рассеяние)"]:
                        # Для этих графиков Y должен быть числовым
                        if numeric_cols:
                            y_col = st.selectbox("Ось Y", numeric_cols, key="y_col")
                        else:
                            st.error("Для этого графика нужны числовые данные по оси Y")
                            y_col = None
                    else:  # Столбчатый
                        # Для столбчатого Y может быть любым
                        y_options = all_cols if all_cols else []
                        y_col = st.selectbox("Ось Y", y_options, key="y_col")

                # Строим график если выбраны обе оси
                if x_col and y_col and y_col is not None:
                    # Убираем строки с пропущенными значениями
                    plot_df = df[[x_col, y_col]].dropna()

                    if len(plot_df) > 0:
                        if chart_type == "Линейный":
                            fig = px.line(plot_df, x=x_col, y=y_col,
                                          title=f"{y_col} от {x_col}")
                            st.plotly_chart(fig, use_container_width=True)

                        elif chart_type == "Точечный (рассеяние)":
                            fig = px.scatter(plot_df, x=x_col, y=y_col,
                                             title=f"{x_col} vs {y_col}")
                            st.plotly_chart(fig, use_container_width=True)

                        elif chart_type == "Столбчатый":
                            if y_col in numeric_cols:
                                # Если Y числовой - группируем и считаем среднее
                                grouped = plot_df.groupby(x_col)[y_col].mean().reset_index()
                                # Сортируем по убыванию для лучшей читаемости
                                grouped = grouped.sort_values(y_col, ascending=False).head(20)
                                fig = px.bar(grouped, x=x_col, y=y_col,
                                             title=f"Средний {y_col} по {x_col}")
                            else:
                                # Если Y не числовой - считаем количество
                                counts = plot_df.groupby(x_col).size().reset_index(name='count')
                                counts = counts.sort_values('count', ascending=False).head(20)
                                fig = px.bar(counts, x=x_col, y='count',
                                             title=f"Количество по {x_col}")

                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Нет данных для построения графика")
        else:
            st.warning("В файле нет столбцов для построения графиков")

else:
    # Если файл не загружен
    st.info("👈 Загрузите CSV файл в боковой панели и нажмите 'Загрузить файл'")

    # Показываем пример
    with st.expander("📋 Посмотреть пример формата CSV"):
        example_data = {
            'Дата': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
            'Продажи': [100, 150, 130, 200, 180],
            'Категория': ['A', 'B', 'A', 'C', 'B'],
            'Регион': ['Москва', 'СПб', 'Москва', 'Казань', 'СПб']
        }
        example_df = pd.DataFrame(example_data)
        st.dataframe(example_df, use_container_width=True)
        st.caption("CSV формат: значения разделены запятыми, первая строка - заголовки")