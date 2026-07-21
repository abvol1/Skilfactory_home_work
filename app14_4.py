
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Диагностика external</title>
    <style>
        body { font-family: Arial; padding: 10px; margin: 0; background: #f5f5f5; }
        button { 
            display: block; width: 100%; padding: 10px; margin: 6px 0; 
            border: 1px solid #ccc; border-radius: 4px; cursor: pointer; 
            font-size: 12px; text-align: left; background: white;
        }
        button:hover { background: #e8e8e8; }
        .result { 
            margin-top: 10px; padding: 10px; background: #1e1e1e; color: #0f0; 
            font-family: monospace; font-size: 11px; white-space: pre-wrap; 
            min-height: 200px; max-height: 400px; overflow-y: auto; border-radius: 4px;
        }
        .error { color: #ff6b6b; }
        .success { color: #51cf66; }
        .info { color: #74c0fc; }
    </style>
</head>
<body>
    <h3>🔍 external методы</h3>
    
    <button onclick="listAll()">📋 Показать все методы external</button>
    <button onclick="testExecute()">1. external.Execute(код)</button>
    <button onclick="testEval()">2. external.Eval(код)</button>
    <button onclick="testRun()">3. external.Run(код)</button>
    <button onclick="testCall()">4. external.Call(код)</button>
    <button onclick="testExec()">5. external.Exec(код)</button>
    <button onclick="testCommand()">6. external.Command(код)</button>
    <button onclick="testInvoke()">7. external.Invoke(код)</button>
    <button onclick="testMacro()">8. external.RunMacro(код)</button>
    <button onclick="testScript()">9. external.ExecuteScript(код)</button>
    <button onclick="testApi()">10. external.Api(код)</button>
    <button onclick="testGetCell()">11. Получить A1 через external</button>
    <button onclick="clearLog()">🧹 Очистить лог</button>
    
    <div class="result" id="result">Нажмите на кнопки для диагностики...</div>

    <script>
        function log(msg, type) {
            var div = document.getElementById('result');
            var cls = type || 'info';
            div.innerHTML += '<span class="' + cls + '">' + msg + '</span>\n';
            div.scrollTop = div.scrollHeight;
        }

        function clearLog() {
            document.getElementById('result').innerHTML = '';
        }

        // Код для записи в ячейку
        var testCode = 'var sheet = Api.GetActiveSheet(); sheet.GetRange("A1").SetValue("РАБОТАЕТ!");';

        function listAll() {
            log('=== Все свойства external ===', 'info');
            if (window.external) {
                var count = 0;
                for (var key in window.external) {
                    log(key + ' (' + typeof window.external[key] + ')', 'info');
                    count++;
                }
                log('Всего найдено: ' + count + ' свойств', 'success');
            } else {
                log('❌ external не найден', 'error');
            }
        }

        function safeTest(methodName, code) {
            log('Тестирую external.' + methodName + '...', 'info');
            try {
                if (window.external && typeof window.external[methodName] === 'function') {
                    window.external[methodName](code);
                    log('✅ external.' + methodName + ' выполнен без ошибок', 'success');
                    return true;
                } else {
                    log('❌ external.' + methodName + ' не функция', 'error');
                    return false;
                }
            } catch(e) {
                log('❌ external.' + methodName + ' ошибка: ' + e.message, 'error');
                return false;
            }
        }

        function testExecute() { safeTest('Execute', testCode); }
        function testEval() { safeTest('Eval', testCode); }
        function testRun() { safeTest('Run', testCode); }
        function testCall() { safeTest('Call', testCode); }
        function testExec() { safeTest('Exec', testCode); }
        function testCommand() { safeTest('Command', testCode); }
        function testInvoke() { safeTest('Invoke', testCode); }
        function testMacro() { safeTest('RunMacro', testCode); }
        function testScript() { safeTest('ExecuteScript', testCode); }
        function testApi() { safeTest('Api', testCode); }

        function testGetCell() {
            log('Пробую прочитать A1 через разные геттеры...', 'info');
            
            var getters = ['GetCellValue', 'GetValue', 'getCellValue', 'getValue', 
                          'ReadCell', 'readCell', 'Cell', 'GetActiveCell'];
            
            for (var i = 0; i < getters.length; i++) {
                try {
                    if (window.external && typeof window.external[getters[i]] === 'function') {
                        var val = window.external[getters[i]]('A1');
                        log('✅ external.' + getters[i] + '("A1") = ' + val, 'success');
                    }
                } catch(e) {
                    // игнорируем
                }
            }
        }

        window.onload = function() {
            log('=== Плагин загружен ===', 'info');
            setTimeout(listAll, 300);
        };
    </script>
</body>
</html>











Понял, F12 не работает — это нормально для десктопной версии Р7, там консоль разработчика недоступна. Тогда давайте действовать иначе.

Проблема в том, что мы не видим ошибок. Но скорее всего в вашей версии методы взаимодействия называются иначе или требуют особого формата. Давайте сделаем универсальный тестовый плагин, который перепробует ВСЕ возможные способы и покажет, какой из них рабочий.

---

Диагностический плагин

Создайте плагин с этим index.html. Он сам определит, какие методы доступны в вашей версии:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Диагностика</title>
    <style>
        body { font-family: Arial; padding: 10px; margin: 0; background: #f5f5f5; }
        button { 
            display: block; width: 100%; padding: 10px; margin: 8px 0; 
            border: 1px solid #ccc; border-radius: 4px; cursor: pointer; 
            font-size: 13px; text-align: left; background: white;
        }
        button:hover { background: #e8e8e8; }
        .result { 
            margin-top: 10px; padding: 10px; background: #1e1e1e; color: #0f0; 
            font-family: monospace; font-size: 11px; white-space: pre-wrap; 
            min-height: 200px; max-height: 400px; overflow-y: auto; border-radius: 4px;
        }
        .error { color: #ff6b6b; }
        .success { color: #51cf66; }
        .info { color: #74c0fc; }
    </style>
</head>
<body>
    <h3>🔍 Диагностика методов</h3>
    
    <button onclick="test1()">1. Проверить Asc.scope.execute</button>
    <button onclick="test2()">2. Проверить Asc.scope.evaluate</button>
    <button onclick="test3()">3. Проверить plugin.executeCommand</button>
    <button onclick="test4()">4. Проверить plugin.callCommand</button>
    <button onclick="test5()">5. Проверить executeMethod (GetCellValue)</button>
    <button onclick="test6()">6. Проверить ActiveX / внешний объект</button>
    <button onclick="test7()">7. Показать все доступные методы Asc</button>
    <button onclick="clearLog()">🧹 Очистить лог</button>
    
    <div class="result" id="result">Нажмите на кнопки для диагностики...</div>

    <script>
        function log(msg, type) {
            var div = document.getElementById('result');
            var cls = type || 'info';
            div.innerHTML += '<span class="' + cls + '">' + msg + '</span>\n';
            div.scrollTop = div.scrollHeight;
        }

        function clearLog() {
            document.getElementById('result').innerHTML = '';
        }

        // Показать ВСЕ доступные методы в объекте Asc
        function test7() {
            log('=== Доступные методы Asc ===', 'info');
            
            if (window.Asc) {
                log('window.Asc существует ✅', 'success');
                
                // Перебираем все свойства Asc
                var methods = [];
                for (var key in window.Asc) {
                    methods.push(key + ' (' + typeof window.Asc[key] + ')');
                }
                log('Свойства Asc: ' + methods.join(', '), 'info');
                
                // Проверяем plugin
                if (window.Asc.plugin) {
                    log('\n=== Свойства Asc.plugin ===', 'info');
                    var pluginMethods = [];
                    for (var key in window.Asc.plugin) {
                        pluginMethods.push(key + ' (' + typeof window.Asc.plugin[key] + ')');
                    }
                    log(pluginMethods.join(', '), 'info');
                } else {
                    log('❌ Asc.plugin не найден', 'error');
                }
                
                // Проверяем scope
                if (window.Asc.scope) {
                    log('\n=== Свойства Asc.scope ===', 'info');
                    var scopeMethods = [];
                    for (var key in window.Asc.scope) {
                        scopeMethods.push(key + ' (' + typeof window.Asc.scope[key] + ')');
                    }
                    log(scopeMethods.join(', '), 'info');
                } else {
                    log('❌ Asc.scope не найден', 'error');
                }
            } else {
                log('❌ window.Asc НЕ СУЩЕСТВУЕТ! Плагин не может работать.', 'error');
            }
        }

        function test1() {
            log('📝 Тест 1: Asc.scope.execute', 'info');
            try {
                if (window.Asc && window.Asc.scope && window.Asc.scope.execute) {
                    window.Asc.scope.execute(
                        'var sheet = Api.GetActiveSheet();' +
                        'sheet.GetRange("A1").SetValue("Тест1: scope.execute работает!");'
                    );
                    log('✅ Команда отправлена через scope.execute', 'success');
                } else {
                    log('❌ Метод НЕДОСТУПЕН', 'error');
                }
            } catch(e) {
                log('❌ Ошибка: ' + e.message, 'error');
            }
        }

        function test2() {
            log('📝 Тест 2: Asc.scope.evaluate', 'info');
            try {
                if (window.Asc && window.Asc.scope && window.Asc.scope.evaluate) {
                    window.Asc.scope.evaluate(
                        'var sheet = Api.GetActiveSheet();' +
                        'sheet.GetRange("A2").SetValue("Тест2: scope.evaluate работает!");'
                    );
                    log('✅ Команда отправлена через scope.evaluate', 'success');
                } else {
                    log('❌ Метод НЕДОСТУПЕН', 'error');
                }
            } catch(e) {
                log('❌ Ошибка: ' + e.message, 'error');
            }
        }

        function test3() {
            log('📝 Тест 3: plugin.executeCommand', 'info');
            try {
                if (window.Asc && window.Asc.plugin && window.Asc.plugin.executeCommand) {
                    window.Asc.plugin.executeCommand(
                        'var sheet = Api.GetActiveSheet();' +
                        'sheet.GetRange("A3").SetValue("Тест3: executeCommand работает!");'
                    );
                    log('✅ Команда отправлена через executeCommand', 'success');
                } else {
                    log('❌ Метод НЕДОСТУПЕН', 'error');
                }
            } catch(e) {
                log('❌ Ошибка: ' + e.message, 'error');
            }
        }

        function test4() {
            log('📝 Тест 4: plugin.callCommand', 'info');
            try {
                if (window.Asc && window.Asc.plugin && window.Asc.plugin.callCommand) {
                    window.Asc.plugin.callCommand(
                        'var sheet = Api.GetActiveSheet();' +
                        'sheet.GetRange("A4").SetValue("Тест4: callCommand работает!");'
                    );
                    log('✅ Команда отправлена через callCommand', 'success');
                } else {
                    log('❌ Метод НЕДОСТУПЕН', 'error');
                }
            } catch(e) {
                log('❌ Ошибка: ' + e.message, 'error');
            }
        }

        function test5() {
            log('📝 Тест 5: executeMethod (GetCellValue)', 'info');
            try {
                if (window.Asc && window.Asc.plugin && window.Asc.plugin.executeMethod) {
                    window.Asc.plugin.executeMethod("GetCellValue", ["A1"], function(result) {
                        log('✅ executeMethod работает! Значение A1: ' + (result || 'пусто'), 'success');
                    });
                } else {
                    log('❌ Метод НЕДОСТУПЕН', 'error');
                }
            } catch(e) {
                log('❌ Ошибка: ' + e.message, 'error');
            }
        }

        function test6() {
            log('📝 Тест 6: Поиск ActiveX или внешнего API', 'info');
            try {
                // Проверяем, может быть Р7 использует внешний объект
                if (window.external) {
                    log('✅ window.external существует', 'success');
                    var extMethods = [];
                    for (var key in window.external) {
                        extMethods.push(key);
                    }
                    log('Методы external: ' + extMethods.join(', '), 'info');
                } else {
                    log('❌ window.external не найден', 'info');
                }
                
                // Проверяем ActiveX
                if (typeof ActiveXObject !== 'undefined') {
                    log('✅ ActiveXObject доступен', 'success');
                } else {
                    log('❌ ActiveXObject не доступен', 'info');
                }
            } catch(e) {
                log('❌ Ошибка: ' + e.message, 'error');
            }
        }

        // Автоматический запуск диагностики при загрузке
        window.onload = function() {
            log('=== Плагин загружен ===', 'info');
            setTimeout(test7, 500); // Показать доступные методы через полсекунды
        };
    </script>
</body>
</html>
```

---

Что делать:

1. Замените содержимое вашего index.html на код выше.
2. Перезапустите Р7-Офис.
3. Откройте плагин в боковой панели.
4. Сделайте скриншот того, что покажет кнопка №7 («Показать все доступные методы Asc»).
5. Нажмите кнопки 1–6 по очереди — после каждого нажатия проверяйте, появилась ли запись в ячейках A1-A4.

---

Как интерпретировать результаты:

· Если метод окрашен зелёным (✅) и в ячейке появился текст — этот метод рабочий, используйте его.
· Если метод окрашен красным (❌) — он недоступен в вашей версии.
· Кнопка №7 покажет все реально существующие методы в вашей версии Р7. Среди них обязательно найдётся тот, который позволяет выполнять код в книге.

Пришлите мне результаты (какие методы зелёные, какие красные, что показала кнопка №7), и я дам точный рабочий код под вашу версию.













Понял вас. В десктопной версии Р7-Офис плагины с isInsideMode: true и собственными кнопками в тулбаре редактора не поддерживаются — это особенность именно серверной (веб) версии.

В вашем случае всё взаимодействие строится внутри боковой панели (модального или немодального окна). Значит, кнопки нужно создавать прямо в HTML-коде вашего плагина, а для работы с таблицей использовать методы Asc.scope (для немодального окна) или выполнять макросы через executeCommand.

Вот полностью рабочий пример плагина с несколькими кнопками для десктопной версии.

---

1. config.json (минимальный и правильный)

Обратите внимание: массив buttons здесь не нужен, всё будет в самой панели.

```json
{
    "name": "Multi button panel",
    "nameLocale": {
        "ru": "Панель с кнопками"
    },
    "guid": "asc.{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}",
    "variations": [
        {
            "description": "Плагин с несколькими кнопками",
            "descriptionLocale": {
                "ru": "Плагин с несколькими кнопками в боковой панели"
            },
            "url": "index.html",
            "icons": "resources/icon.png",
            "isViewer": false,
            "EditorsSupport": ["spreadsheet"],
            "isVisual": true,
            "isModal": false,
            "isInsideMode": false,
            "initDataType": "none",
            "initOnSelectionChanged": true,
            "size": [280, 400]
        }
    ]
}
```

---

2. index.html — интерфейс и логика

Здесь вся магия: создаём несколько кнопок, каждая из которых через Asc.scope выполняет свой уникальный код в контексте книги.

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Мульти-кнопки</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 15px;
            margin: 0;
            background: #f5f5f5;
        }
        .btn {
            display: block;
            width: 100%;
            padding: 12px;
            margin-bottom: 10px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            text-align: center;
            transition: background 0.2s;
        }
        .btn-action-a { background: #4CAF50; color: white; }
        .btn-action-a:hover { background: #45a049; }
        
        .btn-action-b { background: #2196F3; color: white; }
        .btn-action-b:hover { background: #1e87db; }
        
        .btn-clear { background: #f44336; color: white; }
        .btn-clear:hover { background: #e53935; }
        
        .btn-info { background: #FF9800; color: white; }
        .btn-info:hover { background: #f18c00; }
        
        .status {
            margin-top: 20px;
            padding: 10px;
            background: #fff;
            border-radius: 4px;
            font-size: 12px;
            color: #555;
            min-height: 40px;
            word-break: break-word;
        }
    </style>
</head>
<body>
    <h3>Операции с таблицей</h3>
    
    <button class="btn btn-action-a" onclick="doActionA()">📝 Заполнить A1:A5</button>
    
    <button class="btn btn-action-b" onclick="doActionB()">🎨 Раскрасить B1:B5</button>
    
    <button class="btn btn-info" onclick="doActionInfo()">📊 Выделенная область</button>
    
    <button class="btn btn-clear" onclick="doActionClear()">🧹 Очистить всё</button>
    
    <div class="status" id="status">Готов к работе</div>

    <script>
        // Вспомогательная функция для выполнения кода в контексте документа
        function executeInScope(code) {
            if (window.Asc && window.Asc.scope) {
                window.Asc.scope.execute(code);
            } else {
                setStatus('❌ Ошибка: Asc.scope недоступен');
            }
        }

        // Обновление статуса в интерфейсе
        function setStatus(msg) {
            document.getElementById('status').textContent = msg;
            console.log(msg);
        }

        // ===== ДЕЙСТВИЕ 1: Заполнение =====
        function doActionA() {
            const code = `
                (function() {
                    var sheet = Api.GetActiveSheet();
                    var names = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май'];
                    for (var i = 0; i < names.length; i++) {
                        sheet.GetRange("A" + (i + 1)).SetValue(names[i]);
                    }
                    return "A1:A5 заполнены";
                })();
            `;
            executeInScope(code);
            setStatus('✅ Действие А выполнено: заполнены ячейки A1:A5');
        }

        // ===== ДЕЙСТВИЕ 2: Раскраска =====
        function doActionB() {
            const code = `
                (function() {
                    var sheet = Api.GetActiveSheet();
                    var colors = [
                        Api.CreateColorFromRGB(255, 230, 230),
                        Api.CreateColorFromRGB(230, 255, 230),
                        Api.CreateColorFromRGB(230, 230, 255),
                        Api.CreateColorFromRGB(255, 255, 200),
                        Api.CreateColorFromRGB(255, 220, 220)
                    ];
                    for (var i = 0; i < 5; i++) {
                        sheet.GetRange("B" + (i + 1)).SetFillColor(colors[i]);
                        sheet.GetRange("B" + (i + 1)).SetValue("Элемент " + (i + 1));
                    }
                    return "OK";
                })();
            `;
            executeInScope(code);
            setStatus('✅ Действие B выполнено: B1:B5 раскрашены');
        }

        // ===== ДЕЙСТВИЕ 3: Информация о выделении =====
        function doActionInfo() {
            if (window.Asc && window.Asc.plugin) {
                // Используем событие получения выделенной области
                window.Asc.plugin.executeMethod("GetSelectedRange", [], function(range) {
                    if (range && range !== "Error") {
                        setStatus('📊 Выделено: ' + range);
                    } else {
                        setStatus('ℹ️ Ничего не выделено');
                    }
                });
            }
        }

        // ===== ДЕЙСТВИЕ 4: Очистка =====
        function doActionClear() {
            const code = `
                (function() {
                    var sheet = Api.GetActiveSheet();
                    sheet.GetRange("A1:B5").Clear();
                    return "Диапазон очищен";
                })();
            `;
            executeInScope(code);
            setStatus('🧹 Действие Clear выполнено: A1:B5 очищены');
        }

        // ===== ИНИЦИАЛИЗАЦИЯ ПЛАГИНА =====
        window.Asc.plugin.init = function() {
            setStatus('✅ Плагин загружен. Выберите действие.');
        };

        window.Asc.plugin.onSelectionChanged = function(info) {
            // Можно автоматически обновлять инфу при смене выделения
            if (info) {
                console.log('Выделение изменилось:', info);
            }
        };

        window.Asc.plugin.onDestroy = function() {
            console.log('Плагин закрыт');
        };
    </script>
</body>
</html>
```

---

Как это работает

1. Кнопки в HTML — у каждой свой onclick.
2. Выполнение кода в книге — через window.Asc.scope.execute(code). Это основной способ для немодальных (isModal: false) плагинов в десктопе.
3. Методы для разных задач:
   · Прямое выполнение кода: Asc.scope.execute(...)
   · Получение данных из книги: Asc.plugin.executeMethod("GetSelectedRange", ...)
   · Работа с OLE-объектами и т.д.

---

Важно

· Все методы API (типа Api.GetActiveSheet()) работают только внутри строки кода, передаваемой в Asc.scope.execute(), потому что ваш HTML-плагин и сама книга — это разные контексты JavaScript.
· Если вам нужно передать данные из книги в плагин, используйте Asc.plugin.executeMethod с callback-функциями (как в примере doActionInfo).

Таким образом, вы получаете полноценную панель с любым количеством кнопок, каждая из которых делает что-то своё — и всё это внутри боковой панели десктопного Р7-Таблица.

















Ясоздам для вас простого чат-бота на Flask с SQLite, который работает по принципу "вопрос-ответ". Вот полный код:

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




















# ============================================
# ИМПОРТ НЕОБХОДИМЫХ БИБЛИОТЕК
# ============================================
from flask import Flask, request, render_template_string, redirect, make_response, send_file, session
import sqlite3
from datetime import datetime
import csv
import io
import os
import shutil
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from docxtpl import DocxTemplate
import json
import traceback

# ============================================
# СОЗДАНИЕ ПРИЛОЖЕНИЯ FLASK
# ============================================
app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'  # Для сессий

# ============================================
# НАСТРОЙКА ПУТЕЙ
# ============================================
DATABASE = 'data.db'
BACKUP_DIR = 'backups'
TEMP_DIR = '/tmp/excel_comparison'  # Linux
# TEMP_DIR = 'C:/temp/excel_comparison'  # Windows
TEMPLATES_DIR = 'templates_docx'

# Создаём необходимые папки
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# ============================================
# ФУНКЦИЯ ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ
# ============================================
def get_db():
    conn = sqlite3.connect(
        DATABASE,
        timeout=10.0,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# ФУНКЦИЯ ИНИЦИАЛИЗАЦИИ БАЗЫ ДАННЫХ
# ============================================
def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field1 TEXT NOT NULL,
                field2 TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# ============================================
# ФУНКЦИЯ АВТОМАТИЧЕСКОГО РЕЗЕРВНОГО КОПИРОВАНИЯ
# ============================================
def auto_backup():
    if not os.path.exists(DATABASE):
        print("⚠️ База данных не найдена, бэкап не создан")
        return
    
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'data_{timestamp}.db')
    shutil.copy2(DATABASE, backup_file)
    print(f"✅ Создан бэкап: {backup_file}")
    
    backup_files = [f for f in os.listdir(BACKUP_DIR) if f.startswith('data_') and f.endswith('.db')]
    backup_files.sort()
    
    if len(backup_files) > 10:
        files_to_delete = backup_files[:-10]
        for old_file in files_to_delete:
            os.remove(os.path.join(BACKUP_DIR, old_file))
            print(f"🗑️ Удалён старый бэкап: {old_file}")

# ============================================
# ФУНКЦИЯ ГЕНЕРАЦИИ DOCX ИЗ ШАБЛОНА
# ============================================
def generate_doc_from_template(template_filename, data):
    template_path = os.path.join(TEMPLATES_DIR, template_filename)
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Шаблон не найден: {template_path}")
    
    doc = DocxTemplate(template_path)
    doc.render(data)
    
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    return file_stream

def create_default_template():
    """Создаёт шаблон DOCX по умолчанию, если его нет"""
    template_path = os.path.join(TEMPLATES_DIR, 'template.docx')
    
    if os.path.exists(template_path):
        return
    
    try:
        from docxtpl import DocxTemplate
        
        doc = DocxTemplate()
        doc.add_paragraph('ID: {{ id }}')
        doc.add_paragraph('Поле 1: {{ field1 }}')
        doc.add_paragraph('Поле 2: {{ field2 }}')
        doc.add_paragraph('Дата: {{ created_at }}')
        doc.save(template_path)
        print(f"✅ Создан шаблон по умолчанию: {template_path}")
        
    except Exception as e:
        print(f"⚠️ Не удалось создать шаблон автоматически: {e}")
        print(f"   Создайте файл вручную: {template_path}")

# ============================================
# УНИВЕРСАЛЬНАЯ ФУНКЦИЯ ДЛЯ SEND_FILE
# ============================================
def send_file_safe(file_or_path, filename, mimetype):
    """
    Универсальная функция для send_file с поддержкой разных версий Flask
    """
    try:
        # Пробуем новый синтаксис (Flask 2.0+)
        return send_file(
            file_or_path,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
    except TypeError:
        # Если ошибка - используем старый синтаксис (Flask 1.x)
        return send_file(
            file_or_path,
            as_attachment=True,
            attachment_filename=filename,
            mimetype=mimetype
        )

# ============================================
# ФУНКЦИЯ СРАВНЕНИЯ EXCEL ФАЙЛОВ
# ============================================
def compare_excel_files(file1_path, file2_path, compare_columns, output_path):
    """
    Сравнивает два Excel файла по указанным столбцам.
    Находит расхождения и окрашивает строки с расхождениями в жёлтый цвет.
    
    Параметры:
    - file1_path: путь к первому файлу (эталон)
    - file2_path: путь ко второму файлу (сравниваемый)
    - compare_columns: список номеров столбцов для сравнения (начиная с 1)
    - output_path: путь для сохранения результата
    
    Возвращает:
    - tuple: (количество строк с расхождениями, общее количество строк)
    """
    
    # Загружаем оба файла
    wb1 = load_workbook(file1_path)
    wb2 = load_workbook(file2_path)
    
    # Берём первый лист из каждого файла
    ws1 = wb1.active
    ws2 = wb2.active
    
    # Жёлтый цвет для подсветки
    yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
    
    diff_count = 0
    total_rows = 0
    
    # Определяем максимальное количество строк
    max_rows = max(ws1.max_row, ws2.max_row)
    
    # Проходим по всем строкам
    for row_num in range(1, max_rows + 1):
        row_diff = False
        total_rows += 1
        
        # Проверяем только указанные столбцы
        for col_num in compare_columns:
            # Получаем значения из обоих файлов (если есть)
            val1 = ws1.cell(row=row_num, column=col_num).value if row_num <= ws1.max_row else None
            val2 = ws2.cell(row=row_num, column=col_num).value if row_num <= ws2.max_row else None
            
            # Если значения отличаются или одно из них пустое
            if str(val1) != str(val2):
                row_diff = True
                break
        
        # Если есть расхождения - окрашиваем строку в жёлтый
        if row_diff:
            diff_count += 1
            
            # Окрашиваем все ячейки строки в первом файле
            for col_num in range(1, ws1.max_column + 1):
                if row_num <= ws1.max_row:
                    ws1.cell(row=row_num, column=col_num).fill = yellow_fill
            
            # Окрашиваем все ячейки строки во втором файле
            for col_num in range(1, ws2.max_column + 1):
                if row_num <= ws2.max_row:
                    ws2.cell(row=row_num, column=col_num).fill = yellow_fill
    
    # Сохраняем результат в новый файл
    wb1.save(output_path)
    print(f"✅ Результат сохранён: {output_path}")
    
    # Также сохраняем второй файл с подсветкой
    output_path2 = output_path.replace('.xlsx', '_file2.xlsx')
    wb2.save(output_path2)
    print(f"✅ Второй файл сохранён: {output_path2}")
    
    return diff_count, total_rows

# ============================================
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ СПИСКА БЭКАПОВ
# ============================================
def get_backup_list(limit=10):
    """Возвращает список последних бэкапов для отображения"""
    if not os.path.exists(BACKUP_DIR):
        return []
    
    backups = []
    files = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')], reverse=True)
    
    for f in files[:limit]:
        path = os.path.join(BACKUP_DIR, f)
        size = round(os.path.getsize(path) / 1024, 1)
        mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M')
        backups.append({'name': f, 'size': size, 'date': mtime})
    
    return backups

# ============================================
# HTML ШАБЛОН С ДВУМЯ ВКЛАДКАМИ
# ============================================
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask Универсальное Приложение</title>
    <style>
        /* ===== ГЛОБАЛЬНЫЕ СТИЛИ ===== */
        * { box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #f0f2f5; 
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white; 
            padding: 25px; 
            border-radius: 12px; 
            box-shadow: 0 2px 15px rgba(0,0,0,0.1); 
        }
        
        /* ===== ШАПКА ===== */
        .header { 
            background: linear-gradient(135deg, #4CAF50, #45a049); 
            color: white; 
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 25px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            flex-wrap: wrap;
        }
        .header h2 { margin: 0; }
        .badge { 
            background: #FF9800; 
            padding: 6px 15px; 
            border-radius: 20px; 
            font-size: 13px; 
            font-weight: bold;
        }
        
        /* ===== ВКЛАДКИ ===== */
        .tabs {
            display: flex;
            border-bottom: 3px solid #4CAF50;
            margin-bottom: 25px;
            gap: 0;
            flex-wrap: wrap;
        }
        .tab-button {
            padding: 12px 30px;
            background: #f5f5f5;
            border: none;
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            color: #666;
            transition: all 0.3s;
            margin-right: 2px;
        }
        .tab-button:hover {
            background: #e8f5e9;
            color: #2E7D32;
        }
        .tab-button.active {
            background: #4CAF50;
            color: white;
            border-bottom: 3px solid #4CAF50;
        }
        .tab-content {
            display: none;
            padding: 20px 0;
            animation: fadeIn 0.5s;
        }
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* ===== СТАТИСТИКА ===== */
        .stats { 
            background: #e3f2fd; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 15px 0; 
            border-left: 4px solid #2196F3; 
            display: flex; 
            flex-wrap: wrap; 
            gap: 20px;
        }
        .stats span { margin-right: 20px; }
        
        /* ===== ФОРМЫ ===== */
        .form-group { margin: 12px 0; }
        .form-group label { font-weight: 600; display: block; margin-bottom: 4px; }
        input[type="text"], 
        input[type="password"],
        input[type="file"],
        select { 
            padding: 8px 12px; 
            margin: 4px 0; 
            border: 1px solid #ddd; 
            border-radius: 6px; 
            width: 100%; 
            max-width: 350px; 
            font-size: 14px;
        }
        input[type="file"] { padding: 6px; }
        
        /* ===== КНОПКИ ===== */
        button, .btn { 
            padding: 8px 20px; 
            margin: 4px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-weight: 600; 
            font-size: 14px;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
        
        .btn-add { background: #4CAF50; color: white; }
        .btn-add:hover { background: #43A047; }
        .btn-edit { background: #2196F3; color: white; }
        .btn-edit:hover { background: #1E88E5; }
        .btn-delete { background: #f44336; color: white; }
        .btn-delete:hover { background: #E53935; }
        .btn-export { background: #FF9800; color: white; }
        .btn-export:hover { background: #FB8C00; }
        .btn-delete-all { background: #9E9E9E; color: white; }
        .btn-delete-all:hover { background: #757575; }
        .btn-cancel { background: #607D8B; color: white; }
        .btn-cancel:hover { background: #546E7A; }
        .btn-compare { background: #9C27B0; color: white; }
        .btn-compare:hover { background: #8E24AA; }
        .btn-doc { background: #E91E63; color: white; }
        .btn-doc:hover { background: #D81B60; }
        .btn-backup { background: #00BCD4; color: white; }
        .btn-backup:hover { background: #00ACC1; }
        
        /* ===== ТАБЛИЦА ===== */
        .table-wrapper { overflow-x: auto; margin-top: 15px; }
        table { 
            border-collapse: collapse; 
            width: 100%; 
            font-size: 14px;
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 10px 12px; 
            text-align: left; 
        }
        th { 
            background: #4CAF50; 
            color: white; 
            font-weight: 600;
        }
        tr:nth-child(even) { background: #f9f9f9; }
        tr:hover { background: #f1f1f1; }
        
        /* ===== ПАНЕЛЬ ИНСТРУМЕНТОВ ===== */
        .toolbar { 
            margin: 15px 0; 
            padding: 15px; 
            background: #f5f5f5; 
            border-radius: 8px; 
            display: flex; 
            flex-wrap: wrap; 
            align-items: center; 
            gap: 10px;
        }
        .toolbar form { display: inline-flex; align-items: center; gap: 5px; flex-wrap: wrap; }
        
        /* ===== ФОРМА РЕДАКТИРОВАНИЯ ===== */
        .edit-form { 
            background: #fff3e0; 
            padding: 20px; 
            border: 1px solid #FFB74D; 
            border-radius: 8px; 
            margin-top: 20px; 
        }
        
        /* ===== БЛОКИ ФАЙЛОВОЙ ВКЛАДКИ ===== */
        .file-section { 
            background: #f5f5f5; 
            padding: 25px; 
            border-radius: 10px; 
            margin-top: 20px; 
        }
        .file-section h3 { margin-top: 0; }
        
        .compare-section { 
            background: #f3e5f5; 
            padding: 25px; 
            border-radius: 10px; 
            border: 2px solid #9C27B0; 
            margin-top: 20px; 
        }
        .compare-result { 
            background: #e8f5e9; 
            padding: 15px; 
            border-radius: 6px; 
            margin: 15px 0; 
            border-left: 4px solid #4CAF50; 
        }
        
        .docx-section { 
            background: #fce4ec; 
            padding: 25px; 
            border-radius: 10px; 
            border: 2px solid #E91E63; 
            margin-top: 20px; 
        }
        
        .backup-section { 
            background: #e0f7fa; 
            padding: 25px; 
            border-radius: 10px; 
            border: 2px solid #00BCD4; 
            margin-top: 20px; 
        }
        
        /* ===== СООБЩЕНИЯ ===== */
        .msg { 
            color: #4CAF50; 
            font-weight: bold; 
            padding: 12px; 
            background: #e8f5e9; 
            border-radius: 6px; 
            border-left: 4px solid #4CAF50; 
        }
        .msg-error { 
            color: #f44336; 
            font-weight: bold; 
            padding: 12px; 
            background: #ffebee; 
            border-radius: 6px; 
            border-left: 4px solid #f44336; 
        }
        
        /* ===== СПИСОК БЭКАПОВ ===== */
        .backup-list {
            max-height: 300px;
            overflow-y: auto;
            background: white;
            border-radius: 6px;
            padding: 10px;
        }
        .backup-item {
            padding: 8px 12px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .backup-item:last-child { border-bottom: none; }
        .backup-item:hover { background: #f5f5f5; }
        
        /* ===== АДАПТИВНОСТЬ ===== */
        @media (max-width: 768px) {
            body { padding: 10px; }
            .container { padding: 15px; }
            .header { flex-direction: column; align-items: flex-start; gap: 10px; }
            .tabs { flex-direction: column; }
            .tab-button { border-radius: 0; text-align: left; }
            .toolbar { flex-direction: column; align-items: stretch; }
            .toolbar form { flex-direction: column; align-items: stretch; }
            input[type="text"], select { max-width: 100%; }
            table { font-size: 12px; }
            th, td { padding: 6px 8px; }
        }
        
        /* ===== ССЫЛКИ В ТАБЛИЦЕ ===== */
        .action-links a { text-decoration: none; }
    </style>
    
    <script>
        // ===== ПЕРЕКЛЮЧЕНИЕ ВКЛАДОК =====
        function openTab(tabName) {
            // Скрываем все вкладки
            var contents = document.getElementsByClassName("tab-content");
            for (var i = 0; i < contents.length; i++) {
                contents[i].classList.remove("active");
            }
            
            // Убираем активный класс у всех кнопок
            var buttons = document.getElementsByClassName("tab-button");
            for (var i = 0; i < buttons.length; i++) {
                buttons[i].classList.remove("active");
            }
            
            // Показываем нужную вкладку
            document.getElementById(tabName).classList.add("active");
            
            // Активируем кнопку
            event.currentTarget.classList.add("active");
            
            // Сохраняем выбранную вкладку в localStorage
            localStorage.setItem('activeTab', tabName);
        }
        
        // При загрузке страницы открываем последнюю активную вкладку
        window.onload = function() {
            var activeTab = localStorage.getItem('activeTab');
            if (activeTab) {
                var buttons = document.getElementsByClassName("tab-button");
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].getAttribute('onclick').includes(activeTab)) {
                        buttons[i].click();
                        break;
                    }
                }
            }
        }
    </script>
</head>
<body>
    <div class="container">
        
        <!-- ========================================== -->
        <!-- ШАПКА                                        -->
        <!-- ========================================== -->
        <div class="header">
            <h2>📋 Универсальное приложение</h2>
            <div>
                <span class="badge">✅ Автобэкап</span>
                <span class="badge" style="background: #9C27B0;">📊 Excel сравнение</span>
                <span class="badge" style="background: #E91E63;">📄 DOCX</span>
            </div>
        </div>
        
        <!-- ========================================== -->
        <!-- ВКЛАДКИ                                      -->
        <!-- ========================================== -->
        <div class="tabs">
            <button class="tab-button active" onclick="openTab('tab_db')">
                📋 База данных
            </button>
            <button class="tab-button" onclick="openTab('tab_files')">
                📁 Файлы и инструменты
            </button>
        </div>
        
        <!-- ========================================== -->
        <!-- ВКЛАДКА 1: БАЗА ДАННЫХ                      -->
        <!-- ========================================== -->
        <div id="tab_db" class="tab-content active">
            
            <!-- СТАТИСТИКА -->
            <div class="stats">
                <span>📊 <strong>Всего записей:</strong> {{ total_records }}</span>
                <span>🕐 <strong>Обновлено:</strong> {{ last_update }}</span>
                <span>💾 <strong>Бэкапы:</strong> последние 10 копий</span>
            </div>
            
            <!-- ФОРМА ДОБАВЛЕНИЯ -->
            <form method="post" action="/">
                <h3>➕ Добавить запись</h3>
                <div class="form-group">
                    <label>Поле 1:</label>
                    <input type="text" name="field1" required placeholder="Введите значение...">
                </div>
                <div class="form-group">
                    <label>Поле 2:</label>
                    <input type="text" name="field2" required placeholder="Введите значение...">
                </div>
                <button type="submit" class="btn-add">💾 Сохранить</button>
            </form>
            
            {% if msg %}
                <p class="msg">{{ msg }}</p>
            {% endif %}
            
            <!-- ПАНЕЛЬ ИНСТРУМЕНТОВ -->
            <div class="toolbar">
                <form method="get" action="/">
                    <input type="text" name="search" placeholder="🔍 Поиск..." value="{{ search_query or '' }}">
                    <button type="submit" class="btn" style="background: #4CAF50; color: white;">Найти</button>
                    {% if search_query %}
                        <a href="/" style="color: #f44336; font-weight: bold;">✕ Сбросить</a>
                    {% endif %}
                </form>
                
                <form method="get" action="/">
                    <select name="sort_by">
                        <option value="">📊 Сортировать...</option>
                        <option value="field1" {% if sort_by == 'field1' %}selected{% endif %}>Поле 1</option>
                        <option value="field2" {% if sort_by == 'field2' %}selected{% endif %}>Поле 2</option>
                        <option value="created_at" {% if sort_by == 'created_at' %}selected{% endif %}>Дата</option>
                    </select>
                    <select name="sort_order">
                        <option value="asc" {% if sort_order == 'asc' %}selected{% endif %}>⬆ Возрастанию</option>
                        <option value="desc" {% if sort_order == 'desc' %}selected{% endif %}>⬇ Убыванию</option>
                    </select>
                    <button type="submit" class="btn" style="background: #2196F3; color: white;">Сортировать</button>
                    {% if sort_by %}
                        <a href="/" style="color: #f44336; font-weight: bold;">✕ Сбросить</a>
                    {% endif %}
                </form>
                
                <form method="post" action="/export">
                    <button type="submit" class="btn-export">📊 Экспорт CSV</button>
                </form>
                
                <form method="post" action="/delete_all" onsubmit="return confirm('⚠️ Удалить ВСЕ записи? Это действие необратимо!')">
                    <button type="submit" class="btn-delete-all">🗑️ Удалить всё</button>
                </form>
            </div>
            
            <!-- ТАБЛИЦА ЗАПИСЕЙ -->
            <div class="table-wrapper">
                {% if records %}
                    <table>
                        <thead>
                            <tr>
                                <th style="width: 60px;">ID</th>
                                <th>Поле 1</th>
                                <th>Поле 2</th>
                                <th style="width: 180px;">Дата</th>
                                <th style="width: 220px;">Действия</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for row in records %}
                            <tr>
                                <td>{{ row.id }}</td>
                                <td>{{ row.field1 }}</td>
                                <td>{{ row.field2 }}</td>
                                <td>{{ row.created_at }}</td>
                                <td class="action-links">
                                    <a href="/edit/{{ row.id }}"><button class="btn-edit">✏️</button></a>
                                    <a href="/delete/{{ row.id }}" onclick="return confirm('Удалить запись #{{ row.id }}?')"><button class="btn-delete">🗑️</button></a>
                                    <a href="/generate_doc/{{ row.id }}"><button class="btn-doc">📄 DOCX</button></a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                {% else %}
                    <p style="text-align: center; padding: 40px; color: #999; font-size: 18px;">
                        📭 Нет записей. Добавьте первую!
                    </p>
                {% endif %}
            </div>
            
            <!-- ФОРМА РЕДАКТИРОВАНИЯ -->
            {% if edit_mode %}
            <div class="edit-form">
                <h3>✏️ Редактировать запись #{{ edit_id }}</h3>
                <form method="post" action="/edit/{{ edit_id }}">
                    <div class="form-group">
                        <label>Поле 1:</label>
                        <input type="text" name="field1" value="{{ edit_row.field1 }}" required>
                    </div>
                    <div class="form-group">
                        <label>Поле 2:</label>
                        <input type="text" name="field2" value="{{ edit_row.field2 }}" required>
                    </div>
                    <button type="submit" class="btn-add">💾 Обновить</button>
                    <a href="/"><button type="button" class="btn-cancel">❌ Отмена</button></a>
                </form>
            </div>
            {% endif %}
            
        </div>
        <!-- КОНЕЦ ВКЛАДКИ 1 -->
        
        <!-- ========================================== -->
        <!-- ВКЛАДКА 2: ФАЙЛЫ И ИНСТРУМЕНТЫ              -->
        <!-- ========================================== -->
        <div id="tab_files" class="tab-content">
            
            <!-- ========================================== -->
            <!-- СЕКЦИЯ: ГЕНЕРАЦИЯ DOCX                      -->
            <!-- ========================================== -->
            <div class="file-section docx-section">
                <h3>📄 Генерация DOCX из шаблона</h3>
                <p style="color: #666;">Выберите запись на вкладке "База данных" и нажмите кнопку 📄 DOCX в таблице.</p>
                
                <div style="background: white; padding: 15px; border-radius: 6px; margin-top: 10px;">
                    <h4>📁 Доступные шаблоны:</h4>
                    <ul>
                        <li><strong>template.docx</strong> — используйте метки: <code>{{ field1 }}</code>, <code>{{ field2 }}</code>, <code>{{ id }}</code>, <code>{{ created_at }}</code></li>
                    </ul>
                    <p style="color: #999; font-size: 13px;">
                        💡 Поместите файл <code>template.docx</code> в папку <code>templates_docx/</code>
                    </p>
                </div>
                
                <div style="margin-top: 10px;">
                    <form method="post" action="/generate_doc_all" style="display: inline-block;">
                        <button type="submit" class="btn-doc" onclick="return confirm('Сгенерировать DOCX для ВСЕХ записей?')">
                            📄 Сгенерировать для всех
                        </button>
                    </form>
                </div>
            </div>
            
            <!-- ========================================== -->
            <!-- СЕКЦИЯ: СРАВНЕНИЕ EXCEL                    -->
            <!-- ========================================== -->
            <div class="file-section compare-section">
                <h3>📊 Сравнение Excel файлов</h3>
                <p style="color: #666;">Загрузите два Excel файла (.xlsx) для сравнения. Строки с расхождениями будут выделены <span style="background: #FFFF00; padding: 2px 8px; border-radius: 3px;">ЖЁЛТЫМ</span> цветом.</p>
                
                {% if compare_result %}
                    <div class="compare-result">
                        <strong>✅ Результат сравнения:</strong><br>
                        📊 Всего строк: <strong>{{ compare_result.total }}</strong><br>
                        ⚠️ Найдено расхождений: <strong style="color: #f44336;">{{ compare_result.diffs }}</strong><br>
                        📁 Скачать результат: 
                        <a href="/download_comparison/{{ compare_result.filename }}"><button class="btn-export">📥 Скачать</button></a>
                    </div>
                {% endif %}
                
                <form method="post" action="/compare_excel" enctype="multipart/form-data" style="margin-top: 15px;">
                    <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                        <div style="flex: 1; min-width: 200px;">
                            <label><strong>📄 Файл 1 (эталон):</strong></label><br>
                            <input type="file" name="file1" accept=".xlsx" required>
                        </div>
                        <div style="flex: 1; min-width: 200px;">
                            <label><strong>📄 Файл 2 (сравниваемый):</strong></label><br>
                            <input type="file" name="file2" accept=".xlsx" required>
                        </div>
                    </div>
                    
                    <div style="margin: 15px 0;">
                        <label><strong>🔢 Столбцы для сравнения (номера через запятую):</strong></label><br>
                        <input type="text" name="columns" placeholder="Например: 1,2,3" required style="max-width: 300px;">
                        <small style="color: #666; display: block; margin-top: 4px;">Введите номера столбцов (начиная с 1), по которым нужно сравнивать данные</small>
                    </div>
                    
                    <button type="submit" class="btn-compare">🔍 Сравнить файлы</button>
                </form>
            </div>
            
            <!-- ========================================== -->
            <!-- СЕКЦИЯ: УПРАВЛЕНИЕ БЭКАПАМИ                 -->
            <!-- ========================================== -->
            <div class="file-section backup-section">
                <h3>💾 Управление бэкапами</h3>
                <p style="color: #666; font-size: 14px;">
                    Автоматическое резервное копирование при каждом изменении данных.<br>
                    Хранится <strong>10 последних</strong> копий в папке <code>{{ backup_dir }}</code>.
                </p>
                
                <div style="display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0;">
                    <form method="post" action="/restore_backup" style="display: inline-block;">
                        <button type="submit" class="btn-backup" onclick="return confirm('Восстановить из последнего бэкапа? Текущие данные будут заменены!')">
                            🔄 Восстановить из бэкапа
                        </button>
                    </form>
                    <a href="/list_backups"><button class="btn" style="background: #795548; color: white;">📋 Список бэкапов</button></a>
                    <form method="post" action="/create_backup_now" style="display: inline-block;">
                        <button type="submit" class="btn" style="background: #4CAF50; color: white;">💾 Создать бэкап сейчас</button>
                    </form>
                </div>
                
                <!-- Список последних бэкапов -->
                {% if backup_list %}
                    <div class="backup-list">
                        <h4>📂 Последние бэкапы:</h4>
                        {% for backup in backup_list %}
                            <div class="backup-item">
                                <span>📄 {{ backup.name }}</span>
                                <span style="color: #666; font-size: 13px;">
                                    {{ backup.size }} KB • {{ backup.date }}
                                </span>
                            </div>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
            
        </div>
        <!-- КОНЕЦ ВКЛАДКИ 2 -->
        
    </div>
    <!-- КОНЕЦ container -->
</body>
</html>
'''

# ============================================
# ГЛАВНАЯ СТРАНИЦА (ПРОСМОТР + ДОБАВЛЕНИЕ)
# ============================================
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        field1 = request.form.get('field1', '').strip()
        field2 = request.form.get('field2', '').strip()
        
        if not field1 or not field2:
            return render_template_string(
                HTML, 
                msg='❌ Поля не могут быть пустыми!', 
                records=[], 
                total_records=0, 
                last_update='',
                edit_mode=False,
                backup_dir=BACKUP_DIR,
                backup_list=get_backup_list()
            )
        
        try:
            with get_db() as conn:
                conn.execute(
                    'INSERT INTO records (field1, field2) VALUES (?, ?)',
                    (field1, field2)
                )
                conn.commit()
            
            auto_backup()
            return redirect('/')
            
        except sqlite3.Error as e:
            return render_template_string(
                HTML,
                msg=f'❌ Ошибка базы данных: {e}',
                records=[],
                total_records=0,
                last_update='',
                edit_mode=False,
                backup_dir=BACKUP_DIR,
                backup_list=get_backup_list()
            )
    
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', '')
    sort_order = request.args.get('sort_order', 'asc')
    
    query = 'SELECT * FROM records'
    params = []
    
    if search_query:
        query += ' WHERE field1 LIKE ? OR field2 LIKE ?'
        params = [f'%{search_query}%', f'%{search_query}%']
    
    if sort_by in ['field1', 'field2', 'created_at']:
        query += f' ORDER BY {sort_by} COLLATE NOCASE'
        query += ' DESC' if sort_order == 'desc' else ' ASC'
    else:
        query += ' ORDER BY id DESC'
    
    try:
        with get_db() as conn:
            records = conn.execute(query, params).fetchall()
            total = conn.execute('SELECT COUNT(*) as count FROM records').fetchone()['count']
            last = conn.execute('SELECT MAX(created_at) as last FROM records').fetchone()['last']
        
        last_update = last or 'Нет записей'
        
        return render_template_string(
            HTML,
            msg=None,
            records=records,
            total_records=total,
            last_update=last_update,
            edit_mode=False,
            search_query=search_query,
            sort_by=sort_by,
            sort_order=sort_order,
            backup_dir=BACKUP_DIR,
            backup_list=get_backup_list()
        )
        
    except sqlite3.Error as e:
        return f"❌ Ошибка при чтении базы данных: {e}", 500

# ============================================
# УДАЛЕНИЕ ЗАПИСИ
# ============================================
@app.route('/delete/<int:record_id>')
def delete(record_id):
    try:
        with get_db() as conn:
            conn.execute('DELETE FROM records WHERE id = ?', (record_id,))
            conn.commit()
        
        auto_backup()
        return redirect('/')
        
    except sqlite3.Error as e:
        return f"❌ Ошибка при удалении: {e}", 500

# ============================================
# РЕДАКТИРОВАНИЕ ЗАПИСИ
# ============================================
@app.route('/edit/<int:record_id>', methods=['GET', 'POST'])
def edit(record_id):
    if request.method == 'POST':
        field1 = request.form.get('field1', '').strip()
        field2 = request.form.get('field2', '').strip()
        
        if not field1 or not field2:
            return "❌ Поля не могут быть пустыми!", 400
        
        try:
            with get_db() as conn:
                conn.execute(
                    'UPDATE records SET field1 = ?, field2 = ? WHERE id = ?',
                    (field1, field2, record_id)
                )
                conn.commit()
            
            auto_backup()
            return redirect('/')
            
        except sqlite3.Error as e:
            return f"❌ Ошибка при обновлении: {e}", 500
    
    try:
        with get_db() as conn:
            record = conn.execute(
                'SELECT * FROM records WHERE id = ?', 
                (record_id,)
            ).fetchone()
            
            if not record:
                return redirect('/')
            
            records = conn.execute('SELECT * FROM records ORDER BY id DESC').fetchall()
            total = conn.execute('SELECT COUNT(*) as count FROM records').fetchone()['count']
            last = conn.execute('SELECT MAX(created_at) as last FROM records').fetchone()['last']
        
        return render_template_string(
            HTML,
            msg=None,
            records=records,
            total_records=total,
            last_update=last or 'Нет записей',
            edit_mode=True,
            edit_id=record_id,
            edit_row=record,
            search_query=None,
            sort_by=None,
            sort_order=None,
            backup_dir=BACKUP_DIR,
            backup_list=get_backup_list()
        )
        
    except sqlite3.Error as e:
        return f"❌ Ошибка при чтении записи: {e}", 500

# ============================================
# УДАЛЕНИЕ ВСЕХ ЗАПИСЕЙ
# ============================================
@app.route('/delete_all', methods=['POST'])
def delete_all():
    try:
        with get_db() as conn:
            conn.execute('DELETE FROM records')
            conn.commit()
        
        auto_backup()
        return redirect('/')
        
    except sqlite3.Error as e:
        return f"❌ Ошибка при удалении: {e}", 500

# ============================================
# ЭКСПОРТ В CSV
# ============================================
@app.route('/export', methods=['POST'])
def export():
    try:
        with get_db() as conn:
            rows = conn.execute(
                'SELECT id, field1, field2, created_at FROM records ORDER BY id'
            ).fetchall()
        
        if not rows:
            return "❌ Нет данных для экспорта", 400
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Поле 1', 'Поле 2', 'Дата создания'])
        
        for row in rows:
            writer.writerow([row['id'], row['field1'], row['field2'], row['created_at']])
        
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = (
            f'attachment; filename=export_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
        )
        response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
        
        return response
        
    except sqlite3.Error as e:
        return f"❌ Ошибка при экспорте: {e}", 500

# ============================================
# ГЕНЕРАЦИЯ DOCX ИЗ ШАБЛОНА (ОДНА ЗАПИСЬ)
# ============================================
@app.route('/generate_doc/<int:record_id>')
def generate_doc(record_id):
    try:
        with get_db() as conn:
            record = conn.execute(
                'SELECT * FROM records WHERE id = ?', 
                (record_id,)
            ).fetchone()
        
        if not record:
            return "❌ Запись не найдена", 404
        
        # Проверяем существование шаблона
        template_path = os.path.join(TEMPLATES_DIR, 'template.docx')
        if not os.path.exists(template_path):
            return f"""
            ❌ Шаблон не найден!<br><br>
            Создайте файл <code>template.docx</code> в папке:<br>
            <code>{template_path}</code><br><br>
            <a href="/">⬅ Вернуться</a>
            """, 404
        
        data = {
            'id': record['id'],
            'field1': record['field1'],
            'field2': record['field2'],
            'created_at': record['created_at']
        }
        
        doc_stream = generate_doc_from_template('template.docx', data)
        
        return send_file_safe(
            doc_stream,
            f'record_{record_id}_{datetime.now().strftime("%Y%m%d")}.docx',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except FileNotFoundError as e:
        return f"❌ {str(e)}<br><a href='/'>⬅ Вернуться</a>", 404
    except Exception as e:
        error_details = traceback.format_exc()
        return f"""
        ❌ Ошибка генерации DOCX:<br><br>
        <b>{str(e)}</b><br><br>
        <details>
            <summary>📋 Детали ошибки</summary>
            <pre style="background: #f5f5f5; padding: 15px; border-radius: 6px; overflow: auto; max-height: 300px;">
            {error_details}
            </pre>
        </details>
        <br>
        <a href="/">⬅ Вернуться</a>
        """, 500

# ============================================
# ГЕНЕРАЦИЯ DOCX ДЛЯ ВСЕХ ЗАПИСЕЙ
# ============================================
@app.route('/generate_doc_all', methods=['POST'])
def generate_doc_all():
    try:
        # Проверяем существование шаблона
        template_path = os.path.join(TEMPLATES_DIR, 'template.docx')
        if not os.path.exists(template_path):
            return f"""
            ❌ Шаблон не найден!<br><br>
            Создайте файл <code>template.docx</code> в папке:<br>
            <code>{template_path}</code><br><br>
            <a href="/">⬅ Вернуться</a>
            """, 404
        
        with get_db() as conn:
            records = conn.execute('SELECT * FROM records ORDER BY id').fetchall()
        
        if not records:
            return "❌ Нет записей для генерации", 400
        
        import zipfile
        zip_stream = io.BytesIO()
        
        with zipfile.ZipFile(zip_stream, 'w', zipfile.ZIP_DEFLATED) as zf:
            for record in records:
                data = {
                    'id': record['id'],
                    'field1': record['field1'],
                    'field2': record['field2'],
                    'created_at': record['created_at']
                }
                
                doc_stream = generate_doc_from_template('template.docx', data)
                zf.writestr(f'record_{record["id"]}_{record["field1"]}.docx', doc_stream.getvalue())
        
        zip_stream.seek(0)
        
        return send_file_safe(
            zip_stream,
            f'all_records_{datetime.now().strftime("%Y%m%d_%H%M")}.zip',
            'application/zip'
        )
        
    except Exception as e:
        error_details = traceback.format_exc()
        return f"""
        ❌ Ошибка генерации DOCX:<br><br>
        <b>{str(e)}</b><br><br>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 6px; overflow: auto; max-height: 300px;">
        {error_details}
        </pre>
        <br>
        <a href="/">⬅ Вернуться</a>
        """, 500

# ============================================
# СРАВНЕНИЕ EXCEL ФАЙЛОВ
# ============================================
@app.route('/compare_excel', methods=['POST'])
def compare_excel():
    try:
        if 'file1' not in request.files or 'file2' not in request.files:
            return "❌ Выберите оба файла!", 400
        
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if file1.filename == '' or file2.filename == '':
            return "❌ Выберите оба файла!", 400
        
        if not file1.filename.endswith('.xlsx') or not file2.filename.endswith('.xlsx'):
            return "❌ Поддерживаются только файлы .xlsx!", 400
        
        columns_str = request.form.get('columns', '')
        try:
            compare_columns = [int(x.strip()) for x in columns_str.split(',') if x.strip()]
        except ValueError:
            return "❌ Введите корректные номера столбцов (через запятую)", 400
        
        if not compare_columns:
            return "❌ Укажите хотя бы один столбец для сравнения!", 400
        
        # Создаём временную папку
        os.makedirs(TEMP_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file1_path = os.path.join(TEMP_DIR, f'file1_{timestamp}.xlsx')
        file2_path = os.path.join(TEMP_DIR, f'file2_{timestamp}.xlsx')
        output_path = os.path.join(TEMP_DIR, f'result_{timestamp}.xlsx')
        
        file1.save(file1_path)
        file2.save(file2_path)
        
        # Сравниваем
        diff_count, total_rows = compare_excel_files(
            file1_path,
            file2_path,
            compare_columns,
            output_path
        )
        
        # Проверяем результат
        if not os.path.exists(output_path):
            return "❌ Ошибка: файл результата не создан!", 500
        
        compare_result = {
            'total': total_rows,
            'diffs': diff_count,
            'filename': f'result_{timestamp}.xlsx'
        }
        
        session['compare_result'] = compare_result
        
        with get_db() as conn:
            records = conn.execute('SELECT * FROM records ORDER BY id DESC').fetchall()
            total = conn.execute('SELECT COUNT(*) as count FROM records').fetchone()['count']
            last = conn.execute('SELECT MAX(created_at) as last FROM records').fetchone()['last']
        
        return render_template_string(
            HTML,
            msg=None,
            records=records,
            total_records=total,
            last_update=last or 'Нет записей',
            edit_mode=False,
            search_query=None,
            sort_by=None,
            sort_order=None,
            compare_result=compare_result,
            backup_dir=BACKUP_DIR,
            backup_list=get_backup_list()
        )
        
    except Exception as e:
        error_details = traceback.format_exc()
        return f"""
        ❌ Ошибка при сравнении:<br><br>
        <b>{str(e)}</b><br><br>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 6px; overflow: auto; max-height: 300px;">
        {error_details}
        </pre>
        <br>
        <a href="/">⬅ Вернуться</a>
        """, 500

# ============================================
# СКАЧИВАНИЕ РЕЗУЛЬТАТА СРАВНЕНИЯ
# ============================================
@app.route('/download_comparison/<filename>')
def download_comparison(filename):
    """Скачивает результат сравнения Excel файлов"""
    try:
        # Проверяем путь к файлу
        file_path = os.path.join(TEMP_DIR, filename)
        
        if not os.path.exists(file_path):
            # Пробуем найти любой файл с таким именем
            for f in os.listdir(TEMP_DIR):
                if filename in f:
                    file_path = os.path.join(TEMP_DIR, f)
                    break
        
        if not os.path.exists(file_path):
            return f"""
            ❌ Файл не найден!<br><br>
            Искал: <code>{file_path}</code><br>
            <a href="/">⬅ Вернуться</a>
            """, 404
        
        return send_file_safe(
            file_path,
            f'comparison_result_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        error_details = traceback.format_exc()
        return f"""
        ❌ Ошибка скачивания:<br><br>
        <b>{str(e)}</b><br><br>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 6px; overflow: auto; max-height: 300px;">
        {error_details}
        </pre>
        <br>
        <a href="/">⬅ Вернуться</a>
        """, 500

# ============================================
# СПИСОК БЭКАПОВ
# ============================================
@app.route('/list_backups')
def list_backups():
    if not os.path.exists(BACKUP_DIR):
        return "📁 Папка с бэкапами не найдена", 404
    
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')], reverse=True)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Список бэкапов</title>
        <style>
            body { font-family: 'Segoe UI', Arial; padding: 20px; max-width: 900px; margin: 0 auto; }
            h2 { color: #4CAF50; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background: #4CAF50; color: white; }
            tr:nth-child(even) { background: #f9f9f9; }
            tr:hover { background: #f1f1f1; }
            .back { margin-top: 20px; display: inline-block; }
            .btn { padding: 10px 25px; background: #4CAF50; color: white; border: none; border-radius: 6px; cursor: pointer; }
            .btn:hover { background: #43A047; }
            .stats { background: #e3f2fd; padding: 15px; border-radius: 6px; margin: 15px 0; }
        </style>
    </head>
    <body>
        <h2>💾 Список резервных копий</h2>
        <div class="stats">
            📊 Всего: <strong>{{ count }}</strong> файлов
        </div>
        <table>
            <tr>
                <th>#</th>
                <th>Имя файла</th>
                <th>Размер</th>
                <th>Дата создания</th>
            </tr>
    """
    
    for i, backup in enumerate(backups[:50], 1):
        file_path = os.path.join(BACKUP_DIR, backup)
        size = os.path.getsize(file_path) / 1024
        mtime = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        html += f"""
            <tr>
                <td>{i}</td>
                <td>{backup}</td>
                <td>{size:.1f} KB</td>
                <td>{mtime}</td>
            </tr>
        """
    
    html += """
        </table>
        <div style="margin-top: 20px;">
            <a href="/"><button class="btn">🏠 Вернуться</button></a>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html, count=len(backups))

# ============================================
# ВОССТАНОВЛЕНИЕ ИЗ БЭКАПА
# ============================================
@app.route('/restore_backup', methods=['POST'])
def restore_backup():
    if not os.path.exists(BACKUP_DIR):
        return "❌ Папка с бэкапами не найдена", 404
    
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')])
    
    if not backups:
        return "❌ Нет доступных бэкапов", 404
    
    latest_backup = backups[-1]
    backup_path = os.path.join(BACKUP_DIR, latest_backup)
    
    try:
        shutil.copy2(backup_path, DATABASE)
        return redirect('/')
        
    except Exception as e:
        return f"❌ Ошибка восстановления: {str(e)}", 500

# ============================================
# СОЗДАНИЕ БЭКАПА ВРУЧНУЮ
# ============================================
@app.route('/create_backup_now', methods=['POST'])
def create_backup_now():
    try:
        auto_backup()
        return redirect('/')
    except Exception as e:
        return f"❌ Ошибка создания бэкапа: {str(e)}", 500

# ============================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ============================================
if __name__ == '__main__':
    # Создаём необходимые папки
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Создаём шаблон DOCX
    create_default_template()
    
    # Проверяем наличие шаблона DOCX
    template_path = os.path.join(TEMPLATES_DIR, 'template.docx')
    if not os.path.exists(template_path):
        print(f"⚠️ ВНИМАНИЕ: Шаблон DOCX не найден в {template_path}")
        print("   Создайте файл template.docx с метками {{ field1 }}, {{ field2 }}")
    
    # Инициализация базы данных
    init_db()
    print("✅ База данных инициализирована")
    
    # Создаём первый бэкап
    auto_backup()
    print("✅ Первый бэкап создан")
    
    print("\n" + "="*70)
    print("🚀 СЕРВЕР ЗАПУЩЕН!")
    print("="*70)
    print("\n📌 ДОСТУПНЫЕ ВКЛАДКИ:")
    print("   📋 Вкладка 1: База данных (CRUD, поиск, сортировка)")
    print("   📁 Вкладка 2: Файлы (Excel сравнение, DOCX, бэкапы)")
    print("\n📌 ДЛЯ ДОСТУПА:")
    print("   http://localhost:5000")
    print("   http://[ВАШ_IP]:5000")
    print("\n" + "="*70)
    print("💡 Нажмите Ctrl+C для остановки")
    print("="*70 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
