
Я добавлю функциональность ограничения доступа по IP-адресам. Вот обновленный код:

Обновленный файл models.py

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

class AllowedIP(db.Model):
    """Модель для хранения разрешенных IP-адресов"""
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False)  # IPv6 может быть до 45 символов
    description = db.Column(db.String(200), nullable=True)  # Описание (кто это)
    is_active = db.Column(db.Boolean, default=True)  # Активен ли доступ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<IP {self.ip_address}>'

class AccessLog(db.Model):
    """Логирование попыток доступа"""
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    access_granted = db.Column(db.Boolean, default=False)
    endpoint = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AccessLog {self.ip_address} - {"Granted" if self.access_granted else "Denied"}>'
```

Обновленный файл database.py

```python
from models import db, QuestionAnswer, AllowedIP

def init_db():
    """Инициализация базы данных и добавление тестовых данных"""
    db.create_all()
    
    # Добавляем тестовые Q&A данные, если база пустая
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
        print("База данных инициализирована с тестовыми Q&A данными")
    
    # Добавляем тестовые IP-адреса
    if AllowedIP.query.count() == 0:
        default_ips = [
            {
                'ip_address': '127.0.0.1',  # localhost
                'description': 'Локальный доступ',
                'is_active': True
            },
            {
                'ip_address': '192.168.1.1',
                'description': 'Тестовый IP',
                'is_active': False  # Неактивный для примера
            }
        ]
        
        for ip_data in default_ips:
            allowed_ip = AllowedIP(**ip_data)
            db.session.add(allowed_ip)
        
        db.session.commit()
        print("База данных инициализирована с тестовыми IP-адресами")

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

Обновленный файл app.py

```python
from flask import Flask, render_template, request, jsonify, redirect, url_for, abort
from models import db, QuestionAnswer, AllowedIP, AccessLog
from database import init_db, find_best_answer
from functools import wraps
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

db.init_app(app)

# Создаем таблицы и добавляем тестовые данные при первом запуске
with app.app_context():
    init_db()

def get_client_ip():
    """Получение IP-адреса клиента"""
    # Проверяем заголовки для прокси
    if request.headers.get('X-Forwarded-For'):
        # Берем первый IP из списка
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr
    
    return ip

def check_ip_access(ip_address):
    """Проверка доступа по IP-адресу"""
    allowed_ip = AllowedIP.query.filter_by(
        ip_address=ip_address,
        is_active=True
    ).first()
    return allowed_ip is not None

def require_allowed_ip(f):
    """Декоратор для проверки IP-адреса"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = get_client_ip()
        
        # Логируем попытку доступа
        access_log = AccessLog(
            ip_address=client_ip,
            access_granted=check_ip_access(client_ip),
            endpoint=request.endpoint
        )
        db.session.add(access_log)
        db.session.commit()
        
        if not check_ip_access(client_ip):
            # Если это AJAX запрос, возвращаем JSON
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'error': 'Доступ запрещен',
                    'message': f'Ваш IP-адрес ({client_ip}) не имеет доступа к системе',
                    'status': 'forbidden'
                }), 403
            # Иначе показываем страницу с ошибкой
            return render_template('access_denied.html', ip=client_ip), 403
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@require_allowed_ip
def index():
    return render_template('chat.html')

@app.route('/ask', methods=['POST'])
@require_allowed_ip
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
        return jsonify({
            'answer': 'Извините, я пока не знаю ответа на этот вопрос. Попробуйте спросить что-нибудь другое!',
            'status': 'not_found'
        })

@app.route('/add_qa', methods=['GET', 'POST'])
@require_allowed_ip
def add_qa():
    """Добавление новых вопросов и ответов"""
    if request.method == 'POST':
        question = request.form.get('question', '').strip().lower()
        answer = request.form.get('answer', '').strip()
        
        if question and answer:
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
@require_allowed_ip
def list_qa():
    """Просмотр всех вопросов и ответов"""
    all_qa = QuestionAnswer.query.all()
    return render_template('list_qa.html', qa_list=all_qa)

@app.route('/delete_qa/<int:id>', methods=['DELETE'])
@require_allowed_ip
def delete_qa(id):
    """Удаление вопроса-ответа"""
    qa = QuestionAnswer.query.get_or_404(id)
    db.session.delete(qa)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Удалено успешно'})

# Административные маршруты для управления IP-адресами
@app.route('/admin/ips')
@require_allowed_ip
def manage_ips():
    """Управление разрешенными IP-адресами"""
    all_ips = AllowedIP.query.order_by(AllowedIP.created_at.desc()).all()
    recent_logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).limit(50).all()
    return render_template('manage_ips.html', ips=all_ips, logs=recent_logs)

@app.route('/admin/ips/add', methods=['POST'])
@require_allowed_ip
def add_ip():
    """Добавление нового IP-адреса"""
    data = request.get_json()
    ip_address = data.get('ip_address', '').strip()
    description = data.get('description', '').strip()
    
    if not ip_address:
        return jsonify({'status': 'error', 'message': 'IP-адрес обязателен'})
    
    # Проверяем формат IP
    import ipaddress
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Неверный формат IP-адреса'})
    
    existing = AllowedIP.query.filter_by(ip_address=ip_address).first()
    if existing:
        return jsonify({'status': 'error', 'message': 'Этот IP уже существует'})
    
    new_ip = AllowedIP(ip_address=ip_address, description=description)
    db.session.add(new_ip)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'IP-адрес добавлен'})

@app.route('/admin/ips/<int:id>/toggle', methods=['POST'])
@require_allowed_ip
def toggle_ip(id):
    """Включение/выключение IP-адреса"""
    ip = AllowedIP.query.get_or_404(id)
    ip.is_active = not ip.is_active
    db.session.commit()
    
    status = 'активирован' if ip.is_active else 'деактивирован'
    return jsonify({'status': 'success', 'message': f'IP {ip.ip_address} {status}'})

@app.route('/admin/ips/<int:id>/delete', methods=['DELETE'])
@require_allowed_ip
def delete_ip(id):
    """Удаление IP-адреса"""
    ip = AllowedIP.query.get_or_404(id)
    db.session.delete(ip)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'IP-адрес удален'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

Шаблон для страницы отказа в доступе (templates/access_denied.html)

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Доступ запрещен</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
        }
        .error-container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 500px;
        }
        .error-icon {
            font-size: 80px;
            margin-bottom: 20px;
        }
        h1 {
            color: #e53e3e;
            margin-bottom: 15px;
        }
        p {
            color: #666;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        .ip-address {
            background: #f7fafc;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 18px;
            color: #4a5568;
            border: 1px solid #e2e8f0;
        }
        .contact-info {
            margin-top: 20px;
            font-size: 14px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">🚫</div>
        <h1>Доступ запрещен</h1>
        <p>Извините, но ваш IP-адрес не имеет доступа к этой системе.</p>
        <div class="ip-address">
            Ваш IP: <strong>{{ ip }}</strong>
        </div>
        <p>Если вы считаете, что это ошибка, обратитесь к администратору системы.</p>
        <div class="contact-info">
            Для получения доступа необходимо добавить ваш IP-адрес в список разрешенных.
        </div>
    </div>
</body>
</html>
```

Шаблон для управления IP-адресами (templates/manage_ips.html)

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Управление IP-адресами</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            margin-bottom: 30px;
        }
        .add-form {
            background: #f7fafc;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .form-group {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        input {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            flex: 1;
        }
        button {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #5a67d8;
        }
        button.danger {
            background: #e53e3e;
        }
        button.success {
            background: #48bb78;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }
        th {
            background: #f7fafc;
            color: #4a5568;
            font-weight: bold;
        }
        .badge {
            padding: 4px 8px;
            border-radius: 10px;
            font-size: 12px;
        }
        .badge-active {
            background: #c6f6d5;
            color: #276749;
        }
        .badge-inactive {
            background: #fed7d7;
            color: #9b2c2c;
        }
        .nav-link {
            display: inline-block;
            margin-bottom: 20px;
            color: #667eea;
            text-decoration: none;
        }
        .nav-link:hover {
            text-decoration: underline;
        }
        .logs {
            background: #f7fafc;
            padding: 15px;
            border-radius: 10px;
            max-height: 300px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="nav-link">← Вернуться к чату</a>
        <h1>Управление IP-адресами</h1>
        
        <div class="add-form">
            <h3>Добавить новый IP-адрес</h3>
            <div class="form-group">
                <input type="text" id="newIp" placeholder="IP-адрес (например: 192.168.1.1)" required>
                <input type="text" id="ipDescription" placeholder="Описание (кто это)">
                <button onclick="addIp()">Добавить</button>
            </div>
            <div id="addMessage"></div>
        </div>
        
        <h2>Разрешенные IP-адреса</h2>
        <table>
            <thead>
                <tr>
                    <th>IP-адрес</th>
                    <th>Описание</th>
                    <th>Статус</th>
                    <th>Дата добавления</th>
                    <th>Действия</th>
                </tr>
            </thead>
            <tbody id="ipsTableBody">
                {% for ip in ips %}
                <tr>
                    <td><code>{{ ip.ip_address }}</code></td>
                    <td>{{ ip.description or '-' }}</td>
                    <td>
                        <span class="badge {% if ip.is_active %}badge-active{% else %}badge-inactive{% endif %}">
                            {{ 'Активен' if ip.is_active else 'Неактивен' }}
                        </span>
                    </td>
                    <td>{{ ip.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                    <td>
                        <button onclick="toggleIp({{ ip.id }})" class="success">
                            {{ 'Деактивировать' if ip.is_active else 'Активировать' }}
                        </button>
                        <button onclick="deleteIp({{ ip.id }})" class="danger">Удалить</button>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <h2>Последние попытки доступа</h2>
        <div class="logs">
            <table>
                <thead>
                    <tr>
                        <th>Время</th>
                        <th>IP-адрес</th>
                        <th>Статус</th>
                        <th>Страница</th>
                    </tr>
                </thead>
                <tbody>
                    {% for log in logs %}
                    <tr>
                        <td>{{ log.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</td>
                        <td><code>{{ log.ip_address }}</code></td>
                        <td>
                            <span class="badge {% if log.access_granted %}badge-active{% else %}badge-inactive{% endif %}">
                                {{ 'Разрешен' if log.access_granted else 'Запрещен' }}
                            </span>
                        </td>
                        <td>{{ log.endpoint }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        async function addIp() {
            const ip = document.getElementById('newIp').value.trim();
            const description = document.getElementById('ipDescription').value.trim();
            
            if (!ip) {
                showMessage('addMessage', 'Введите IP-адрес', 'red');
                return;
            }
            
            try {
                const response = await fetch('/admin/ips/add', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        ip_address: ip, 
                        description: description 
                    })
                });
                
                const data = await response.json();
                showMessage('addMessage', data.message, data.status === 'success' ? 'green' : 'red');
                
                if (data.status === 'success') {
                    setTimeout(() => location.reload(), 1000);
                }
            } catch (error) {
                showMessage('addMessage', 'Ошибка при добавлении', 'red');
            }
        }
        
        async function toggleIp(id) {
            try {
                const response = await fetch(`/admin/ips/${id}/toggle`, {
                    method: 'POST'
                });
                
                const data = await response.json();
                if (data.status === 'success') {
                    location.reload();
                }
            } catch (error) {
                alert('Ошибка при изменении статуса');
            }
        }
        
        async function deleteIp(id) {
            if (!confirm('Вы уверены, что хотите удалить этот IP-адрес?')) {
                return;
            }
            
            try {
                const response = await fetch(`/admin/ips/${id}/delete`, {
                    method: 'DELETE'
                });
                
                const data = await response.json();
                if (data.status === 'success') {
                    location.reload();
                }
            } catch (error) {
                alert('Ошибка при удалении');
            }
        }
        
        function showMessage(elementId, message, color) {
            const element = document.getElementById(elementId);
            element.textContent = message;
            element.style.color = color;
            setTimeout(() => {
                element.textContent = '';
            }, 3000);
        }
    </script>
</body>
</html>
```

Основные изменения:

1. Добавлена модель AllowedIP - хранит разрешенные IP-адреса с возможностью активации/деактивации
2. Добавлена модель AccessLog - логирует все попытки доступа
3. Создан декоратор @require_allowed_ip - проверяет доступ по IP перед выполнением запроса
4. Функция get_client_ip() - корректно определяет IP клиента даже за прокси
5. Административная панель для управления IP-адресами по адресу /admin/ips
6. Страница с отказом в доступе - показывается пользователям с неразрешенных IP

Как использовать:

1. При первом запуске в базу добавляется 127.0.0.1 (localhost)
2. Для доступа с другого IP, администратор должен добавить его через /admin/ips
3. IP-адреса можно временно деактивировать без удаления
4. Все попытки доступа логируются для аудита

Приложение теперь будет проверять IP-адрес каждого запроса и разрешать доступ только тем, чьи адреса есть в базе и активны.
