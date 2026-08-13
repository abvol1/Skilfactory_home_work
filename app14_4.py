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
