
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
        button:hover { opacity: 0.9; }
        .status {
            margin-top: 15px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 40px; word-break: break-word;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h3>🔄 Обработка и фильтр</h3>
    
    <!-- Секция старого функционала (замена и копирование) -->
    <p style="font-size:12px; color:#666;">Замена в столбцах Z и копирование:</p>
    <button onclick="processAll()">⚡ Выполнить замену и копирование</button>
    <div class="status" id="status">Готов к работе</div>
    
    <hr style="margin:15px 0;">
    
    <!-- Новая секция: фильтр "уратекст + проба" -->
    <p style="font-size:12px; color:#666;">Фильтр активного листа:</p>
    <button onclick="runFilter()" style="background:#2196F3;">📋 Найти «уратекст» + «проба» → лист «тест1»</button>
    <button onclick="clearTest1()" style="background:#f44336;">🗑️ Удалить лист «тест1»</button>

    <script>
        // ========== ВСПОМОГАТЕЛЬНЫЕ МИНИ-ФУНКЦИИ (без бизнес-логики) ==========
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

        function getLastRowInColumn(sheet, colLetter) {
            var used = sheet.GetUsedRange();
            if (!used) return 0;
            var lastRow = used.GetRow() + used.GetRows().GetCount() - 1;
            for (var r = lastRow; r >= 1; r--) {
                var val = sheet.GetRange(colLetter + r).GetValue();
                if (val !== null && val !== undefined && String(val).trim() !== '') return r;
            }
            return 0;
        }

        // ========== СТАРЫЙ ФУНКЦИОНАЛ (замена и копирование) ==========
        function processAll() {
            setStatus('⏳ Выполняю замену и копирование...');
            try {
                var ed = editor();
                // Пара 1: 60323_iskhod → 60323_ОБОРОТ
                var src1 = getSheet('60323_iskhod'), dst1 = getSheet('60323_ОБОРОТ');
                if (!src1 || !dst1) throw 'Не найдены листы 60323_iskhod или 60323_ОБОРОТ';
                var lastRow1 = getLastRowInColumn(src1, 'Z');
                if (lastRow1 === 0) throw 'Столбец Z пуст на 60323_iskhod';
                for (var r = 1; r <= lastRow1; r++) {
                    var cell = src1.GetRange('Z' + r);
                    var val = cell.GetValue();
                    if (val !== null && val !== undefined) {
                        var newVal = String(val).replace(/,/g, '').replace(/\./g, ',');
                        if (newVal !== String(val)) cell.SetValue(newVal);
                    }
                }
                refresh();
                src1.GetRange('Z1:Z' + lastRow1).Copy(dst1.GetRange('A1'));
                refresh();

                // Пара 2: 60324_iskhod → 60324_ОБОРОТ
                var src2 = getSheet('60324_iskhod'), dst2 = getSheet('60324_ОБОРОТ');
                if (!src2 || !dst2) throw 'Не найдены листы 60324_iskhod или 60324_ОБОРОТ';
                var lastRow2 = getLastRowInColumn(src2, 'Z');
                if (lastRow2 === 0) throw 'Столбец Z пуст на 60324_iskhod';
                for (var r = 1; r <= lastRow2; r++) {
                    var cell = src2.GetRange('Z' + r);
                    var val = cell.GetValue();
                    if (val !== null && val !== undefined) {
                        var newVal = String(val).replace(/,/g, '').replace(/\./g, ',');
                        if (newVal !== String(val)) cell.SetValue(newVal);
                    }
                }
                refresh();
                src2.GetRange('Z1:Z' + lastRow2).Copy(dst2.GetRange('A1'));
                refresh();
                setStatus('✅ Готово! 60323: ' + lastRow1 + ' строк, 60324: ' + lastRow2 + ' строк.');
            } catch(e) { setStatus('❌ Ошибка: ' + (e.message || e)); }
        }

        // ========== НОВЫЙ ФУНКЦИОНАЛ (фильтр уратекст + проба) ==========
        function runFilter() {
            setStatus('⏳ Ищу строки с "уратекст" и "проба"...');
            try {
                var ed = editor();
                // 1. Запоминаем активный лист (источник)
                var sourceSheet = ed.GetActiveSheet();
                if (!sourceSheet) throw 'Нет активного листа';
                var sourceName = 'исходный';
                try { sourceName = sourceSheet.GetName(); } catch(e) {}

                // 2. Получаем используемый диапазон
                var used = sourceSheet.GetUsedRange();
                if (!used) throw 'На листе «' + sourceName + '» нет данных';
                var startRow = used.GetRow();
                var endRow = startRow + used.GetRows().GetCount() - 1;
                var startCol = used.GetCol();
                var endCol = startCol + used.GetCols().GetCount() - 1;
                var lastColLetter = String.fromCharCode(64 + endCol); // буква последнего столбца

                // 3. Ищем строки, где A = "уратекст" и B = "проба" (без учёта регистра)
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
                    setStatus('❌ На листе «' + sourceName + '» нет строк с A="уратекст" и B="проба".');
                    return;
                }

                // 4. Удаляем старый лист «тест1», если есть
                var test1 = getSheet('тест1');
                if (test1) {
                    test1.Delete();
                    refresh();
                }

                // 5. Создаём новый лист «тест1»
                if (typeof ed.AddSheet === 'function') {
                    test1 = ed.AddSheet('тест1');
                } else {
                    ed.asc_addWorksheet('тест1');
                    test1 = getSheet('тест1');
                }
                if (!test1) throw 'Не удалось создать лист «тест1»';

                // 6. Активируем «тест1» (важно для Copy)
                test1.SetActive();
                refresh();

                // 7. Копируем каждую найденную строку через проверенный Copy
                for (var i = 0; i < matchingRows.length; i++) {
                    var srcRow = matchingRows[i];
                    var targetRow = i + 1;
                    // Копируем диапазон от A до последнего столбца в найденной строке
                    var srcRange = sourceSheet.GetRange('A' + srcRow + ':' + lastColLetter + srcRow);
                    var dstCell = test1.GetRange('A' + targetRow);
                    srcRange.Copy(dstCell);
                }
                refresh();

                // 8. Возвращаем активацию исходному листу
                sourceSheet.SetActive();
                refresh();

                setStatus('✅ На лист «тест1» скопировано ' + matchingRows.length + ' строк из листа «' + sourceName + '».');
            } catch(e) {
                setStatus('❌ Ошибка: ' + (e.message || e));
            }
        }

        function clearTest1() {
            setStatus('🗑️ Удаляю лист «тест1»...');
            try {
                var test1 = getSheet('тест1');
                if (test1) {
                    test1.Delete();
                    refresh();
                    setStatus('✅ Лист «тест1» удалён');
                } else {
                    setStatus('⚠️ Лист «тест1» не существует');
                }
            } catch(e) {
                setStatus('❌ Ошибка: ' + (e.message || e));
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

                // 7. Активируем лист «тест1» для корректной записи
                test1.SetActive();
                try { ed.asc_Recalculate(); } catch(e) {}

                // 8. Копирование данных с ИСХОДНОГО листа на тест1 через ed.asc_setData
                for (var i = 0; i < matchingRows.length; i++) {
                    var srcRow = matchingRows[i];
                    var targetRow = i + 1;
                    for (var c = startCol; c <= endCol; c++) {
                        var colLetter = String.fromCharCode(64 + c);
                        // Читаем из sourceSheet (он не активен, но чтение работает)
                        var srcCell = sourceSheet.GetRange(colLetter + srcRow);
                        var value = srcCell.GetValue();
                        // Формируем адрес ячейки на активном листе (тест1)
                        var targetAddress = colLetter + targetRow;
                        // Записываем через проверенный asc_setData
                        ed.asc_setData(targetAddress, value);
                    }
                }
                try { ed.asc_Recalculate(); } catch(e) {}

                // 9. Возвращаем активацию исходному листу
                sourceSheet.SetActive();
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
