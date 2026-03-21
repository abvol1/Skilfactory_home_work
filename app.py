# Импорт необходимых библиотек
import streamlit as st  # Для создания веб-интерфейса
import sqlite3  # Для работы с SQLite базой данных
import polars as pl  # Для быстрой обработки данных (альтернатива pandas)
import pandas as pd  # Для некоторых операций с данными
import plotly.express as px  # Для создания интерактивных графиков
import plotly.graph_objects as go  # Для более сложных графиков
from datetime import date, datetime, timedelta  # Для работы с датами
import numpy as np  # Для математических операций
import os  # Для работы с файловой системой

# Путь к файлу базы данных
#DB_PATH = "weather.db"


def find_database():
    """Ищет базу данных в возможных местах"""
    possible_paths = [
        # Для запуска в контейнере Airflow
        "/opt/airflow/project/data/weather.db",
        # Для запуска в отдельном контейнере Streamlit с volume
        "/app/data/weather.db",
        # Для локального запуска
        "data/weather.db",
        "./data/weather.db",
        "weather.db",
        # Относительно текущей директории
        os.path.join(os.path.dirname(__file__), "data", "weather.db"),
        os.path.join(os.path.dirname(__file__), "weather.db"),
        # На уровень выше
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "weather.db"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


st.set_page_config(page_title="WeatherInsight", layout="wide")
st.title("🌦️ WeatherInsight: Погодные тренды")

# Находим базу данных
DB_PATH = find_database()

if DB_PATH is None:
    st.error("❌ База данных не найдена!")
    st.info(f"Текущая директория: {os.getcwd()}")
    st.info("Поиск выполнялся в следующих путях:")
    possible_paths = [
        "/opt/airflow/project/data/weather.db",
        "/app/data/weather.db",
        "data/weather.db",
        "./data/weather.db",
        "weather.db",
    ]
    for path in possible_paths:
        st.code(f"- {path}")
    st.stop()

st.info(f"✅ База данных найдена: {DB_PATH}")


# Загрузка данных
@st.cache_data
def load_data(db_path):
    conn = sqlite3.connect(db_path)
    df = pl.read_database("SELECT * FROM weather ORDER BY date", conn)
    conn.close()
    return df


try:
    df = load_data(DB_PATH)
except Exception as e:
    st.error(f"❌ Не удалось загрузить данные: {e}")
    st.stop()


# Настройка страницы Streamlit
st.set_page_config(
    page_title="WeatherInsight",  # Заголовок вкладки браузера
    layout="wide"  # Широкий формат страницы
)

# Заголовок приложения
st.title("🌦️ WeatherInsight: Погодные тренды")

# ===== ПРОВЕРКА СУЩЕСТВОВАНИЯ ФАЙЛА БАЗЫ ДАННЫХ =====
# Проверяем, существует ли файл weather.db
if not os.path.exists(DB_PATH):
    # Если файл не найден, показываем ошибку
    st.error(f"❌ Файл базы данных не найден по пути: {DB_PATH}")
    # Показываем текущую директорию для отладки
    st.info(f"Текущая директория: {os.getcwd()}")
    # Подсказка пользователю
    st.info("Убедитесь, что файл 'weather.db' находится в той же папке, что и скрипт")
    # Останавливаем выполнение программы
    st.stop()


# ===== ФУНКЦИЯ ДЛЯ ЗАГРУЗКИ ДАННЫХ =====
# @st.cache_data - кэширует результат, чтобы при повторных запусках не загружать данные заново
@st.cache_data
def load_data():
    """Загружает данные из SQLite базы данных"""
    # Подключаемся к базе данных
    conn = sqlite3.connect(DB_PATH)
    # Читаем все данные из таблицы weather, сортируем по дате
    # pl.read_database - читает SQL запрос напрямую в polars DataFrame
    df = pl.read_database("SELECT * FROM weather ORDER BY date", conn)
    # Закрываем соединение с базой данных
    conn.close()
    # Возвращаем загруженные данные
    return df


# ===== ЗАГРУЗКА И ПРЕОБРАЗОВАНИЕ ДАННЫХ =====
try:
    # Пытаемся загрузить данные
    df = load_data()

    # ПРЕОБРАЗОВАНИЕ ДАТЫ
    # Преобразуем строку с временем в дату
    # with_columns - добавляет или изменяет столбцы в polars DataFrame
    df = df.with_columns(
        # str.strptime - преобразует строку в datetime по указанному формату
        # format="%Y-%m-%d %H:%M:%S" - формат "ГГГГ-ММ-ДД ЧЧ:ММ:СС"
        # cast(pl.Date) - преобразует datetime в просто дату (без времени)
        pl.col("date").str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S").cast(pl.Date)
    )

except Exception as e:
    # Если произошла ошибка при загрузке, показываем сообщение
    st.error(f"❌ Ошибка при загрузке данных: {str(e)}")
    st.info("Пробуем альтернативный способ преобразования дат...")

    try:
        # Альтернативный способ - загружаем через pandas
        conn = sqlite3.connect(DB_PATH)
        # pd.read_sql_query - читает SQL запрос в pandas DataFrame
        pandas_df = pd.read_sql_query("SELECT * FROM weather ORDER BY date", conn)
        conn.close()

        # Преобразуем дату с помощью pandas
        # pd.to_datetime - преобразует в datetime, .dt.date - оставляет только дату
        pandas_df['date'] = pd.to_datetime(pandas_df['date']).dt.date

        # Конвертируем pandas DataFrame в polars DataFrame
        df = pl.from_pandas(pandas_df)
    except Exception as e2:
        # Если и этот способ не сработал, показываем ошибку и останавливаем программу
        st.error(f"❌ И альтернативный способ не сработал: {str(e2)}")
        st.stop()


# ===== СОЗДАНИЕ ПРОИЗВОДНЫХ СТОЛБЦОВ =====
@st.cache_data
def create_derived_columns(df):
    """Создает новые вычисляемые столбцы на основе имеющихся данных"""

    # 1. Категория температуры на основе avg_temp
    df = df.with_columns([
        # pl.when(условие).then(значение) - аналог CASE WHEN в SQL
        pl.when(pl.col("avg_temp") < 5)  # Если температура < 5°C
        .then(pl.lit("❄️ Холодно"))  # То "Холодно"
        .when(pl.col("avg_temp") < 15)  # Иначе если < 15°C
        .then(pl.lit("🌡️ Умеренно"))  # То "Умеренно"
        .when(pl.col("avg_temp") < 25)  # Иначе если < 25°C
        .then(pl.lit("☀️ Тепло"))  # То "Тепло"
        .otherwise(pl.lit("🔥 Жарко"))  # Иначе "Жарко"
        .alias("temp_category")  # Название нового столбца
    ])

    # 2. Уровень осадков на основе total_precip
    df = df.with_columns([
        pl.when(pl.col("total_precip") == 0)  # Если осадков нет
        .then(pl.lit("☀️ Без осадков"))  # То "Без осадков"
        .when(pl.col("total_precip") < 5)  # Иначе если < 5 мм
        .then(pl.lit("💧 Небольшие"))  # То "Небольшие"
        .otherwise(pl.lit("🌧️ Сильные"))  # Иначе "Сильные"
        .alias("precip_category")  # Название нового столбца
    ])

    # 3. Комфортность погоды на основе температуры, ветра и осадков
    df = df.with_columns([
        pl.when(
            (pl.col("avg_temp").is_between(18, 25)) &  # Температура 18-25°C
            (pl.col("avg_wind") < 5) &  # Ветер < 5 м/с
            (pl.col("total_precip") == 0)  # Без осадков
        )
        .then(pl.lit("🌟🌟 Идеально"))  # Идеальные условия
        .when(
            (pl.col("avg_temp").is_between(10, 28)) &  # Температура 10-28°C
            (pl.col("avg_wind") < 8) &  # Ветер < 8 м/с
            (pl.col("total_precip") < 2)  # Осадки < 2 мм
        )
        .then(pl.lit("👍 Комфортно"))  # Комфортные условия
        .when(
            (pl.col("avg_temp") < 0) |  # Температура < 0°C ИЛИ
            (pl.col("avg_temp") > 35) |  # > 35°C ИЛИ
            (pl.col("avg_wind") > 15) |  # Ветер > 15 м/с ИЛИ
            (pl.col("total_precip") > 10)  # Осадки > 10 мм
        )
        .then(pl.lit("⚠️ Сложные условия"))  # Сложные условия
        .otherwise(pl.lit("👌 Приемлемо"))  # Во всех остальных случаях
        .alias("comfort_level")  # Название нового столбца
    ])

    return df


# Применяем создание новых столбцов к нашим данным
df = create_derived_columns(df)

# ===== ПОЛУЧАЕМ БАЗОВУЮ ИНФОРМАЦИЮ ДЛЯ ФИЛЬТРОВ =====
# Список всех городов (уникальные значения, сортированные)
cities = sorted(df["city"].unique().to_list())
# Минимальная и максимальная дата в данных
min_date = df["date"].min()
max_date = df["date"].max()

# ===== БОКОВАЯ ПАНЕЛЬ С ФИЛЬТРАМИ =====
# Все, что внутри with st.sidebar, отображается на боковой панели
with st.sidebar:
    # Заголовок боковой панели
    st.header("🔍 Фильтры")
    # Показываем доступный период данных
    st.write(f"📅 Период данных: {min_date} - {max_date}")

    # Выбор городов (мультивыбор - можно выбрать несколько)
    selected_cities = st.multiselect(
        "Выберите города",  # Подпись поля
        cities,  # Доступные варианты
        default=[cities[0]] if cities else []  # По умолчанию первый город
    )

    # Календарь для выбора диапазона дат
    st.subheader("📅 Диапазон дат")

    # Создаем две колонки для полей "От" и "До"
    col1, col2 = st.columns(2)

    with col1:  # Первая колонка - дата "От"
        start_date = st.date_input(
            "От",  # Подпись
            min_date,  # Значение по умолчанию
            min_value=min_date,  # Минимально допустимая дата
            max_value=max_date  # Максимально допустимая дата
        )

    with col2:  # Вторая колонка - дата "До"
        end_date = st.date_input(
            "До",  # Подпись
            max_date,  # Значение по умолчанию
            min_value=min_date,  # Минимально допустимая дата
            max_value=max_date  # Максимально допустимая дата
        )

# ===== ПРИМЕНЕНИЕ ФИЛЬТРОВ =====
# Начинаем с полного набора данных
filtered_df = df

# Фильтр по городам (если выбраны какие-то города)
if selected_cities:
    # .filter() - оставляет только строки, удовлетворяющие условию
    # pl.col("city").is_in(selected_cities) - город должен быть в списке выбранных
    filtered_df = filtered_df.filter(pl.col("city").is_in(selected_cities))

# Фильтр по диапазону дат (если обе даты выбраны)
if start_date and end_date:
    # Оставляем строки, где дата между start_date и end_date включительно
    filtered_df = filtered_df.filter(
        (pl.col("date") >= start_date) &
        (pl.col("date") <= end_date)
    )

# ===== ОСНОВНАЯ СТАТИСТИКА =====
st.subheader("📊 Общая статистика")

# Создаем 4 колонки для метрик
col1, col2, col3, col4 = st.columns(4)

with col1:  # Первая колонка - количество записей
    # len(filtered_df) - количество строк в отфильтрованных данных
    st.metric("Всего записей", len(filtered_df))

with col2:  # Вторая колонка - количество уникальных городов
    # n_unique() - количество уникальных значений в столбце
    st.metric("Уникальных городов", filtered_df["city"].n_unique())

with col3:  # Третья колонка - средняя температура
    # mean() - среднее арифметическое
    st.metric("Средняя температура", f"{filtered_df['avg_temp'].mean():.1f}°C")

with col4:  # Четвертая колонка - количество дождливых дней
    # sum() - сумма значений (1 - дождь, 0 - нет дождя)
    st.metric("Дождливых дней", filtered_df["is_rainy"].sum())

# ===== СОЗДАНИЕ ВКЛАДОК =====
# st.tabs создает набор вкладок для организации контента
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Данные",  # Вкладка с таблицей данных
    "📈 Разведочный анализ",  # Вкладка с графиками распределений
    "🌍 Сравнение городов",  # Вкладка для сравнения городов
    "📅 Временные ряды",  # Вкладка с динамикой во времени
    "📊 Прогнозирование"  # Вкладка с прогнозами
])

# ===== ВКЛАДКА 1: ПРОСМОТР ДАННЫХ =====
with tab1:
    st.subheader("Исходные данные с новыми столбцами")

    # Преобразуем polars DataFrame в pandas для удобной работы с таблицей
    # pandas лучше подходит для отображения и сортировки в Streamlit
    pdf = filtered_df.to_pandas()

    # Выбор столбца для сортировки
    sort_col = st.selectbox(
        "Сортировать по",  # Подпись
        pdf.columns.tolist()  # Все доступные столбцы
    )

    # Выбор направления сортировки
    sort_asc = st.checkbox(
        "По возрастанию",  # Подпись
        value=True  # По умолчанию - по возрастанию
    )

    # Сортируем DataFrame
    pdf_sorted = pdf.sort_values(by=sort_col, ascending=sort_asc)

    # Постраничный просмотр (чтобы не загружать все данные сразу)
    page_size = st.selectbox(
        "Строк на странице",
        [10, 25, 50, 100]  # Варианты количества строк на странице
    )

    # Расчет количества страниц
    total_pages = len(pdf_sorted) // page_size + (1 if len(pdf_sorted) % page_size > 0 else 0)

    if total_pages > 0:
        # Выбор номера страницы
        page_num = st.number_input(
            "Страница",
            min_value=1,
            max_value=total_pages,
            value=1
        )

        # Вычисляем индексы начала и конца текущей страницы
        start_idx = (page_num - 1) * page_size
        end_idx = min(start_idx + page_size, len(pdf_sorted))

        # Отображаем данные текущей страницы
        st.dataframe(
            pdf_sorted.iloc[start_idx:end_idx],  # Срез данных для страницы
            use_container_width=True,  # Растягиваем на всю ширину
            height=400  # Высота таблицы в пикселях
        )

        # Подпись с информацией о текущей странице
        st.caption(f"Показаны записи {start_idx + 1}-{end_idx} из {len(pdf_sorted)}")

# ===== ВКЛАДКА 2: РАЗВЕДОЧНЫЙ АНАЛИЗ =====
with tab2:
    st.subheader("Разведочный анализ данных")

    # Проверяем, есть ли данные после фильтрации
    if not filtered_df.is_empty():
        # Преобразуем в pandas для удобства
        pdf = filtered_df.to_pandas()

        # Выбор признака для анализа
        metric = st.selectbox(
            "Выберите показатель",
            ["avg_temp", "total_precip", "avg_wind"],  # Доступные показатели
            # format_func определяет, как отображать названия в выпадающем списке
            format_func=lambda x: {
                "avg_temp": "Температура",
                "total_precip": "Осадки",
                "avg_wind": "Скорость ветра"
            }[x]
        )

        # Создаем две колонки для графиков
        col1, col2 = st.columns(2)

        with col1:  # Левая колонка - гистограмма
            # px.histogram - создает интерактивную гистограмму
            fig_hist = px.histogram(
                pdf,  # Данные
                x=metric,  # Столбец для оси X
                nbins=30,  # Количество интервалов
                title=f"Гистограмма распределения {metric}",  # Заголовок
                color_discrete_sequence=['skyblue']  # Цвет столбцов
            )
            # Отображаем график в Streamlit
            st.plotly_chart(fig_hist, use_container_width=True)

        with col2:  # Правая колонка - ящик с усами (boxplot)
            # px.box - создает boxplot
            fig_box = px.box(
                pdf,  # Данные
                y=metric,  # Столбец для оси Y
                title=f"Boxplot {metric}",  # Заголовок
                points="all"  # Показывать все точки
            )
            st.plotly_chart(fig_box, use_container_width=True)

        # Анализ по категориям температуры
        st.subheader("Анализ по категориям температуры")

        # Группируем данные по категории температуры и считаем статистику
        category_stats = pdf.groupby('temp_category')[metric].agg(['mean', 'std', 'count']).round(2)
        # Переименовываем столбцы для лучшего отображения
        category_stats.columns = ['Среднее', 'Ст.отклонение', 'Количество']

        # Отображаем таблицу со статистикой
        st.dataframe(category_stats, use_container_width=True)

# ===== ВКЛАДКА 3: СРАВНЕНИЕ ГОРОДОВ =====
with tab3:
    st.subheader("Сравнение погодных показателей между городами")

    # Для сравнения нужно хотя бы 2 города
    if len(selected_cities) > 1:
        # Агрегируем данные по городам (группировка и вычисление статистик)
        city_stats = filtered_df.group_by("city").agg([
            pl.col("avg_temp").mean().alias("Средняя температура"),  # Средняя температура
            pl.col("total_precip").sum().alias("Сумма осадков"),  # Сумма осадков за период
            pl.col("avg_wind").mean().alias("Средний ветер"),  # Средняя скорость ветра
            pl.col("is_rainy").sum().alias("Дождливые дни")  # Количество дождливых дней
        ]).to_pandas()  # Преобразуем в pandas для удобства

        # Выбор метрики для сравнения
        compare_metric = st.selectbox(
            "Метрика для сравнения",
            ["Средняя температура", "Сумма осадков", "Средний ветер", "Дождливые дни"]
        )

        # Столбчатая диаграмма для сравнения городов
        fig_compare = px.bar(
            city_stats,  # Данные
            x="city",  # Ось X - города
            y=compare_metric,  # Ось Y - выбранная метрика
            title=f"Сравнение городов: {compare_metric}",  # Заголовок
            color="city"  # Раскрашиваем по городам
        )
        st.plotly_chart(fig_compare, use_container_width=True)

        # Опционально: линейный график динамики по всем городам
        if st.checkbox("Показать динамику по всем городам"):
            pdf = filtered_df.to_pandas()
            # px.line - линейный график
            fig_lines = px.line(
                pdf,  # Данные
                x="date",  # Ось X - дата
                y="avg_temp",  # Ось Y - температура
                color="city",  # Разные линии для разных городов
                title="Динамика температуры по городам"  # Заголовок
            )
            st.plotly_chart(fig_lines, use_container_width=True)
    else:
        # Если выбран только один город, показываем подсказку
        st.info("👆 Выберите несколько городов в боковой панели для сравнения")

# ===== ВКЛАДКА 4: ВРЕМЕННЫЕ РЯДЫ =====
with tab4:
    st.subheader("Анализ временных рядов")

    # Проверяем, выбран ли хотя бы один город
    if selected_cities:
        # Берем первый выбранный город для анализа
        current_city = selected_cities[0]

        # Фильтруем данные только для этого города
        city_data = filtered_df.filter(pl.col("city") == current_city).to_pandas()

        if not city_data.empty:
            # Сортируем по дате для правильного отображения
            city_data = city_data.sort_values("date")

            # Выбор показателя для отображения
            time_metric = st.selectbox(
                "Показатель",
                ["avg_temp", "total_precip", "avg_wind"],
                key="time_metric",  # Уникальный ключ для виджета
                format_func=lambda x: {
                    "avg_temp": "Температура",
                    "total_precip": "Осадки",
                    "avg_wind": "Ветер"
                }[x]
            )

            # Основной временной ряд
            fig_time = px.line(
                city_data,  # Данные
                x="date",  # Ось X - дата
                y=time_metric,  # Ось Y - выбранный показатель
                title=f"{time_metric} в {current_city}",  # Заголовок
                labels={time_metric: time_metric, "date": "Дата"}  # Подписи осей
            )

            # Добавляем скользящее среднее
            window = st.slider(
                "Окно скользящего среднего (дни)",
                min_value=3,
                max_value=30,
                value=7  # По умолчанию 7 дней
            )

            # rolling(window).mean() - вычисляет скользящее среднее
            city_data[f'ma_{window}'] = city_data[time_metric].rolling(window=window, center=True).mean()

            # Добавляем линию скользящего среднего на график
            fig_time.add_trace(go.Scatter(
                x=city_data['date'],
                y=city_data[f'ma_{window}'],
                mode='lines',
                name=f'Скользящее среднее ({window} дн.)',
                line=dict(color='red', width=2, dash='dash')  # Красная пунктирная линия
            ))

            # Отображаем график
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.warning(f"Нет данных для города {current_city}")
    else:
        st.info("👆 Выберите город в боковой панели")

# ===== ВКЛАДКА 5: ПРОГНОЗИРОВАНИЕ =====
with tab5:
    st.subheader("Простой прогноз на основе скользящего среднего")

    # Проверяем, выбран ли город
    if selected_cities:
        # Берем первый выбранный город
        current_city = selected_cities[0]

        # Получаем данные для города
        city_data = filtered_df.filter(pl.col("city") == current_city).to_pandas()

        # Для прогноза нужно минимум 7 записей
        if not city_data.empty and len(city_data) > 7:
            city_data = city_data.sort_values("date")

            # Разделяем данные на исторические (прошлые) и будущие (прогнозные)
            today = date.today()
            # Создаем колонку с объектами даты для сравнения
            city_data['date_obj'] = pd.to_datetime(city_data['date']).dt.date
            # Исторические данные - дата <= сегодня
            historical = city_data[city_data['date_obj'] <= today].copy()
            # Будущие данные - дата > сегодня
            future = city_data[city_data['date_obj'] > today].copy()

            if len(historical) > 0:
                # Выбор показателя для прогноза
                metric_for_pred = st.selectbox(
                    "Показатель для прогноза",
                    ["avg_temp", "total_precip", "avg_wind"],
                    format_func=lambda x: {
                        "avg_temp": "Температура",
                        "total_precip": "Осадки",
                        "avg_wind": "Скорость ветра"
                    }[x]
                )

                # Размер окна для скользящего среднего
                window_pred = st.slider(
                    "Окно для прогноза",
                    min_value=3,
                    max_value=14,
                    value=7
                )

                # Вычисляем скользящее среднее
                historical[f'ma_pred'] = historical[metric_for_pred].rolling(window=window_pred).mean()

                # Создаем график
                fig_pred = go.Figure()

                # 1. Исторические данные (синяя линия)
                fig_pred.add_trace(go.Scatter(
                    x=historical['date'],
                    y=historical[metric_for_pred],
                    mode='lines',
                    name='Исторические данные',
                    line=dict(color='blue')
                ))

                # 2. Скользящее среднее (оранжевая линия)
                fig_pred.add_trace(go.Scatter(
                    x=historical['date'],
                    y=historical['ma_pred'],
                    mode='lines',
                    name=f'Скользящее среднее ({window_pred} дн.)',
                    line=dict(color='orange', width=2)
                ))

                # 3. Прогноз (красная пунктирная линия)
                if len(future) > 0:
                    # Последнее значение скользящего среднего используем как прогноз
                    last_ma = historical['ma_pred'].iloc[-1]
                    future_dates = future['date'].tolist()

                    fig_pred.add_trace(go.Scatter(
                        x=future_dates,
                        y=[last_ma] * len(future_dates),  # Одинаковое значение для всех будущих дат
                        mode='lines+markers',
                        name='Прогноз',
                        line=dict(color='red', dash='dash'),
                        marker=dict(size=8)
                    ))

                # Настройка внешнего вида графика
                fig_pred.update_layout(
                    title=f"Прогноз {metric_for_pred} - {current_city}",
                    xaxis_title="Дата",
                    yaxis_title=metric_for_pred
                )

                # Отображаем график
                st.plotly_chart(fig_pred, use_container_width=True)

                # Пояснение к прогнозу
                st.info("""
                **Как работает прогноз:**
                - Используется простое скользящее среднее за выбранный период
                - Последнее значение скользящего среднего экстраполируется на будущие даты
                - Это очень простой метод, для реального прогноза нужны более сложные модели
                """)
            else:
                st.warning("Нет исторических данных для прогнозирования")
        else:
            st.warning("Недостаточно данных для прогнозирования (нужно минимум 7 записей)")
    else:
        st.info("👆 Выберите город в боковой панели")

# ===== АНОМАЛИИ =====
st.subheader("⚠️ Аномалии")

# Проверяем, есть ли данные
if not filtered_df.is_empty():
    # Поиск аномалий: дождливые дни с экстремальными условиями
    anomalies = filtered_df.filter(
        (pl.col("is_rainy") == 1) &  # Дождливый день
        (
                (pl.col("avg_temp") > 30) |  # И температура > 30°C ИЛИ
                (pl.col("avg_wind") > 12) |  # Ветер > 12 м/с ИЛИ
                (pl.col("total_precip") > 20)  # Осадки > 20 мм
        )
    )

    if not anomalies.is_empty():
        # Если аномалии найдены
        st.write(f"Найдено {len(anomalies)} аномальных дней (дождь при экстремальных условиях)")

        # Визуализация аномалий - точечная диаграмма
        anomalies_pd = anomalies.to_pandas()
        fig_anom = px.scatter(
            anomalies_pd,  # Данные
            x="date",  # Ось X - дата
            y="avg_temp",  # Ось Y - температура
            size="total_precip",  # Размер точек зависит от количества осадков
            color="city",  # Цвет точек зависит от города
            hover_data=["avg_wind"],  # Дополнительные данные при наведении
            title="Аномальные погодные явления"  # Заголовок
        )
        st.plotly_chart(fig_anom, use_container_width=True)

        # Таблица с аномалиями (в сворачиваемом блоке)
        with st.expander("Показать таблицу аномалий"):
            st.dataframe(anomalies_pd, use_container_width=True)
    else:
        # Если аномалий нет
        st.info("✅ Аномалии не обнаружены за выбранный период")

