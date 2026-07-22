<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; padding: 10px; background: #f5f5f5; }
        button { padding: 12px; margin: 5px; width: 100%; cursor: pointer; font-size: 14px; background: #E91E63; color: white; border: none; border-radius: 5px; }
        textarea { width: 100%; height: 300px; font-family: monospace; font-size: 11px; background: #1e1e1e; color: #0f0; padding: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <h3>🔍 Подробный лог ошибок</h3>
    
    <button onclick="test1()">1. CreateColorFromRGB + asc_setCellFill</button>
    <button onclick="test2()">2. CreateColorFromRGB + asc_setCellBackgroundColor</button>
    <button onclick="test3()">3. CreateRGBColor + asc_setCellFill</button>
    <button onclick="clearLog()">🧹 Очистить</button>
    
    <textarea id="log"></textarea>

    <script>
        var el = document.getElementById('log');
        function log(msg) { el.value += msg + '\n'; el.scrollTop = el.scrollHeight; }
        function clearLog() { el.value = ''; }

        function api() { return window.parent.Asc.editor; }

        function test1() {
            log('=== Тест 1: CreateColorFromRGB + asc_setCellFill ===');
            try {
                var editor = api();
                log('CreateColorFromRGB существует: ' + (typeof editor.CreateColorFromRGB));
                var color = editor.CreateColorFromRGB(255, 215, 0);
                log('color: ' + typeof color + ' = ' + JSON.stringify(color));
                
                log('asc_setCellFill существует: ' + (typeof editor.asc_setCellFill));
                editor.asc_setCellFill('B1', color);
                log('Выполнено без ошибок');
            } catch(e) {
                log('❌ ОШИБКА: ' + e.message);
                log('   стек: ' + (e.stack ? e.stack.split('\n').slice(0,3).join('\n') : 'нет'));
            }
        }

        function test2() {
            log('\n=== Тест 2: CreateColorFromRGB + asc_setCellBackgroundColor ===');
            try {
                var editor = api();
                var color = editor.CreateColorFromRGB(135, 206, 235);
                editor.asc_setCellBackgroundColor('B2', color);
                log('Выполнено без ошибок');
            } catch(e) {
                log('❌ ОШИБКА: ' + e.message);
                log('   стек: ' + (e.stack ? e.stack.split('\n').slice(0,3).join('\n') : 'нет'));
            }
        }

        function test3() {
            log('\n=== Тест 3: CreateRGBColor + asc_setCellFill ===');
            try {
                var editor = api();
                log('CreateRGBColor существует: ' + (typeof editor.CreateRGBColor));
                if (typeof editor.CreateRGBColor === 'function') {
                    var color = editor.CreateRGBColor(255, 182, 193);
                    log('color: ' + typeof color + ' = ' + JSON.stringify(color));
                    editor.asc_setCellFill('B3', color);
                    log('Выполнено без ошибок');
                } else {
                    log('CreateRGBColor не функция');
                }
            } catch(e) {
                log('❌ ОШИБКА: ' + e.message);
                log('   стек: ' + (e.stack ? e.stack.split('\n').slice(0,3).join('\n') : 'нет'));
            }
        }
    </script>
</body>
</html>
