
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; padding: 12px; background: #f5f5f5; margin: 0; }
        button {
            width: 100%; padding: 12px; margin: 8px 0;
            border: none; border-radius: 6px; font-size: 14px; font-weight: bold;
            cursor: pointer; color: white; background: #4CAF50;
        }
        .status {
            margin-top: 15px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 40px; word-break: break-word;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h3>🔄 Обработка столбца Z</h3>
    <p style="font-size:12px; color:#666;">
        Лист2: в столбце Z ","→"", "."→","<br>
        Копирует Z → A на Лист1
    </p>
    <button onclick="process()">⚡ Выполнить</button>
    <div class="status" id="status">Нажмите кнопку для запуска</div>

    <script>
        function editor() { return window.parent.Asc.editor; }
        function setStatus(msg) { document.getElementById('status').textContent = msg; }
        function refresh() {
            try { if (typeof editor().asc_Recalculate === 'function') editor().asc_Recalculate(); } catch(e) {}
        }

        function getSheet(name) {
            try {
                var ed = editor();
                if (typeof ed.GetSheet === 'function') return ed.GetSheet(name);
                var sheets = ed.GetSheets();
                for (var i = 0; i < sheets.GetCount(); i++) {
                    var sh = sheets.GetSheet(i);
                    if (sh && sh.GetName && sh.GetName() === name) return sh;
                }
                return null;
            } catch(e) { return null; }
        }

        // Ищем последнюю непустую строку в заданном столбце (colLetter)
        function getLastRowInColumn(sheet, colLetter) {
            var used = sheet.GetUsedRange();
            if (!used) return 0;
            var lastRow = used.GetRow() + used.GetRows().GetCount() - 1;
            // Идём снизу вверх, пока не встретим значение
            for (var r = lastRow; r >= 1; r--) {
                var val = sheet.GetRange(colLetter + r).GetValue();
                if (val !== null && val !== undefined && String(val).trim() !== '') {
                    return r;
                }
            }
            return 0;
        }

        function process() {
            setStatus('⏳ Анализирую столбец Z...');
            try {
                var sheet2 = getSheet('Лист2');
                var sheet1 = getSheet('Лист1');
                if (!sheet2 || !sheet1) {
                    setStatus('❌ Не найдены листы "Лист1" или "Лист2"');
                    return;
                }

                // Определяем последнюю реально заполненную строку в столбце Z
                var lastRowZ = getLastRowInColumn(sheet2, 'Z');
                if (lastRowZ === 0) {
                    setStatus('⚠️ Столбец Z пуст');
                    return;
                }

                setStatus('⏳ Меняю запятые/точки в строках 1-' + lastRowZ + '...');
                
                // === 1. Замена только в столбце Z до последней непустой строки ===
                for (var r = 1; r <= lastRowZ; r++) {
                    var cell = sheet2.GetRange('Z' + r);
                    var value = cell.GetValue();
                    if (value !== null && value !== undefined) {
                        var strValue = String(value);
                        var newStr = strValue.replace(/,/g, '').replace(/\./g, ',');
                        if (newStr !== strValue) {
                            cell.SetValue(newStr);
                        }
                    }
                }
                refresh();
                setStatus('✅ Замена выполнена. Копирую Z1:Z' + lastRowZ + ' на Лист1...');

                // === 2. Копируем только заполненный диапазон Z на Лист1 ===
                var rangeZ = sheet2.GetRange('Z1:Z' + lastRowZ);
                rangeZ.Copy(sheet1.GetRange('A1'));

                refresh();
                setStatus('✅ Готово! Обработано ' + lastRowZ + ' строк. Данные в столбце A на Лист1.');
            } catch(e) {
                setStatus('❌ Ошибка: ' + (e.message || e));
            }
        }
    </script>
</body>
</html>







Вот готовый плагин, который делает именно то, что вы описали: обрабатывает столбец Z на Лист2 (меняет 19,987.00 → 19987,00) и копирует его в столбец A на Лист1.

---

Плагин «Замена в столбце Z и копирование»

1. config.json

```json
{
    "name": "Замена и копирование Z",
    "guid": "asc.{z-replace-copy-1234-5678}",
    "variations": [
        {
            "url": "index.html",
            "EditorsSupport": ["spreadsheet"],
            "isVisual": true,
            "isModal": false,
            "isInsideMode": false,
            "size": [320, 180]
        }
    ]
}
```

2. index.html

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; padding: 12px; background: #f5f5f5; margin: 0; }
        button {
            width: 100%; padding: 12px; margin: 8px 0;
            border: none; border-radius: 6px; font-size: 14px; font-weight: bold;
            cursor: pointer; color: white; background: #4CAF50;
        }
        .status {
            margin-top: 15px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 40px; word-break: break-word;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h3>🔄 Обработка столбца Z</h3>
    <p style="font-size:12px; color:#666;">
        Лист2: в столбце Z ","→"", "."→","<br>
        Копирует Z → A на Лист1
    </p>
    <button onclick="process()">⚡ Выполнить</button>
    <div class="status" id="status">Нажмите кнопку для запуска</div>

    <script>
        function editor() { return window.parent.Asc.editor; }
        function setStatus(msg) { document.getElementById('status').textContent = msg; }
        function refresh() {
            try { if (typeof editor().asc_Recalculate === 'function') editor().asc_Recalculate(); } catch(e) {}
        }

        function getSheet(name) {
            try {
                var ed = editor();
                if (typeof ed.GetSheet === 'function') return ed.GetSheet(name);
                var sheets = ed.GetSheets();
                for (var i = 0; i < sheets.GetCount(); i++) {
                    var sh = sheets.GetSheet(i);
                    if (sh && sh.GetName && sh.GetName() === name) return sh;
                }
                return null;
            } catch(e) { return null; }
        }

        function process() {
            setStatus('⏳ Обрабатываю столбец Z на Лист2...');
            try {
                var sheet2 = getSheet('Лист2');
                var sheet1 = getSheet('Лист1');
                if (!sheet2 || !sheet1) {
                    setStatus('❌ Не найдены листы "Лист1" или "Лист2"');
                    return;
                }

                // === 1. Замена в столбце Z ===
                var used = sheet2.GetUsedRange();
                if (used) {
                    var lastRow = used.GetRow() + used.GetRows().GetCount() - 1;
                    for (var r = 1; r <= lastRow; r++) {
                        var cell = sheet2.GetRange('Z' + r);
                        var value = cell.GetValue();
                        if (value !== null && value !== undefined) {
                            var strValue = String(value);
                            var newStr = strValue.replace(/,/g, '').replace(/\./g, ',');
                            if (newStr !== strValue) {
                                cell.SetValue(newStr);
                            }
                        }
                    }
                    setStatus('✅ Замена выполнена. Копирую...');
                    refresh();
                } else {
                    setStatus('⚠️ Лист2 пуст');
                    return;
                }

                // === 2. Копирование Z → A на Лист1 ===
                sheet2.GetRange('Z:Z').Copy(sheet1.GetRange('A1'));
                refresh();
                setStatus('✅ Готово! Столбец Z скопирован в A на Лист1.');
            } catch(e) {
                setStatus('❌ Ошибка: ' + (e.message || e));
            }
        }
    </script>
</body>
</html>
```

---

Как это работает

1. Находит листы Лист2 и Лист1.
2. Определяет последнюю использованную строку на Лист2 (через GetUsedRange).
3. Построчно проходит по столбцу Z с первой до последней значимой строки.
4. В каждой ячейке читает значение, приводит к строке, удаляет все запятые, заменяет точку на запятую. Если строка изменилась – записывает обратно.
5. Копирует весь столбец Z с Лист2 и вставляет в столбец A на Лист1.

---

Установка

1. Создайте папку плагина (например, z_replace).
2. Поместите в неё два файла: config.json и index.html.
3. Скопируйте папку в директорию плагинов Р7-Офис (обычно /opt/r7-office/desktopeditors/editors/sdkjs-plugins/ или ~/.local/share/R7-Office/desktopeditors/sdkjs-plugins/).
4. Перезапустите Р7-Офис.
5. Откройте книгу с листами «Лист1» и «Лист2».
6. Запустите плагин через меню «Плагины» → «Замена и копирование Z».
7. Нажмите кнопку «Выполнить».

После этого данные в столбце Z на Лист2 изменятся (19,987.00 → 19987,00), и весь столбец появится на Лист1 в столбце A.

Если нужно копировать в другой столбец или на другой лист – просто измените адрес в строке sheet1.GetRange('A1') на нужный.






В макросах Р7 иногда помогает метод ForEach — он перебирает все ячейки диапазона и применяет к ним функцию. Попробуем его для замены в столбце Z и последующего копирования на Лист1.

```javascript
(function()
{
    var sheet2 = Api.GetSheet("Лист2");
    var sheet1 = Api.GetSheet("Лист1");
    
    if (!sheet2 || !sheet1) {
        alert("Не найдены листы 'Лист1' и/или 'Лист2'");
        return;
    }
    
    // Функция для обработки одной ячейки
    function processCell(cell) {
        var value = cell.GetValue();
        if (value !== null && value !== undefined) {
            var strValue = String(value);
            // Удаляем все запятые, затем точку меняем на запятую
            var newStr = strValue.replace(/,/g, "").replace(/\./g, ",");
            if (newStr !== strValue) {
                cell.SetValue(newStr);
            }
        }
    }
    
    // --- 1. Замена на Лист2 (во всём листе или только в столбце Z) ---
    // Если нужно только в столбце Z, замените на:
    // var rangeZ = sheet2.GetRange("Z1:Z1048576"); // весь столбец Z
    // Но проще взять используемый диапазон всего листа (как ранее)
    var usedRange = sheet2.GetUsedRange();
    if (usedRange) {
        usedRange.ForEach(processCell);
    }
    
    // --- 2. Копирование столбца Z Лист2 в столбец A Лист1 ---
    sheet2.GetRange("Z:Z").Copy(sheet1.GetRange("A1"));
    
    // Обновление (для версий 2026+)
    if (typeof Api.asc_Recalculate === 'function') {
        Api.asc_Recalculate();
    }
})();
```

Что сделано

· ForEach проходит по каждой ячейке используемого диапазона и вызывает processCell.
· Внутри processCell мы читаем значение, приводим к строке, делаем замены и записываем обратно, только если были изменения.
· Затем столбец Z целиком копируется в столбец A листа «Лист1».
    Если нужно скопировать в другой столбец или другой лист, замените "A1" на нужный адрес.

Если всё равно не сработает

Значит, макросы в вашей версии действительно не могут изменять значения через скрипты. Это известная проблема некоторых сборок. Тогда единственный рабочий способ — использовать проверенный плагин. Я могу за 5 минут собрать мини-плагин, который делает то же самое: открываете его, нажимаете одну кнопку — и готово. Он использует window.parent.Asc.editor, который мы уже успешно применяли в других задачах.

Попробуйте этот макрос. Если не получится – дайте знать, и я подготовлю плагин.







(function()
{
    var sheet2 = Api.GetSheet("Лист2");
    var sheet1 = Api.GetSheet("Лист1");
    
    if (!sheet2 || !sheet1) {
        alert("Не найдены листы 'Лист1' и/или 'Лист2'");
        return;
    }
    
    // Функция для обработки одной ячейки
    function processCell(cell) {
        var value = cell.GetValue();
        if (value !== null && value !== undefined) {
            var strValue = String(value);
            // Удаляем все запятые, затем точку меняем на запятую
            var newStr = strValue.replace(/,/g, "").replace(/\./g, ",");
            if (newStr !== strValue) {
                cell.SetValue(newStr);
            }
        }
    }
    
    // --- 1. Замена на Лист2 (во всём листе или только в столбце Z) ---
    // Если нужно только в столбце Z, замените на:
    // var rangeZ = sheet2.GetRange("Z1:Z1048576"); // весь столбец Z
    // Но проще взять используемый диапазон всего листа (как ранее)
    var usedRange = sheet2.GetUsedRange();
    if (usedRange) {
        usedRange.ForEach(processCell);
    }
    
    // --- 2. Копирование столбца Z Лист2 в столбец A Лист1 ---
    sheet2.GetRange("Z:Z").Copy(sheet1.GetRange("A1"));
    
    // Обновление (для версий 2026+)
    if (typeof Api.asc_Recalculate === 'function') {
        Api.asc_Recalculate();
    }
})();










(function()
{
    var sheet2 = Api.GetSheet("Лист2");
    var sheet1 = Api.GetSheet("Лист1");
    
    if (!sheet2 || !sheet1) {
        alert("Не найдены листы 'Лист1' и/или 'Лист2'");
        return;
    }
    
    // === 1. Замена на всём Лист2 ===
    var usedRange = sheet2.GetUsedRange();
    if (usedRange) {
        // Получаем коллекцию всех ячеек в используемом диапазоне
        var cells = usedRange.GetCells();
        var cellCount = cells.GetCount();
        
        for (var i = 0; i < cellCount; i++) {
            // Item принимает индекс от 0
            var cell = cells.Item(i);
            var value = cell.GetValue();
            
            if (value !== null && value !== undefined) {
                var strValue = String(value);
                
                // Удаляем все запятые
                var newStr = strValue.replace(/,/g, "");
                // Заменяем точки на запятые
                newStr = newStr.replace(/\./g, ",");
                
                if (newStr !== strValue) {
                    cell.SetValue(newStr);
                }
            }
        }
    }
    
    // === 2. Копирование столбцов B и C на Лист1 ===
    var rangeB2 = sheet2.GetRange("B:B");
    rangeB2.Copy(sheet1.GetRange("A1"));
    
    var rangeC2 = sheet2.GetRange("C:C");
    rangeC2.Copy(sheet1.GetRange("B1"));
    
    // Обновление книги
    if (typeof Api.asc_Recalculate === 'function') {
        Api.asc_Recalculate();
    }
})();





(function()
{
    var sheet2 = Api.GetSheet("Лист2");
    var sheet1 = Api.GetSheet("Лист1");
    
    if (!sheet2 || !sheet1) {
        alert("Не найдены листы 'Лист1' и/или 'Лист2'");
        return;
    }
    
    // === 1. Замена символов на всём Листе2 ===
    var usedRange = sheet2.GetUsedRange();
    if (usedRange) {
        var rowCount = usedRange.GetRows().GetCount();
        var colCount = usedRange.GetCols().GetCount();
        var startRow = usedRange.GetRow();
        var startCol = usedRange.GetCol();
        var endRow = startRow + rowCount - 1;
        var endCol = startCol + colCount - 1;
        
        // Проходим по каждой ячейке
        for (var r = startRow; r <= endRow; r++) {
            for (var c = startCol; c <= endCol; c++) {
                // Получаем букву столбца (A = 65)
                var colLetter = String.fromCharCode(64 + c);
                var cellAddress = colLetter + r;
                var cell = sheet2.GetRange(cellAddress);
                
                var value = cell.GetValue();
                if (value !== null && value !== undefined) {
                    var strValue = String(value);
                    
                    // Удаляем все запятые (разделители тысяч)
                    var newStr = strValue.replace(/,/g, "");
                    // Заменяем точку (десятичный разделитель) на запятую
                    newStr = newStr.replace(/\./g, ",");
                    
                    // Если изменения произошли – записываем обратно
                    if (newStr !== strValue) {
                        // Пытаемся понять, число это или текст
                        var num = parseFloat(newStr.replace(",", "."));
                        if (!isNaN(num) && newStr.indexOf(",") !== -1) {
                            // Число с запятой (десятичный разделитель) — оставляем как текст,
                            // чтобы запятая сохранилась
                            cell.SetValue(newStr);
                        } else if (!isNaN(num)) {
                            // Обычное число без запятой — сохраняем как число
                            cell.SetValue(num);
                        } else {
                            // Не число — пишем как текст
                            cell.SetValue(newStr);
                        }
                    }
                }
            }
        }
    }
    
    // === 2. Копирование столбцов B и C с Лист2 на Лист1 ===
    var rangeB2 = sheet2.GetRange("B:B");
    rangeB2.Copy(sheet1.GetRange("A1"));
    
    var rangeC2 = sheet2.GetRange("C:C");
    rangeC2.Copy(sheet1.GetRange("B1"));
    
    // Обновление книги (для версий 2026+)
    if (typeof Api.asc_Recalculate === 'function') {
        Api.asc_Recalculate();
    }
})();






(function()
{
    var currentSheet = Api.GetActiveSheet(); // Лист2, если кнопка там
    var targetSheet = Api.GetSheet("Лист1");
    
    if (!currentSheet || !targetSheet) {
        alert("Не найден активный лист или лист 'Лист1'");
        return;
    }
    
    // === 1. Ручная замена символов на текущем листе ===
    var usedRange = currentSheet.GetUsedRange();
    if (usedRange) {
        // Определяем границы диапазона
        var rowCount = usedRange.GetRows().GetCount();
        var colCount = usedRange.GetCols().GetCount();
        var startRow = usedRange.GetRow();
        var startCol = usedRange.GetCol();
        var endRow = startRow + rowCount - 1;
        var endCol = startCol + colCount - 1;
        
        // Перебираем все ячейки
        for (var r = startRow; r <= endRow; r++) {
            for (var c = startCol; c <= endCol; c++) {
                // Получаем букву столбца
                var colLetter = String.fromCharCode(64 + c); // 65 = 'A'
                var cellAddress = colLetter + r;
                var cell = currentSheet.GetRange(cellAddress);
                
                var value = cell.GetValue();
                if (value !== null && value !== undefined) {
                    // Преобразуем в строку и делаем замены
                    var strValue = String(value);
                    // Удаляем все запятые
                    var newStr = strValue.replace(/,/g, "");
                    // Заменяем точки на запятые
                    newStr = newStr.replace(/\./g, ",");
                    
                    // Если строка изменилась – записываем обратно
                    if (newStr !== strValue) {
                        // Проверим, является ли результат числом (если да – можно сохранить как число)
                        var num = parseFloat(newStr.replace(",", "."));
                        if (!isNaN(num) && newStr.indexOf(",") !== -1) {
                            // Содержит запятую как десятичный разделитель – оставляем текст
                            cell.SetValue(newStr);
                        } else if (!isNaN(num)) {
                            // Целое число без запятой – запишем как число
                            cell.SetValue(num);
                        } else {
                            // Не число – пишем как текст
                            cell.SetValue(newStr);
                        }
                    }
                }
            }
        }
    }
    
    // === 2. Копирование столбцов B и C на Лист1 ===
    currentSheet.GetRange("B:B").Copy(targetSheet.GetRange("A1"));
    currentSheet.GetRange("C:C").Copy(targetSheet.GetRange("B1"));
    
    // Обновление (для версий 2026+)
    if (typeof Api.asc_Recalculate === 'function') {
        Api.asc_Recalculate();
    }
})();







(function()
{
    var currentSheet = Api.GetActiveSheet();
    var targetSheet = Api.GetSheet("Лист1");
    
    if (!currentSheet || !targetSheet) {
        alert("Не найден активный лист или лист 'Лист1'");
        return;
    }
    
    // === 1. Замена символов на текущем листе ===
    var usedRange = currentSheet.GetUsedRange();
    if (usedRange) {
        var rows = usedRange.GetRows();
        var cols = usedRange.GetCols();
        var startRow = usedRange.GetRow();
        var startCol = usedRange.GetCol();
        var endRow = startRow + rows.GetCount() - 1;
        var endCol = startCol + cols.GetCount() - 1;
        
        for (var r = startRow; r <= endRow; r++) {
            for (var c = startCol; c <= endCol; c++) {
                var colLetter = String.fromCharCode(64 + c);
                var cell = currentSheet.GetRange(colLetter + r);
                
                // Получаем ОТОБРАЖАЕМЫЙ текст (с разделителями, знаком минус и т.д.)
                var displayedText = cell.GetText();
                
                if (displayedText !== null && displayedText !== undefined) {
                    // Удаляем все запятые (разделители тысяч)
                    var newText = displayedText.replace(/,/g, "");
                    // Заменяем точку (десятичный разделитель) на запятую
                    newText = newText.replace(/\./g, ",");
                    
                    // Пытаемся преобразовать в число (если это число, сохраним как число)
                    var num = parseFloat(newText.replace(",", ".")); // для парсинга возвращаем точку
                    if (!isNaN(num) && newText.indexOf(",") !== -1) {
                        // Это число с запятой в качестве десятичного разделителя
                        // Записываем его как текст, чтобы сохранить запятую
                        cell.SetValue(newText);
                    } else if (!isNaN(num)) {
                        // Обычное число без запятой – пишем как число
                        cell.SetValue(num);
                    } else {
                        // Текст – пишем изменённую строку
                        cell.SetValue(newText);
                    }
                }
            }
        }
    }
    
    // === 2. Копирование столбцов B и C на Лист1 ===
    currentSheet.GetRange("B:B").Copy(targetSheet.GetRange("A1"));
    currentSheet.GetRange("C:C").Copy(targetSheet.GetRange("B1"));
    
    // Обновление (для версий 2026+)
    if (typeof Api.asc_Recalculate === 'function') {
        Api.asc_Recalculate();
    }
})();





(function()
{
    // Текущий лист (на котором кнопка)
    var currentSheet = Api.GetActiveSheet();
    // Лист для вставки данных
    var targetSheet = Api.GetSheet("Лист1");
    
    if (!currentSheet || !targetSheet) {
        alert("Не найден активный лист или лист 'Лист1'");
        return;
    }
    
    // === 1. Ручная замена символов на текущем листе ===
    // Получаем используемый диапазон (или задайте конкретный, например "A1:C1000")
    var usedRange = currentSheet.GetUsedRange();
    if (usedRange) {
        // Получаем количество строк и столбцов
        var rows = usedRange.GetRows();
        var cols = usedRange.GetCols();
        
        var startRow = usedRange.GetRow();
        var startCol = usedRange.GetCol();
        var endRow = startRow + rows.GetCount() - 1;
        var endCol = startCol + cols.GetCount() - 1;
        
        // Перебираем все ячейки
        for (var r = startRow; r <= endRow; r++) {
            for (var c = startCol; c <= endCol; c++) {
                // Получаем адрес ячейки: буква + номер
                var colLetter = String.fromCharCode(64 + c);
                var cellAddress = colLetter + r;
                var cell = currentSheet.GetRange(cellAddress);
                
                var value = cell.GetValue();
                if (value !== null && value !== undefined && typeof value === "string") {
                    // Заменяем: сначала запятые на пусто, потом точки на запятые
                    var newValue = value.replace(/,/g, "").replace(/\./g, ",");
                    if (newValue !== value) {
                        cell.SetValue(newValue);
                    }
                }
            }
        }
    }
    
    // === 2. Копирование столбцов B и C с текущего листа на Лист1 ===
    currentSheet.GetRange("B:B").Copy(targetSheet.GetRange("A1"));
    currentSheet.GetRange("C:C").Copy(targetSheet.GetRange("B1"));
    
    // Обновление (для версий 2026+)
    if (typeof Api.asc_Recalculate === 'function') {
        Api.asc_Recalculate();
    }
})();






В Р7-Офис макросы пишутся на JavaScript с использованием встроенного API. Создадим макрос, который:

1. На листе Лист2 удаляет все запятые (, → пусто), затем меняет точки на запятые (. → ,).
2. Копирует столбец B с Лист2 в столбец A на Лист1, а столбец C – в столбец B.
3. Добавим кнопку на Лист2 для запуска макроса.

---

1. Создание макроса

· Откройте книгу в Р7-Таблица.
· Перейдите во вкладку «Макросы» → нажмите «Создать макрос».
· В открывшемся редакторе вставьте следующий код:

```javascript
(function()
{
    // Получаем листы по именам
    var sheet2 = Api.GetSheet("Лист2");
    var sheet1 = Api.GetSheet("Лист1");
    
    if (!sheet2 || !sheet1) {
        alert("Не найдены листы 'Лист1' и/или 'Лист2'");
        return;
    }
    
    // === 1. Замена на Лист2 ===
    // Получаем используемый диапазон
    var usedRange = sheet2.GetUsedRange();
    if (usedRange) {
        // Удаляем все запятые (заменяем на пустую строку)
        usedRange.Replace(",", "", false, false, false, false, false, false);
        // Заменяем точки на запятые
        usedRange.Replace(".", ",", false, false, false, false, false, false);
    }
    
    // === 2. Копирование столбцов B и C с Лист2 на Лист1 ===
    // Столбец B (Лист2) → столбец A (Лист1)
    var rangeB2 = sheet2.GetRange("B:B");
    rangeB2.Copy(sheet1.GetRange("A1"));
    
    // Столбец C (Лист2) → столбец B (Лист1)
    var rangeC2 = sheet2.GetRange("C:C");
    rangeC2.Copy(sheet1.GetRange("B1"));
    
    // Принудительно обновляем книгу (для версий 2026+)
    if (typeof Api.asc_Recalculate === 'function') {
        Api.asc_Recalculate();
    }
})();
```

· Нажмите «Сохранить» и закройте редактор. Дайте макросу имя, например ReplaceAndCopy.

---

2. Добавление кнопки на Лист2

· Перейдите на Лист2.
· Откройте вкладку «Вставка» → выберите «Фигура» (например, прямоугольник или кнопку).
· Нарисуйте фигуру в удобном месте листа.
· Нажмите на фигуру правой кнопкой мыши → «Назначить макрос».
· В появившемся списке выберите созданный макрос (ReplaceAndCopy) → ОК.

Теперь при нажатии на кнопку макрос выполнит все описанные действия.

---

Примечания

· Если нужно заменить запятые/точки не во всей таблице, а только в определённом диапазоне, замените GetUsedRange() на конкретный диапазон, например sheet2.GetRange("A1:C100").
· Макрос копирует весь столбец целиком (все строки). Если объём данных большой, это может занять время.
· Для корректной работы убедитесь, что листы называются именно Лист1 и Лист2. Если имена отличаются, измените их в коде или переименуйте листы в книге.

Теперь у вас есть готовая автоматизация с кнопкой. Если потребуется что-то доработать — обращайтесь!
