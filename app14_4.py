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
