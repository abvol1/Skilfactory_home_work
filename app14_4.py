
(function() {
    var srcSheet = Api.GetActiveSheet();
    srcSheet.GetRange("Z1").SetValue("1. Старт");

    var destSheet = Api.GetSheet("текст");
    srcSheet.GetRange("Z2").SetValue("2. Поиск листа");

    if (!destSheet) {
        destSheet = Api.CreateSheet("текст");
        srcSheet.GetRange("Z3").SetValue("3. Создан новый лист");
    } else {
        srcSheet.GetRange("Z3").SetValue("3. Лист уже есть");
    }
    if (!destSheet) {
        srcSheet.GetRange("Z1").SetValue("Ошибка создания листа");
        return;
    }
    srcSheet.GetRange("Z4").SetValue("4. Лист готов");

    // Проверяем первую ячейку, чтобы убедиться, что чтение работает
    var testVal = srcSheet.GetRange("A1").GetValue();
    srcSheet.GetRange("Z5").SetValue("5. Значение A1: " + (testVal || "пусто"));

    // Ищем последнюю строку (упрощённо, только до 100)
    var lastRow = 0;
    for (var i = 1; i <= 100; i++) {
        var v = srcSheet.GetRange("A" + i).GetValue();
        if (v && v !== "") lastRow = i;
    }
    srcSheet.GetRange("Z6").SetValue("6. Последняя строка: " + lastRow);

    var copied = 0;
    for (var r = 1; r <= lastRow; r++) {
        var val = srcSheet.GetRange("A" + r).GetValue();
        if (val && val.toString().toLowerCase().indexOf("проба") !== -1) {
            // копируем только столбец A для теста
            destSheet.GetRange(copied + 1, 1).SetValue(val);
            copied++;
        }
    }
    srcSheet.GetRange("Z7").SetValue("7. Скопировано: " + copied);
    srcSheet.GetRange("Z1").SetValue("Готово");
})();






(function() {
    var srcSheet = Api.GetActiveSheet();
    // Пишем начало работы в ячейку Z1 (чтобы видеть, что макрос стартовал)
    srcSheet.GetRange("Z1").SetValue("Макрос запущен...");

    // ---- 1. Создаём или получаем лист "текст" ----
    var destSheet = Api.GetSheet("текст");
    if (!destSheet) {
        destSheet = Api.CreateSheet("текст");
        srcSheet.GetRange("Z2").SetValue("Лист 'текст' создан");
    } else {
        srcSheet.GetRange("Z2").SetValue("Лист 'текст' уже существует");
    }
    if (!destSheet) {
        srcSheet.GetRange("Z1").SetValue("Ошибка: не удалось создать лист 'текст'");
        return;
    }

    // ---- 2. Определяем последнюю строку с данными (перебор до 5000) ----
    var lastRow = 0;
    for (var i = 1; i <= 5000; i++) {
        var val = srcSheet.GetRange("A" + i).GetValue();
        if (val !== undefined && val !== null && val !== "") {
            lastRow = i;
        } else {
            // Если 5 пустых подряд – считаем, что данные кончились
            var emptyCount = 0;
            for (var j = i; j <= i + 4 && j <= 5000; j++) {
                var check = srcSheet.GetRange("A" + j).GetValue();
                if (check === undefined || check === null || check === "") emptyCount++;
            }
            if (emptyCount >= 5) break;
        }
    }
    srcSheet.GetRange("Z3").SetValue("Последняя строка: " + lastRow);

    if (lastRow === 0) {
        srcSheet.GetRange("Z1").SetValue("Нет данных в столбце A");
        return;
    }

    // ---- 3. Копирование строк (столбцы A–T, можно увеличить) ----
    var destRow = 1;
    var copiedCount = 0;
    var maxCols = 20; // если нужно больше – увеличьте

    for (var r = 1; r <= lastRow; r++) {
        var cellA = srcSheet.GetRange("A" + r);
        var cellValue = cellA.GetValue();

        if (cellValue && cellValue.toString().toLowerCase().indexOf("проба") !== -1) {
            // Копируем все столбцы от 1 до maxCols
            for (var c = 1; c <= maxCols; c++) {
                var srcVal = srcSheet.GetRange(r, c).GetValue();
                destSheet.GetRange(destRow, c).SetValue(srcVal);
            }
            destRow++;
            copiedCount++;
        }
    }

    // ---- 4. Вывод результатов ----
    srcSheet.GetRange("Z1").SetValue("Готово! Скопировано строк: " + copiedCount);
    destSheet.GetRange("A1").SetValue("Скопировано строк: " + copiedCount);
})();







(function() {
    // ---- 1. Получаем активный лист ----
    var srcSheet = Api.GetActiveSheet();
    if (!srcSheet) {
        // Если не удалось, записываем ошибку в ячейку A1 текущего листа
        var errSheet = Api.GetActiveSheet();
        if (errSheet) errSheet.GetRange("A1").SetValue("Ошибка: нет активного листа");
        return;
    }

    // ---- 2. Работа с листом "текст" ----
    var destSheet = Api.GetSheet("текст");
    if (!destSheet) {
        destSheet = Api.CreateSheet("текст");
        // Если создать не удалось – выходим
        if (!destSheet) {
            srcSheet.GetRange("Z1").SetValue("Ошибка: не удалось создать лист 'текст'");
            return;
        }
    }

    // Очищаем лист назначения (опционально, чтобы не было мусора)
    // destSheet.GetUsedRange().Clear();

    // ---- 3. Определяем границы данных на исходном листе ----
    // Пытаемся получить используемый диапазон
    var usedRange = srcSheet.GetUsedRange();
    var totalRows, totalCols, startRow, startCol;

    if (usedRange) {
        totalRows = usedRange.GetRowsCount();
        totalCols = usedRange.GetColumnsCount();
        startRow = usedRange.GetRow();
        startCol = usedRange.GetColumn();
    } else {
        // Если UsedRange не работает – вручную ищем последнюю строку и столбец
        totalRows = 0;
        totalCols = 0;
        startRow = 1;
        startCol = 1;
        // Ищем последнюю непустую строку (максимум 10000)
        for (var i = 1; i <= 10000; i++) {
            var val = srcSheet.GetRange("A" + i).GetValue();
            if (val !== undefined && val !== null && val !== "") {
                totalRows = i;
            } else {
                // Если 5 пустых подряд – стоп
                var empty = 0;
                for (var j = i; j <= i + 4 && j <= 10000; j++) {
                    if (!srcSheet.GetRange("A" + j).GetValue()) empty++;
                }
                if (empty >= 5) break;
            }
        }
        // Ищем последнюю непустую колонку (максимум 50)
        for (var c = 1; c <= 50; c++) {
            var colVal = srcSheet.GetRange(startRow, c).GetValue();
            if (colVal !== undefined && colVal !== null && colVal !== "") {
                totalCols = c;
            }
        }
        if (totalRows === 0) {
            srcSheet.GetRange("Z1").SetValue("Нет данных для копирования");
            return;
        }
        // Если totalCols остался 0, ставим хотя бы 1
        if (totalCols === 0) totalCols = 1;
    }

    // ---- 4. Копирование строк ----
    var destRow = 1;
    var copiedCount = 0;

    for (var r = 0; r < totalRows; r++) {
        var rowIndex = startRow + r;
        var cellA = srcSheet.GetRange(rowIndex, startCol); // столбец A
        var cellValue = cellA.GetValue();

        // Проверяем наличие "проба" (без учёта регистра)
        if (cellValue && cellValue.toString().toLowerCase().indexOf("проба") !== -1) {
            // Копируем все столбцы из диапазона
            for (var c = 0; c < totalCols; c++) {
                var colIndex = startCol + c;
                var srcVal = srcSheet.GetRange(rowIndex, colIndex).GetValue();
                destSheet.GetRange(destRow, c + 1).SetValue(srcVal);
            }
            destRow++;
            copiedCount++;
        }
    }

    // ---- 5. Вывод результата на лист "текст" ----
    destSheet.GetRange("A1").SetValue("Скопировано строк: " + copiedCount);
    // Также можно записать отчёт на исходный лист (в ячейку Z1)
    srcSheet.GetRange("Z1").SetValue("Макрос выполнен, скопировано " + copiedCount + " строк");
})();







(function() {
    var srcSheet = Api.ActiveSheet();
    if (!srcSheet) { Api.ShowMessage("Нет активного листа"); return; }

    var destSheet = Api.Sheets("текст");
    if (!destSheet) {
        destSheet = Api.Sheets.Add();
        destSheet.Name = "текст";
    }

    var destRow = 1;
    for (var i = 1; i <= 100; i++) {
        var val = srcSheet.Cells(i, 1).Value;
        if (val && val.toString().toLowerCase().indexOf("проба") !== -1) {
            for (var j = 1; j <= 5; j++) {
                destSheet.Cells(destRow, j).Value = srcSheet.Cells(i, j).Value;
            }
            destRow++;
        }
    }
    Api.ShowMessage("Готово!");
})();







(function() {
    var srcSheet = Api.GetActiveSheet();
    var destSheet = Api.GetSheet("текст");
    
    // Создаём лист "текст", если его нет
    if (!destSheet) {
        destSheet = Api.CreateSheet("текст");
    }

    // Определяем последнюю строку с данными в столбце A
    var lastRow = 1;
    for (var i = 1; i <= 10000; i++) {
        var val = srcSheet.GetRange("A" + i).GetValue();
        if (val !== undefined && val !== null && val !== "") {
            lastRow = i;
        } else {
            // Если встретили подряд 5 пустых строк — считаем, что данные кончились
            var emptyCount = 0;
            for (var j = i; j <= i + 5; j++) {
                var checkVal = srcSheet.GetRange("A" + j).GetValue();
                if (checkVal === undefined || checkVal === null || checkVal === "") {
                    emptyCount++;
                }
            }
            if (emptyCount >= 5) break;
        }
    }

    var destRow = 1;
    var maxCols = 20; // Копируем столбцы A–T (можно увеличить)

    for (var i = 1; i <= lastRow; i++) {
        var cellValue = srcSheet.GetRange("A" + i).GetValue();
        if (cellValue && cellValue.toString().toLowerCase().indexOf("проба") !== -1) {
            for (var j = 1; j <= maxCols; j++) {
                var srcCell = srcSheet.GetRange(i, j);
                var val = srcCell.GetValue();
                destSheet.GetRange(destRow, j).SetValue(val);
            }
            destRow++;
        }
    }

    Api.ShowMessage("Готово! Скопировано строк: " + (destRow - 1));
})();






(function() {
    var srcSheet = Api.GetActiveSheet();
    if (!srcSheet) {
        Api.ShowMessage("Нет активного листа.");
        return;
    }

    // Создаем или получаем лист "текст"
    var destSheet = Api.GetSheet("текст");
    if (!destSheet) {
        destSheet = Api.CreateSheet("текст");
        if (!destSheet) {
            Api.ShowMessage("Не удалось создать лист 'текст'.");
            return;
        }
    }

    // Определяем используемый диапазон на исходном листе
    var usedRange = srcSheet.GetUsedRange();
    if (!usedRange) {
        Api.ShowMessage("На активном листе нет данных.");
        return;
    }

    // Получаем количество строк и столбцов в используемом диапазоне
    var totalRows = usedRange.GetRowsCount();
    var totalCols = usedRange.GetColumnsCount();

    // Если данные начинаются не с первой строки, нужно смещение
    var startRow = usedRange.GetRow(); // номер первой строки диапазона
    var startCol = usedRange.GetColumn(); // номер первого столбца

    // Переменная для строки назначения (начинаем с первой свободной)
    var destRow = destSheet.GetUsedRange() ? destSheet.GetUsedRange().GetRow() + destSheet.GetUsedRange().GetRowsCount() : 1;

    // Проходим по всем строкам используемого диапазона
    for (var i = 0; i < totalRows; i++) {
        var rowIndex = startRow + i; // абсолютный номер строки
        // Получаем значение в столбце А (индекс столбца = startCol)
        var cell = srcSheet.GetRange(rowIndex, startCol); // ячейка A
        var cellValue = cell.GetValue();

        // Проверяем, содержит ли значение "проба" (без учета регистра и пробелов)
        if (cellValue && cellValue.toString().toLowerCase().indexOf("проба") !== -1) {
            // Копируем всю строку по ячейкам
            for (var j = 0; j < totalCols; j++) {
                var colIndex = startCol + j;
                var srcCell = srcSheet.GetRange(rowIndex, colIndex);
                var val = srcCell.GetValue();
                // Записываем в лист назначения
                destSheet.GetRange(destRow, colIndex - startCol + 1).SetValue(val);
            }
            destRow++; // переходим на следующую строку в назначении
        }
    }

    Api.ShowMessage("Готово! Скопировано строк: " + (destRow - (destSheet.GetUsedRange() ? destSheet.GetUsedRange().GetRow() : 1)));
})();







(function() {
    var oWorksheet = Api.GetActiveSheet();
    var destSheetName = "текст";
    var destSheet = Api.GetSheet(destSheetName);

    if (!destSheet) {
        destSheet = Api.CreateSheet(destSheetName);
    }

    var lastRow = oWorksheet.GetRowsCount();
    var destRow = 1;

    for (var i = 1; i <= lastRow; i++) {
        var cell = oWorksheet.GetRange("A" + i);
        var cellValue = cell.GetValue();

        if (cellValue && cellValue.toString().toLowerCase().indexOf("проба") !== -1) {
            var srcRange = oWorksheet.GetRange("A" + i + ":" + oWorksheet.GetColumnsCount() + i);
            var destRange = destSheet.GetRange("A" + destRow);
            srcRange.Copy(destRange);
            destRow++;
        }
    }
})();




Действительно, в Р7-Офис не используется VBA. Программирование макросов и плагинов в нем ведется на языке JavaScript.

Это связано с архитектурой Р7-Офис, который является ответвлением OnlyOffice. Макросы Microsoft Office используют VBA, а редакторы Р7 — JavaScript. Однако это не сложно — ваши ранее используемые макросы можно преобразовать в новый формат.

📝 Как будут выглядеть ваши макросы на JavaScript

Вот как можно переписать ваши задачи:

Макрос 1: Поиск "проба" и копирование на лист "текст"

```javascript
(function() {
    const oWorksheet = Api.GetActiveSheet();
    const destSheetName = "текст";
    let destSheet = Api.GetSheet(destSheetName);
    
    if (!destSheet) {
        destSheet = Api.CreateSheet(destSheetName);
    }

    const lastRow = oWorksheet.GetRowsCount();
    let destRow = 1;

    for (let i = 1; i <= lastRow; i++) {
        const cellValue = oWorksheet.GetRange("A" + i).GetValue();
        if (cellValue && cellValue.toString().toLowerCase().includes("проба")) {
            const srcRange = oWorksheet.GetRange("A" + i + ":" + oWorksheet.GetColumnsCount() + i);
            const destRange = destSheet.GetRange("A" + destRow);
            srcRange.Copy(destRange);
            destRow++;
        }
    }
})();
```

Макрос 2: Импорт данных из выбранного файла

```javascript
(function() {
    const filePath = Api.OpenFileDialog("Выберите файл для импорта", "*.xls;*.xlsx;*.xlsm");
    if (!filePath) return;

    const oWorkbook = Api.OpenFile(filePath);
    if (!oWorkbook) return;

    const srcSheet = oWorkbook.GetSheet("Лист1") || oWorkbook.GetActiveSheet();
    const destSheet = Api.GetSheet("текст");
    if (!destSheet) {
        Api.ShowMessage("Лист 'текст' не найден. Сначала выполните первый макрос.");
        oWorkbook.Close();
        return;
    }

    const usedRange = srcSheet.GetUsedRange();
    const lastDestRow = destSheet.GetRowsCount() + 1;
    usedRange.Copy(destSheet.GetRange("A" + lastDestRow));

    oWorkbook.Close();
    Api.ShowMessage("Импорт завершён!");
})();
```

🚀 Как запустить макросы в Р7-Офис

1. Откройте таблицу и перейдите на вкладку «Плагины» → выберите «Макросы».
2. В открывшемся окне нажмите «Создать» (или «Новый»).
3. В поле редактора вставьте код JavaScript (вместо стандартной заготовки).
4. Нажмите «ОК» для сохранения, затем снова откройте окно макросов, выберите ваш макрос и нажмите «Выполнить».

💡 Альтернативные подходы

· RPA-инструменты: для автоматизации подойдут системы вроде Primo RPA с пакетом Primo.Office.P7 или Robin RPA с поддержкой Python-скриптов для Р7.
· Готовые решения: поищите на GitHub (например, проект championship_r7_2025) или обратитесь к специалистам по разработке макросов для Р7.

Если нужна помощь с адаптацией других конкретных задач — пишите, постараюсь помочь с переводом на JavaScript.





Вот два макроса для Р7-Офис (совместимого с VBA).

---

Макрос 1: Поиск строк с «проба» в столбце А и копирование на лист «текст»

```vba
Sub CopyRowsWithProba()
    Dim wsSrc As Worksheet
    Dim wsDest As Worksheet
    Dim lastRow As Long
    Dim i As Long
    Dim destRow As Long
    
    ' Активный лист как источник
    Set wsSrc = ActiveSheet
    
    ' Проверяем, существует ли лист "текст", если нет — создаём
    On Error Resume Next
    Set wsDest = ThisWorkbook.Worksheets("текст")
    On Error GoTo 0
    If wsDest Is Nothing Then
        Set wsDest = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(ThisWorkbook.Worksheets.Count))
        wsDest.Name = "текст"
    End If
    
    ' Находим последнюю заполненную строку в столбце А источника
    lastRow = wsSrc.Cells(wsSrc.Rows.Count, 1).End(xlUp).Row
    
    ' Первая свободная строка на листе назначения (для добавления)
    destRow = wsDest.Cells(wsDest.Rows.Count, 1).End(xlUp).Row + 1
    
    ' Проходим по всем строкам источника
    For i = 1 To lastRow
        ' Ищем вхождение "проба" (без учёта регистра) в ячейке столбца А
        ' Если нужно строго с пробелом в начале, замените на LCase(wsSrc.Cells(i, 1).Value) Like " проба*"
        If InStr(1, LCase(wsSrc.Cells(i, 1).Value), "проба") > 0 Then
            ' Копируем всю строку
            wsSrc.Rows(i).Copy Destination:=wsDest.Rows(destRow)
            destRow = destRow + 1
        End If
    Next i
    
    MsgBox "Готово! Скопировано " & (destRow - wsDest.Cells(wsDest.Rows.Count, 1).End(xlUp).Row - 1) & " строк.", vbInformation
End Sub
```

---

Макрос 2: Импорт данных из выбранного файла (с листа «Лист1») в лист «текст»

```vba
Sub ImportFromFile()
    Dim filePath As Variant
    Dim wbSrc As Workbook
    Dim wsSrc As Worksheet
    Dim wsDest As Worksheet
    Dim lastRowSrc As Long
    Dim lastRowDest As Long
    Dim importRange As Range
    
    ' Открываем диалог выбора файла
    filePath = Application.GetOpenFilename( _
        FileFilter:="Файлы Excel (*.xls;*.xlsx;*.xlsm), *.xls;*.xlsx;*.xlsm", _
        Title:="Выберите файл для импорта")
    
    ' Если пользователь отменил выбор
    If filePath = False Then Exit Sub
    
    ' Открываем выбранную книгу
    Set wbSrc = Workbooks.Open(filePath)
    
    ' Пытаемся взять лист "Лист1", если нет — берём первый лист
    On Error Resume Next
    Set wsSrc = wbSrc.Worksheets("Лист1")
    On Error GoTo 0
    If wsSrc Is Nothing Then
        Set wsSrc = wbSrc.Worksheets(1)
    End If
    
    ' Проверяем наличие листа "текст" в текущей книге
    On Error Resume Next
    Set wsDest = ThisWorkbook.Worksheets("текст")
    On Error GoTo 0
    If wsDest Is Nothing Then
        MsgBox "В текущей книге нет листа 'текст'. Сначала выполните первый макрос.", vbExclamation
        wbSrc.Close SaveChanges:=False
        Exit Sub
    End If
    
    ' Определяем последнюю заполненную строку в источнике (по столбцу А)
    lastRowSrc = wsSrc.Cells(wsSrc.Rows.Count, 1).End(xlUp).Row
    If lastRowSrc < 1 Then
        MsgBox "В источнике нет данных.", vbInformation
        wbSrc.Close SaveChanges:=False
        Exit Sub
    End If
    
    ' Определяем первую свободную строку в листе "текст"
    lastRowDest = wsDest.Cells(wsDest.Rows.Count, 1).End(xlUp).Row + 1
    
    ' Копируем все данные с листа-источника (используем UsedRange для полноты)
    wsSrc.UsedRange.Copy Destination:=wsDest.Cells(lastRowDest, 1)
    
    ' Закрываем исходную книгу без сохранения
    wbSrc.Close SaveChanges:=False
    
    MsgBox "Импорт завершён. Добавлено " & wsSrc.UsedRange.Rows.Count & " строк.", vbInformation
End Sub
```

---

Как использовать

1. Откройте книгу в Р7-Офис.
2. Нажмите Alt+F11, чтобы открыть редактор VBA.
3. Вставьте оба макроса в любой модуль (через Insert → Module).
4. Закройте редактор.
5. Запускайте макросы через Alt+F8 или назначьте на кнопки.

---

Примечания

· Первый макрос ищет подстроку «проба» без учёта регистра. Если нужен именно пробел в начале, замените условие на wsSrc.Cells(i, 1).Value Like " проба*".
· Второй макрос открывает файл, берёт данные с листа «Лист1» (или первого листа) и добавляет их в конец листа «текст».
· Оба макроса обрабатывают ошибки (например, отсутствие листа, отмена выбора файла).
