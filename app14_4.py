
Конечно, можно обойтись без Flask-SQLAlchemy и использовать встроенный модуль sqlite3.
Тогда не придётся ставить никакие дополнительные библиотеки, кроме самого Flask.

Я переписал код. Вот обновлённые файлы:

1. app.py — основное приложение

```python
import sqlite3
import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, g

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
DATABASE = 'chatbot.db'

# ---------- Работа с базой данных ----------
def get_db():
    """Возвращает соединение с базой данных для текущего запроса"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """Закрывает соединение после запроса"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Создаёт таблицы и заполняет тестовыми данными, если их нет"""
    db = sqlite3.connect(DATABASE)
    db.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS allowed_ips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT UNIQUE NOT NULL,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT NULL,
            access_granted INTEGER DEFAULT 0,
            endpoint TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Проверяем, есть ли уже вопросы
    if db.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0:
        sample_qa = [
            ('привет', 'Здравствуйте! Я чат-бот. Чем могу помочь?'),
            ('как дела', 'У меня всё отлично! Я готов отвечать на ваши вопросы.'),
            ('что ты умеешь', 'Я могу отвечать на вопросы, которые есть в моей базе данных. Спросите меня о чём-нибудь!'),
            ('пока', 'До свидания! Буду ждать вашего возвращения.'),
            ('спасибо', 'Пожалуйста! Рад был помочь.'),
            ('какая погода', 'Извините, я не умею проверять погоду. Но могу ответить на другие вопросы!'),
            ('расскажи шутку', 'Почему программисты путают Рождество и Хэллоуин? Потому что 31 OCT = 25 DEC!')
        ]
        db.executemany("INSERT INTO questions (question, answer) VALUES (?, ?)", sample_qa)

    # Проверяем, есть ли IP-адреса
    if db.execute("SELECT COUNT(*) FROM allowed_ips").fetchone()[0] == 0:
        db.execute("INSERT INTO allowed_ips (ip_address, description, is_active) VALUES (?, ?, ?)",
                   ('127.0.0.1', 'Локальный доступ', 1))

    db.commit()
    db.close()

# Инициализируем базу при старте
with app.app_context():
    init_db()

# ---------- IP-ограничения ----------
def get_client_ip():
    """Получение IP клиента с учётом прокси"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr

def check_ip_access(ip_address):
    """Проверка, есть ли IP в списке разрешённых и активных"""
    db = get_db()
    row = db.execute(
        "SELECT id FROM allowed_ips WHERE ip_address = ? AND is_active = 1",
        (ip_address,)
    ).fetchone()
    return row is not None

def require_allowed_ip(f):
    """Декоратор для защиты маршрутов по IP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = get_client_ip()
        access = check_ip_access(client_ip)

        # Логируем попытку
        db = get_db()
        db.execute(
            "INSERT INTO access_logs (ip_address, access_granted, endpoint) VALUES (?, ?, ?)",
            (client_ip, int(access), request.endpoint)
        )
        db.commit()

        if not access:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'error': 'Доступ запрещен',
                    'message': f'Ваш IP-адрес ({client_ip}) не имеет доступа',
                    'status': 'forbidden'
                }), 403
            return render_template('access_denied.html', ip=client_ip), 403
        return f(*args, **kwargs)
    return decorated_function

# ---------- Маршруты чат-бота ----------
@app.route('/')
@require_allowed_ip
def index():
    return render_template('chat.html')

@app.route('/ask', methods=['POST'])
@require_allowed_ip
def ask():
    data = request.get_json()
    question = data.get('question', '').strip().lower()

    if not question:
        return jsonify({'answer': 'Пожалуйста, задайте вопрос.', 'status': 'error'})

    db = get_db()

    # Точное совпадение
    row = db.execute("SELECT answer FROM questions WHERE question = ?", (question,)).fetchone()
    if row:
        return jsonify({'answer': row['answer'], 'status': 'success'})

    # Частичное совпадение
    row = db.execute("SELECT answer FROM questions WHERE ? LIKE '%' || question || '%'", (question,)).fetchone()
    if row:
        return jsonify({'answer': row['answer'], 'status': 'success'})

    # Поиск по вхождению вопроса в базу
    row = db.execute("SELECT answer FROM questions WHERE question LIKE ?", ('%' + question + '%',)).fetchone()
    if row:
        return jsonify({'answer': row['answer'], 'status': 'success'})

    # Ответ по умолчанию
    return jsonify({
        'answer': 'Извините, я пока не знаю ответа. Попробуйте спросить что-нибудь другое.',
        'status': 'not_found'
    })

@app.route('/add_qa', methods=['GET', 'POST'])
@require_allowed_ip
def add_qa():
    if request.method == 'POST':
        question = request.form.get('question', '').strip().lower()
        answer = request.form.get('answer', '').strip()
        if not question or not answer:
            return jsonify({'message': 'Заполните оба поля!', 'status': 'error'})

        db = get_db()
        existing = db.execute("SELECT id FROM questions WHERE question = ?", (question,)).fetchone()
        if existing:
            return jsonify({'message': 'Такой вопрос уже существует!', 'status': 'error'})

        db.execute("INSERT INTO questions (question, answer) VALUES (?, ?)", (question, answer))
        db.commit()
        return jsonify({'message': 'Вопрос и ответ добавлены!', 'status': 'success'})

    return render_template('add_qa.html')

@app.route('/list_qa')
@require_allowed_ip
def list_qa():
    db = get_db()
    rows = db.execute("SELECT * FROM questions ORDER BY created_at DESC").fetchall()
    return render_template('list_qa.html', qa_list=rows)

@app.route('/delete_qa/<int:id>', methods=['DELETE'])
@require_allowed_ip
def delete_qa(id):
    db = get_db()
    db.execute("DELETE FROM questions WHERE id = ?", (id,))
    db.commit()
    return jsonify({'status': 'success', 'message': 'Удалено'})

# ---------- Админка IP ----------
@app.route('/admin/ips')
@require_allowed_ip
def manage_ips():
    db = get_db()
    ips = db.execute("SELECT * FROM allowed_ips ORDER BY created_at DESC").fetchall()
    logs = db.execute("SELECT * FROM access_logs ORDER BY timestamp DESC LIMIT 50").fetchall()
    return render_template('manage_ips.html', ips=ips, logs=logs)

@app.route('/admin/ips/add', methods=['POST'])
@require_allowed_ip
def add_ip():
    data = request.get_json()
    ip = data.get('ip_address', '').strip()
    desc = data.get('description', '').strip()

    if not ip:
        return jsonify({'status': 'error', 'message': 'IP-адрес обязателен'})

    # Простая проверка формата (можно усилить)
    import ipaddress
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Неверный формат IP'})

    db = get_db()
    existing = db.execute("SELECT id FROM allowed_ips WHERE ip_address = ?", (ip,)).fetchone()
    if existing:
        return jsonify({'status': 'error', 'message': 'Такой IP уже существует'})

    db.execute("INSERT INTO allowed_ips (ip_address, description) VALUES (?, ?)", (ip, desc))
    db.commit()
    return jsonify({'status': 'success', 'message': 'IP добавлен'})

@app.route('/admin/ips/<int:id>/toggle', methods=['POST'])
@require_allowed_ip
def toggle_ip(id):
    db = get_db()
    row = db.execute("SELECT * FROM allowed_ips WHERE id = ?", (id,)).fetchone()
    if not row:
        return jsonify({'status': 'error', 'message': 'IP не найден'})
    new_status = 0 if row['is_active'] else 1
    db.execute("UPDATE allowed_ips SET is_active = ? WHERE id = ?", (new_status, id))
    db.commit()
    status_text = 'активирован' if new_status else 'деактивирован'
    return jsonify({'status': 'success', 'message': f'IP {row["ip_address"]} {status_text}'})

@app.route('/admin/ips/<int:id>/delete', methods=['DELETE'])
@require_allowed_ip
def delete_ip(id):
    db = get_db()
    db.execute("DELETE FROM allowed_ips WHERE id = ?", (id,))
    db.commit()
    return jsonify({'status': 'success', 'message': 'IP удалён'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

2. requirements.txt (теперь только Flask)

```txt
Flask==3.0.0
```

3. Шаблоны

Остаются те же: chat.html, add_qa.html, list_qa.html, access_denied.html, manage_ips.html — их не меняем.

Что изменилось

· Полностью убрана зависимость от flask-sqlalchemy и SQLAlchemy.
· Вся работа с БД идёт через стандартный модуль sqlite3.
· Соединение с базой создаётся один раз на запрос и хранится в объекте g (Flask).
· Таблицы создаются автоматически при запуске, тестовые данные добавляются один раз.

Установка и запуск

```bash
pip install flask        # только Flask, sqlite3 уже внутри Python
python app.py
```

Теперь никаких проблем с недостающими модулями быть не должно. Если возникнут вопросы — пишите.









Я создам для вас простого чат-бота на Flask с SQLite, который работает по принципу "вопрос-ответ". Вот полный код:

1. Структура проекта

```
chatbot/
├── app.py
├── database.py
├── models.py
├── requirements.txt
└── templates/
    └── chat.html
```

2. Файл requirements.txt

```txt
Flask==3.0.0
```

3. Файл models.py

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class QuestionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<QA {self.question[:30]}...>'
```

4. Файл database.py

```python
from models import db, QuestionAnswer

def init_db():
    """Инициализация базы данных и добавление тестовых данных"""
    db.create_all()
    
    # Добавляем тестовые данные, если база пустая
    if QuestionAnswer.query.count() == 0:
        sample_qa = [
            {
                'question': 'привет',
                'answer': 'Здравствуйте! Я чат-бот. Чем могу помочь?'
            },
            {
                'question': 'как дела',
                'answer': 'У меня всё отлично! Я готов отвечать на ваши вопросы.'
            },
            {
                'question': 'что ты умеешь',
                'answer': 'Я могу отвечать на вопросы, которые есть в моей базе данных. Спросите меня о чём-нибудь!'
            },
            {
                'question': 'пока',
                'answer': 'До свидания! Буду ждать вашего возвращения.'
            },
            {
                'question': 'спасибо',
                'answer': 'Пожалуйста! Рад был помочь.'
            },
            {
                'question': 'какая погода',
                'answer': 'Извините, я не умею проверять погоду. Но могу ответить на другие вопросы!'
            },
            {
                'question': 'расскажи шутку',
                'answer': 'Почему программисты путают Рождество и Хэллоуин? Потому что 31 OCT = 25 DEC!'
            }
        ]
        
        for qa in sample_qa:
            new_qa = QuestionAnswer(
                question=qa['question'].lower(),
                answer=qa['answer']
            )
            db.session.add(new_qa)
        
        db.session.commit()
        print("База данных инициализирована с тестовыми данными")

def find_best_answer(user_question):
    """Поиск наиболее подходящего ответа"""
    user_question = user_question.lower().strip()
    
    # Сначала ищем точное совпадение
    exact_match = QuestionAnswer.query.filter_by(question=user_question).first()
    if exact_match:
        return exact_match.answer
    
    # Если точного совпадения нет, ищем частичное
    partial_match = QuestionAnswer.query.filter(
        QuestionAnswer.question.contains(user_question)
    ).first()
    
    if partial_match:
        return partial_match.answer
    
    # Проверяем, содержит ли вопрос ключевые слова из базы
    all_qa = QuestionAnswer.query.all()
    for qa in all_qa:
        if user_question in qa.question or qa.question in user_question:
            return qa.answer
    
    return None
```

5. Файл app.py

```python
from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, QuestionAnswer
from database import init_db, find_best_answer
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

db.init_app(app)

# Создаем таблицы и добавляем тестовые данные при первом запуске
with app.app_context():
    init_db()

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/ask', methods=['POST'])
def ask():
    """Обработка вопроса пользователя"""
    data = request.get_json()
    user_question = data.get('question', '').strip()
    
    if not user_question:
        return jsonify({
            'answer': 'Пожалуйста, задайте вопрос.',
            'status': 'error'
        })
    
    # Ищем ответ в базе данных
    answer = find_best_answer(user_question)
    
    if answer:
        return jsonify({
            'answer': answer,
            'status': 'success'
        })
    else:
        # Ответ по умолчанию
        return jsonify({
            'answer': 'Извините, я пока не знаю ответа на этот вопрос. Попробуйте спросить что-нибудь другое!',
            'status': 'not_found'
        })

@app.route('/add_qa', methods=['GET', 'POST'])
def add_qa():
    """Добавление новых вопросов и ответов"""
    if request.method == 'POST':
        question = request.form.get('question', '').strip().lower()
        answer = request.form.get('answer', '').strip()
        
        if question and answer:
            # Проверяем, нет ли уже такого вопроса
            existing = QuestionAnswer.query.filter_by(question=question).first()
            if existing:
                return jsonify({
                    'message': 'Такой вопрос уже существует!',
                    'status': 'error'
                })
            
            new_qa = QuestionAnswer(question=question, answer=answer)
            db.session.add(new_qa)
            db.session.commit()
            
            return jsonify({
                'message': 'Вопрос и ответ успешно добавлены!',
                'status': 'success'
            })
        
        return jsonify({
            'message': 'Заполните оба поля!',
            'status': 'error'
        })
    
    return render_template('add_qa.html')

@app.route('/list_qa')
def list_qa():
    """Просмотр всех вопросов и ответов"""
    all_qa = QuestionAnswer.query.all()
    return render_template('list_qa.html', qa_list=all_qa)

@app.route('/delete_qa/<int:id>', methods=['DELETE'])
def delete_qa(id):
    """Удаление вопроса-ответа"""
    qa = QuestionAnswer.query.get_or_404(id)
    db.session.delete(qa)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Удалено успешно'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

6. Файл templates/chat.html

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Чат-бот</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chat-container {
            width: 400px;
            height: 600px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: #667eea;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 20px;
            font-weight: bold;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .message {
            max-width: 80%;
            padding: 10px 15px;
            border-radius: 15px;
            word-wrap: break-word;
        }
        
        .user-message {
            align-self: flex-end;
            background: #667eea;
            color: white;
            border-bottom-right-radius: 5px;
        }
        
        .bot-message {
            align-self: flex-start;
            background: #f0f0f0;
            color: #333;
            border-bottom-left-radius: 5px;
        }
        
        .chat-input {
            padding: 20px;
            background: #f8f8f8;
            display: flex;
            gap: 10px;
        }
        
        .chat-input input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 25px;
            outline: none;
        }
        
        .chat-input button {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .chat-input button:hover {
            background: #5a67d8;
        }
        
        .typing-indicator {
            display: none;
            align-self: flex-start;
            background: #f0f0f0;
            padding: 10px 15px;
            border-radius: 15px;
            margin-top: 10px;
        }
        
        .typing-indicator span {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #999;
            margin: 0 2px;
            animation: typing 1s infinite;
        }
        
        .typing-indicator span:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-indicator span:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
                opacity: 0.5;
            }
            30% {
                transform: translateY(-10px);
                opacity: 1;
            }
        }
        
        .nav-buttons {
            text-align: center;
            padding: 10px;
        }
        
        .nav-buttons a {
            color: #667eea;
            text-decoration: none;
            margin: 0 10px;
            font-size: 14px;
        }
        
        .nav-buttons a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            🤖 Чат-бот
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                Привет! Я чат-бот. Задайте мне вопрос!
            </div>
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
        
        <div class="nav-buttons">
            <a href="/add_qa">Добавить вопрос-ответ</a>
            <a href="/list_qa">Список всех Q&A</a>
        </div>
        
        <div class="chat-input">
            <input type="text" id="userInput" placeholder="Введите ваш вопрос..." 
                   onkeypress="if(event.key === 'Enter') sendMessage()">
            <button onclick="sendMessage()">Отправить</button>
        </div>
    </div>
    
    <script>
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Добавляем сообщение пользователя
            addMessage(message, 'user');
            input.value = '';
            
            // Показываем индикатор печати
            showTyping(true);
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: message })
                });
                
                const data = await response.json();
                
                // Скрываем индикатор печати
                setTimeout(() => {
                    showTyping(false);
                    // Добавляем ответ бота
                    addMessage(data.answer, 'bot');
                }, 1000);
                
            } catch (error) {
                showTyping(false);
                addMessage('Произошла ошибка. Попробуйте позже.', 'bot');
            }
        }
        
        function addMessage(text, sender) {
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = text;
            messagesContainer.appendChild(messageDiv);
            
            // Автопрокрутка вниз
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function showTyping(show) {
            const indicator = document.getElementById('typingIndicator');
            indicator.style.display = show ? 'block' : 'none';
        }
    </script>
</body>
</html>
```

7. Дополнительные шаблоны

templates/add_qa.html (для добавления вопросов-ответов):

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Добавить вопрос-ответ</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            width: 500px;
        }
        h1 {
            color: #667eea;
            margin-bottom: 20px;
        }
        form {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        input, textarea {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        textarea {
            height: 100px;
            resize: vertical;
        }
        button {
            padding: 10px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        a {
            color: #667eea;
            text-decoration: none;
            display: block;
            text-align: center;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Добавить новый вопрос-ответ</h1>
        <form id="qaForm">
            <input type="text" id="question" placeholder="Вопрос" required>
            <textarea id="answer" placeholder="Ответ" required></textarea>
            <button type="submit">Добавить</button>
        </form>
        <div id="message"></div>
        <a href="/">← Вернуться к чату</a>
    </div>
    
    <script>
        document.getElementById('qaForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData();
            formData.append('question', document.getElementById('question').value);
            formData.append('answer', document.getElementById('answer').value);
            
            const response = await fetch('/add_qa', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            const messageDiv = document.getElementById('message');
            messageDiv.textContent = data.message;
            messageDiv.style.color = data.status === 'success' ? 'green' : 'red';
            
            if (data.status === 'success') {
                document.getElementById('question').value = '';
                document.getElementById('answer').value = '';
            }
        });
    </script>
</body>
</html>
```

Запуск приложения

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Запустите приложение:

```bash
python app.py
```

3. Откройте браузер и перейдите по адресу: http://localhost:5000

Функциональность

· ✅ Чат-интерфейс в реальном времени
· ✅ Поиск точных и частичных совпадений вопросов
· ✅ База данных SQLite для хранения Q&A пар
· ✅ Возможность добавления новых вопросов-ответов через веб-интерфейс
· ✅ Просмотр всех пар вопрос-ответ
· ✅ Тестовые данные для начала работы
· ✅ Индикатор "печатания" для реалистичности
· ✅ Адаптивный дизайн

Бот ищет ответы в следующем порядке:

1. Точное совпадение вопроса
2. Частичное совпадение (вопрос содержится в базе)
3. Совпадение по ключевым словам
4. Если ничего не найдено - выдает стандартный ответ
