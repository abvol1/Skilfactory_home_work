

<?xml version="1.0" encoding="UTF-8"?>

<?import javafx.scene.control.*?>
<?import javafx.scene.layout.*?>
<?import javafx.geometry.Insets?>

<VBox xmlns="http://javafx.com/javafx/8.0.171" xmlns:fx="http://javafx.com/fxml/1"
      fx:controller="com.example.checklist.controllers.MainController"
      spacing="10" alignment="TOP_CENTER" prefWidth="800" prefHeight="600">

    <!-- Панель логина -->
    <VBox fx:id="loginPanel" spacing="10" alignment="CENTER" VBox.vgrow="ALWAYS">
        <Label text="Авторизация" style="-fx-font-size: 20px; -fx-font-weight: bold;" />
        <HBox spacing="10" alignment="CENTER">
            <Label text="Логин:" />
            <TextField fx:id="loginField" promptText="rf_ivanov_av" />
            <Button text="Войти" onAction="#handleLogin" style="-fx-background-color: #4CAF50; -fx-text-fill: white;" />
        </HBox>
        <Label fx:id="loginErrorLabel" textFill="red" />
    </VBox>

    <!-- Основная панель -->
    <VBox fx:id="mainPanel" spacing="10" alignment="CENTER" VBox.vgrow="ALWAYS"
          visible="false" managed="false">
        <Label fx:id="userInfoLabel" style="-fx-font-size: 14px;" />
        <HBox spacing="20" alignment="CENTER">
            <Label text="ВСП:" />
            <ComboBox fx:id="vspCombo" prefWidth="300" />
            <Label text="Дата:" />
            <DatePicker fx:id="datePicker" />
            <Button text="Показать чек-лист" onAction="#handleShowChecklist"
                    style="-fx-background-color: #2196F3; -fx-text-fill: white; -fx-font-weight: bold;" />
        </HBox>
        <ScrollPane fx:id="checklistScroll" fitToWidth="true" VBox.vgrow="ALWAYS">
            <VBox fx:id="checklistContainer" spacing="5" alignment="TOP_LEFT">
                <padding>
                    <Insets top="10" right="10" bottom="10" left="10"/>
                </padding>
            </VBox>
        </ScrollPane>
    </VBox>
</VBox>



@Override
public void initialize(URL location, ResourceBundle resources) {
    loginPanel.setVisible(true);
    loginPanel.setManaged(true);
    mainPanel.setVisible(false);
    mainPanel.setManaged(false);
}

@FXML
private void handleLogin() {
    String login = loginField.getText().trim();
    if (login.isEmpty()) {
        loginErrorLabel.setText("Введите логин");
        return;
    }
    User user = db.checkUserByLogin(login);
    if (user == null || user.getFilialId() <= 0) {
        loginErrorLabel.setText("Пользователь не найден или отсутствует филиал");
        return;
    }
    currentUser = user;
    // Скрываем панель логина
    loginPanel.setVisible(false);
    loginPanel.setManaged(false);
    // Показываем основную панель
    mainPanel.setManaged(true);
    mainPanel.setVisible(true);
    userInfoLabel.setText("Пользователь: " + user.getFullName() +
            "  |  Филиал: " + user.getFilialName());
    loadVspList();
}
















@Override
public void initialize(URL location, ResourceBundle resources) {
    loginPanel.setVisible(true);
    loginPanel.setManaged(true);
    mainPanel.setVisible(false);
    mainPanel.setManaged(false);
}

@FXML
private void handleLogin() {
    String login = loginField.getText().trim();
    if (login.isEmpty()) {
        loginErrorLabel.setText("Введите логин");
        return;
    }
    User user = db.checkUserByLogin(login);
    if (user == null || user.getFilialId() <= 0) {
        // ... ваша обработка ошибок
        return;
    } else {
        currentUser = user;
        loginPanel.setVisible(false);
        loginPanel.setManaged(false);
        mainPanel.setManaged(true);
        mainPanel.setVisible(true);
        userInfoLabel.setText(...);
        loadVspList();
    }
}






<?xml version="1.0" encoding="UTF-8"?>

<?import javafx.scene.control.*?>
<?import javafx.scene.layout.*?>
<?import javafx.geometry.Insets?>

<VBox xmlns="http://javafx.com/javafx/8.0.171" xmlns:fx="http://javafx.com/fxml/1"
      fx:controller="com.example.checklist.controllers.MainController"
      spacing="10" alignment="TOP_CENTER" prefWidth="800" prefHeight="600">

    <!-- Панель логина -->
    <VBox fx:id="loginPanel" spacing="10" alignment="CENTER" VBox.vgrow="ALWAYS">
        <Label text="Авторизация" style="-fx-font-size: 20px; -fx-font-weight: bold;" />
        <HBox spacing="10" alignment="CENTER">
            <Label text="Логин:" />
            <TextField fx:id="loginField" promptText="rf_ivanov_av" />
            <Button text="Войти" onAction="#handleLogin" style="-fx-background-color: #4CAF50; -fx-text-fill: white;" />
        </HBox>
        <Label fx:id="loginErrorLabel" textFill="red" />
    </VBox>

    <!-- Центрируем основную панель через StackPane -->
    <StackPane VBox.vgrow="ALWAYS">
        <VBox fx:id="mainPanel" spacing="10" alignment="TOP_CENTER"
              visible="false" managed="false">
            <Label fx:id="userInfoLabel" style="-fx-font-size: 14px;" />
            <HBox spacing="20" alignment="CENTER">
                <Label text="ВСП:" />
                <ComboBox fx:id="vspCombo" prefWidth="300" />
                <Label text="Дата:" />
                <DatePicker fx:id="datePicker" />
                <Button text="Показать чек-лист" onAction="#handleShowChecklist"
                        style="-fx-background-color: #2196F3; -fx-text-fill: white; -fx-font-weight: bold;" />
            </HBox>
            <ScrollPane fx:id="checklistScroll" fitToWidth="true" VBox.vgrow="ALWAYS">
                <VBox fx:id="checklistContainer" spacing="5" alignment="TOP_LEFT">
                    <padding>
                        <Insets top="10" right="10" bottom="10" left="10"/>
                    </padding>
                </VBox>
            </ScrollPane>
        </VBox>
    </StackPane>
</VBox>






<?xml version="1.0" encoding="UTF-8"?>

<?import javafx.scene.control.*?>
<?import javafx.scene.layout.*?>
<?import javafx.geometry.Insets?>

<VBox xmlns="http://javafx.com/javafx/8.0.171" xmlns:fx="http://javafx.com/fxml/1"
      fx:controller="com.example.checklist.controllers.MainController"
      spacing="10" alignment="TOP_CENTER" prefWidth="800" prefHeight="600">

    <!-- Панель логина – без изменений -->
    <VBox fx:id="loginPanel" spacing="10" alignment="CENTER" VBox.vgrow="ALWAYS">
        <Label text="Авторизация" style="-fx-font-size: 20px; -fx-font-weight: bold;" />
        <HBox spacing="10" alignment="CENTER">
            <Label text="Логин:" />
            <TextField fx:id="loginField" promptText="rf_ivanov_av" />
            <Button text="Войти" onAction="#handleLogin" style="-fx-background-color: #4CAF50; -fx-text-fill: white;" />
        </HBox>
        <Label fx:id="loginErrorLabel" textFill="red" />
    </VBox>

    <!-- Основная панель, центрированная через StackPane -->
    <StackPane VBox.vgrow="ALWAYS">
        <VBox fx:id="mainPanel" spacing="10" alignment="TOP_CENTER"
              visible="false" managed="false"
              maxWidth="700" maxHeight="550">
            <Label fx:id="userInfoLabel" style="-fx-font-size: 14px;" />
            <HBox spacing="20" alignment="CENTER">
                <Label text="ВСП:" />
                <ComboBox fx:id="vspCombo" prefWidth="300" />
                <Label text="Дата:" />
                <DatePicker fx:id="datePicker" />
                <Button text="Показать чек-лист" onAction="#handleShowChecklist"
                        style="-fx-background-color: #2196F3; -fx-text-fill: white; -fx-font-weight: bold;" />
            </HBox>
            <ScrollPane fx:id="checklistScroll" fitToWidth="true" VBox.vgrow="ALWAYS">
                <VBox fx:id="checklistContainer" spacing="5" alignment="TOP_LEFT">
                    <padding>
                        <Insets top="10" right="10" bottom="10" left="10"/>
                    </padding>
                </VBox>
            </ScrollPane>
        </VBox>
    </StackPane>
</VBox>






<?xml version="1.0" encoding="UTF-8"?>

<?import javafx.scene.control.*?>
<?import javafx.scene.layout.*?>
<?import javafx.geometry.Insets?>

<VBox xmlns="http://javafx.com/javafx/8.0.171" xmlns:fx="http://javafx.com/fxml/1"
      fx:controller="com.example.checklist.controllers.MainController"
      spacing="10" alignment="TOP_CENTER" prefWidth="800" prefHeight="600">

    <!-- Панель логина -->
    <VBox fx:id="loginPanel" spacing="10" alignment="CENTER" VBox.vgrow="ALWAYS">
        <Label text="Авторизация" style="-fx-font-size: 20px; -fx-font-weight: bold;" />
        <HBox spacing="10" alignment="CENTER">
            <Label text="Логин:" />
            <TextField fx:id="loginField" promptText="rf_ivanov_av" />
            <Button text="Войти" onAction="#handleLogin" style="-fx-background-color: #4CAF50; -fx-text-fill: white;" />
        </HBox>
        <Label fx:id="loginErrorLabel" textFill="red" />
    </VBox>

    <!-- Основная панель -->
    <VBox fx:id="mainPanel" spacing="10" alignment="TOP_CENTER" visible="false" managed="false">
        <Label fx:id="userInfoLabel" style="-fx-font-size: 14px;" />
        <!-- Оборачиваем строку выбора в HBox с центрированием и даём ей максимальную ширину, чтобы не растягивалась -->
        <HBox spacing="20" alignment="CENTER">
            <Label text="ВСП:" />
            <ComboBox fx:id="vspCombo" prefWidth="300" />
            <Label text="Дата:" />
            <DatePicker fx:id="datePicker" />
            <Button text="Показать чек-лист" onAction="#handleShowChecklist"
                    style="-fx-background-color: #2196F3; -fx-text-fill: white; -fx-font-weight: bold;" />
        </HBox>
        <!-- ScrollPane тоже должен центрировать содержимое? Обычно чек-лист лучше растягивать, но заголовок мы центрируем в коде -->
        <ScrollPane fx:id="checklistScroll" fitToWidth="true" VBox.vgrow="ALWAYS">
            <VBox fx:id="checklistContainer" spacing="5" alignment="TOP_CENTER">
                <padding>
                    <Insets top="10" right="10" bottom="10" left="10"/>
                </padding>
            </VBox>
        </ScrollPane>
    </VBox>
</VBox>





Конечно! Вот подробная инструкция по запуску вашего Tkinter-приложения в Linux, включая создание аналога .bat — скрипта для быстрого запуска одним кликом.

1. Подготовка системы

Убедитесь, что у вас установлены:

· Python 3 (обычно уже есть)
· pip (менеджер пакетов Python)
· Tkinter (графическая библиотека)
· Драйвер PostgreSQL (psycopg2)
· Сервер PostgreSQL (локальный или удалённый) и настроенная база

Установка недостающих компонентов

Откройте терминал и выполните (для Debian/Ubuntu/Mint):

```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
```

Для Fedora/CentOS/RHEL:
sudo dnf install python3 python3-pip python3-tkinter

Установите драйвер psycopg2:

```bash
pip3 install psycopg2-binary
```

Проверьте работу Tkinter (должно открыться маленькое окошко):

```bash
python3 -m tkinter
```

2. Подготовка базы данных PostgreSQL

Если PostgreSQL ещё не установлен, установите и запустите:

```bash
sudo apt install postgresql postgresql-client
sudo systemctl start postgresql
```

Создайте пользователя, базу и таблицу:

```bash
sudo -u postgres psql
```

Внутри psql выполните:

```sql
CREATE DATABASE testdb;
\c testdb
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100)
);
INSERT INTO users (name, email) VALUES
    ('Иван Иванов', 'ivan@example.com'),
    ('Мария Петрова', 'maria@example.com');
\q
```

Запомните пароль пользователя postgres (или создайте отдельного пользователя). Если вы меняли пароль, используйте его в настройках подключения.

3. Разместите скрипт Python

Сохраните ваш код в удобную папку, например ~/myapp/load_form.py.
Отредактируйте параметры подключения в DB_CONFIG (укажите верные host, user, password). Если база на том же компьютере, хост — localhost.

Примерный код (уже знакомый вам):

# -*- coding: utf-8 -*-
# Подключение необходимых библиотек
import tkinter as tk                      # Библиотека для создания графического интерфейса (GUI)
from tkinter import messagebox            # Модуль для показа диалоговых окон (ошибки, предупреждения, информация)
import psycopg2                           # Драйвер для работы с PostgreSQL из Python

# ------------------------------------------------------------------------------
# Конфигурация подключения к базе данных PostgreSQL
# ------------------------------------------------------------------------------
DB_CONFIG = {
    'host': 'localhost',      # Адрес сервера базы данных (если база на том же компьютере — localhost)
    'port': 5432,             # Стандартный порт PostgreSQL
    'database': 'testdb',     # Имя вашей базы данных
    'user': 'postgres',       # Имя пользователя PostgreSQL
    'password': 'your_password'  # Пароль пользователя (ОБЯЗАТЕЛЬНО замените на реальный!)
}

# ------------------------------------------------------------------------------
# Функция получения данных одного пользователя из БД по его ID
# ------------------------------------------------------------------------------
def get_user_from_db(user_id=1):
    """
    Подключается к PostgreSQL, выполняет запрос SELECT для таблицы users
    и возвращает кортеж (name, email) или None, если запись не найдена/произошла ошибка.
    """
    try:
        # Устанавливаем соединение с базой данных, используя параметры из словаря DB_CONFIG
        # Символ ** распаковывает словарь в именованные аргументы функции connect()
        conn = psycopg2.connect(**DB_CONFIG)

        # Создаём курсор — объект для выполнения SQL-запросов
        cur = conn.cursor()

        # Выполняем параметризованный SQL-запрос.
        # %s — плейсхолдер, который будет заменён на реальное значение user_id.
        # Вторым аргументом передаётся кортеж с параметрами (user_id,).
        # Это защищает от SQL-инъекций, так как psycopg2 экранирует значения автоматически.
        cur.execute("SELECT name, email FROM users WHERE id = %s", (user_id,))

        # Извлекаем первую (и в данном случае единственную) строку результата.
        # Если записи с таким id нет, fetchone() вернёт None.
        row = cur.fetchone()

        # Закрываем курсор — освобождаем ресурсы на стороне сервера
        cur.close()
        # Закрываем соединение с базой данных
        conn.close()

        # Возвращаем полученную строку: кортеж из двух элементов (name, email) или None
        return row

    except Exception as e:
        # Если на любом этапе произошла ошибка (например, нет соединения, ошибка в SQL),
        # показываем окно с сообщением об ошибке.
        messagebox.showerror("Ошибка БД", str(e))
        # Возвращаем None, сигнализируя о том, что данные не получены
        return None

# ------------------------------------------------------------------------------
# Обработчик нажатия на кнопку "Загрузить"
# ------------------------------------------------------------------------------
def load_data():
    """
    Считывает ID из текстового поля, проверяет корректность,
    получает данные пользователя из БД и заполняет поля формы.
    """
    # Получаем текст, введённый в поле entry_id (ID пользователя)
    user_id = entry_id.get()

    # Проверяем, состоит ли введённая строка только из цифр.
    # isdigit() вернёт True, если строка непустая и все символы — цифры.
    if not user_id.isdigit():
        # Если введено не число — показываем предупреждение
        messagebox.showwarning("Ошибка", "Введите число")
        return  # Прерываем выполнение функции, чтобы не обращаться к БД с некорректным ID

    # Преобразуем строку в целое число и вызываем функцию получения данных
    data = get_user_from_db(int(user_id))

    # Если функция вернула None (пользователь не найден или ошибка)
    if data is None:
        # Очищаем текстовые поля "Имя" и "Email"
        # delete(0, tk.END) удаляет весь текст от позиции 0 до конца строки
        entry_name.delete(0, tk.END)
        entry_email.delete(0, tk.END)

        # Выводим информационное окно, что запись с таким ID не найдена
        messagebox.showinfo("Не найдено", f"Пользователь с ID {user_id} не найден")
    else:
        # Распаковываем кортеж (name, email) в отдельные переменные
        name, email = data

        # Очищаем поле "Имя" и вставляем туда полученное имя
        entry_name.delete(0, tk.END)
        entry_name.insert(0, name)      # insert(0, ...) — вставить текст в начало поля (позиция 0)

        # Очищаем поле "Email" и вставляем полученный email
        entry_email.delete(0, tk.END)
        entry_email.insert(0, email)

# ==============================================================================
# СОЗДАНИЕ ГРАФИЧЕСКОГО ИНТЕРФЕЙСА
# ==============================================================================

# Создаём главное окно приложения
root = tk.Tk()

# Устанавливаем заголовок окна (отображается в строке заголовка)
root.title("Форма из PostgreSQL")

# Задаём размеры окна в пикселях: ширина x высота
root.geometry("400x200")

# ------------------------------------------------------------------------------
# Размещение виджетов с помощью менеджера сетки grid()
# ------------------------------------------------------------------------------
# Сетка состоит из строк (row) и столбцов (column). Нумерация начинается с 0.
# padx и pady задают внешние отступы по горизонтали и вертикали от ячейки.
# sticky определяет, к какой стороне ячейки прижимается виджет (W — запад/лево, E — восток/право).

# ---------- Первая строка (row=0): ID, поле ввода, кнопка ----------

# Метка "ID:" в первой строке, нулевой колонке
tk.Label(root, text="ID:").grid(row=0, column=0, padx=10, pady=10, sticky="e")

# Поле ввода (Entry) для ID пользователя
entry_id = tk.Entry(root, width=10)     # width — ширина в символах
entry_id.grid(row=0, column=1, padx=10, pady=10, sticky="w")

# Вставляем в поле значение по умолчанию "1" (чтобы не вводить каждый раз)
entry_id.insert(0, "1")

# Кнопка "Загрузить", которая вызовет функцию load_data при нажатии
btn_load = tk.Button(root, text="Загрузить", command=load_data)
btn_load.grid(row=0, column=2, padx=10, pady=10)

# ---------- Вторая строка (row=1): метка "Имя:" и поле для имени ----------

# Метка "Имя:"
tk.Label(root, text="Имя:").grid(row=1, column=0, padx=10, pady=10, sticky="e")

# Поле ввода для имени, занимает две колонки (columnspan=2), чтобы быть шире
entry_name = tk.Entry(root, width=30)
entry_name.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="w")

# ---------- Третья строка (row=2): метка "Email:" и поле для email ----------

# Метка "Email:"
tk.Label(root, text="Email:").grid(row=2, column=0, padx=10, pady=10, sticky="e")

# Поле ввода для email, тоже растянуто на две колонки
entry_email = tk.Entry(root, width=30)
entry_email.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="w")

# ------------------------------------------------------------------------------
# Запуск главного цикла обработки событий
# ------------------------------------------------------------------------------
# mainloop() запускает бесконечный цикл, который ждёт действий пользователя
# (нажатий клавиш, кликов мыши) и обновляет окно. Код после mainloop() не выполнится,
# пока окно не будет закрыто.
root.mainloop()














4. Запуск из терминала (проверка)

Проверьте, что всё работает, запустив скрипт:

```bash
cd ~/myapp
python3 load_form.py
```

Должно появиться окно. Если не появляется, прочитайте ошибки в терминале и устраните их (обычно проблемы с паролем или соединением с PostgreSQL).

5. Создание скрипта-запускателя (аналог .bat)

Теперь сделаем так, чтобы приложение запускалось по двойному щелчку в файловом менеджере или из меню приложений, как обычная программа.

5.1. Создайте shell-скрипт

Создайте файл load_form.sh в той же папке (или в домашней):

```bash
nano ~/myapp/load_form.sh
```

Вставьте следующий код:

```bash
#!/bin/bash
# Активировать виртуальное окружение (если используете)
# source ~/myapp/venv/bin/activate

# Перейти в папку со скриптом (на случай запуска из другого места)
cd "$(dirname "$0")"

# Запустить Python-приложение
python3 load_form.py
```

Если вы используете виртуальное окружение, раскомментируйте строку source ... и укажите путь к активации.

Сохраните файл (Ctrl+O, Ctrl+X в nano).

5.2. Сделайте скрипт исполняемым

```bash
chmod +x ~/myapp/load_form.sh
```

Теперь вы можете запустить его из терминала: ~/myapp/load_form.sh

5.3. Запуск двойным щелчком

В большинстве файловых менеджеров (Nautilus, Dolphin, Thunar) двойной клик по .sh файлу просто откроет его в текстовом редакторе. Чтобы он запускался, настройте поведение:

· Nautilus (GNOME):
    Откройте «Файлы» → меню (три полоски) → «Настройки» → вкладка «Поведение» → раздел «Исполняемые текстовые файлы» → выберите «Запускать при открытии».
· Dolphin (KDE):
    Щёлкните правой кнопкой по load_form.sh → «Свойства» → вкладка «Права» → установите флажок «Исполняемый» → на вкладке «Общие» нажмите «Изменить…» для «Открывать с помощью» и выберите «Терминал» (или создайте собственную команду вида konsole -e).
    Альтернативно: в настройках Dolphin → «Подтверждение» → для исполняемых скриптов выбрать «Спрашивать» или «Запускать».
· Thunar (XFCE):
    Правый клик → «Свойства» → «Права» → «Разрешить выполнение как программы». Затем правый клик → «Открыть с помощью» → «Выполнить в терминале» (или создать постоянную ассоциацию).

После настройки двойной клик по load_form.sh откроет терминал, в нём выполнится скрипт, и появится окно приложения. Терминал можно не закрывать, чтобы видеть возможные сообщения.

6. Создание ярлыка .desktop (для меню приложений / рабочего стола)

Чтобы приложение выглядело как обычная программа и запускалось из системного меню, создайте файл .desktop.

Создайте файл, например ~/Рабочий стол/load_form.desktop (или ~/.local/share/applications/load_form.desktop для системного меню):

```bash
nano ~/.local/share/applications/load_form.desktop
```

Содержимое:

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Загрузка данных из PostgreSQL
Comment=Форма для отображения данных пользователей
Exec=/home/ваш_пользователь/myapp/load_form.sh
Icon=utilities-terminal
Terminal=true
Categories=Utility;
```

· Exec — полный путь к вашему скрипту-запускателю.
· Terminal=true — откроется терминал при запуске. Если вы не хотите видеть терминал, поставьте false, но тогда не увидите ошибок.
· Icon — можно указать любой значок из темы, например accessories-text-editor.

Сделайте файл исполняемым (не обязательно, но не помешает):

```bash
chmod +x ~/.local/share/applications/load_form.desktop
```

Теперь найдите в меню приложений «Загрузка данных из PostgreSQL» или перетащите .desktop файл на панель задач / рабочий стол для быстрого доступа.

7. Дополнительно: виртуальное окружение (рекомендуется)

Чтобы изолировать зависимости, создайте виртуальное окружение:

```bash
cd ~/myapp
python3 -m venv venv
source venv/bin/activate
pip install psycopg2-binary
deactivate
```

Затем в скрипте load_form.sh перед запуском Python активируйте окружение:

```bash
#!/bin/bash
cd "$(dirname "$0")"
source ./venv/bin/activate
python3 load_form.py
```

Итог

Теперь у вас есть полноценное приложение на Python+Tkinter+PostgreSQL, которое можно запускать в Linux:

· Из терминала командой python3 load_form.py
· Двойным щелчком по load_form.sh (если настроен запуск скриптов)
· Из меню приложений через созданный .desktop-файл

Если при запуске возникают ошибки, связанные с подключением к PostgreSQL, проверьте:

· Запущен ли сервер: sudo systemctl status postgresql
· Правильность пароля и параметров подключения
· Существует ли база testdb и таблица users
· Не блокирует ли соединение брандмауэр (если база на другом компьютере)
