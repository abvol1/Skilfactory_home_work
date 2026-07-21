
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; padding: 10px; background: #f5f5f5; }
        button { padding: 12px; margin: 5px; width: 100%; cursor: pointer; font-size: 14px; background: #4CAF50; color: white; border: none; border-radius: 5px; }
        button:hover { background: #45a049; }
        textarea { width: 100%; height: 350px; font-family: monospace; font-size: 11px; background: #1e1e1e; color: #0f0; padding: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <h3>🎯 Быстрый тест</h3>
    
    <button onclick="testWb()">1. Проверить api.wb</button>
    <button onclick="testWbMethods()">2. Только методы wb</button>
    <button onclick="testWbSheet()">3. wb.getActiveSheet()</button>
    <button onclick="testWbRange()">4. wb.GetRange("A1")</button>
    <button onclick="testAscAsc()">5. window.parent.Asc напрямую</button>
    <button onclick="clearLog()">🧹 Очистить</button>
    
    <textarea id="log"></textarea>

    <script>
        var el = document.getElementById('log');
        function log(msg) { el.value += msg + '\n'; el.scrollTop = el.scrollHeight; }
        function clearLog() { el.value = ''; }

        function getApi() { return window.parent.g_asc_plugins && window.parent.g_asc_plugins.api; }

        function testWb() {
            log('=== Тест api.wb ===');
            try {
                var api = getApi();
                if (!api) { log('❌ api недоступен'); return; }
                if (!api.wb) { log('❌ api.wb отсутствует'); return; }
                
                log('✅ api.wb существует');
                log('Тип wb: ' + typeof api.wb);
                log('Конструктор: ' + (api.wb.constructor ? api.wb.constructor.name : 'неизвестно'));
                
                // Проверяем только 3 ключевых свойства
                log('wb.getActiveSheet: ' + typeof api.wb.getActiveSheet);
                log('wb.getActiveWorksheet: ' + typeof api.wb.getActiveWorksheet);
                log('wb.GetActiveSheet: ' + typeof api.wb.GetActiveSheet);
                log('wb.activeSheet: ' + typeof api.wb.activeSheet);
                log('wb.ActiveSheet: ' + typeof api.wb.ActiveSheet);
                
            } catch(e) {
                log('❌ Ошибка: ' + e.message);
            }
        }

        function testWbMethods() {
            log('=== Методы wb ===');
            try {
                var api = getApi();
                if (!api || !api.wb) { log('❌ wb недоступен'); return; }
                
                var count = 0;
                for (var k in api.wb) {
                    if (typeof api.wb[k] === 'function' && count < 40) {
                        log('  ' + k + '()');
                        count++;
                    }
                }
                log('Показано функций: ' + count);
                
            } catch(e) {
                log('❌ Ошибка: ' + e.message);
            }
        }

        function testWbSheet() {
            log('=== Получение активного листа ===');
            try {
                var api = getApi();
                if (!api || !api.wb) return;
                
                var sheet = null;
                
                if (typeof api.wb.getActiveSheet === 'function') {
                    sheet = api.wb.getActiveSheet();
                    log('getActiveSheet(): ' + sheet);
                }
                if (typeof api.wb.getActiveWorksheet === 'function') {
                    sheet = api.wb.getActiveWorksheet();
                    log('getActiveWorksheet(): ' + sheet);
                }
                if (typeof api.wb.GetActiveSheet === 'function') {
                    sheet = api.wb.GetActiveSheet();
                    log('GetActiveSheet(): ' + sheet);
                }
                
                if (sheet && typeof sheet === 'object') {
                    log('✅ Лист получен! Его методы:');
                    for (var k in sheet) {
                        if (typeof sheet[k] === 'function') {
                            log('  ' + k + '()');
                        }
                    }
                }
                
            } catch(e) {
                log('❌ Ошибка: ' + e.message);
            }
        }

        function testWbRange() {
            log('=== Работа с ячейкой A1 ===');
            try {
                var api = getApi();
                if (!api || !api.wb) return;
                
                // Пробуем GetRange
                if (typeof api.wb.GetRange === 'function') {
                    var range = api.wb.GetRange('A1');
                    log('GetRange("A1"): ' + range);
                    if (range && typeof range.SetValue === 'function') {
                        range.SetValue('УРА!!! ЗАРАБОТАЛО!');
                        log('✅ Значение установлено!');
                    }
                }
                
                // Пробуем getRange
                if (typeof api.wb.getRange === 'function') {
                    var range2 = api.wb.getRange('A1');
                    log('getRange("A1"): ' + range2);
                }
                
            } catch(e) {
                log('❌ Ошибка: ' + e.message);
            }
        }

        function testAscAsc() {
            log('=== window.parent.Asc ===');
            try {
                var Asc = window.parent.Asc;
                if (!Asc) { log('❌ Asc недоступен'); return; }
                
                log('Тип Asc: ' + typeof Asc);
                
                // Ищем editor
                log('Asc.editor: ' + typeof Asc.editor);
                log('Asc.spreadsheet: ' + typeof Asc.spreadsheet);
                log('Asc.api: ' + typeof Asc.api);
                
                // Пробуем Asc.editor
                if (Asc.editor) {
                    log('\nМетоды Asc.editor:');
                    for (var k in Asc.editor) {
                        if (typeof Asc.editor[k] === 'function') {
                            log('  ' + k + '()');
                        }
                    }
                }
                
            } catch(e) {
                log('❌ Ошибка: ' + e.message);
            }
        }

        window.onload = function() {
            log('=== Плагин готов ===');
            log('Нажимайте кнопки 1-5 по порядку');
        };
    </script>
</body>
</html>
