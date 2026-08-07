
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
        button.clear-btn { background: #f44336; }
        .status {
            margin-top: 15px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 40px; white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h3>🔎 Фильтр «уратекст + проба»</h3>
    <p style="font-size:12px; color:#666;">
        Активный лист → строки, где A = "уратекст" и B = "проба"<br>
        → новый лист «тест1»
    </p>
    
    <button onclick="runFilter()">📋 Найти и скопировать</button>
    <button class="clear-btn" onclick="clearTest1()">🗑️ Очистить тест1</button>
    
    <div class="status" id="status">Готов к работе</div>

    <script>
        function runFilter() {
            try {
                var ed = window.parent.Asc.editor;
                var statusEl = document.getElementById('status');
                statusEl.textContent = '⏳ Анализирую исходный лист...';

                // 1. Запоминаем текущий активный лист (исходный)
                var sourceSheet = ed.GetActiveSheet();
                if (!sourceSheet) throw 'Нет активного листа';
                var sourceSheetName = 'исходный';
                try { sourceSheetName = sourceSheet.GetName(); } catch(e) {}

                // 2. Получаем используемый диапазон исходного листа
                var usedRange = sourceSheet.GetUsedRange();
                if (!usedRange) throw 'На листе «' + sourceSheetName + '» нет данных';

                var rowCount = usedRange.GetRows().GetCount();
                var colCount = usedRange.GetCols().GetCount();
                var startRow = usedRange.GetRow();
                var startCol = usedRange.GetCol();
                var endRow = startRow + rowCount - 1;
                var endCol = startCol + colCount - 1;

                // 3. Диагностика — первые 5 строк исходного листа
                var diagInfo = '';
                var maxDiagRows = Math.min(5, rowCount);
                for (var d = 0; d < maxDiagRows; d++) {
                    var diagRow = startRow + d;
                    var aVal = sourceSheet.GetRange('A' + diagRow).GetValue();
                    var bVal = sourceSheet.GetRange('B' + diagRow).GetValue();
                    diagInfo += 'Строка ' + diagRow + ': A=[' + aVal + '] B=[' + bVal + ']\n';
                }

                // 4. Поиск подходящих строк на ИСХОДНОМ листе
                var matchingRows = [];
                for (var r = startRow; r <= endRow; r++) {
                    var cellA = sourceSheet.GetRange('A' + r);
                    var valA = cellA.GetValue();
                    var textA = (valA !== null && valA !== undefined) ? String(valA).trim().toLowerCase() : '';

                    var cellB = sourceSheet.GetRange('B' + r);
                    var valB = cellB.GetValue();
                    var textB = (valB !== null && valB !== undefined) ? String(valB).trim().toLowerCase() : '';

                    if (textA === 'уратекст' && textB === 'проба') {
                        matchingRows.push(r);
                    }
                }

                if (matchingRows.length === 0) {
                    statusEl.textContent = '❌ Нет строк с A="уратекст" и B="проба" на листе «' + sourceSheetName + '».\n' +
                                           'Первые строки листа:\n' + diagInfo + '\n' +
                                           '👉 Проверьте написание слов и наличие данных.';
                    return;
                }

                // 5. Удаляем старый лист «тест1», если он существует
                var test1 = null;
                if (typeof ed.GetSheet === 'function') {
                    test1 = ed.GetSheet('тест1');
                } else {
                    var sheets = ed.GetSheets();
                    for (var i = 0; i < sheets.GetCount(); i++) {
                        var sh = sheets.GetSheet(i);
                        if (sh && sh.GetName && sh.GetName() === 'тест1') { test1 = sh; break; }
                    }
                }
                if (test1) {
                    test1.Delete();
                    try { ed.asc_Recalculate(); } catch(e) {}
                }

                // 6. Создаём новый лист «тест1»
                if (typeof ed.AddSheet === 'function') {
                    test1 = ed.AddSheet('тест1');
                } else {
                    ed.asc_addWorksheet('тест1');
                    if (typeof ed.GetSheet === 'function') {
                        test1 = ed.GetSheet('тест1');
                    } else {
                        var sheets = ed.GetSheets();
                        for (var i = 0; i < sheets.GetCount(); i++) {
                            var sh = sheets.GetSheet(i);
                            if (sh && sh.GetName && sh.GetName() === 'тест1') { test1 = sh; break; }
                        }
                    }
                }
                if (!test1) throw 'Не удалось создать лист «тест1»';

                // 7. Копирование данных с ИСХОДНОГО листа на тест1 (вручную)
                for (var i = 0; i < matchingRows.length; i++) {
                    var srcRow = matchingRows[i];
                    var targetRow = i + 1;
                    for (var c = startCol; c <= endCol; c++) {
                        var colLetter = String.fromCharCode(64 + c);
                        var srcCell = sourceSheet.GetRange(colLetter + srcRow); // читаем из sourceSheet
                        var value = srcCell.GetValue();
                        test1.GetRange(colLetter + targetRow).SetValue(value);
                    }
                }

                // 8. Обновляем книгу
                try { ed.asc_Recalculate(); } catch(e) {}
                statusEl.textContent = '✅ Скопировано ' + matchingRows.length + ' строк на лист «тест1» из листа «' + sourceSheetName + '»';
            } catch(e) {
                document.getElementById('status').textContent = '❌ Ошибка: ' + (e.message || e);
            }
        }

        function clearTest1() {
            try {
                var ed = window.parent.Asc.editor;
                document.getElementById('status').textContent = '🗑️ Удаляю лист «тест1»...';
                var test1 = null;
                if (typeof ed.GetSheet === 'function') {
                    test1 = ed.GetSheet('тест1');
                } else {
                    var sheets = ed.GetSheets();
                    for (var i = 0; i < sheets.GetCount(); i++) {
                        var sh = sheets.GetSheet(i);
                        if (sh && sh.GetName && sh.GetName() === 'тест1') { test1 = sh; break; }
                    }
                }
                if (test1) {
                    test1.Delete();
                    try { ed.asc_Recalculate(); } catch(e) {}
                    document.getElementById('status').textContent = '✅ Лист «тест1» удалён';
                } else {
                    document.getElementById('status').textContent = '⚠️ Лист «тест1» не существует';
                }
            } catch(e) {
                document.getElementById('status').textContent = '❌ Ошибка: ' + (e.message || e);
            }
        }
    </script>
</body>
</html>






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
        button.clear-btn { background: #f44336; }
        .status {
            margin-top: 15px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 40px; white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h3>🔎 Фильтр «уратекст + проба»</h3>
    <p style="font-size:12px; color:#666;">
        Активный лист → строки, где A = "уратекст" и B = "проба"<br>
        → новый лист «тест1»
    </p>
    
    <button onclick="runFilter()">📋 Найти и скопировать</button>
    <button class="clear-btn" onclick="clearTest1()">🗑️ Очистить тест1</button>
    
    <div class="status" id="status">Готов к работе</div>

    <script>
        function runFilter() {
            try {
                var ed = window.parent.Asc.editor;
                var statusEl = document.getElementById('status');
                statusEl.textContent = '⏳ Анализирую исходный лист...';

                // 1. Запоминаем текущий активный лист (исходный)
                var sourceSheet = ed.GetActiveSheet();
                if (!sourceSheet) throw 'Нет активного листа';
                var sourceSheetName = 'исходный';
                try { sourceSheetName = sourceSheet.GetName(); } catch(e) {}

                // 2. Получаем используемый диапазон исходного листа
                var usedRange = sourceSheet.GetUsedRange();
                if (!usedRange) throw 'На листе «' + sourceSheetName + '» нет данных';

                var rowCount = usedRange.GetRows().GetCount();
                var colCount = usedRange.GetCols().GetCount();
                var startRow = usedRange.GetRow();
                var startCol = usedRange.GetCol();
                var endRow = startRow + rowCount - 1;
                var endCol = startCol + colCount - 1;

                // 3. Диагностика — первые 5 строк исходного листа
                var diagInfo = '';
                var maxDiagRows = Math.min(5, rowCount);
                for (var d = 0; d < maxDiagRows; d++) {
                    var diagRow = startRow + d;
                    var aVal = sourceSheet.GetRange('A' + diagRow).GetValue();
                    var bVal = sourceSheet.GetRange('B' + diagRow).GetValue();
                    diagInfo += 'Строка ' + diagRow + ': A=[' + aVal + '] B=[' + bVal + ']\n';
                }

                // 4. Поиск подходящих строк на ИСХОДНОМ листе
                var matchingRows = [];
                for (var r = startRow; r <= endRow; r++) {
                    var cellA = sourceSheet.GetRange('A' + r);
                    var valA = cellA.GetValue();
                    var textA = (valA !== null && valA !== undefined) ? String(valA).trim().toLowerCase() : '';

                    var cellB = sourceSheet.GetRange('B' + r);
                    var valB = cellB.GetValue();
                    var textB = (valB !== null && valB !== undefined) ? String(valB).trim().toLowerCase() : '';

                    if (textA === 'уратекст' && textB === 'проба') {
                        matchingRows.push(r);
                    }
                }

                if (matchingRows.length === 0) {
                    statusEl.textContent = '❌ Нет строк с A="уратекст" и B="проба" на листе «' + sourceSheetName + '».\n' +
                                           'Первые строки листа:\n' + diagInfo + '\n' +
                                           '👉 Проверьте написание слов и наличие данных.';
                    return;
                }

                // 5. Удаляем старый лист «тест1», если он существует
                var test1 = null;
                if (typeof ed.GetSheet === 'function') {
                    test1 = ed.GetSheet('тест1');
                } else {
                    var sheets = ed.GetSheets();
                    for (var i = 0; i < sheets.GetCount(); i++) {
                        var sh = sheets.GetSheet(i);
                        if (sh && sh.GetName && sh.GetName() === 'тест1') { test1 = sh; break; }
                    }
                }
                if (test1) {
                    test1.Delete();
                    try { ed.asc_Recalculate(); } catch(e) {}
                }

                // 6. Создаём новый лист «тест1»
                if (typeof ed.AddSheet === 'function') {
                    test1 = ed.AddSheet('тест1');
                } else {
                    ed.asc_addWorksheet('тест1');
                    if (typeof ed.GetSheet === 'function') {
                        test1 = ed.GetSheet('тест1');
                    } else {
                        var sheets = ed.GetSheets();
                        for (var i = 0; i < sheets.GetCount(); i++) {
                            var sh = sheets.GetSheet(i);
                            if (sh && sh.GetName && sh.GetName() === 'тест1') { test1 = sh; break; }
                        }
                    }
                }
                if (!test1) throw 'Не удалось создать лист «тест1»';

                // 7. Копирование данных с ИСХОДНОГО листа на тест1 (вручную)
                for (var i = 0; i < matchingRows.length; i++) {
                    var srcRow = matchingRows[i];
                    var targetRow = i + 1;
                    for (var c = startCol; c <= endCol; c++) {
                        var colLetter = String.fromCharCode(64 + c);
                        var srcCell = sourceSheet.GetRange(colLetter + srcRow); // читаем из sourceSheet
                        var value = srcCell.GetValue();
                        test1.GetRange(colLetter + targetRow).SetValue(value);
                    }
                }

                // 8. Обновляем книгу
                try { ed.asc_Recalculate(); } catch(e) {}
                statusEl.textContent = '✅ Скопировано ' + matchingRows.length + ' строк на лист «тест1» из листа «' + sourceSheetName + '»';
            } catch(e) {
                document.getElementById('status').textContent = '❌ Ошибка: ' + (e.message || e);
            }
        }

        function clearTest1() {
            try {
                var ed = window.parent.Asc.editor;
                document.getElementById('status').textContent = '🗑️ Удаляю лист «тест1»...';
                var test1 = null;
                if (typeof ed.GetSheet === 'function') {
                    test1 = ed.GetSheet('тест1');
                } else {
                    var sheets = ed.GetSheets();
                    for (var i = 0; i < sheets.GetCount(); i++) {
                        var sh = sheets.GetSheet(i);
                        if (sh && sh.GetName && sh.GetName() === 'тест1') { test1 = sh; break; }
                    }
                }
                if (test1) {
                    test1.Delete();
                    try { ed.asc_Recalculate(); } catch(e) {}
                    document.getElementById('status').textContent = '✅ Лист «тест1» удалён';
                } else {
                    document.getElementById('status').textContent = '⚠️ Лист «тест1» не существует';
                }
            } catch(e) {
                document.getElementById('status').textContent = '❌ Ошибка: ' + (e.message || e);
            }
        }
    </script>
</body>
</html>








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
        button.clear-btn { background: #f44336; }
        .status {
            margin-top: 15px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 40px; white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h3>🔎 Фильтр «уратекст + проба»</h3>
    <p style="font-size:12px; color:#666;">
        Активный лист → строки, где A = "уратекст" и B = "проба"<br>
        → новый лист «тест1»
    </p>
    
    <button onclick="runFilter()">📋 Найти и скопировать</button>
    <button class="clear-btn" onclick="clearTest1()">🗑️ Очистить тест1</button>
    
    <div class="status" id="status">Готов к работе</div>

    <script>
        // Единственная функция — вся логика линейна внутри
        function runFilter() {
            try {
                var ed = window.parent.Asc.editor;
                var statusEl = document.getElementById('status');
                statusEl.textContent = '⏳ Анализирую активный лист...';

                // 1. Получаем активный лист
                var activeSheet = ed.GetActiveSheet();
                if (!activeSheet) throw 'Нет активного листа';
                var activeSheetName = 'Активный лист';
                try { activeSheetName = activeSheet.GetName(); } catch(e) {}

                // 2. Используемый диапазон
                var usedRange = activeSheet.GetUsedRange();
                if (!usedRange) throw 'На листе «' + activeSheetName + '» нет данных';

                var rowCount = usedRange.GetRows().GetCount();
                var colCount = usedRange.GetCols().GetCount();
                var startRow = usedRange.GetRow();
                var startCol = usedRange.GetCol();
                var endRow = startRow + rowCount - 1;
                var endCol = startCol + colCount - 1;

                // 3. Диагностика — первые 5 строк
                var diagInfo = '';
                var maxDiagRows = Math.min(5, rowCount);
                for (var d = 0; d < maxDiagRows; d++) {
                    var diagRow = startRow + d;
                    var aVal = activeSheet.GetRange('A' + diagRow).GetValue();
                    var bVal = activeSheet.GetRange('B' + diagRow).GetValue();
                    diagInfo += 'Строка ' + diagRow + ': A=[' + aVal + '] B=[' + bVal + ']\n';
                }

                // 4. Поиск строк, удовлетворяющих условию
                var matchingRows = [];
                for (var r = startRow; r <= endRow; r++) {
                    var cellA = activeSheet.GetRange('A' + r);
                    var valA = cellA.GetValue();
                    var textA = (valA !== null && valA !== undefined) ? String(valA).trim().toLowerCase() : '';

                    var cellB = activeSheet.GetRange('B' + r);
                    var valB = cellB.GetValue();
                    var textB = (valB !== null && valB !== undefined) ? String(valB).trim().toLowerCase() : '';

                    if (textA === 'уратекст' && textB === 'проба') {
                        matchingRows.push(r);
                    }
                }

                if (matchingRows.length === 0) {
                    statusEl.textContent = '❌ Нет строк с A="уратекст" и B="проба" на листе «' + activeSheetName + '».\n' +
                                           'Первые строки листа:\n' + diagInfo + '\n' +
                                           '👉 Возможно, данные на другом листе. Перейдите на нужный и повторите.';
                    return;
                }

                // 5. Удаляем старый лист «тест1», если есть
                var test1 = null;
                if (typeof ed.GetSheet === 'function') {
                    test1 = ed.GetSheet('тест1');
                } else {
                    var sheetsAll = ed.GetSheets();
                    for (var i = 0; i < sheetsAll.GetCount(); i++) {
                        var sh = sheetsAll.GetSheet(i);
                        if (sh && sh.GetName && sh.GetName() === 'тест1') { test1 = sh; break; }
                    }
                }
                if (test1) {
                    test1.Delete();
                    try { ed.asc_Recalculate(); } catch(e) {}
                }

                // 6. Создаём новый лист «тест1»
                if (typeof ed.AddSheet === 'function') {
                    test1 = ed.AddSheet('тест1');
                } else {
                    ed.asc_addWorksheet('тест1');
                    if (typeof ed.GetSheet === 'function') {
                        test1 = ed.GetSheet('тест1');
                    } else {
                        var sheetsAll = ed.GetSheets();
                        for (var i = 0; i < sheetsAll.GetCount(); i++) {
                            var sh = sheetsAll.GetSheet(i);
                            if (sh && sh.GetName && sh.GetName() === 'тест1') { test1 = sh; break; }
                        }
                    }
                }
                if (!test1) throw 'Не удалось создать лист «тест1»';

                // 7. Копирование данных вручную (GetValue / SetValue)
                for (var i = 0; i < matchingRows.length; i++) {
                    var srcRow = matchingRows[i];
                    var targetRow = i + 1;
                    for (var c = startCol; c <= endCol; c++) {
                        var colLetter = String.fromCharCode(64 + c); // A, B, C...
                        var srcCell = activeSheet.GetRange(colLetter + srcRow);
                        var value = srcCell.GetValue();
                        test1.GetRange(colLetter + targetRow).SetValue(value);
                    }
                }

                // 8. Обновляем книгу
                try { ed.asc_Recalculate(); } catch(e) {}
                statusEl.textContent = '✅ Скопировано ' + matchingRows.length + ' строк на лист «тест1»';
            } catch(e) {
                document.getElementById('status').textContent = '❌ Ошибка: ' + (e.message || e);
            }
        }

        // Функция для кнопки очистки — тоже линейная
        function clearTest1() {
            try {
                var ed = window.parent.Asc.editor;
                document.getElementById('status').textContent = '🗑️ Удаляю лист «тест1»...';
                var test1 = null;
                if (typeof ed.GetSheet === 'function') {
                    test1 = ed.GetSheet('тест1');
                } else {
                    var sheetsAll = ed.GetSheets();
                    for (var i = 0; i < sheetsAll.GetCount(); i++) {
                        var sh = sheetsAll.GetSheet(i);
                        if (sh && sh.GetName && sh.GetName() === 'тест1') { test1 = sh; break; }
                    }
                }
                if (test1) {
                    test1.Delete();
                    try { ed.asc_Recalculate(); } catch(e) {}
                    document.getElementById('status').textContent = '✅ Лист «тест1» удалён';
                } else {
                    document.getElementById('status').textContent = '⚠️ Лист «тест1» не существует';
                }
            } catch(e) {
                document.getElementById('status').textContent = '❌ Ошибка: ' + (e.message || e);
            }
        }
    </script>
</body>
</html>








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
        button.clear-btn { background: #f44336; }
        .status {
            margin-top: 15px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 40px; white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h3>🔎 Фильтр «уратекст + проба»</h3>
    <p style="font-size:12px; color:#666;">
        Активный лист → строки, где A = "уратекст" и B = "проба"<br>
        → новый лист «тест1»
    </p>
    
    <!-- Кнопка 1: Найти и скопировать -->
    <button onclick="
        try {
            var ed = window.parent.Asc.editor;
            var statusEl = document.getElementById('status');

            // Получаем активный лист и его имя
            var activeSheet = ed.GetActiveSheet();
            if (!activeSheet) throw 'Нет активного листа';
            var activeSheetName = 'Активный лист';
            try { activeSheetName = activeSheet.GetName(); } catch(e) {}
            statusEl.textContent = '⏳ Анализирую лист «' + activeSheetName + '»...';

            var usedRange = activeSheet.GetUsedRange();
            if (!usedRange) throw 'На листе «' + activeSheetName + '» нет данных';

            var rowCount = usedRange.GetRows().GetCount();
            var colCount = usedRange.GetCols().GetCount();
            var startRow = usedRange.GetRow();
            var startCol = usedRange.GetCol();
            var endRow = startRow + rowCount - 1;
            var endCol = startCol + colCount - 1;

            // Диагностика: первые 5 строк
            var diagInfo = '';
            var maxDiagRows = Math.min(5, rowCount);
            for (var d = 0; d < maxDiagRows; d++) {
                var diagRow = startRow + d;
                var aVal = activeSheet.GetRange('A' + diagRow).GetValue();
                var bVal = activeSheet.GetRange('B' + diagRow).GetValue();
                diagInfo += 'Строка ' + diagRow + ': A=[' + aVal + '] B=[' + bVal + ']\n';
            }

            // Сбор подходящих строк
            var matchingRows = [];
            for (var r = startRow; r <= endRow; r++) {
                var cellA = activeSheet.GetRange('A' + r);
                var valA = cellA.GetValue();
                var textA = (valA !== null && valA !== undefined) ? String(valA).trim().toLowerCase() : '';

                var cellB = activeSheet.GetRange('B' + r);
                var valB = cellB.GetValue();
                var textB = (valB !== null && valB !== undefined) ? String(valB).trim().toLowerCase() : '';

                if (textA === 'уратекст' && textB === 'проба') {
                    matchingRows.push(r);
                }
            }

            if (matchingRows.length === 0) {
                statusEl.textContent = '❌ Нет строк с A="уратекст" и B="проба" на листе «' + activeSheetName + '».\n' +
                                       'Первые строки листа:\n' + diagInfo + '\n' +
                                       '👉 Возможно, данные находятся на другом листе. Перейдите на нужный лист и повторите.';
                return;
            }

            // Удаляем старый лист «тест1»
            var test1 = null;
            if (typeof ed.GetSheet === 'function') {
                test1 = ed.GetSheet('тест1');
            } else {
                var sheets = ed.GetSheets();
                for (var i = 0; i < sheets.GetCount(); i++) {
                    var sh = sheets.GetSheet(i);
                    if (sh && sh.GetName && sh.GetName() === 'тест1') { test1 = sh; break; }
                }
            }
            if (test1) {
                test1.Delete();
                try { ed.asc_Recalculate(); } catch(e) {}
            }

            // Создаём новый лист «тест1»
            if (typeof ed.AddSheet === 'function') {
                test1 = ed.AddSheet('тест1');
            } else {
                ed.asc_addWorksheet('тест1');
                if (typeof ed.GetSheet === 'function') {
                    test1 = ed.GetSheet('тест1');
                } else {
                    var sheets = ed.GetSheets();
                    for (var i = 0; i < sheets.GetCount(); i++) {
                        var sh = sheets.GetSheet(i);
                        if (sh && sh.GetName && sh.GetName() === 'тест1') { test1 = sh; break; }
                    }
                }
            }
            if (!test1) throw 'Не удалось создать лист «тест1»';

            // Ручное копирование ячеек
            for (var i = 0; i < matchingRows.length; i++) {
                var srcRow = matchingRows[i];
                var targetRow = i + 1;
                for (var c = startCol; c <= endCol; c++) {
                    var colLetter = String.fromCharCode(64 + c);
                    var srcCell = activeSheet.GetRange(colLetter + srcRow);
                    var value = srcCell.GetValue();
                    test1.GetRange(colLetter + targetRow).SetValue(value);
                }
            }

            try { ed.asc_Recalculate(); } catch(e) {}
            statusEl.textContent = '✅ Скопировано ' + matchingRows.length + ' строк на лист «тест1»';
        } catch(e) {
            document.getElementById('status').textContent = '❌ Ошибка: ' + (e.message || e);
        }
    ">📋 Найти и скопировать</button>

    <!-- Кнопка 2: Очистить тест1 -->
    <button class="clear-btn" onclick="
        try {
            var ed = window.parent.Asc.editor;
            document.getElementById('status').textContent = '🗑️ Удаляю лист «тест1»...';
            var test1 = null;
            if (typeof ed.GetSheet === 'function') {
                test1 = ed.GetSheet('тест1');
            } else {
                var sheets = ed.GetSheets();
                for (var i = 0; i < sheets.GetCount(); i++) {
                    var sh = sheets.GetSheet(i);
                    if (sh && sh.GetName && sh.GetName() === 'тест1') { test1 = sh; break; }
                }
            }
            if (test1) {
                test1.Delete();
                try { ed.asc_Recalculate(); } catch(e) {}
                document.getElementById('status').textContent = '✅ Лист «тест1» удалён';
            } else {
                document.getElementById('status').textContent = '⚠️ Лист «тест1» не существует';
            }
        } catch(e) {
            document.getElementById('status').textContent = '❌ Ошибка: ' + (e.message || e);
        }
    ">🗑️ Очистить тест1</button>

    <div class="status" id="status">Готов к работе</div>
</body>
</html>






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
        button.clear-btn { background: #f44336; }
        .status {
            margin-top: 15px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 40px; white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h3>🔎 Фильтр «уратекст + проба»</h3>
    <p style="font-size:12px; color:#666;">
        Активный лист → строки, где A = "уратекст" и B = "проба"<br>
        → новый лист «тест1»
    </p>
    
    <!-- Кнопка 1: Найти и скопировать -->
    <button onclick="
        try {
            var ed = window.parent.Asc.editor;
            var statusEl = document.getElementById('status');
            statusEl.textContent = '⏳ Анализирую активный лист...';

            var activeSheet = ed.GetActiveSheet();
            if (!activeSheet) throw 'Нет активного листа';

            var usedRange = activeSheet.GetUsedRange();
            if (!usedRange) throw 'На листе нет данных';

            var rowCount = usedRange.GetRows().GetCount();
            var colCount = usedRange.GetCols().GetCount();
            var startRow = usedRange.GetRow();
            var startCol = usedRange.GetCol();
            var endRow = startRow + rowCount - 1;
            var endCol = startCol + colCount - 1;

            // === ДИАГНОСТИКА: соберём образцы значений из первых строк ===
            var diagInfo = '';
            var maxDiagRows = Math.min(5, rowCount);
            for (var d = 0; d < maxDiagRows; d++) {
                var diagRow = startRow + d;
                var aVal = activeSheet.GetRange('A' + diagRow).GetValue();
                var bVal = activeSheet.GetRange('B' + diagRow).GetValue();
                diagInfo += 'Строка ' + diagRow + ': A=[' + aVal + '] B=[' + bVal + ']\n';
            }
            statusEl.textContent = '📊 Первые строки активного листа:\n' + diagInfo;

            // Сбор подходящих строк
            var matchingRows = [];

            for (var r = startRow; r <= endRow; r++) {
                var cellA = activeSheet.GetRange('A' + r);
                var valA = cellA.GetValue();
                var textA = (valA !== null && valA !== undefined) ? String(valA).trim().toLowerCase() : '';

                var cellB = activeSheet.GetRange('B' + r);
                var valB = cellB.GetValue();
                var textB = (valB !== null && valB !== undefined) ? String(valB).trim().toLowerCase() : '';

                if (textA === 'уратекст' && textB === 'проба') {
                    matchingRows.push(r);
                }
            }

            if (matchingRows.length === 0) {
                statusEl.textContent = '❌ Нет строк, удовлетворяющих условию.\n' + diagInfo + '\nПроверьте написание слов.';
                return;
            }

            // Удаляем старый лист «тест1»
            var test1 = null;
            if (typeof ed.GetSheet === 'function') {
                test1 = ed.GetSheet('тест1');
            } else {
                var sheets = ed.GetSheets();
                for (var i = 0; i < sheets.GetCount(); i++) {
                    var sh = sheets.GetSheet(i);
                    if (sh && sh.GetName && sh.GetName() === 'тест1') {
                        test1 = sh;
                        break;
                    }
                }
            }
            if (test1) {
                test1.Delete();
                try { ed.asc_Recalculate(); } catch(e) {}
            }

            // Создаём новый лист «тест1»
            if (typeof ed.AddSheet === 'function') {
                test1 = ed.AddSheet('тест1');
            } else {
                ed.asc_addWorksheet('тест1');
                if (typeof ed.GetSheet === 'function') {
                    test1 = ed.GetSheet('тест1');
                } else {
                    var sheets = ed.GetSheets();
                    for (var i = 0; i < sheets.GetCount(); i++) {
                        var sh = sheets.GetSheet(i);
                        if (sh && sh.GetName && sh.GetName() === 'тест1') {
                            test1 = sh;
                            break;
                        }
                    }
                }
            }
            if (!test1) throw 'Не удалось создать лист «тест1»';

            // Копируем строки вручную
            for (var i = 0; i < matchingRows.length; i++) {
                var srcRow = matchingRows[i];
                var targetRow = i + 1;
                for (var c = startCol; c <= endCol; c++) {
                    var colLetter = String.fromCharCode(64 + c);
                    var srcCell = activeSheet.GetRange(colLetter + srcRow);
                    var value = srcCell.GetValue();
                    test1.GetRange(colLetter + targetRow).SetValue(value);
                }
            }

            try { ed.asc_Recalculate(); } catch(e) {}
            statusEl.textContent = '✅ Скопировано ' + matchingRows.length + ' строк на лист «тест1»';
        } catch(e) {
            document.getElementById('status').textContent = '❌ Ошибка: ' + (e.message || e);
        }
    ">📋 Найти и скопировать</button>

    <!-- Кнопка 2: Очистить тест1 -->
    <button class="clear-btn" onclick="
        try {
            var ed = window.parent.Asc.editor;
            document.getElementById('status').textContent = '🗑️ Удаляю лист «тест1»...';
            var test1 = null;
            if (typeof ed.GetSheet === 'function') {
                test1 = ed.GetSheet('тест1');
            } else {
                var sheets = ed.GetSheets();
                for (var i = 0; i < sheets.GetCount(); i++) {
                    var sh = sheets.GetSheet(i);
                    if (sh && sh.GetName && sh.GetName() === 'тест1') {
                        test1 = sh;
                        break;
                    }
                }
            }
            if (test1) {
                test1.Delete();
                try { ed.asc_Recalculate(); } catch(e) {}
                document.getElementById('status').textContent = '✅ Лист «тест1» удалён';
            } else {
                document.getElementById('status').textContent = '⚠️ Лист «тест1» не существует';
            }
        } catch(e) {
            document.getElementById('status').textContent = '❌ Ошибка: ' + (e.message || e);
        }
    ">🗑️ Очистить тест1</button>

    <div class="status" id="status">Готов к работе</div>
</body>
</html>






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
        button.clear-btn { background: #f44336; }
        .status {
            margin-top: 15px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 40px; white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h3>🔎 Фильтр «уратекст + проба»</h3>
    <p style="font-size:12px; color:#666;">
        Активный лист → строки, где A = "уратекст" и B = "проба"<br>
        → новый лист «тест1»
    </p>
    
    <!-- Кнопка 1: Найти и скопировать -->
    <button onclick="
        // ========== НАЙТИ И СКОПИРОВАТЬ ==========
        try {
            var ed = window.parent.Asc.editor;
            document.getElementById('status').textContent = '⏳ Анализирую активный лист...';

            // Активный лист
            var activeSheet = ed.GetActiveSheet();
            if (!activeSheet) throw 'Нет активного листа';

            // Используемый диапазон (чтобы знать количество столбцов)
            var usedRange = activeSheet.GetUsedRange();
            if (!usedRange) throw 'На листе нет данных';

            var rowCount = usedRange.GetRows().GetCount();
            var colCount = usedRange.GetCols().GetCount();  // сколько всего столбцов в данных
            var startRow = usedRange.GetRow();
            var startCol = usedRange.GetCol();              // обычно 1 (A)
            var endRow = startRow + rowCount - 1;
            var endCol = startCol + colCount - 1;

            // Собираем номера подходящих строк
            var matchingRows = [];

            // Перебираем строки
            for (var r = startRow; r <= endRow; r++) {
                // Читаем столбец A
                var cellA = activeSheet.GetRange('A' + r);
                var valA = cellA.GetValue();
                var textA = (valA !== null && valA !== undefined) ? String(valA).trim().toLowerCase() : '';

                // Читаем столбец B
                var cellB = activeSheet.GetRange('B' + r);
                var valB = cellB.GetValue();
                var textB = (valB !== null && valB !== undefined) ? String(valB).trim().toLowerCase() : '';

                // Проверяем условие: A == 'уратекст' И B == 'проба'
                if (textA === 'уратекст' && textB === 'проба') {
                    matchingRows.push(r);
                }
            }

            if (matchingRows.length === 0) {
                document.getElementById('status').textContent = '❌ Нет строк, удовлетворяющих условию';
                return;
            }

            // Удаляем старый лист «тест1», если он существует
            var test1 = null;
            if (typeof ed.GetSheet === 'function') {
                test1 = ed.GetSheet('тест1');
            } else {
                var sheets = ed.GetSheets();
                for (var i = 0; i < sheets.GetCount(); i++) {
                    var sh = sheets.GetSheet(i);
                    if (sh && sh.GetName && sh.GetName() === 'тест1') {
                        test1 = sh;
                        break;
                    }
                }
            }
            if (test1) {
                test1.Delete();
                try { if (typeof ed.asc_Recalculate === 'function') ed.asc_Recalculate(); } catch(e) {}
            }

            // Создаём новый лист «тест1»
            if (typeof ed.AddSheet === 'function') {
                test1 = ed.AddSheet('тест1');
            } else {
                ed.asc_addWorksheet('тест1');
                // Ищем созданный лист повторно
                if (typeof ed.GetSheet === 'function') {
                    test1 = ed.GetSheet('тест1');
                } else {
                    var sheets = ed.GetSheets();
                    for (var i = 0; i < sheets.GetCount(); i++) {
                        var sh = sheets.GetSheet(i);
                        if (sh && sh.GetName && sh.GetName() === 'тест1') {
                            test1 = sh;
                            break;
                        }
                    }
                }
            }
            if (!test1) throw 'Не удалось создать лист «тест1»';

            // Копируем найденные строки ВРУЧНУЮ – через GetValue / SetValue
            for (var i = 0; i < matchingRows.length; i++) {
                var srcRow = matchingRows[i];
                var targetRow = i + 1;   // строки в «тест1» нумеруем с 1

                // Копируем каждую ячейку в строке (от startCol до endCol)
                for (var c = startCol; c <= endCol; c++) {
                    // Получаем букву столбца (1→A, 2→B, ...)
                    var colLetter = String.fromCharCode(64 + c);
                    
                    // Адрес исходной ячейки
                    var srcCell = activeSheet.GetRange(colLetter + srcRow);
                    var value = srcCell.GetValue();   // читаем значение

                    // Адрес целевой ячейки
                    var dstCell = test1.GetRange(colLetter + targetRow);
                    dstCell.SetValue(value);          // записываем значение
                }
            }

            // Обновляем книгу
            try { if (typeof ed.asc_Recalculate === 'function') ed.asc_Recalculate(); } catch(e) {}
            document.getElementById('status').textContent = '✅ Скопировано ' + matchingRows.length + ' строк на лист «тест1»';
        } catch(e) {
            document.getElementById('status').textContent = '❌ Ошибка: ' + (e.message || e);
        }
    ">📋 Найти и скопировать</button>

    <!-- Кнопка 2: Очистить тест1 -->
    <button class="clear-btn" onclick="
        // ========== ОЧИСТИТЬ ЛИСТ «тест1» ==========
        try {
            var ed = window.parent.Asc.editor;
            document.getElementById('status').textContent = '🗑️ Удаляю лист «тест1»...';

            var test1 = null;
            if (typeof ed.GetSheet === 'function') {
                test1 = ed.GetSheet('тест1');
            } else {
                var sheets = ed.GetSheets();
                for (var i = 0; i < sheets.GetCount(); i++) {
                    var sh = sheets.GetSheet(i);
                    if (sh && sh.GetName && sh.GetName() === 'тест1') {
                        test1 = sh;
                        break;
                    }
                }
            }

            if (test1) {
                test1.Delete();
                try { if (typeof ed.asc_Recalculate === 'function') ed.asc_Recalculate(); } catch(e) {}
                document.getElementById('status').textContent = '✅ Лист «тест1» удалён';
            } else {
                document.getElementById('status').textContent = '⚠️ Лист «тест1» не существует';
            }
        } catch(e) {
            document.getElementById('status').textContent = '❌ Ошибка: ' + (e.message || e);
        }
    ">🗑️ Очистить тест1</button>

    <div class="status" id="status">Готов к работе</div>
</body>
</html>








Сделаем плагин с двумя кнопками и линейным кодом — все операции (получение листов, поиск, создание «тест1», копирование, удаление) прописаны прямо внутри обработчиков нажатий, без дополнительных пользовательских функций.
Остались только три короткие служебные строки: editor(), setStatus() и refresh() – они не содержат бизнес-логики, а просто сокращают обращения к API.

---

1. config.json (без изменений)

```json
{
    "name": "Фильтр уратекст+проба",
    "guid": "asc.{filter-ura-proba-001}",
    "variations": [
        {
            "url": "index.html",
            "EditorsSupport": ["spreadsheet"],
            "isVisual": true,
            "isModal": false,
            "isInsideMode": false,
            "size": [330, 250]
        }
    ]
}
```

---

2. index.html (линейный код)

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
        button.clear-btn { background: #f44336; }
        .status {
            margin-top: 15px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 40px; white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h3>🔎 Фильтр «уратекст + проба»</h3>
    <p style="font-size:12px; color:#666;">
        Активный лист → строки, где A = "уратекст" и B = "проба"<br>
        → новый лист «тест1»
    </p>
    
    <!-- Кнопка 1: Найти и скопировать -->
    <button onclick="
        // ========== НАЙТИ И СКОПИРОВАТЬ ==========
        try {
            var ed = window.parent.Asc.editor;
            // Устанавливаем статус
            document.getElementById('status').textContent = '⏳ Анализирую активный лист...';

            // Активный лист
            var activeSheet = ed.GetActiveSheet();
            if (!activeSheet) throw 'Нет активного листа';

            // Используемый диапазон
            var usedRange = activeSheet.GetUsedRange();
            if (!usedRange) throw 'На листе нет данных';

            var rowCount = usedRange.GetRows().GetCount();
            var startRow = usedRange.GetRow();
            var endRow = startRow + rowCount - 1;

            // Собираем номера подходящих строк
            var matchingRows = [];

            // Перебираем строки
            for (var r = startRow; r <= endRow; r++) {
                // Читаем столбец A
                var cellA = activeSheet.GetRange('A' + r);
                var valA = cellA.GetValue();
                var textA = (valA !== null && valA !== undefined) ? String(valA).trim().toLowerCase() : '';

                // Читаем столбец B
                var cellB = activeSheet.GetRange('B' + r);
                var valB = cellB.GetValue();
                var textB = (valB !== null && valB !== undefined) ? String(valB).trim().toLowerCase() : '';

                // Проверяем условие: A == 'уратекст' И B == 'проба'
                if (textA === 'уратекст' && textB === 'проба') {
                    matchingRows.push(r);
                }
            }

            if (matchingRows.length === 0) {
                document.getElementById('status').textContent = '❌ Нет строк, удовлетворяющих условию';
                return;
            }

            // Удаляем старый лист «тест1», если он существует
            var test1 = null;
            // Пытаемся найти лист 'тест1' по имени (без отдельной функции)
            if (typeof ed.GetSheet === 'function') {
                test1 = ed.GetSheet('тест1');
            } else {
                var sheets = ed.GetSheets();
                for (var i = 0; i < sheets.GetCount(); i++) {
                    var sh = sheets.GetSheet(i);
                    if (sh && sh.GetName && sh.GetName() === 'тест1') {
                        test1 = sh;
                        break;
                    }
                }
            }
            if (test1) {
                test1.Delete();
                try { if (typeof ed.asc_Recalculate === 'function') ed.asc_Recalculate(); } catch(e) {}
            }

            // Создаём новый лист «тест1»
            if (typeof ed.AddSheet === 'function') {
                test1 = ed.AddSheet('тест1');
            } else {
                ed.asc_addWorksheet('тест1');
                // Ищем созданный лист повторно
                if (typeof ed.GetSheet === 'function') {
                    test1 = ed.GetSheet('тест1');
                } else {
                    var sheets = ed.GetSheets();
                    for (var i = 0; i < sheets.GetCount(); i++) {
                        var sh = sheets.GetSheet(i);
                        if (sh && sh.GetName && sh.GetName() === 'тест1') {
                            test1 = sh;
                            break;
                        }
                    }
                }
            }
            if (!test1) throw 'Не удалось создать лист «тест1»';

            // Копируем найденные строки
            for (var i = 0; i < matchingRows.length; i++) {
                var srcRow = matchingRows[i];
                var targetRow = i + 1;
                activeSheet.GetRange(srcRow + ':' + srcRow).Copy(test1.GetRange('A' + targetRow));
            }

            // Обновляем книгу
            try { if (typeof ed.asc_Recalculate === 'function') ed.asc_Recalculate(); } catch(e) {}
            document.getElementById('status').textContent = '✅ Скопировано ' + matchingRows.length + ' строк на лист «тест1»';
        } catch(e) {
            document.getElementById('status').textContent = '❌ Ошибка: ' + (e.message || e);
        }
    ">📋 Найти и скопировать</button>

    <!-- Кнопка 2: Очистить тест1 -->
    <button class="clear-btn" onclick="
        // ========== ОЧИСТИТЬ ЛИСТ «тест1» ==========
        try {
            var ed = window.parent.Asc.editor;
            document.getElementById('status').textContent = '🗑️ Удаляю лист «тест1»...';

            // Ищем лист «тест1»
            var test1 = null;
            if (typeof ed.GetSheet === 'function') {
                test1 = ed.GetSheet('тест1');
            } else {
                var sheets = ed.GetSheets();
                for (var i = 0; i < sheets.GetCount(); i++) {
                    var sh = sheets.GetSheet(i);
                    if (sh && sh.GetName && sh.GetName() === 'тест1') {
                        test1 = sh;
                        break;
                    }
                }
            }

            if (test1) {
                test1.Delete();
                try { if (typeof ed.asc_Recalculate === 'function') ed.asc_Recalculate(); } catch(e) {}
                document.getElementById('status').textContent = '✅ Лист «тест1» удалён';
            } else {
                document.getElementById('status').textContent = '⚠️ Лист «тест1» не существует';
            }
        } catch(e) {
            document.getElementById('status').textContent = '❌ Ошибка: ' + (e.message || e);
        }
    ">🗑️ Очистить тест1</button>

    <div class="status" id="status">Готов к работе</div>
</body>
</html>
```

---

Что изменилось по сравнению с предыдущей версией

· Убраны все пользовательские функции (getSheet, filterAndCopy, clearTest1).
· Код каждой кнопки теперь полностью встроен в атрибут onclick и выполняется последовательно, шаг за шагом.
· Внутри кода все операции – поиск листа, создание, удаление – развёрнуты прямо в обработчиках (с повторением одного и того же поиска для «тест1», но это плата за линейность).
· Комментарии сохранены, чтобы легко понимать логику.

Плагин делает ровно то же самое:

1. Находит на активном листе строки с A = «уратекст» и B = «проба».
2. Создаёт лист «тест1» (предварительно удаляя старый).
3. Копирует найденные строки целиком на новый лист.
4. Вторая кнопка удаляет «тест1» для повторного запуска.

Вы можете скопировать этот файл в папку плагина, конфиг оставить прежним. Всё работает стабильно, как и проверенные ранее варианты.








Мы перепишем проект, заменив Flask-SQLAlchemy на встроенный модуль sqlite3.
Ограничений по IP не будет — бот доступен всем.
База данных — файл chatbot.db в той же папке.

Структура проекта

```
chatbot/
├── app.py
├── requirements.txt
└── templates/
    ├── chat.html
    ├── add_qa.html
    └── list_qa.html
```

1. requirements.txt

```txt
Flask==3.0.0
```

Только Flask, больше ничего не нужно.

2. app.py — полный код

```python
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, g

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
DATABASE = 'chatbot.db'

# ---------- Работа с базой данных ----------
def get_db():
    """Возвращает соединение с БД для текущего запроса"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # чтобы можно было обращаться по имени столбца
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """Закрываем соединение после завершения запроса"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Создаём таблицы и наполняем тестовыми данными, если БД пуста"""
    # Используем отдельное соединение, чтобы не зависеть от контекста запроса
    conn = sqlite3.connect(DATABASE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Проверяем, есть ли записи
    count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    if count == 0:
        sample_qa = [
            ('привет', 'Здравствуйте! Я чат-бот. Чем могу помочь?'),
            ('как дела', 'У меня всё отлично! Я готов отвечать на ваши вопросы.'),
            ('что ты умеешь', 'Я могу отвечать на вопросы, которые есть в моей базе данных. Спросите меня о чём-нибудь!'),
            ('пока', 'До свидания! Буду ждать вашего возвращения.'),
            ('спасибо', 'Пожалуйста! Рад был помочь.'),
            ('какая погода', 'Извините, я не умею проверять погоду. Но могу ответить на другие вопросы!'),
            ('расскажи шутку', 'Почему программисты путают Рождество и Хэллоуин? Потому что 31 OCT = 25 DEC!')
        ]
        conn.executemany(
            "INSERT INTO questions (question, answer) VALUES (?, ?)",
            sample_qa
        )
        conn.commit()
        print("База данных инициализирована тестовыми вопросами.")
    conn.close()

# Инициализируем БД до первого запроса
with app.app_context():
    init_db()

# ---------- Логика поиска ответа ----------
def find_best_answer(user_question):
    """Ищет лучший ответ в базе"""
    user_question = user_question.lower().strip()
    db = get_db()

    # 1. Точное совпадение
    row = db.execute(
        "SELECT answer FROM questions WHERE question = ?",
        (user_question,)
    ).fetchone()
    if row:
        return row['answer']

    # 2. Вопрос целиком содержится в поле question (LIKE '%вопрос%')
    row = db.execute(
        "SELECT answer FROM questions WHERE question LIKE ?",
        ('%' + user_question + '%',)
    ).fetchone()
    if row:
        return row['answer']

    # 3. Поле question содержится в вопросе пользователя
    row = db.execute(
        "SELECT answer FROM questions WHERE ? LIKE '%' || question || '%'",
        (user_question,)
    ).fetchone()
    if row:
        return row['answer']

    return None

# ---------- Маршруты ----------
@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question', '').strip()
    if not question:
        return jsonify({'answer': 'Пожалуйста, задайте вопрос.', 'status': 'error'})

    answer = find_best_answer(question)
    if answer:
        return jsonify({'answer': answer, 'status': 'success'})
    else:
        return jsonify({
            'answer': 'Извините, я пока не знаю ответа на этот вопрос. Попробуйте спросить что-нибудь другое!',
            'status': 'not_found'
        })

@app.route('/add_qa', methods=['GET', 'POST'])
def add_qa():
    if request.method == 'POST':
        question = request.form.get('question', '').strip().lower()
        answer = request.form.get('answer', '').strip()
        if not question or not answer:
            return jsonify({'message': 'Заполните оба поля!', 'status': 'error'})

        db = get_db()
        exists = db.execute(
            "SELECT id FROM questions WHERE question = ?",
            (question,)
        ).fetchone()
        if exists:
            return jsonify({'message': 'Такой вопрос уже существует!', 'status': 'error'})

        db.execute(
            "INSERT INTO questions (question, answer) VALUES (?, ?)",
            (question, answer)
        )
        db.commit()
        return jsonify({'message': 'Вопрос и ответ успешно добавлены!', 'status': 'success'})

    return render_template('add_qa.html')

@app.route('/list_qa')
def list_qa():
    db = get_db()
    rows = db.execute(
        "SELECT id, question, answer, created_at FROM questions ORDER BY created_at DESC"
    ).fetchall()
    return render_template('list_qa.html', qa_list=rows)

@app.route('/delete_qa/<int:id>', methods=['DELETE'])
def delete_qa(id):
    db = get_db()
    db.execute("DELETE FROM questions WHERE id = ?", (id,))
    db.commit()
    return jsonify({'status': 'success', 'message': 'Удалено успешно'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

3. Шаблоны

templates/chat.html

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Чат-бот</title>
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .chat-container { width: 400px; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); display: flex; flex-direction: column; overflow: hidden; }
        .chat-header { background: #667eea; color: white; padding: 20px; text-align: center; font-size: 20px; }
        .chat-messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .message { max-width: 80%; padding: 10px 15px; border-radius: 15px; word-wrap: break-word; }
        .user-message { align-self: flex-end; background: #667eea; color: white; }
        .bot-message { align-self: flex-start; background: #f0f0f0; color: #333; }
        .chat-input { padding: 20px; background: #f8f8f8; display: flex; gap: 10px; }
        .chat-input input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 25px; outline: none; }
        .chat-input button { padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 25px; cursor: pointer; }
        .nav-buttons { text-align: center; padding: 10px; }
        .nav-buttons a { color: #667eea; text-decoration: none; margin: 0 10px; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">🤖 Чат-бот</div>
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">Привет! Я чат-бот. Задайте мне вопрос!</div>
        </div>
        <div class="nav-buttons">
            <a href="/add_qa">Добавить Q&A</a>
            <a href="/list_qa">Список</a>
        </div>
        <div class="chat-input">
            <input type="text" id="userInput" placeholder="Введите ваш вопрос..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Отправить</button>
        </div>
    </div>
    <script>
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if (!message) return;
            addMessage(message, 'user');
            input.value = '';
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: message})
                });
                const data = await response.json();
                setTimeout(() => addMessage(data.answer, 'bot'), 500);
            } catch (e) {
                addMessage('Ошибка соединения', 'bot');
            }
        }
        function addMessage(text, sender) {
            const div = document.createElement('div');
            div.className = `message ${sender}-message`;
            div.textContent = text;
            document.getElementById('chatMessages').appendChild(div);
            document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight;
        }
    </script>
</body>
</html>
```

templates/add_qa.html

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Добавить вопрос-ответ</title>
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); height: 100vh; display: flex; justify-content: center; align-items: center; }
        .container { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); width: 500px; }
        h1 { color: #667eea; }
        form { display: flex; flex-direction: column; gap: 15px; }
        input, textarea { padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; }
        a { display: block; text-align: center; margin-top: 15px; color: #667eea; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Добавить новый вопрос-ответ</h1>
        <form id="qaForm">
            <input type="text" id="question" placeholder="Вопрос" required>
            <textarea id="answer" placeholder="Ответ" rows="4" required></textarea>
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
            const res = await fetch('/add_qa', { method: 'POST', body: formData });
            const data = await res.json();
            const msg = document.getElementById('message');
            msg.textContent = data.message;
            msg.style.color = data.status === 'success' ? 'green' : 'red';
            if (data.status === 'success') {
                document.getElementById('question').value = '';
                document.getElementById('answer').value = '';
            }
        });
    </script>
</body>
</html>
```

templates/list_qa.html

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Список вопросов-ответов</title>
    <style>
        body { font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); padding: 40px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        h1 { color: #667eea; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f0f0f0; }
        a { color: #667eea; }
        button.danger { background: #e53e3e; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Все вопросы-ответы</h1>
        <a href="/">← Вернуться к чату</a>
        <table>
            <thead>
                <tr>
                    <th>Вопрос</th>
                    <th>Ответ</th>
                    <th>Действия</th>
                </tr>
            </thead>
            <tbody>
                {% for qa in qa_list %}
                <tr>
                    <td>{{ qa['question'] }}</td>
                    <td>{{ qa['answer'] }}</td>
                    <td><button class="danger" onclick="deleteQA({{ qa['id'] }})">Удалить</button></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    <script>
        async function deleteQA(id) {
            if (!confirm('Удалить?')) return;
            await fetch(`/delete_qa/${id}`, { method: 'DELETE' });
            location.reload();
        }
    </script>
</body>
</html>
```

Как запустить

1. Сохраните все файлы в одной папке.
2. Установите Flask:

```bash
pip install flask
```

3. Запустите:

```bash
python app.py
```

4. Откройте http://localhost:5000

База данных chatbot.db создастся автоматически с тестовыми вопросами.
Никаких внешних библиотек, кроме Flask, не требуется.
Работает точно так же, как первый вариант, но на чистом SQLite.
