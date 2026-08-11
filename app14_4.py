
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
