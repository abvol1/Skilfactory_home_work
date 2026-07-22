
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; padding: 12px; background: #f5f5f5; margin: 0; }
        button { 
            display: block; width: 100%; padding: 12px; margin: 8px 0; 
            border: none; border-radius: 6px; font-size: 14px; font-weight: bold;
            cursor: pointer; color: white; text-align: center;
        }
        .btn-write  { background: #4CAF50; }
        .btn-fill   { background: #FF9800; }
        .btn-font   { background: #2196F3; }
        .btn-clear  { background: #f44336; }
        .btn-read   { background: #9C27B0; }
        .status {
            margin-top: 15px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 40px; word-break: break-word;
        }
    </style>
</head>
<body>
    <h3>⚡ Действия с таблицей</h3>
    
    <button class="btn-write" onclick="writeCell()">📝 Записать в A1</button>
    <button class="btn-fill" onclick="fillCell()">🎨 Закрасить B1</button>
    <button class="btn-font" onclick="formatText()">🔤 Красный жирный в C1</button>
    <button class="btn-clear" onclick="clearCells()">🧹 Очистить A1:C1</button>
    <button class="btn-read" onclick="readCell()">📖 Прочитать A1</button>
    
    <div class="status" id="status">Готов к работе</div>

    <script>
        // Короткий доступ к API редактора
        function editor() { return window.parent.Asc.editor; }

        function setStatus(msg) {
            document.getElementById('status').textContent = msg;
        }

        // Вспомогательная функция: принудительно обновить лист
        function refresh() {
            if (typeof editor().asc_Recalculate === 'function') {
                editor().asc_Recalculate();
            }
        }

        // ===== 1. Запись текста в A1 =====
        function writeCell() {
            try {
                // asc_setData надёжно записывает значение
                editor().asc_setData('A1', 'Привет! ' + new Date().toLocaleTimeString());
                setStatus('✅ A1: записано');
                refresh();
            } catch(e) {
                setStatus('❌ Ошибка: ' + e.message);
            }
        }

        // ===== 2. Заливка B1 золотым цветом =====
        function fillCell() {
            try {
                var sheet = editor().GetActiveSheet();
                var range = sheet.GetRange('B1');
                var color = editor().CreateColorFromRGB(255, 215, 0);
                range.SetFillColor(color);
                refresh(); // обязательно обновить
                setStatus('🎨 B1: заливка золотым');
            } catch(e) {
                setStatus('❌ Ошибка заливки: ' + e.message);
            }
        }

        // ===== 3. Красный жирный текст в C1 =====
        function formatText() {
            try {
                var sheet = editor().GetActiveSheet();
                var range = sheet.GetRange('C1');
                
                // Установить значение
                range.SetValue('Важно!');
                
                // Красный цвет шрифта
                var red = editor().CreateColorFromRGB(255, 0, 0);
                range.SetFontColor(red);
                
                // Жирный шрифт
                range.SetBold(true);
                
                refresh();
                setStatus('🔤 C1: красный жирный');
            } catch(e) {
                setStatus('❌ Ошибка форматирования: ' + e.message);
            }
        }

        // ===== 4. Очистка A1:C1 =====
        function clearCells() {
            try {
                var sheet = editor().GetActiveSheet();
                var range = sheet.GetRange('A1:C1');
                range.Clear(); // очищает всё: значения, фон, форматирование
                refresh();
                setStatus('🧹 A1:C1 очищены');
            } catch(e) {
                setStatus('❌ Ошибка очистки: ' + e.message);
            }
        }

        // ===== 5. Прочитать значение A1 =====
        function readCell() {
            try {
                var sheet = editor().GetActiveSheet();
                var range = sheet.GetRange('A1');
                var value = range.GetValue();
                if (value === null || value === undefined || value === '') {
                    value = '(пусто)';
                }
                setStatus('📖 A1 = ' + value);
            } catch(e) {
                setStatus('❌ Ошибка чтения: ' + e.message);
            }
        }

        window.onload = function() {
            setStatus('✅ Плагин готов. Нажимайте кнопки.');
        };
    </script>
</body>
</html>








<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; padding: 10px; background: #f5f5f5; }
        button { padding: 12px; margin: 5px; width: 100%; cursor: pointer; font-size: 14px; background: #4CAF50; color: white; border: none; border-radius: 5px; }
        textarea { width: 100%; height: 200px; font-family: monospace; font-size: 11px; background: #1e1e1e; color: #0f0; padding: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <h3>🎨 Финальный тест заливки</h3>
    
    <button onclick="testFillAndRecalc()">1. Установить цвет + asc_Recalculate</button>
    <button onclick="testFontColor()">2. Проверить SetFontColor (текст)</button>
    <button onclick="clearLog()">🧹 Очистить</button>
    
    <textarea id="log"></textarea>

    <script>
        var el = document.getElementById('log');
        function log(msg) { el.value += msg + '\n'; el.scrollTop = el.scrollHeight; }
        function clearLog() { el.value = ''; }

        function api() { return window.parent.Asc.editor; }

        function testFillAndRecalc() {
            log('=== Заливка B1 + asc_Recalculate ===');
            try {
                var sheet = api().GetActiveSheet();
                var range = sheet.GetRange('B1');
                var color = api().CreateColorFromRGB(255, 215, 0);
                range.SetFillColor(color);
                log('Цвет установлен');
                // Принудительно обновляем
                if (typeof api().asc_Recalculate === 'function') {
                    api().asc_Recalculate();
                    log('asc_Recalculate вызван');
                } else if (typeof api().RecalculateAllFormulas === 'function') {
                    api().RecalculateAllFormulas();
                    log('RecalculateAllFormulas вызван');
                }
                log('Готово. Проверьте B1');
            } catch(e) { log('❌ ' + e.message); }
        }

        function testFontColor() {
            log('=== Цвет текста в B2 ===');
            try {
                var sheet = api().GetActiveSheet();
                var range = sheet.GetRange('B2');
                range.SetValue('Тест');
                var color = api().CreateColorFromRGB(255, 0, 0);
                range.SetFontColor(color);
                log('Текст и цвет установлены. Проверьте B2');
            } catch(e) { log('❌ ' + e.message); }
        }
    </script>
</body>
</html>







=== Число ===
Установлено число
GetFillColor: No Fill
=== HEX-строка ===
Установлена строка HEX
GetFillColor: No Fill
=== RGB-строка ===
Установлена строка RGB
GetFillColor: No Fill
=== Объект цвета ===
Объект: {"color":{"rgb":16766720}}
Установлен объект
GetFillColor: [object Object]
=== Чтение FillColor ===
До: No Fill
После установки числа: No Fill











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
    <h3>🔧 Форматы для SetFillColor</h3>
    
    <button onclick="testNumber()">1. Число (16766720)</button>
    <button onclick="testHexString()">2. Строка "#FFD700"</button>
    <button onclick="testRgbString()">3. Строка "rgb(255,215,0)"</button>
    <button onclick="testColorObject()">4. Объект {"color":{"rgb":...}}</button>
    <button onclick="testGetFill()">5. Прочитать FillColor до и после</button>
    <button onclick="clearLog()">🧹 Очистить</button>
    
    <textarea id="log"></textarea>

    <script>
        var el = document.getElementById('log');
        function log(msg) { el.value += msg + '\n'; el.scrollTop = el.scrollHeight; }
        function clearLog() { el.value = ''; }

        function api() { return window.parent.Asc.editor; }

        function testNumber() {
            log('=== Число ===');
            try {
                var sheet = api().GetActiveSheet();
                var range = sheet.GetRange('B1');
                range.SetFillColor(16766720); // золотой в decimal
                log('Установлено число');
                log('GetFillColor: ' + range.GetFillColor());
            } catch(e) { log('❌ ' + e.message); }
        }

        function testHexString() {
            log('=== HEX-строка ===');
            try {
                var sheet = api().GetActiveSheet();
                var range = sheet.GetRange('B2');
                range.SetFillColor('#FFD700');
                log('Установлена строка HEX');
                log('GetFillColor: ' + range.GetFillColor());
            } catch(e) { log('❌ ' + e.message); }
        }

        function testRgbString() {
            log('=== RGB-строка ===');
            try {
                var sheet = api().GetActiveSheet();
                var range = sheet.GetRange('B3');
                range.SetFillColor('rgb(255,215,0)');
                log('Установлена строка RGB');
                log('GetFillColor: ' + range.GetFillColor());
            } catch(e) { log('❌ ' + e.message); }
        }

        function testColorObject() {
            log('=== Объект цвета ===');
            try {
                var sheet = api().GetActiveSheet();
                var range = sheet.GetRange('B4');
                var color = api().CreateColorFromRGB(255, 215, 0);
                log('Объект: ' + JSON.stringify(color));
                range.SetFillColor(color);
                log('Установлен объект');
                log('GetFillColor: ' + range.GetFillColor());
            } catch(e) { log('❌ ' + e.message); }
        }

        function testGetFill() {
            log('=== Чтение FillColor ===');
            try {
                var sheet = api().GetActiveSheet();
                var range = sheet.GetRange('B5');
                log('До: ' + range.GetFillColor());
                range.SetFillColor(16766720);
                log('После установки числа: ' + range.GetFillColor());
            } catch(e) { log('❌ ' + e.message); }
        }
    </script>
</body>
</html>






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
    <h3>🔧 Форматы для SetFillColor</h3>
    
    <button onclick="testNumber()">1. Число (16766720)</button>
    <button onclick="testHexString()">2. Строка "#FFD700"</button>
    <button onclick="testRgbString()">3. Строка "rgb(255,215,0)"</button>
    <button onclick="testColorObject()">4. Объект {"color":{"rgb":...}}</button>
    <button onclick="testGetFill()">5. Прочитать FillColor до и после</button>
    <button onclick="clearLog()">🧹 Очистить</button>
    
    <textarea id="log"></textarea>

    <script>
        var el = document.getElementById('log');
        function log(msg) { el.value += msg + '\n'; el.scrollTop = el.scrollHeight; }
        function clearLog() { el.value = ''; }

        function api() { return window.parent.Asc.editor; }

        function testNumber() {
            log('=== Число ===');
            try {
                var sheet = api().GetActiveSheet();
                var range = sheet.GetRange('B1');
                range.SetFillColor(16766720); // золотой в decimal
                log('Установлено число');
                log('GetFillColor: ' + range.GetFillColor());
            } catch(e) { log('❌ ' + e.message); }
        }

        function testHexString() {
            log('=== HEX-строка ===');
            try {
                var sheet = api().GetActiveSheet();
                var range = sheet.GetRange('B2');
                range.SetFillColor('#FFD700');
                log('Установлена строка HEX');
                log('GetFillColor: ' + range.GetFillColor());
            } catch(e) { log('❌ ' + e.message); }
        }

        function testRgbString() {
            log('=== RGB-строка ===');
            try {
                var sheet = api().GetActiveSheet();
                var range = sheet.GetRange('B3');
                range.SetFillColor('rgb(255,215,0)');
                log('Установлена строка RGB');
                log('GetFillColor: ' + range.GetFillColor());
            } catch(e) { log('❌ ' + e.message); }
        }

        function testColorObject() {
            log('=== Объект цвета ===');
            try {
                var sheet = api().GetActiveSheet();
                var range = sheet.GetRange('B4');
                var color = api().CreateColorFromRGB(255, 215, 0);
                log('Объект: ' + JSON.stringify(color));
                range.SetFillColor(color);
                log('Установлен объект');
                log('GetFillColor: ' + range.GetFillColor());
            } catch(e) { log('❌ ' + e.message); }
        }

        function testGetFill() {
            log('=== Чтение FillColor ===');
            try {
                var sheet = api().GetActiveSheet();
                var range = sheet.GetRange('B5');
                log('До: ' + range.GetFillColor());
                range.SetFillColor(16766720);
                log('После установки числа: ' + range.GetFillColor());
            } catch(e) { log('❌ ' + e.message); }
        }
    </script>
</body>
</html>







<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; padding: 10px; background: #f5f5f5; }
        button { padding: 12px; margin: 5px; width: 100%; cursor: pointer; font-size: 14px; background: #4CAF50; color: white; border: none; border-radius: 5px; }
        textarea { width: 100%; height: 150px; font-family: monospace; font-size: 11px; background: #1e1e1e; color: #0f0; padding: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <h3>🎨 SetFillColor</h3>
    
    <button onclick="test()">Закрасить B1 золотым</button>
    <button onclick="clearLog()">🧹 Очистить</button>
    
    <textarea id="log"></textarea>

    <script>
        var el = document.getElementById('log');
        function log(msg) { el.value += msg + '\n'; el.scrollTop = el.scrollHeight; }
        function clearLog() { el.value = ''; }

        function api() { return window.parent.Asc.editor; }

        function test() {
            log('=== SetFillColor на B1 ===');
            try {
                var sheet = api().GetActiveSheet();
                var range = sheet.GetRange('B1');
                var color = api().CreateColorFromRGB(255, 215, 0);
                range.SetFillColor(color);
                log('✅ Готово! Проверьте B1');
            } catch(e) { log('❌ ' + e.message); }
        }
    </script>
</body>
</html>







=== Методы Range ===
  GetClassType()
  GetRow()
  GetCol()
  Clear()
  GetRows()
  GetCols()
  End()
  GetCells()
  SetOffset()
  GetAddress()
  GetCount()
  GetValue()
  SetValue()
  GetFormula()
  GetValue2()
  GetText()
  SetFontColor()
  GetHidden()
  SetHidden()
  GetColumnWidth()
  SetColumnWidth()
  GetRowHeight()
  SetRowHeight()
  SetFontSize()
  SetFontName()
  SetAlignVertical()
  SetAlignHorizontal()
  SetBold()
  SetItalic()
  SetUnderline()
  SetStrikeout()
  SetWrap()
  GetWrapText()
  SetFillColor()
  GetFillColor()
  GetNumberFormat()
  SetNumberFormat()
  SetBorders()
  Merge()
  UnMerge()
  ForEach()
  AddComment()
  GetWorksheet()
  GetDefName()
  GetComment()
  Select()
  GetOrientation()
  SetOrientation()
  SetSort()
  Delete()
  Insert()
  AutoFit()
  GetAreas()
  Copy()
  Paste()
  Find()
  FindNext()
  FindPrevious()
  Replace()
  GetCharacters()
Показано: 60
=== range.SetFill ===
SetFill отсутствует
=== range.SetBackground ===
SetBackground отсутствует










<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; padding: 10px; background: #f5f5f5; }
        button { padding: 12px; margin: 5px; width: 100%; cursor: pointer; font-size: 14px; background: #9C27B0; color: white; border: none; border-radius: 5px; }
        textarea { width: 100%; height: 300px; font-family: monospace; font-size: 11px; background: #1e1e1e; color: #0f0; padding: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <h3>🔍 Методы Range</h3>
    
    <button onclick="showRangeMethods()">1. Показать методы Range</button>
    <button onclick="testRangeSetFill()">2. range.SetFill(цвет)</button>
    <button onclick="testRangeSetBackground()">3. range.SetBackground(цвет)</button>
    <button onclick="clearLog()">🧹 Очистить</button>
    
    <textarea id="log"></textarea>

    <script>
        var el = document.getElementById('log');
        function log(msg) { el.value += msg + '\n'; el.scrollTop = el.scrollHeight; }
        function clearLog() { el.value = ''; }

        function api() { return window.parent.Asc.editor; }

        function showRangeMethods() {
            log('=== Методы Range ===');
            try {
                var sheet = api().GetActiveSheet();
                var range = sheet.GetRange('A1');
                var count = 0;
                for (var k in range) {
                    if (typeof range[k] === 'function') {
                        log('  ' + k + '()');
                        count++;
                        if (count >= 60) break;
                    }
                }
                log('Показано: ' + count);
            } catch(e) { log('❌ ' + e.message); }
        }

        function testRangeSetFill() {
            log('=== range.SetFill ===');
            try {
                var sheet = api().GetActiveSheet();
                var range = sheet.GetRange('B1');
                if (typeof range.SetFill === 'function') {
                    var color = api().CreateColorFromRGB(255, 215, 0);
                    range.SetFill(color);
                    log('Вызван SetFill');
                } else {
                    log('SetFill отсутствует');
                }
            } catch(e) { log('❌ ' + e.message); }
        }

        function testRangeSetBackground() {
            log('=== range.SetBackground ===');
            try {
                var sheet = api().GetActiveSheet();
                var range = sheet.GetRange('B2');
                if (typeof range.SetBackground === 'function') {
                    var color = api().CreateColorFromRGB(135, 206, 235);
                    range.SetBackground(color);
                    log('Вызван SetBackground');
                } else {
                    log('SetBackground отсутствует');
                }
            } catch(e) { log('❌ ' + e.message); }
        }
    </script>
</body>
</html>






<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; padding: 10px; background: #f5f5f5; }
        button { padding: 12px; margin: 5px; width: 100%; cursor: pointer; font-size: 14px; background: #4CAF50; color: white; border: none; border-radius: 5px; }
        button:hover { background: #45a049; }
        textarea { width: 100%; height: 200px; font-family: monospace; font-size: 11px; background: #1e1e1e; color: #0f0; padding: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <h3>🎨 Финальный тест заливки</h3>
    
    <button onclick="test()">Закрасить B1 через SolidFill → asc_setCellBackgroundColor</button>
    <button onclick="clearLog()">🧹 Очистить</button>
    
    <textarea id="log"></textarea>

    <script>
        var el = document.getElementById('log');
        function log(msg) { el.value += msg + '\n'; el.scrollTop = el.scrollHeight; }
        function clearLog() { el.value = ''; }

        function api() { return window.parent.Asc.editor; }

        function test() {
            log('=== Закраска B1 ===');
            try {
                var editor = api();
                
                // 1. Создаём цвет
                var color = editor.CreateColorFromRGB(255, 200, 0);
                log('Цвет создан: ' + JSON.stringify(color));
                
                // 2. Создаём заливку
                var fill = editor.CreateSolidFill(color);
                log('Заливка создана: ' + typeof fill);
                
                // 3. Применяем
                editor.asc_setCellBackgroundColor('B1', fill);
                log('✅ Готово! Проверьте B1');
            } catch(e) {
                log('❌ ' + e.message);
            }
        }
    </script>
</body>
</html>











=== Тест 1: CreateColorFromRGB + asc_setCellFill ===
CreateColorFromRGB существует: function
color: object = {"color":{"rgb":16766720}}
asc_setCellFill существует: function
❌ ОШИБКА: Cr.checkEmptyContent is not a function
   стек: TypeError: Cr.checkEmptyContent is not a function
    at Ci.setFill (file:///opt/r7-office/desktopeditors/editors/sdkjs/cell/sdk-all.js:38:198932)
    at wo.setFill (file:///opt/r7-office/desktopeditors/editors/sdkjs/cell/sdk-all.js:414:262997)

=== Тест 2: CreateColorFromRGB + asc_setCellBackgroundColor ===
Выполнено без ошибок

=== Тест 3: CreateRGBColor + asc_setCellFill ===
CreateRGBColor существует: function
color: object = {"Unicolor":{"color":{"RGBA":{"R":255,"G":182,"B":193,"A":255,"needRecalc":true},"Mods":null,"h":null,"s":null,"l":null},"Mods":null,"RGBA":{"R":0,"G":0,"B":0,"A":255}}}
❌ ОШИБКА: Cr.checkEmptyContent is not a function
   стек: TypeError: Cr.checkEmptyContent is not a function
    at Ci.setFill (file:///opt/r7-office/desktopeditors/editors/sdkjs/cell/sdk-all.js:38:198932)
    at wo.setFill (file:///opt/r7-office/desktopeditors/editors/sdkjs/cell/sdk-all.js:414:262997)








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
