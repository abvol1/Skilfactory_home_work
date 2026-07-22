<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 12px; background: #f5f5f5; }
        h3 { margin-top: 0; }
        .row { display: flex; gap: 8px; align-items: center; margin-bottom: 10px; }
        .row label { width: 90px; font-size: 13px; }
        .row select, .row button { flex: 1; padding: 8px; font-size: 13px; border-radius: 4px; border: 1px solid #ccc; }
        button {
            display: block; width: 100%; padding: 10px; margin: 8px 0;
            border: none; border-radius: 6px; font-size: 14px; font-weight: bold;
            cursor: pointer; color: white; background: #4CAF50;
        }
        button:hover { opacity: 0.9; }
        .status {
            margin-top: 12px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 30px; white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h3>📊 Мастер сводной</h3>
    <p style="font-size:12px; color:#555;">Активный лист будет использован как источник.</p>
    
    <div class="row">
        <label>Группировка:</label>
        <select id="groupCol"><option value="">Выберите столбец</option></select>
    </div>
    <div class="row">
        <label>Значения:</label>
        <select id="valueCol"><option value="">Выберите столбец</option></select>
    </div>
    <div class="row">
        <label>Агрегация:</label>
        <select id="aggType">
            <option value="sum">Сумма</option>
            <option value="avg">Среднее</option>
            <option value="max">Максимум</option>
            <option value="min">Минимум</option>
            <option value="count">Количество</option>
        </select>
    </div>
    
    <button onclick="loadColumns()">🔄 Обновить список столбцов</button>
    <button onclick="createPivotTable()">⚡ Построить сводную таблицу</button>
    
    <div class="status" id="status">Готов. Нажмите «Обновить», чтобы загрузить заголовки с активного листа.</div>

    <script>
        // ========== БАЗОВЫЕ ФУНКЦИИ ==========
        function editor() { 
            var ed = window.parent && window.parent.Asc && window.parent.Asc.editor;
            if (!ed) throw 'Редактор не доступен';
            return ed;
        }
        function setStatus(msg) { document.getElementById('status').textContent = msg; }
        function refresh() { 
            try { 
                var ed = editor();
                if (typeof ed.asc_Recalculate === 'function') ed.asc_Recalculate(); 
            } catch(e) {} 
        }

        // Получить лист по имени
        function getSheet(name) {
            try {
                var ed = editor();
                if (typeof ed.GetSheet === 'function') return ed.GetSheet(name);
                var sheets = ed.GetSheets();
                if (sheets && typeof sheets.GetSheet === 'function') {
                    for (var i = 0; i < sheets.GetCount(); i++) {
                        var sh = sheets.GetSheet(i);
                        if (sh && sh.GetName && sh.GetName() === name) return sh;
                    }
                }
                return null;
            } catch(e) { return null; }
        }

        // Загрузка заголовков
        function loadColumns() {
            setStatus('⏳ Считываю заголовки...');
            try {
                var ed = editor();
                var sheet = ed.GetActiveSheet();
                if (!sheet) { setStatus('❌ Нет активного листа'); return; }
                
                var used = sheet.GetUsedRange();
                if (!used) { setStatus('❌ На листе нет данных'); return; }
                
                var firstRow = used.GetRow();
                var lastCol = used.GetCol() + used.GetCols().GetCount() - 1;
                
                var groupSel = document.getElementById('groupCol');
                var valueSel = document.getElementById('valueCol');
                groupSel.innerHTML = '<option value="">Выберите столбец</option>';
                valueSel.innerHTML = '<option value="">Выберите столбец</option>';
                
                for (var col = 1; col <= lastCol; col++) {
                    try {
                        var colLetter = String.fromCharCode(64 + col);
                        var cell = sheet.GetRange(colLetter + firstRow);
                        var val = cell.GetValue();
                        if (val !== null && val !== undefined && String(val).trim() !== '') {
                            var text = String(val).trim();
                            groupSel.add(new Option(text, colLetter));
                            valueSel.add(new Option(text, colLetter));
                        }
                    } catch(e) {}
                }
                setStatus('✅ Заголовки загружены. Выберите столбцы и нажмите «Построить сводную таблицу».');
            } catch(e) {
                setStatus('❌ Ошибка загрузки: ' + (e.message || e));
            }
        }

        // Построение сводной таблицы (без диаграммы)
        function createPivotTable() {
            var groupCol = document.getElementById('groupCol').value;
            var valueCol = document.getElementById('valueCol').value;
            var aggType = document.getElementById('aggType').value;
            
            if (!groupCol || !valueCol) {
                setStatus('⚠️ Выберите столбцы для группировки и значений.');
                return;
            }
            
            setStatus('⏳ Начинаю построение...');
            try {
                var ed = editor();
                var srcSheet = ed.GetActiveSheet();
                if (!srcSheet) throw 'Не удалось получить активный лист';
                
                var used = srcSheet.GetUsedRange();
                if (!used) throw 'На листе нет данных';
                
                var firstRow = used.GetRow();
                var rowsCount = used.GetRows().GetCount();
                var dataStartRow = firstRow + 1;
                
                // Сбор данных
                var groups = {};
                for (var r = dataStartRow; r < firstRow + rowsCount; r++) {
                    var keyCell = srcSheet.GetRange(groupCol + r).GetValue();
                    var valCell = srcSheet.GetRange(valueCol + r).GetValue();
                    if (keyCell === null || keyCell === undefined || keyCell === '') continue;
                    var key = String(keyCell).trim();
                    var num = parseFloat(valCell);
                    if (!groups[key]) {
                        groups[key] = { sum: 0, count: 0, values: [] };
                    }
                    if (!isNaN(num)) {
                        groups[key].sum += num;
                        groups[key].count += 1;
                        groups[key].values.push(num);
                    } else {
                        groups[key].values.push(0);
                    }
                }
                
                if (Object.keys(groups).length === 0) {
                    setStatus('⚠️ Нет данных для группировки');
                    return;
                }
                
                // Создаём новый лист
                var pivotSheetName = 'Сводная_' + new Date().toISOString().replace(/[:.]/g, '-');
                ed.asc_addWorksheet(pivotSheetName);
                var pivotSheet = getSheet(pivotSheetName);
                if (!pivotSheet) throw 'Не удалось создать/найти лист ' + pivotSheetName;
                
                // Заголовки
                pivotSheet.GetRange('A1').SetValue('Группа');
                pivotSheet.GetRange('B1').SetValue(aggType.charAt(0).toUpperCase() + aggType.slice(1));
                pivotSheet.GetRange('A1:B1').SetBold(true);
                
                // Заполнение данных
                var row = 2;
                var groupNames = Object.keys(groups).sort();
                for (var i = 0; i < groupNames.length; i++) {
                    var g = groupNames[i];
                    var aggValue;
                    switch(aggType) {
                        case 'sum': aggValue = groups[g].sum; break;
                        case 'avg': aggValue = groups[g].count ? groups[g].sum / groups[g].count : 0; break;
                        case 'max': aggValue = Math.max(...groups[g].values); break;
                        case 'min': aggValue = Math.min(...groups[g].values); break;
                        case 'count': aggValue = groups[g].values.length; break;
                        default: aggValue = groups[g].sum;
                    }
                    pivotSheet.GetRange('A' + row).SetValue(g);
                    pivotSheet.GetRange('B' + row).SetValue(aggValue);
                    row++;
                }
                
                // Автоподбор ширины
                try { pivotSheet.GetRange('A:A').AutoFit(); } catch(e) {}
                try { pivotSheet.GetRange('B:B').AutoFit(); } catch(e) {}
                
                // Числовой формат
                if (aggType !== 'count') {
                    pivotSheet.GetRange('B2:B' + (row-1)).SetNumberFormat('#,##0.00');
                }
                
                refresh();
                setStatus('✅ Сводная таблица создана на листе "' + pivotSheetName + '"');
            } catch(e) {
                setStatus('❌ Ошибка: ' + (e.message || e) + (e.stack ? '\nСтек: ' + e.stack.split('\n').slice(0,3).join('\n') : ''));
            }
        }

        window.onload = function() {
            setStatus('✅ Плагин готов. Нажмите «Обновить список столбцов».');
            setTimeout(loadColumns, 500);
        };
    </script>
</body>
</html>












function createPivotTable() {
    var groupCol = document.getElementById('groupCol').value;
    var valueCol = document.getElementById('valueCol').value;
    var aggType = document.getElementById('aggType').value;
    
    if (!groupCol || !valueCol) {
        setStatus('⚠️ Выберите столбцы для группировки и значений.');
        return;
    }
    
    setStatus('⏳ Начинаю построение...');
    try {
        var srcSheet = editor().GetActiveSheet();
        if (!srcSheet) throw 'Не удалось получить активный лист';
        setStatus('⏳ Активный лист получен');
        
        var used = srcSheet.GetUsedRange();
        if (!used) throw 'На листе нет данных (GetUsedRange вернул null)';
        setStatus('⏳ Используемый диапазон получен');
        
        var firstRow = used.GetRow();
        var rowsCount = used.GetRows().GetCount();
        var dataStartRow = firstRow + 1;
        setStatus('⏳ Строк: ' + rowsCount + ', первая строка: ' + firstRow);
        
        // Сбор данных
        var groups = {};
        for (var r = dataStartRow; r < firstRow + rowsCount; r++) {
            var keyCell = srcSheet.GetRange(groupCol + r).GetValue();
            var valCell = srcSheet.GetRange(valueCol + r).GetValue();
            if (keyCell === null || keyCell === undefined || keyCell === '') continue;
            var key = String(keyCell).trim();
            var num = parseFloat(valCell);
            if (!groups[key]) {
                groups[key] = { sum: 0, count: 0, values: [] };
            }
            if (!isNaN(num)) {
                groups[key].sum += num;
                groups[key].count += 1;
                groups[key].values.push(num);
            } else {
                groups[key].values.push(0); // для count
            }
        }
        setStatus('⏳ Данные собраны. Групп: ' + Object.keys(groups).length);
        
        if (Object.keys(groups).length === 0) {
            setStatus('⚠️ Нет данных для группировки');
            return;
        }
        
        // Создаём новый лист
        var pivotSheetName = 'Сводная_' + new Date().toISOString().replace(/[:.]/g, '-');
        setStatus('⏳ Создаю лист ' + pivotSheetName);
        editor().asc_addWorksheet(pivotSheetName);
        var pivotSheet = getSheet(pivotSheetName);
        if (!pivotSheet) throw 'Не удалось найти созданный лист';
        setStatus('⏳ Лист создан');
        
        // Заголовки
        pivotSheet.GetRange('A1').SetValue('Группа');
        pivotSheet.GetRange('B1').SetValue(aggType.charAt(0).toUpperCase() + aggType.slice(1));
        pivotSheet.GetRange('A1:B1').SetBold(true);
        
        // Заполняем данные
        var row = 2;
        var groupNames = Object.keys(groups).sort();
        for (var i = 0; i < groupNames.length; i++) {
            var g = groupNames[i];
            var aggValue;
            switch(aggType) {
                case 'sum': aggValue = groups[g].sum; break;
                case 'avg': aggValue = groups[g].count ? groups[g].sum / groups[g].count : 0; break;
                case 'max': aggValue = Math.max(...groups[g].values); break;
                case 'min': aggValue = Math.min(...groups[g].values); break;
                case 'count': aggValue = groups[g].values.length; break;
                default: aggValue = groups[g].sum;
            }
            pivotSheet.GetRange('A' + row).SetValue(g);
            pivotSheet.GetRange('B' + row).SetValue(aggValue);
            row++;
        }
        
        setStatus('⏳ Данные записаны');
        
        // Автоподбор ширины
        try { pivotSheet.GetRange('A:A').AutoFit(); } catch(e) {}
        try { pivotSheet.GetRange('B:B').AutoFit(); } catch(e) {}
        
        if (aggType !== 'count') {
            pivotSheet.GetRange('B2:B' + (row-1)).SetNumberFormat('#,##0.00');
        }
        
        setStatus('⏳ Попытка создать диаграмму...');
        // Создание диаграммы (безопасно)
        try {
            var chartRange = 'A1:B' + (row-1);
            if (typeof pivotSheet.AddChart === 'function') {
                // Пробуем несколько типов диаграмм
                var types = ['column', 'bar', 'histogram'];
                var chartAdded = false;
                for (var t = 0; t < types.length; t++) {
                    try {
                        pivotSheet.AddChart(types[t], chartRange, 'D1');
                        chartAdded = true;
                        break;
                    } catch(e) {}
                }
                if (chartAdded) {
                    setStatus('✅ Диаграмма создана');
                } else {
                    setStatus('⚠️ Не удалось создать диаграмму ни с одним типом');
                }
            } else {
                setStatus('⚠️ Метод AddChart не поддерживается, диаграмма пропущена');
            }
        } catch(chartError) {
            setStatus('⚠️ Ошибка диаграммы: ' + chartError.message);
        }
        
        refresh();
        setStatus('✅ Сводная таблица построена на листе "' + pivotSheetName + '"');
    } catch(e) {
        setStatus('❌ Ошибка: ' + e.message + '\nСтек: ' + (e.stack ? e.stack.split('\n').slice(0,3).join('\n') : ''));
    }
}






<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 12px; background: #f5f5f5; }
        h3 { margin-top: 0; }
        .row { display: flex; gap: 8px; align-items: center; margin-bottom: 10px; }
        .row label { width: 90px; font-size: 13px; }
        .row select, .row button { flex: 1; padding: 8px; font-size: 13px; border-radius: 4px; border: 1px solid #ccc; }
        button {
            display: block; width: 100%; padding: 10px; margin: 8px 0;
            border: none; border-radius: 6px; font-size: 14px; font-weight: bold;
            cursor: pointer; color: white; background: #4CAF50;
        }
        button:hover { opacity: 0.9; }
        .status {
            margin-top: 12px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 30px; white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h3>📊 Мастер сводной</h3>
    <p style="font-size:12px; color:#555;">Активный лист будет использован как источник.</p>
    
    <div class="row">
        <label>Группировка:</label>
        <select id="groupCol"><option value="">Выберите столбец</option></select>
    </div>
    <div class="row">
        <label>Значения:</label>
        <select id="valueCol"><option value="">Выберите столбец</option></select>
    </div>
    <div class="row">
        <label>Агрегация:</label>
        <select id="aggType">
            <option value="sum">Сумма</option>
            <option value="avg">Среднее</option>
            <option value="max">Максимум</option>
            <option value="min">Минимум</option>
            <option value="count">Количество</option>
        </select>
    </div>
    
    <button onclick="loadColumns()">🔄 Обновить список столбцов</button>
    <button onclick="createPivotTable()">⚡ Построить сводную и диаграмму</button>
    
    <div class="status" id="status">Готов. Нажмите «Обновить», чтобы загрузить заголовки с активного листа.</div>

    <script>
        // ========== БАЗОВЫЕ ФУНКЦИИ ==========
        function editor() { return window.parent.Asc.editor; }
        function setStatus(msg) { document.getElementById('status').textContent = msg; }
        function refresh() { if (typeof editor().asc_Recalculate === 'function') editor().asc_Recalculate(); }

        // Получить лист по имени
        function getSheet(name) {
            try {
                if (typeof editor().GetSheet === 'function') return editor().GetSheet(name);
                var sheets = editor().GetSheets();
                for (var i = 0; i < sheets.GetCount(); i++) {
                    if (sheets.GetSheet(i).GetName() === name) return sheets.GetSheet(i);
                }
                return null;
            } catch(e) { return null; }
        }

        // Конвертация буквы столбца в номер (A=1, B=2...)
        function colLetterToNumber(letter) {
            letter = letter.toUpperCase();
            var num = 0;
            for (var i = 0; i < letter.length; i++) {
                num = num * 26 + (letter.charCodeAt(i) - 64);
            }
            return num;
        }

        // Загрузка заголовков из первой строки используемого диапазона активного листа
        function loadColumns() {
            setStatus('⏳ Считываю заголовки...');
            try {
                var sheet = editor().GetActiveSheet();
                if (!sheet) { setStatus('❌ Нет активного листа'); return; }
                
                var used = sheet.GetUsedRange();
                if (!used) { setStatus('❌ На листе нет данных'); return; }
                
                var firstRow = used.GetRow();
                var lastCol = used.GetCol() + used.GetCols().GetCount() - 1;
                
                var groupSel = document.getElementById('groupCol');
                var valueSel = document.getElementById('valueCol');
                groupSel.innerHTML = '<option value="">Выберите столбец</option>';
                valueSel.innerHTML = '<option value="">Выберите столбец</option>';
                
                for (var col = 1; col <= lastCol; col++) {
                    try {
                        var colLetter = String.fromCharCode(64 + col);
                        var cell = sheet.GetRange(colLetter + firstRow);
                        var val = cell.GetValue();
                        if (val !== null && val !== undefined && String(val).trim() !== '') {
                            var text = String(val).trim();
                            var opt1 = new Option(text, colLetter);
                            var opt2 = new Option(text, colLetter);
                            groupSel.add(opt1);
                            valueSel.add(opt2);
                        }
                    } catch(e) {}
                }
                setStatus('✅ Заголовки загружены. Выберите столбцы и нажмите «Построить сводную».');
            } catch(e) {
                setStatus('❌ Ошибка: ' + e.message);
            }
        }

        // Построение сводной таблицы и диаграммы
        function createPivotTable() {
            var groupCol = document.getElementById('groupCol').value;
            var valueCol = document.getElementById('valueCol').value;
            var aggType = document.getElementById('aggType').value;
            
            if (!groupCol || !valueCol) {
                setStatus('⚠️ Выберите столбцы для группировки и значений.');
                return;
            }
            
            setStatus('⏳ Строю сводную таблицу...');
            try {
                var srcSheet = editor().GetActiveSheet();
                if (!srcSheet) throw 'Нет активного листа';
                
                var used = srcSheet.GetUsedRange();
                if (!used) throw 'Нет данных';
                
                var firstRow = used.GetRow();
                var rowsCount = used.GetRows().GetCount();
                var dataStartRow = firstRow + 1; // пропускаем заголовок
                
                // Сбор данных
                var groups = {};
                for (var r = dataStartRow; r < firstRow + rowsCount; r++) {
                    var keyCell = srcSheet.GetRange(groupCol + r).GetValue();
                    var valCell = srcSheet.GetRange(valueCol + r).GetValue();
                    if (keyCell === null || keyCell === undefined || keyCell === '') continue;
                    var key = String(keyCell).trim();
                    var num = parseFloat(valCell);
                    if (!groups[key]) {
                        groups[key] = { sum: 0, count: 0, values: [] };
                    }
                    if (!isNaN(num)) {
                        groups[key].sum += num;
                        groups[key].count += 1;
                        groups[key].values.push(num);
                    } else {
                        groups[key].values.push(0); // для count
                    }
                }
                
                if (Object.keys(groups).length === 0) {
                    setStatus('⚠️ Нет данных для группировки');
                    return;
                }
                
                // Создаём новый лист
                var pivotSheetName = 'Сводная_' + new Date().toISOString().replace(/[:.]/g, '-');
                editor().asc_addWorksheet(pivotSheetName);
                var pivotSheet = getSheet(pivotSheetName);
                if (!pivotSheet) throw 'Не удалось создать лист';
                
                // Заголовки сводной
                pivotSheet.GetRange('A1').SetValue('Группа');
                pivotSheet.GetRange('B1').SetValue(aggType.charAt(0).toUpperCase() + aggType.slice(1));
                pivotSheet.GetRange('A1:B1').SetBold(true);
                
                // Заполняем данные
                var row = 2;
                var groupNames = Object.keys(groups).sort();
                for (var i = 0; i < groupNames.length; i++) {
                    var g = groupNames[i];
                    var aggValue;
                    switch(aggType) {
                        case 'sum': aggValue = groups[g].sum; break;
                        case 'avg': aggValue = groups[g].count ? groups[g].sum / groups[g].count : 0; break;
                        case 'max': aggValue = Math.max(...groups[g].values); break;
                        case 'min': aggValue = Math.min(...groups[g].values); break;
                        case 'count': aggValue = groups[g].values.length; break;
                        default: aggValue = groups[g].sum;
                    }
                    pivotSheet.GetRange('A' + row).SetValue(g);
                    pivotSheet.GetRange('B' + row).SetValue(aggValue);
                    row++;
                }
                
                // Автоподбор ширины столбцов
                try { pivotSheet.GetRange('A:A').AutoFit(); } catch(e) {}
                try { pivotSheet.GetRange('B:B').AutoFit(); } catch(e) {}
                
                // Числовой формат для столбца значений (если числа)
                if (aggType !== 'count') {
                    pivotSheet.GetRange('B2:B' + (row-1)).SetNumberFormat('#,##0.00');
                }
                
                // Создание диаграммы (гистограмма)
                try {
                    var chartRange = 'A1:B' + (row-1);
                    // Пробуем разные типы – выбираем первый сработавший
                    var chartTypes = ['column', 'bar', 'histogram'];
                    for (var t = 0; t < chartTypes.length; t++) {
                        try {
                            pivotSheet.AddChart(chartTypes[t], chartRange, 'D1');
                            break;
                        } catch(e) { continue; }
                    }
                } catch(e) {
                    // без диаграммы – не критично
                }
                
                refresh();
                setStatus('✅ Сводная таблица создана на листе "' + pivotSheetName + '"');
            } catch(e) {
                setStatus('❌ Ошибка: ' + e.message);
            }
        }

        // Инициализация – сразу пробуем загрузить столбцы
        window.onload = function() {
            setStatus('✅ Плагин готов. Нажмите «Обновить список столбцов».');
            // Автоматически загрузим заголовки при открытии
            setTimeout(loadColumns, 500);
        };
    </script>
</body>
</html>









<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 10px; background: #f5f5f5; }
        .tabs { display: flex; gap: 5px; margin-bottom: 10px; }
        .tab-btn {
            flex: 1; padding: 8px; border: none; border-radius: 6px 6px 0 0;
            font-size: 12px; font-weight: bold; cursor: pointer; color: #555; background: #ddd;
        }
        .tab-btn.active { color: white; background: #4CAF50; }
        .tab-panel { display: none; }
        .tab-panel.active { display: block; }
        button {
            display: block; width: 100%; padding: 10px; margin: 6px 0;
            border: none; border-radius: 6px; font-size: 13px; font-weight: bold;
            cursor: pointer; color: white; background: #4CAF50;
        }
        button:hover { opacity: 0.9; }
        .status {
            margin-top: 12px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 11px; color: #333; min-height: 30px; word-break: break-word;
            white-space: pre-wrap;
        }
        .row { display: flex; gap: 6px; align-items: center; margin-bottom: 6px; }
        .row input, .row select { flex: 1; padding: 6px; border-radius: 4px; border: 1px solid #ccc; font-size: 12px; }
        .row label { font-size: 12px; width: 70px; }
    </style>
</head>
<body>
    <h3>🧠 Анализ таблиц</h3>
    
    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('compare')">📊 Сравнение</button>
        <button class="tab-btn" onclick="switchTab('duplicates')">🔍 Дубликаты</button>
        <button class="tab-btn" onclick="switchTab('tools')">⚙️ Инструменты</button>
    </div>

    <!-- Вкладка Сравнение -->
    <div id="tab-compare" class="tab-panel active">
        <button onclick="compareSheets()">📋 Сравнить Лист1 и Лист2 (столбец A)</button>
        <button onclick="clearHighlight()">🧹 Снять выделение со столбца A</button>
        <button onclick="copyUniqueToNewSheet()">📤 Копировать уникальные на новый лист</button>
        <div class="row">
            <label>Лист1:</label><input type="text" id="sheet1Name" value="Лист1">
            <label>Лист2:</label><input type="text" id="sheet2Name" value="Лист2">
        </div>
        <div class="row">
            <label>Столбец:</label><input type="text" id="compareCol" value="A">
        </div>
        <p style="font-size:10px;color:#666;">Сравнение по указанному столбцу (A, B, C...)</p>
    </div>

    <!-- Вкладка Дубликаты -->
    <div id="tab-duplicates" class="tab-panel">
        <button onclick="findDuplicates()">🔴 Найти дубликаты</button>
        <button onclick="removeDuplicates()">🗑️ Удалить дубликаты (оставить первое)</button>
        <div class="row">
            <label>Лист:</label><input type="text" id="dupSheet" value="Лист1">
            <label>Столбец:</label><input type="text" id="dupCol" value="A">
        </div>
        <p style="font-size:10px;color:#666;">Дубликаты выделяются красным. Удаление необратимо!</p>
    </div>

    <!-- Вкладка Инструменты -->
    <div id="tab-tools" class="tab-panel">
        <button onclick="highlightByCondition()">🎯 Выделить строки по условию</button>
        <div class="row">
            <label>Лист:</label><input type="text" id="condSheet" value="Лист1">
            <label>Столбец:</label><input type="text" id="condCol" value="C">
        </div>
        <div class="row">
            <label>Условие:</label>
            <select id="condOp">
                <option value=">">Больше</option>
                <option value="<">Меньше</option>
                <option value="==">Равно</option>
                <option value="contains">Содержит текст</option>
            </select>
            <input type="text" id="condVal" placeholder="Значение">
        </div>

        <button onclick="freezeHeaders()">📌 Закрепить первую строку и столбец</button>
        <button onclick="syncColumnWidths()">📏 Синхронизировать ширину столбцов (Лист1 → Лист2)</button>
        <button onclick="compareTwoColumns()">📊 Сравнить два столбца на одном листе</button>
        <div class="row">
            <label>Лист:</label><input type="text" id="twoColSheet" value="Лист1">
            <label>Столбец1:</label><input type="text" id="col1" value="A">
            <label>Столбец2:</label><input type="text" id="col2" value="B">
        </div>
    </div>

    <div class="status" id="status">Готов к работе</div>

    <script>
        // ========== БАЗОВЫЕ ФУНКЦИИ ==========
        function editor() { return window.parent.Asc.editor; }
        function setStatus(msg) { document.getElementById('status').textContent = msg; }
        function refresh() { if (typeof editor().asc_Recalculate === 'function') editor().asc_Recalculate(); }

        // Переключение вкладок
        function switchTab(tabId) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            document.getElementById('tab-' + tabId).classList.add('active');
            event.target.classList.add('active');
        }

        // Получить лист по имени
        function getSheet(name) {
            try {
                if (typeof editor().GetSheet === 'function') return editor().GetSheet(name);
                var sheets = editor().GetSheets();
                for (var i = 0; i < sheets.GetCount(); i++) {
                    if (sheets.GetSheet(i).GetName() === name) return sheets.GetSheet(i);
                }
                return null;
            } catch(e) { return null; }
        }

        // Собрать значения столбца (colStr = "A", "B"...) -> [{value, row}]
        function getColumnData(sheet, colStr) {
            var data = [], row = 1;
            while (true) {
                try {
                    var range = sheet.GetRange(colStr + row);
                    var value = range.GetValue();
                    if (value === null || value === undefined || value === '') break;
                    data.push({ value: value, row: row });
                    row++;
                } catch(e) { break; }
            }
            return data;
        }

        // Выделить строки на листе цветом (номера строк)
        function highlightRows(sheet, rows, color) {
            for (var i = 0; i < rows.length; i++) {
                try {
                    sheet.GetRange('A' + rows[i] + ':Z' + rows[i]).SetFillColor(color);
                } catch(e) {}
            }
        }

        // ========== 1. СРАВНЕНИЕ ЛИСТОВ ==========
        function compareSheets() {
            var sheet1Name = document.getElementById('sheet1Name').value || 'Лист1';
            var sheet2Name = document.getElementById('sheet2Name').value || 'Лист2';
            var colStr = document.getElementById('compareCol').value || 'A';

            setStatus('⏳ Сравниваю...');
            try {
                var sheet1 = getSheet(sheet1Name), sheet2 = getSheet(sheet2Name);
                if (!sheet1 || !sheet2) { setStatus('❌ Листы не найдены'); return; }

                var data1 = getColumnData(sheet1, colStr);
                var data2 = getColumnData(sheet2, colStr);

                var set1 = new Set(data1.map(d => d.value));
                var set2 = new Set(data2.map(d => d.value));

                var only1 = data1.filter(d => !set2.has(d.value));
                var only2 = data2.filter(d => !set1.has(d.value));

                if (only1.length === 0 && only2.length === 0) {
                    setStatus('✅ Расхождений нет'); return;
                }

                var yellow = editor().CreateColorFromRGB(255, 255, 0);
                var orange = editor().CreateColorFromRGB(255, 165, 0);

                highlightRows(sheet1, only1.map(d => d.row), yellow);
                highlightRows(sheet2, only2.map(d => d.row), orange);
                refresh();
                setStatus('✅ Лист1: ' + only1.length + ' строк (жёлтые), Лист2: ' + only2.length + ' строк (оранжевые)');
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        function clearHighlight() {
            var sheet1Name = document.getElementById('sheet1Name').value || 'Лист1';
            var sheet2Name = document.getElementById('sheet2Name').value || 'Лист2';
            var colStr = document.getElementById('compareCol').value || 'A';
            setStatus('🧹 Снимаю заливку...');
            try {
                var sheet1 = getSheet(sheet1Name), sheet2 = getSheet(sheet2Name);
                var noFill = editor().CreateNoFill();

                var clearCol = function(sheet) {
                    if (!sheet) return;
                    var used = sheet.GetUsedRange();
                    if (!used) return;
                    var rowsCount = used.GetRows().GetCount();
                    var startRow = used.GetRow();
                    for (var i = 0; i < rowsCount; i++) {
                        sheet.GetRange(colStr + (startRow + i)).SetFillColor(noFill);
                    }
                };
                clearCol(sheet1); clearCol(sheet2);
                refresh();
                setStatus('✅ Заливка снята');
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        function copyUniqueToNewSheet() {
            var sheet1Name = document.getElementById('sheet1Name').value || 'Лист1';
            var sheet2Name = document.getElementById('sheet2Name').value || 'Лист2';
            var colStr = document.getElementById('compareCol').value || 'A';
            setStatus('📤 Копирую уникальные...');
            try {
                var sheet1 = getSheet(sheet1Name);
                var sheet2 = getSheet(sheet2Name);
                if (!sheet1 || !sheet2) { setStatus('❌ Листы не найдены'); return; }

                var data1 = getColumnData(sheet1, colStr);
                var data2 = getColumnData(sheet2, colStr);
                var set2 = new Set(data2.map(d => d.value));
                var uniqueIn1 = data1.filter(d => !set2.has(d.value));

                var newSheetName = 'Уникальные_' + sheet1Name;
                try {
                    editor().asc_addWorksheet(newSheetName);
                } catch(e) {
                    // может уже существовать
                }

                var newSheet = getSheet(newSheetName);
                if (!newSheet) {
                    setStatus('❌ Не удалось создать или найти лист ' + newSheetName);
                    return;
                }

                // Копируем заголовок (первая строка листа1)
                sheet1.GetRange('1:1').Copy(newSheet.GetRange('A1'));

                // Копируем уникальные строки
                for (var i = 0; i < uniqueIn1.length; i++) {
                    var srcRow = uniqueIn1[i].row;
                    sheet1.GetRange(srcRow + ':' + srcRow).Copy(newSheet.GetRange('A' + (i + 2)));
                }

                newSheet.GetRange('A1:Z1').SetBold(true);
                refresh();
                setStatus('✅ Создан лист "' + newSheetName + '" с ' + uniqueIn1.length + ' строками');
            } catch(e) {
                setStatus('❌ Ошибка: ' + e.message);
            }
        }

        // ========== 2. ДУБЛИКАТЫ ==========
        function findDuplicates() {
            var sheetName = document.getElementById('dupSheet').value || 'Лист1';
            var colStr = document.getElementById('dupCol').value || 'A';
            setStatus('🔍 Ищу дубликаты...');
            try {
                var sheet = getSheet(sheetName);
                if (!sheet) { setStatus('❌ Лист не найден'); return; }

                var data = getColumnData(sheet, colStr);
                if (data.length === 0) { setStatus('⚠️ Нет данных в столбце ' + colStr); return; }

                var seen = new Set();
                var duplicateRows = [];
                for (var i = 0; i < data.length; i++) {
                    if (seen.has(data[i].value)) {
                        duplicateRows.push(data[i].row);
                    } else {
                        seen.add(data[i].value);
                    }
                }

                if (duplicateRows.length === 0) {
                    setStatus('✅ Дубликаты не найдены');
                    return;
                }

                var red = editor().CreateColorFromRGB(255, 100, 100);
                highlightRows(sheet, duplicateRows, red);
                refresh();
                setStatus('🔴 Найдено дубликатов: ' + duplicateRows.length + ' строк');
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        function removeDuplicates() {
            var sheetName = document.getElementById('dupSheet').value || 'Лист1';
            var colStr = document.getElementById('dupCol').value || 'A';
            setStatus('🗑️ Удаляю дубликаты...');
            try {
                var sheet = getSheet(sheetName);
                if (!sheet) { setStatus('❌ Лист не найден'); return; }

                var data = getColumnData(sheet, colStr);
                var seen = new Set();
                var rowsToDelete = [];
                for (var i = 0; i < data.length; i++) {
                    if (seen.has(data[i].value)) {
                        rowsToDelete.push(data[i].row);
                    } else {
                        seen.add(data[i].value);
                    }
                }
                // Удаляем с конца
                rowsToDelete.sort((a,b) => b - a);
                for (var j = 0; j < rowsToDelete.length; j++) {
                    sheet.GetRange(rowsToDelete[j] + ':' + rowsToDelete[j]).Delete();
                }
                refresh();
                setStatus('✅ Удалено дубликатов: ' + rowsToDelete.length);
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        // ========== 3. ИНСТРУМЕНТЫ ==========
        function highlightByCondition() {
            var sheetName = document.getElementById('condSheet').value || 'Лист1';
            var colStr = document.getElementById('condCol').value || 'C';
            var op = document.getElementById('condOp').value;
            var val = document.getElementById('condVal').value;

            setStatus('🎯 Применяю условие...');
            try {
                var sheet = getSheet(sheetName);
                if (!sheet) { setStatus('❌ Лист не найден'); return; }

                var data = getColumnData(sheet, colStr);
                var rowsToHighlight = [];

                for (var i = 0; i < data.length; i++) {
                    var cellVal = data[i].value;
                    var match = false;
                    if (op === '>') match = Number(cellVal) > Number(val);
                    else if (op === '<') match = Number(cellVal) < Number(val);
                    else if (op === '==') match = String(cellVal) === val;
                    else if (op === 'contains') match = String(cellVal).toLowerCase().includes(val.toLowerCase());
                    if (match) rowsToHighlight.push(data[i].row);
                }

                var green = editor().CreateColorFromRGB(144, 238, 144);
                highlightRows(sheet, rowsToHighlight, green);
                refresh();
                setStatus('✅ Выделено строк: ' + rowsToHighlight.length);
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        function freezeHeaders() {
            setStatus('📌 Закрепляю...');
            try {
                if (typeof editor().asc_freezePane === 'function') {
                    editor().asc_freezePane(1, 1);
                }
                refresh();
                setStatus('✅ Первая строка и столбец закреплены');
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        function syncColumnWidths() {
            setStatus('📏 Синхронизирую ширину...');
            try {
                var sheet1 = getSheet('Лист1');
                var sheet2 = getSheet('Лист2');
                if (!sheet1 || !sheet2) { setStatus('❌ Нужны Лист1 и Лист2'); return; }
                var maxCol = 20;
                for (var c = 1; c <= maxCol; c++) {
                    try {
                        var colLetter = String.fromCharCode(64 + c);
                        var w = sheet1.GetRange(colLetter + '1').GetColumnWidth();
                        if (w && w > 0) sheet2.GetRange(colLetter + '1').SetColumnWidth(w);
                    } catch(e) {}
                }
                refresh();
                setStatus('✅ Ширина столбцов скопирована с Лист1 на Лист2');
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        function compareTwoColumns() {
            var sheetName = document.getElementById('twoColSheet').value || 'Лист1';
            var col1 = document.getElementById('col1').value || 'A';
            var col2 = document.getElementById('col2').value || 'B';
            setStatus('📊 Сравниваю два столбца...');
            try {
                var sheet = getSheet(sheetName);
                if (!sheet) { setStatus('❌ Лист не найден'); return; }

                var data1 = getColumnData(sheet, col1);
                var data2 = getColumnData(sheet, col2);
                var set2 = new Set(data2.map(d => d.value));

                var onlyInCol1 = data1.filter(d => !set2.has(d.value));

                var blue = editor().CreateColorFromRGB(173, 216, 230);
                highlightRows(sheet, onlyInCol1.map(d => d.row), blue);
                refresh();
                setStatus('✅ В столбце ' + col1 + ' уникальных значений: ' + onlyInCol1.length);
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        window.onload = function() {
            setStatus('✅ Плагин готов. Выберите вкладку и действие.');
        };
    </script>
</body>
</html>







function copyUniqueToNewSheet() {
    var sheet1Name = document.getElementById('sheet1Name').value || 'Лист1';
    var sheet2Name = document.getElementById('sheet2Name').value || 'Лист2';
    var colStr = document.getElementById('compareCol').value || 'A';
    setStatus('📤 Копирую уникальные...');
    try {
        var sheet1 = getSheet(sheet1Name);
        var sheet2 = getSheet(sheet2Name);
        if (!sheet1 || !sheet2) { setStatus('❌ Листы не найдены'); return; }

        var data1 = getColumnData(sheet1, colStr);
        var data2 = getColumnData(sheet2, colStr);
        var set2 = new Set(data2.map(d => d.value));
        var uniqueIn1 = data1.filter(d => !set2.has(d.value));

        // Создаём новый лист командой asc_addWorksheet
        var newSheetName = 'Уникальные_' + sheet1Name;
        try {
            editor().asc_addWorksheet(newSheetName);
        } catch(e) {
            // Возможно, уже существует – пробуем получить
        }

        // Получаем созданный лист по имени
        var newSheet = getSheet(newSheetName);
        if (!newSheet) {
            setStatus('❌ Не удалось создать или найти лист ' + newSheetName);
            return;
        }

        // Копируем заголовок (первая строка листа1) в новую первую строку
        sheet1.GetRange('1:1').Copy(newSheet.GetRange('A1'));

        // Копируем уникальные строки
        for (var i = 0; i < uniqueIn1.length; i++) {
            var srcRow = uniqueIn1[i].row;
            // Копируем всю строку из sheet1
            sheet1.GetRange(srcRow + ':' + srcRow).Copy(newSheet.GetRange('A' + (i + 2)));
        }

        // Делаем первую строку жирной (заголовок)
        newSheet.GetRange('A1:Z1').SetBold(true);

        refresh();
        setStatus('✅ Создан лист "' + newSheetName + '" с ' + uniqueIn1.length + ' строками');
    } catch(e) {
        setStatus('❌ Ошибка: ' + e.message);
    }
}







<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 10px; background: #f5f5f5; }
        .tabs { display: flex; gap: 5px; margin-bottom: 10px; }
        .tab-btn {
            flex: 1; padding: 8px; border: none; border-radius: 6px 6px 0 0;
            font-size: 12px; font-weight: bold; cursor: pointer; color: #555; background: #ddd;
        }
        .tab-btn.active { color: white; background: #4CAF50; }
        .tab-panel { display: none; }
        .tab-panel.active { display: block; }
        button {
            display: block; width: 100%; padding: 10px; margin: 6px 0;
            border: none; border-radius: 6px; font-size: 13px; font-weight: bold;
            cursor: pointer; color: white; background: #4CAF50;
        }
        button:hover { opacity: 0.9; }
        .status {
            margin-top: 12px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 11px; color: #333; min-height: 30px; word-break: break-word;
            white-space: pre-wrap;
        }
        .row { display: flex; gap: 6px; align-items: center; margin-bottom: 6px; }
        .row input, .row select { flex: 1; padding: 6px; border-radius: 4px; border: 1px solid #ccc; font-size: 12px; }
        .row label { font-size: 12px; width: 70px; }
    </style>
</head>
<body>
    <h3>🧠 Анализ таблиц</h3>
    
    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('compare')">📊 Сравнение</button>
        <button class="tab-btn" onclick="switchTab('duplicates')">🔍 Дубликаты</button>
        <button class="tab-btn" onclick="switchTab('tools')">⚙️ Инструменты</button>
    </div>

    <!-- Вкладка Сравнение -->
    <div id="tab-compare" class="tab-panel active">
        <button onclick="compareSheets()">📋 Сравнить Лист1 и Лист2 (столбец A)</button>
        <button onclick="clearHighlight()">🧹 Снять выделение со столбца A</button>
        <button onclick="copyUniqueToNewSheet()">📤 Копировать уникальные на новый лист</button>
        <div class="row">
            <label>Лист1:</label><input type="text" id="sheet1Name" value="Лист1">
            <label>Лист2:</label><input type="text" id="sheet2Name" value="Лист2">
        </div>
        <div class="row">
            <label>Столбец:</label><input type="text" id="compareCol" value="A">
        </div>
        <p style="font-size:10px;color:#666;">Сравнение по указанному столбцу (A, B, C...)</p>
    </div>

    <!-- Вкладка Дубликаты -->
    <div id="tab-duplicates" class="tab-panel">
        <button onclick="findDuplicates()">🔴 Найти дубликаты</button>
        <button onclick="removeDuplicates()">🗑️ Удалить дубликаты (оставить первое)</button>
        <div class="row">
            <label>Лист:</label><input type="text" id="dupSheet" value="Лист1">
            <label>Столбец:</label><input type="text" id="dupCol" value="A">
        </div>
        <p style="font-size:10px;color:#666;">Дубликаты выделяются красным. Удаление необратимо!</p>
    </div>

    <!-- Вкладка Инструменты -->
    <div id="tab-tools" class="tab-panel">
        <button onclick="highlightByCondition()">🎯 Выделить строки по условию</button>
        <div class="row">
            <label>Лист:</label><input type="text" id="condSheet" value="Лист1">
            <label>Столбец:</label><input type="text" id="condCol" value="C">
        </div>
        <div class="row">
            <label>Условие:</label>
            <select id="condOp">
                <option value=">">Больше</option>
                <option value="<">Меньше</option>
                <option value="==">Равно</option>
                <option value="contains">Содержит текст</option>
            </select>
            <input type="text" id="condVal" placeholder="Значение">
        </div>

        <button onclick="freezeHeaders()">📌 Закрепить первую строку и столбец</button>
        <button onclick="syncColumnWidths()">📏 Синхронизировать ширину столбцов (Лист1 → Лист2)</button>
        <button onclick="compareTwoColumns()">📊 Сравнить два столбца на одном листе</button>
        <div class="row">
            <label>Лист:</label><input type="text" id="twoColSheet" value="Лист1">
            <label>Столбец1:</label><input type="text" id="col1" value="A">
            <label>Столбец2:</label><input type="text" id="col2" value="B">
        </div>
    </div>

    <div class="status" id="status">Готов к работе</div>

    <script>
        // ========== БАЗОВЫЕ ФУНКЦИИ ==========
        function editor() { return window.parent.Asc.editor; }
        function setStatus(msg) { document.getElementById('status').textContent = msg; }
        function refresh() { if (typeof editor().asc_Recalculate === 'function') editor().asc_Recalculate(); }

        // Переключение вкладок
        function switchTab(tabId) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            document.getElementById('tab-' + tabId).classList.add('active');
            event.target.classList.add('active');
        }

        // Получить лист по имени
        function getSheet(name) {
            try {
                if (typeof editor().GetSheet === 'function') return editor().GetSheet(name);
                var sheets = editor().GetSheets();
                for (var i = 0; i < sheets.GetCount(); i++) {
                    if (sheets.GetSheet(i).GetName() === name) return sheets.GetSheet(i);
                }
                return null;
            } catch(e) { return null; }
        }

        // Собрать значения столбца (colStr = "A", "B"...) -> [{value, row}]
        function getColumnData(sheet, colStr) {
            var data = [], row = 1;
            while (true) {
                try {
                    var range = sheet.GetRange(colStr + row);
                    var value = range.GetValue();
                    if (value === null || value === undefined || value === '') break;
                    data.push({ value: value, row: row });
                    row++;
                } catch(e) { break; }
            }
            return data;
        }

        // Получить номер столбца из буквы (A=1, B=2...)
        function colLetterToNumber(letter) {
            letter = letter.toUpperCase();
            var num = 0;
            for (var i = 0; i < letter.length; i++) {
                num = num * 26 + (letter.charCodeAt(i) - 64);
            }
            return num;
        }

        // Выделить строки на листе цветом (номера строк)
        function highlightRows(sheet, rows, color) {
            for (var i = 0; i < rows.length; i++) {
                try {
                    sheet.GetRange('A' + rows[i] + ':Z' + rows[i]).SetFillColor(color);
                } catch(e) {}
            }
        }

        // Очистить заливку в указанных строках и столбце (colStr)
        function clearFillInColumn(sheet, colStr, rows) {
            var noFill = editor().CreateNoFill();
            for (var i = 0; i < rows.length; i++) {
                try {
                    sheet.GetRange(colStr + rows[i]).SetFillColor(noFill);
                } catch(e) {}
            }
        }

        // ========== 1. СРАВНЕНИЕ ЛИСТОВ ==========
        function compareSheets() {
            var sheet1Name = document.getElementById('sheet1Name').value || 'Лист1';
            var sheet2Name = document.getElementById('sheet2Name').value || 'Лист2';
            var colStr = document.getElementById('compareCol').value || 'A';

            setStatus('⏳ Сравниваю...');
            try {
                var sheet1 = getSheet(sheet1Name), sheet2 = getSheet(sheet2Name);
                if (!sheet1 || !sheet2) { setStatus('❌ Листы не найдены'); return; }

                var data1 = getColumnData(sheet1, colStr);
                var data2 = getColumnData(sheet2, colStr);

                var set1 = new Set(data1.map(d => d.value));
                var set2 = new Set(data2.map(d => d.value));

                var only1 = data1.filter(d => !set2.has(d.value));
                var only2 = data2.filter(d => !set1.has(d.value));

                if (only1.length === 0 && only2.length === 0) {
                    setStatus('✅ Расхождений нет'); return;
                }

                var yellow = editor().CreateColorFromRGB(255, 255, 0);
                var orange = editor().CreateColorFromRGB(255, 165, 0);

                highlightRows(sheet1, only1.map(d => d.row), yellow);
                highlightRows(sheet2, only2.map(d => d.row), orange);
                refresh();
                setStatus('✅ Лист1: ' + only1.length + ' строк (жёлтые), Лист2: ' + only2.length + ' строк (оранжевые)');
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        function clearHighlight() {
            var sheet1Name = document.getElementById('sheet1Name').value || 'Лист1';
            var sheet2Name = document.getElementById('sheet2Name').value || 'Лист2';
            var colStr = document.getElementById('compareCol').value || 'A';
            setStatus('🧹 Снимаю заливку...');
            try {
                var sheet1 = getSheet(sheet1Name), sheet2 = getSheet(sheet2Name);
                var noFill = editor().CreateNoFill();

                var clearCol = function(sheet) {
                    if (!sheet) return;
                    var used = sheet.GetUsedRange();
                    if (!used) return;
                    var rowsCount = used.GetRows().GetCount();
                    var startRow = used.GetRow();
                    for (var i = 0; i < rowsCount; i++) {
                        sheet.GetRange(colStr + (startRow + i)).SetFillColor(noFill);
                    }
                };
                clearCol(sheet1); clearCol(sheet2);
                refresh();
                setStatus('✅ Заливка снята');
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        function copyUniqueToNewSheet() {
            var sheet1Name = document.getElementById('sheet1Name').value || 'Лист1';
            var sheet2Name = document.getElementById('sheet2Name').value || 'Лист2';
            var colStr = document.getElementById('compareCol').value || 'A';
            setStatus('📤 Копирую уникальные...');
            try {
                var sheet1 = getSheet(sheet1Name), sheet2 = getSheet(sheet2Name);
                if (!sheet1 || !sheet2) { setStatus('❌ Листы не найдены'); return; }

                var data1 = getColumnData(sheet1, colStr);
                var data2 = getColumnData(sheet2, colStr);
                var set2 = new Set(data2.map(d => d.value));
                var uniqueIn1 = data1.filter(d => !set2.has(d.value));

                // Создаём новый лист
                var newSheet = editor().AddSheet('Уникальные_' + sheet1Name);
                // Копируем заголовок и строки
                if (uniqueIn1.length > 0) {
                    // Копируем шапку (первая строка листа1)
                    sheet1.GetRange('1:1').Copy(newSheet.GetRange('A1'));
                    for (var i = 0; i < uniqueIn1.length; i++) {
                        var srcRow = uniqueIn1[i].row;
                        sheet1.GetRange(srcRow + ':' + srcRow).Copy(newSheet.GetRange('A' + (i + 2)));
                    }
                    newSheet.GetRange('A1:Z1').SetFontBold(true);
                }
                refresh();
                setStatus('✅ Создан лист "Уникальные_' + sheet1Name + '" с ' + uniqueIn1.length + ' строками');
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        // ========== 2. ДУБЛИКАТЫ ==========
        function findDuplicates() {
            var sheetName = document.getElementById('dupSheet').value || 'Лист1';
            var colStr = document.getElementById('dupCol').value || 'A';
            setStatus('🔍 Ищу дубликаты...');
            try {
                var sheet = getSheet(sheetName);
                if (!sheet) { setStatus('❌ Лист не найден'); return; }

                var data = getColumnData(sheet, colStr);
                var seen = new Set();
                var duplicateRows = [];
                for (var i = 0; i < data.length; i++) {
                    if (seen.has(data[i].value)) {
                        duplicateRows.push(data[i].row);
                    } else {
                        seen.add(data[i].value);
                    }
                }

                var red = editor().CreateColorFromRGB(255, 100, 100);
                highlightRows(sheet, duplicateRows, red);
                refresh();
                setStatus('🔴 Найдено дубликатов: ' + duplicateRows.length + ' строк');
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        function removeDuplicates() {
            var sheetName = document.getElementById('dupSheet').value || 'Лист1';
            var colStr = document.getElementById('dupCol').value || 'A';
            setStatus('🗑️ Удаляю дубликаты...');
            try {
                var sheet = getSheet(sheetName);
                if (!sheet) { setStatus('❌ Лист не найден'); return; }

                var data = getColumnData(sheet, colStr);
                var seen = new Set();
                var rowsToDelete = [];
                for (var i = 0; i < data.length; i++) {
                    if (seen.has(data[i].value)) {
                        rowsToDelete.push(data[i].row);
                    } else {
                        seen.add(data[i].value);
                    }
                }
                // Удаляем строки с конца, чтобы не сбить нумерацию
                rowsToDelete.sort((a,b) => b - a);
                for (var j = 0; j < rowsToDelete.length; j++) {
                    sheet.GetRange(rowsToDelete[j] + ':' + rowsToDelete[j]).Delete();
                }
                refresh();
                setStatus('✅ Удалено дубликатов: ' + rowsToDelete.length);
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        // ========== 3. ИНСТРУМЕНТЫ ==========
        function highlightByCondition() {
            var sheetName = document.getElementById('condSheet').value || 'Лист1';
            var colStr = document.getElementById('condCol').value || 'C';
            var op = document.getElementById('condOp').value;
            var val = document.getElementById('condVal').value;

            setStatus('🎯 Применяю условие...');
            try {
                var sheet = getSheet(sheetName);
                if (!sheet) { setStatus('❌ Лист не найден'); return; }

                var data = getColumnData(sheet, colStr);
                var rowsToHighlight = [];

                for (var i = 0; i < data.length; i++) {
                    var cellVal = data[i].value;
                    var match = false;
                    if (op === '>') match = Number(cellVal) > Number(val);
                    else if (op === '<') match = Number(cellVal) < Number(val);
                    else if (op === '==') match = String(cellVal) === val;
                    else if (op === 'contains') match = String(cellVal).toLowerCase().includes(val.toLowerCase());
                    if (match) rowsToHighlight.push(data[i].row);
                }

                var green = editor().CreateColorFromRGB(144, 238, 144);
                highlightRows(sheet, rowsToHighlight, green);
                refresh();
                setStatus('✅ Выделено строк: ' + rowsToHighlight.length);
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        function freezeHeaders() {
            setStatus('📌 Закрепляю...');
            try {
                // Закрепить 1 строку и 1 столбец
                if (typeof editor().asc_freezePane === 'function') {
                    editor().asc_freezePane(1, 1); // строки, столбцы
                } else {
                    // альтернатива: установка через asc_setSheetView
                    var sheet = editor().GetActiveSheet();
                    // некоторые версии API: sheet.SetFrozenPanes(1, 1)
                }
                refresh();
                setStatus('✅ Первая строка и столбец закреплены');
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        function syncColumnWidths() {
            setStatus('📏 Синхронизирую ширину...');
            try {
                var sheet1 = getSheet('Лист1');
                var sheet2 = getSheet('Лист2');
                if (!sheet1 || !sheet2) { setStatus('❌ Нужны Лист1 и Лист2'); return; }
                var maxCol = 20; // предположим, до 20 столбцов
                for (var c = 1; c <= maxCol; c++) {
                    try {
                        var colLetter = String.fromCharCode(64 + c);
                        var w = sheet1.GetRange(colLetter + '1').GetColumnWidth();
                        if (w && w > 0) sheet2.GetRange(colLetter + '1').SetColumnWidth(w);
                    } catch(e) {}
                }
                refresh();
                setStatus('✅ Ширина столбцов скопирована с Лист1 на Лист2');
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        function compareTwoColumns() {
            var sheetName = document.getElementById('twoColSheet').value || 'Лист1';
            var col1 = document.getElementById('col1').value || 'A';
            var col2 = document.getElementById('col2').value || 'B';
            setStatus('📊 Сравниваю два столбца...');
            try {
                var sheet = getSheet(sheetName);
                if (!sheet) { setStatus('❌ Лист не найден'); return; }

                var data1 = getColumnData(sheet, col1);
                var data2 = getColumnData(sheet, col2);
                var set2 = new Set(data2.map(d => d.value));

                var onlyInCol1 = data1.filter(d => !set2.has(d.value));
                // Только в col2 не ищем, но можно добавить

                var blue = editor().CreateColorFromRGB(173, 216, 230);
                highlightRows(sheet, onlyInCol1.map(d => d.row), blue);
                refresh();
                setStatus('✅ В столбце ' + col1 + ' уникальных значений: ' + onlyInCol1.length);
            } catch(e) { setStatus('❌ Ошибка: ' + e.message); }
        }

        window.onload = function() {
            setStatus('✅ Плагин готов. Выберите вкладку и действие.');
        };
    </script>
</body>
</html>













// Снять выделение ТОЛЬКО со столбца A
function clearHighlight() {
    setStatus('🧹 Снимаю заливку со столбца A...');
    try {
        var sheet1 = getSheetByName('Лист1');
        var sheet2 = getSheetByName('Лист2');
        var noFill = editor().CreateNoFill();

        var clearColumnA = function(sheet) {
            if (!sheet) return;
            var used = sheet.GetUsedRange();
            if (!used) return;
            var rowsCount = used.GetRows().GetCount();
            var startRow = used.GetRow();
            for (var i = 0; i < rowsCount; i++) {
                var rowNum = startRow + i;
                var cell = sheet.GetRange('A' + rowNum); // ТОЛЬКО столбец A
                cell.SetFillColor(noFill);
            }
        };

        clearColumnA(sheet1);
        clearColumnA(sheet2);
        refresh();
        setStatus('✅ Заливка в столбце A снята.');
    } catch(e) {
        setStatus('❌ Ошибка: ' + e.message);
    }
}








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
        button:hover { background: #45a049; }
        .status {
            margin-top: 15px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 40px; word-break: break-word;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h3>🔍 Сравнить Лист1 и Лист2</h3>
    <p style="font-size:12px; color:#666;">Будут выделены строки, которые есть только на одном из листов (по столбцу A).</p>
    
    <button onclick="compareSheets()">⚡ Найти и покрасить расхождения</button>
    <button onclick="clearHighlight()" style="background:#f44336;">🧹 Снять выделение</button>
    
    <div class="status" id="status">Готов к работе</div>

    <script>
        function editor() { return window.parent.Asc.editor; }

        function setStatus(msg) {
            document.getElementById('status').textContent = msg;
        }

        function refresh() {
            if (typeof editor().asc_Recalculate === 'function') {
                editor().asc_Recalculate();
            }
        }

        // Получить лист по имени
        function getSheetByName(name) {
            if (typeof editor().GetSheet === 'function') {
                return editor().GetSheet(name);
            }
            var sheets = editor().GetSheets();
            for (var i = 0; i < sheets.GetCount(); i++) {
                var sh = sheets.GetSheet(i);
                if (sh.GetName() === name) return sh;
            }
            return null;
        }

        // Собрать значения столбца A и номера строк
        function getColumnValues(sheet) {
            var data = [];
            var row = 1;
            while (true) {
                try {
                    var range = sheet.GetRange('A' + row);
                    var value = range.GetValue();
                    if (value === null || value === undefined || value === '') break;
                    data.push({ value: value, row: row });
                    row++;
                } catch(e) {
                    break;
                }
            }
            return data;
        }

        // Закрасить строки
        function highlightRows(sheet, rows, color) {
            for (var i = 0; i < rows.length; i++) {
                try {
                    var range = sheet.GetRange('A' + rows[i] + ':Z' + rows[i]);
                    range.SetFillColor(color);
                } catch(e) {}
            }
        }

        // Сравнение листов
        function compareSheets() {
            setStatus('⏳ Получаю листы...');
            try {
                var sheet1 = getSheetByName('Лист1');
                var sheet2 = getSheetByName('Лист2');
                
                if (!sheet1 || !sheet2) {
                    setStatus('❌ Не найдены листы "Лист1" и/или "Лист2". Проверьте названия.');
                    return;
                }

                setStatus('📊 Читаю столбец A на Лист1...');
                var data1 = getColumnValues(sheet1);
                setStatus('📊 Читаю столбец A на Лист2...');
                var data2 = getColumnValues(sheet2);

                var set1 = new Set(data1.map(function(d) { return d.value; }));
                var set2 = new Set(data2.map(function(d) { return d.value; }));

                var onlyIn1 = data1.filter(function(d) { return !set2.has(d.value); });
                var onlyIn2 = data2.filter(function(d) { return !set1.has(d.value); });

                var rows1 = onlyIn1.map(function(d) { return d.row; });
                var rows2 = onlyIn2.map(function(d) { return d.row; });

                if (rows1.length === 0 && rows2.length === 0) {
                    setStatus('✅ Расхождений не найдено. Все значения столбца A совпадают.');
                    return;
                }

                var color1 = editor().CreateColorFromRGB(255, 255, 0);   // жёлтый
                var color2 = editor().CreateColorFromRGB(255, 165, 0); // оранжевый

                setStatus('🎨 Выделяю ' + rows1.length + ' строк на Лист1 и ' + rows2.length + ' строк на Лист2...');
                
                highlightRows(sheet1, rows1, color1);
                highlightRows(sheet2, rows2, color2);
                
                refresh();
                setStatus('✅ Готово! Жёлтые строки — только на Лист1, оранжевые — только на Лист2.\nЛист1: ' + rows1.length + ' строк, Лист2: ' + rows2.length + ' строк.');
            } catch(e) {
                setStatus('❌ Ошибка: ' + e.message);
            }
        }

        // Снять выделение (исправлено!)
        function clearHighlight() {
            setStatus('🧹 Снимаю заливку...');
            try {
                var sheet1 = getSheetByName('Лист1');
                var sheet2 = getSheetByName('Лист2');
                var noFill = editor().CreateNoFill(); // Создаём объект "No Fill"

                [sheet1, sheet2].forEach(function(sheet) {
                    if (sheet) {
                        var used = sheet.GetUsedRange();
                        if (used) {
                            used.SetFillColor(noFill); // Применяем "No Fill" ко всему диапазону
                        }
                    }
                });
                refresh();
                setStatus('✅ Заливка снята.');
            } catch(e) {
                setStatus('❌ Ошибка: ' + e.message);
            }
        }

        window.onload = function() {
            setStatus('✅ Плагин готов. Нажмите кнопку для сравнения листов "Лист1" и "Лист2" по столбцу A.');
        };
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
        button:hover { background: #45a049; }
        .status {
            margin-top: 15px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 40px; word-break: break-word;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h3>🔍 Сравнить Лист1 и Лист2</h3>
    <p style="font-size:12px; color:#666;">Будут выделены строки, которые есть только на одном из листов (по столбцу A).</p>
    
    <button onclick="compareSheets()">⚡ Найти и покрасить расхождения</button>
    <button onclick="clearHighlight()" style="background:#f44336;">🧹 Снять выделение</button>
    
    <div class="status" id="status">Готов к работе</div>

    <script>
        function editor() { return window.parent.Asc.editor; }

        function setStatus(msg) {
            document.getElementById('status').textContent = msg;
        }

        function refresh() {
            if (typeof editor().asc_Recalculate === 'function') {
                editor().asc_Recalculate();
            }
        }

        // Получить лист по имени
        function getSheetByName(name) {
            if (typeof editor().GetSheet === 'function') {
                return editor().GetSheet(name);
            }
            // Альтернатива: перебор всех листов
            var sheets = editor().GetSheets();
            for (var i = 0; i < sheets.GetCount(); i++) {
                var sh = sheets.GetSheet(i);
                if (sh.GetName() === name) return sh;
            }
            return null;
        }

        // Собрать значения столбца A и номера строк
        function getColumnValues(sheet) {
            var data = [];
            var row = 1;
            while (true) {
                try {
                    var range = sheet.GetRange('A' + row);
                    var value = range.GetValue();
                    if (value === null || value === undefined || value === '') break;
                    data.push({ value: value, row: row });
                    row++;
                } catch(e) {
                    break;
                }
            }
            return data;
        }

        // Закрасить строки (номера строк)
        function highlightRows(sheet, rows, color) {
            for (var i = 0; i < rows.length; i++) {
                try {
                    var range = sheet.GetRange('A' + rows[i] + ':Z' + rows[i]);
                    range.SetFillColor(color);
                } catch(e) {}
            }
        }

        // Основная функция сравнения
        function compareSheets() {
            setStatus('⏳ Получаю листы...');
            try {
                var sheet1 = getSheetByName('Лист1');
                var sheet2 = getSheetByName('Лист2');
                
                if (!sheet1 || !sheet2) {
                    setStatus('❌ Не найдены листы "Лист1" и/или "Лист2". Проверьте названия.');
                    return;
                }

                setStatus('📊 Читаю столбец A на Лист1...');
                var data1 = getColumnValues(sheet1);
                setStatus('📊 Читаю столбец A на Лист2...');
                var data2 = getColumnValues(sheet2);

                // Строим множества значений
                var set1 = new Set(data1.map(function(d) { return d.value; }));
                var set2 = new Set(data2.map(function(d) { return d.value; }));

                // Уникальные для каждого листа
                var onlyIn1 = data1.filter(function(d) { return !set2.has(d.value); });
                var onlyIn2 = data2.filter(function(d) { return !set1.has(d.value); });

                var rows1 = onlyIn1.map(function(d) { return d.row; });
                var rows2 = onlyIn2.map(function(d) { return d.row; });

                if (rows1.length === 0 && rows2.length === 0) {
                    setStatus('✅ Расхождений не найдено. Все значения столбца A совпадают.');
                    return;
                }

                // Цвета: жёлтый и оранжевый
                var color1 = editor().CreateColorFromRGB(255, 255, 0);
                var color2 = editor().CreateColorFromRGB(255, 165, 0);

                setStatus('🎨 Выделяю ' + rows1.length + ' строк на Лист1 и ' + rows2.length + ' строк на Лист2...');
                
                highlightRows(sheet1, rows1, color1);
                highlightRows(sheet2, rows2, color2);
                
                refresh();
                setStatus('✅ Готово! Жёлтые строки — только на Лист1, оранжевые — только на Лист2.\nЛист1: ' + rows1.length + ' строк, Лист2: ' + rows2.length + ' строк.');
            } catch(e) {
                setStatus('❌ Ошибка: ' + e.message);
            }
        }

        // Снять выделение
        function clearHighlight() {
            setStatus('🧹 Снимаю заливку...');
            try {
                var sheet1 = getSheetByName('Лист1');
                var sheet2 = getSheetByName('Лист2');

                var clearSheet = function(sheet) {
                    if (!sheet) return;
                    var used = sheet.GetUsedRange();
                    if (!used) return;
                    var rowsCount = used.GetRows().GetCount();
                    var startRow = used.GetRow();
                    for (var i = 0; i < rowsCount; i++) {
                        var rowNum = startRow + i;
                        var range = sheet.GetRange('A' + rowNum + ':Z' + rowNum);
                        range.SetFillColor(null);
                    }
                };

                clearSheet(sheet1);
                clearSheet(sheet2);
                refresh();
                setStatus('✅ Заливка снята.');
            } catch(e) {
                setStatus('❌ Ошибка: ' + e.message);
            }
        }

        window.onload = function() {
            setStatus('✅ Плагин готов. Нажмите кнопку для сравнения листов "Лист1" и "Лист2" по столбцу A.');
        };
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
        button:hover { background: #45a049; }
        .status {
            margin-top: 15px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 40px; word-break: break-word;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h3>🔍 Сравнить Лист1 и Лист2</h3>
    <p style="font-size:12px; color:#666;">Будут выделены строки, которые есть только на одном из листов (по столбцу A).</p>
    
    <button onclick="compareSheets()">⚡ Найти и покрасить расхождения</button>
    <button onclick="clearHighlight()" style="background:#f44336;">🧹 Снять выделение</button>
    
    <div class="status" id="status">Готов к работе</div>

    <script>
        function editor() { return window.parent.Asc.editor; }

        function setStatus(msg) {
            document.getElementById('status').textContent = msg;
        }

        function refresh() {
            if (typeof editor().asc_Recalculate === 'function') {
                editor().asc_Recalculate();
            }
        }

        // Получить лист по имени
        function getSheetByName(name) {
            // Возможно GetSheet или GetSheets
            if (typeof editor().GetSheet === 'function') {
                return editor().GetSheet(name);
            }
            // Альтернатива: перебор всех листов
            var sheets = editor().GetSheets();
            for (var i = 0; i < sheets.GetCount(); i++) {
                var sh = sheets.GetSheet(i);
                if (sh.GetName() === name) return sh;
            }
            return null;
        }

        // Собрать значения столбца A (col=1) и номера строк
        function getColumnValues(sheet) {
            var data = [];
            var row = 1;
            while (true) {
                try {
                    var range = sheet.GetRange('A' + row);
                    var value = range.GetValue();
                    if (value === null || value === undefined || value === '') break;
                    data.push({ value: value, row: row });
                    row++;
                } catch(e) {
                    break;
                }
            }
            return data;
        }

        // Закрасить строки (номера строк)
        function highlightRows(sheet, rows, color) {
            for (var i = 0; i < rows.length; i++) {
                try {
                    // Закрашиваем столбцы A-Z текущей строки
                    var range = sheet.GetRange('A' + rows[i] + ':Z' + rows[i]);
                    range.SetFillColor(color);
                } catch(e) {}
            }
        }

        // Снять заливку с указанных строк
        function clearHighlightRows(sheet, rows) {
            for (var i = 0; i < rows.length; i++) {
                try {
                    var range = sheet.GetRange('A' + rows[i] + ':Z' + rows[i]);
                    range.SetFillColor(null); // или No Fill
                } catch(e) {}
            }
        }

        // Основная функция сравнения
        function compareSheets() {
            setStatus('⏳ Получаю листы...');
            try {
                var sheet1 = getSheetByName('Лист1');
                var sheet2 = getSheetByName('Лист2');
                
                if (!sheet1 || !sheet2) {
                    setStatus('❌ Не найдены листы "Лист1" и/или "Лист2". Проверьте названия.');
                    return;
                }

                setStatus('📊 Читаю столбец A на Лист1...');
                var data1 = getColumnValues(sheet1);
                setStatus('📊 Читаю столбец A на Лист2...');
                var data2 = getColumnValues(sheet2);

                // Строим множества значений
                var set1 = new Set(data1.map(function(d) { return d.value; }));
                var set2 = new Set(data2.map(function(d) { return d.value; }));

                // Находим уникальные строки для каждого листа
                var onlyIn1 = data1.filter(function(d) { return !set2.has(d.value); });
                var onlyIn2 = data2.filter(function(d) { return !set1.has(d.value); });

                // Собираем номера строк
                var rows1 = onlyIn1.map(function(d) { return d.row; });
                var rows2 = onlyIn2.map(function(d) { return d.row; });

                if (rows1.length === 0 && rows2.length === 0) {
                    setStatus('✅ Расхождений не найдено. Все значения столбца A совпадают.');
                    return;
                }

                // Цвета: желтый и оранжевый
                var color1 = editor().CreateColorFromRGB(255, 255, 0);   // желтый
                var color2 = editor().CreateColorFromRGB(255, 165, 0); // оранжевый

                setStatus('🎨 Выделяю ' + rows1.length + ' строк на Лист1 и ' + rows2.length + ' строк на Лист2...');
                
                highlightRows(sheet1, rows1, color1);
                highlightRows(sheet2, rows2, color2);
                
                refresh();
                setStatus('✅ Готово! Жёлтые строки — только на Лист1, оранжевые — только на Лист2.\nЛист1: ' + rows1.length + ' строк, Лист2: ' + rows2.length + ' строк.');
            } catch(e) {
                setStatus('❌ Ошибка: ' + e.message);
            }
        }

        // Снять выделение (опционально)
        function clearHighlight() {
            setStatus('🧹 Снимаю заливку...');
            try {
                var sheet1 = getSheetByName('Лист1');
                var sheet2 = getSheetByName('Лист2');
                if (sheet1) {
                    // Перебираем все строки, снимаем заливку (упрощённо – до 1000 строки)
                    var used1 = sheet1.GetUsedRange();
                    if (used1) {
                        var rows = used1.GetRows();
                        for (var i = 0; i < rows.GetCount(); i++) {
                            var rng = rows.GetRow(i).GetRange('A1:Z1'); // каждая строка
                            rng.SetFillColor(null);
                        }
                    }
                }
                if (sheet2) {
                    var used2 = sheet2.GetUsedRange();
                    if (used2) {
                        var rows = used2.GetRows();
                        for (var i = 0; i < rows.GetCount(); i++) {
                            var rng = rows.GetRow(i).GetRange('A1:Z1');
                            rng.SetFillColor(null);
                        }
                    }
                }
                refresh();
                setStatus('✅ Заливка снята.');
            } catch(e) {
                setStatus('❌ Ошибка: ' + e.message);
            }
        }

        window.onload = function() {
            setStatus('✅ Плагин готов. Нажмите кнопку для сравнения листов "Лист1" и "Лист2" по столбцу A.');
        };
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
