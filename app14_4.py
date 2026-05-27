

(function()
{
    try {
        if (typeof Api === 'undefined') {
            throw new Error('Api не определён');
        }

        var sheet = Api.GetActiveSheet();
        var selection = sheet.GetSelection();
        if (!selection || selection.Count !== 1) {
            sheet.GetRange("Z1").SetValue("Выделите ровно одну ячейку в столбце A.");
            return;
        }

        // Получаем адрес выделенной ячейки (например, "$A$1" или "A1")
        var address = selection.GetAddress();
        sheet.GetRange("Z1").SetValue("Адрес выделения: " + address);

        // Проверяем, что адрес начинается с 'A' (столбец A)
        // Убираем знаки '$' и берём первую букву
        var cleanAddress = address.replace(/\$/g, '');
        var columnLetter = cleanAddress.match(/^[A-Za-z]+/)[0];
        if (columnLetter.toUpperCase() !== 'A') {
            sheet.GetRange("Z1").SetValue("Ячейка не в столбце A, а в столбце " + columnLetter);
            return;
        }

        // Пытаемся получить объект ячейки для окрашивания (может быть ActiveCell или первый элемент выделения)
        var cell = null;
        try { cell = selection.ActiveCell; } catch(e) {}
        if (!cell) {
            try { cell = selection.Get(0); } catch(e) {}
        }
        if (!cell) {
            // Если вообще не получили объект, красим через GetRange по адресу
            cell = sheet.GetRange(address);
        }

        // Закрашиваем зелёным
        var greenColor = Api.CreateColorFromRGB(0, 255, 0);
        cell.SetFillColor(greenColor);

        // Копируем выделение в буфер обмена (работает, даже если cell.Copy нет)
        selection.Copy();

        sheet.GetRange("Z1").SetValue("Готово! Ячейка " + address + " окрашена и скопирована.");

    } catch(e) {
        try {
            Api.GetActiveSheet().GetRange("Z1").SetValue("Ошибка: " + e.message);
        } catch(e2) {}
    }
})();









(function()
{
    try {
        if (typeof Api === 'undefined') {
            throw new Error('Api не определён');
        }

        var sheet = Api.GetActiveSheet();
        sheet.GetRange("Z1").SetValue("Шаг1: лист получен");

        var cell = null;
        var selection = sheet.GetSelection();
        sheet.GetRange("Z1").SetValue("Шаг2: выделение получено, Count=" + (selection ? selection.Count : 'нет'));

        // Способ 1: ActiveCell у выделения
        if (selection && selection.ActiveCell) {
            cell = selection.ActiveCell;
            sheet.GetRange("Z1").SetValue("Шаг3: ActiveCell найден");
        }
        // Способ 2: GetActiveCell листа
        else if (sheet.GetActiveCell) {
            try {
                cell = sheet.GetActiveCell();
                sheet.GetRange("Z1").SetValue("Шаг3: GetActiveCell() вернул");
            } catch(e) {
                sheet.GetRange("Z1").SetValue("Ошибка GetActiveCell(): " + e.message);
            }
        }

        if (!cell) {
            sheet.GetRange("Z1").SetValue("Активная ячейка не найдена. Выделите ровно одну ячейку.");
            return;
        }

        var col = cell.GetColIndex();
        sheet.GetRange("Z1").SetValue("Шаг4: столбец=" + col + ", значение=" + cell.GetValue());

        if (col !== 0) {
            sheet.GetRange("Z1").SetValue("Ячейка не в столбце A (столбец " + col + ")");
            return;
        }

        // Закрашиваем
        var green = Api.CreateColorFromRGB(0, 255, 0);
        cell.SetFillColor(green);
        sheet.GetRange("Z1").SetValue("Шаг5: закрашено");

        // Копируем
        cell.Copy();
        sheet.GetRange("Z1").SetValue("Готово! Ячейка A" + (cell.GetRowIndex()+1) + " скопирована и окрашена.");

    } catch(e) {
        try {
            Api.GetActiveSheet().GetRange("Z1").SetValue("Критическая ошибка: " + e.message);
        } catch(e2) {}
    }
})();







(function()
{
    if (typeof Api === 'undefined') {
        try { Api.GetActiveSheet().GetRange("Z1").SetValue("Ошибка: Api не определён."); } catch(e) {}
        return;
    }

    var sheet = Api.GetActiveSheet();
    var cell = null;

    // Способ 1: получить активную ячейку через лист
    try {
        cell = sheet.GetActiveCell();
    } catch(e) {}

    // Способ 2: если не получилось, пробуем через выделение (первая ячейка)
    if (!cell) {
        var selection = sheet.GetSelection();
        if (selection && selection.Count === 1) {
            try {
                cell = selection.Get(0); // первая ячейка выделения
            } catch(e) {}
        }
    }

    // Если всё равно не нашли — ошибка
    if (!cell) {
        sheet.GetRange("Z1").SetValue("Не удалось получить активную ячейку. Выделите ровно одну ячейку и попробуйте снова.");
        return;
    }

    // Проверяем столбец A (индекс 0)
    if (cell.GetColIndex() !== 0) {
        sheet.GetRange("Z1").SetValue("Выделите ячейку в столбце A.");
        return;
    }

    // Закрашиваем зелёным
    var greenColor = Api.CreateColorFromRGB(0, 255, 0);
    cell.SetFillColor(greenColor);

    // Копируем значение в буфер обмена
    cell.Copy();

    // Успех
    sheet.GetRange("Z1").SetValue("Ячейка A" + (cell.GetRowIndex() + 1) + " окрашена и скопирована.");
})();







(function()
{
    if (typeof Api === 'undefined') {
        try { Api.GetActiveSheet().GetRange("Z1").SetValue("Ошибка: Api не определён."); } catch(e) {}
        return;
    }

    var sheet = Api.GetActiveSheet();
    var selection = sheet.GetSelection();
    if (!selection || selection.Count === 0) {
        sheet.GetRange("Z1").SetValue("Нет выделения.");
        return;
    }

    // Берём активную ячейку
    var cell = selection.ActiveCell;
    if (!cell) {
        sheet.GetRange("Z1").SetValue("Ошибка: не удалось получить активную ячейку.");
        return;
    }

    // Проверяем, что выделена ровно одна ячейка и она в столбце A (индекс 0)
    if (selection.Count !== 1 || cell.GetColIndex() !== 0) {
        sheet.GetRange("Z1").SetValue("Выделите ровно одну ячейку в столбце A.");
        return;
    }

    // Закрашиваем в зелёный
    var greenColor = Api.CreateColorFromRGB(0, 255, 0);
    cell.SetFillColor(greenColor);

    // Копируем содержимое в буфер обмена
    cell.Copy();

    // Сообщение об успехе
    sheet.GetRange("Z1").SetValue("Готово: ячейка A" + (cell.GetRowIndex()+1) + " окрашена и скопирована.");
})();








(function()
{
    if (typeof Api === 'undefined') {
        try { Api.GetActiveSheet().GetRange("Z1").SetValue("Ошибка: Api не определён."); } catch(e) {}
        return;
    }

    var sheet = Api.GetActiveSheet();
    var errorCell = sheet.GetRange("Z1");

    // Обработчик изменения выделения
    function onSelectionChange() {
        // Вместо переданного аргумента сами получаем выделение
        var selection = sheet.GetSelection();
        if (!selection) {
            errorCell.SetValue("Обработчик: selection == null");
            return;
        }

        var cell = selection.ActiveCell;
        if (!cell) {
            errorCell.SetValue("Обработчик: ActiveCell == null, Count=" + selection.Count);
            return;
        }

        // Диагностика: выводим параметры в Z1
        var colIndex = cell.GetColIndex();
        errorCell.SetValue("Клик: столбец=" + colIndex + ", Count=" + selection.Count + ", значение=" + cell.GetValue());

        // Проверяем, что выделена одна ячейка и столбец A (индекс 0)
        if (selection.Count === 1 && colIndex === 0) {
            // Закрашиваем в зелёный
            var greenColor = Api.CreateColorFromRGB(0, 255, 0);
            cell.SetFillColor(greenColor);

            // Копируем содержимое ячейки в буфер обмена
            cell.Copy();
        }
    }

    // Назначаем обработчик
    sheet.OnSelectionChange = onSelectionChange;

    // Первичная активация
    errorCell.SetValue("Обработчик активирован. Кликните в столбце A.");
})();








(function()
{
    if (typeof Api === 'undefined') {
        try { Api.GetActiveSheet().GetRange("Z1").SetValue("Ошибка: Api не определён."); } catch(e) {}
        return;
    }

    var sheet = Api.GetActiveSheet();
    var errorCell = sheet.GetRange("Z1");

    // Функция-обработчик изменения выделения
    function onSelectionChange(selection) {
        var cell = selection.ActiveCell;
        if (!cell) return;

        // Проверяем: одна ячейка в столбце A (индекс 0)
        if (selection.Count === 1 && cell.GetColIndex() === 0) {
            // Закрашиваем в зелёный
            var greenColor = Api.CreateColorFromRGB(0, 255, 0);
            cell.SetFillColor(greenColor);

            // Копируем содержимое ячейки в буфер обмена
            cell.Copy();
        }
    }

    // Назначаем обработчик на лист
    sheet.OnSelectionChange = onSelectionChange;

    // Подтверждение активации
    errorCell.SetValue("Обработчик клика по столбцу A активирован.");
})();









(function()
{
    if (typeof Api === 'undefined') {
        try {
            Api.GetActiveSheet().GetRange("Z1").SetValue("Ошибка: Api не определён.");
        } catch(e) {}
        return;
    }

    var sheet = Api.GetActiveSheet();
    var errorCell = sheet.GetRange("Z1");

    // Удаляем предыдущий обработчик, если он был (чтобы не дублировался)
    if (this.selectionHandler) {
        Api.detachEvent("onSelectionChange", this.selectionHandler);
    }

    // Функция копирования текста в буфер обмена
    function copyToClipboard(text) {
        var textArea = document.createElement("textarea");
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
        } catch (err) {
            errorCell.SetValue("Ошибка копирования: " + err.message);
        }
        document.body.removeChild(textArea);
    }

    // Основной обработчик изменения выделения
    var selectionHandler = function(selection) {
        var cell = selection.ActiveCell;
        if (!cell) return;

        // Проверяем: выделена ровно одна ячейка и это столбец A (индекс 0)
        if (selection.Count === 1 && cell.GetColIndex() === 0) {
            // Закрашиваем в зелёный
            var greenColor = Api.CreateColorFromRGB(0, 255, 0);
            cell.SetFillColor(greenColor);

            // Копируем значение ячейки в буфер
            var value = cell.GetValue();
            if (value !== null && value !== undefined) {
                copyToClipboard(String(value));
            }
        }
    };

    // Сохраняем обработчик для возможности удаления в будущем
    this.selectionHandler = selectionHandler;

    // Регистрируем событие
    Api.attachEvent("onSelectionChange", selectionHandler);

    // Сообщение об успешном запуске
    errorCell.SetValue("Обработчик клика по столбцу A активирован.");
})();










(function()
{
    // Если Api не определён, пытаемся вывести ошибку на лист (если возможно)
    if (typeof Api === 'undefined') {
        try {
            var actSheet = Api.GetActiveSheet();
            if (actSheet) actSheet.GetRange("Z1").SetValue("Ошибка: Api не определён.");
        } catch(e) {}
        return;
    }

    var sheet = Api.GetActiveSheet();

    // Функция копирования текста в буфер обмена
    function copyToClipboard(text) {
        var textArea = document.createElement("textarea");
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
        } catch (err) {
            // Ошибка копирования выводится на лист
            sheet.GetRange("Z1").SetValue("Ошибка копирования в буфер: " + err.message);
        }
        document.body.removeChild(textArea);
    }

    // Обработчик изменения выделения
    function onSelectionChange(selection) {
        var cell = selection.ActiveCell;
        if (!cell) return;

        // Проверяем: одна ячейка и столбец A (индекс 0)
        if (selection.Count === 1 && cell.GetColIndex() === 0) {
            // Зелёная заливка
            var greenColor = Api.CreateColorFromRGB(0, 255, 0);
            cell.SetFillColor(greenColor);

            // Копируем значение в буфер
            var value = cell.GetValue();
            if (value !== null && value !== undefined) {
                copyToClipboard(String(value));
            }
        }
    }

    // Назначаем обработчик на текущий лист
    sheet.OnSelectionChange = onSelectionChange;
})();











(function()
{
    if (typeof(Api) === 'undefined') {
        Api.GetActiveSheet().GetRange("Z1").SetValue("Ошибка: Api не определён.");
        return;
    }

    // 1. Получаем листы
    let sheetTemplate = Api.GetSheet("Шаблон");
    let sheetWork = Api.GetActiveSheet();   // это и есть "чек_лист"
    let sheetCheck = Api.GetSheet("чек_лист");

    if (!sheetTemplate) {
        sheetWork.GetRange("Z1").SetValue("Ошибка: лист 'Шаблон' не найден.");
        return;
    }
    if (!sheetCheck) {
        sheetWork.GetRange("Z1").SetValue("Ошибка: лист 'чек_лист' не найден.");
        return;
    }

    // 2. Сохраняем значение A2 листа "чек_лист" ДО копирования
    let rangeA2 = sheetCheck.GetRange("A2");
    let savedValueA2 = rangeA2 ? rangeA2.GetValue() : null;

    // 3. Копируем шаблон на активный лист (чек_лист)
    let usedRangeTemplate = sheetTemplate.GetUsedRange();
    if (!usedRangeTemplate) {
        sheetWork.GetRange("Z1").SetValue("Ошибка: на листе 'Шаблон' нет данных.");
        return;
    }

    let targetAddress = usedRangeTemplate.GetAddress();
    let targetRange = sheetWork.GetRange(targetAddress);
    usedRangeTemplate.Copy(targetRange);

    // 4. Восстанавливаем сохранённое значение A2 (чтобы не затиралось)
    if (savedValueA2 !== null) {
        rangeA2.SetValue(savedValueA2);
    }

    // 5. Формируем текущую дату
    let today = new Date();
    let day = String(today.getDate()).padStart(2, '0');
    let month = String(today.getMonth() + 1).padStart(2, '0');
    let year = today.getFullYear();
    let currentDate = `${day}.${month}.${year}`;

    // 6. Замены на рабочем листе (чек_лист)
    let usedRangeWork = sheetWork.GetUsedRange();
    if (!usedRangeWork) {
        sheetWork.GetRange("Z1").SetValue("Ошибка: нет данных для замены.");
        return;
    }

    let logMessage = "";
    if (savedValueA2 && savedValueA2 !== "[РФ]") {
        usedRangeWork.Replace("[РФ]", savedValueA2, "xlPart", "xlByRows", "xlNext", false, true);
        logMessage += `'[РФ]' → '${savedValueA2}'; `;
    } else {
        logMessage += `'[РФ]' не заменён (A2 пусто или равно '[РФ]'); `;
    }
    usedRangeWork.Replace("[ДАТА1]", currentDate, "xlPart", "xlByRows", "xlNext", false, true);
    logMessage += `'[ДАТА1]' → '${currentDate}'`;

    // 7. Отладка в Z1
    sheetWork.GetRange("Z1").SetValue("✅ Готово: " + logMessage);
})();














(function()
{
    if (typeof(Api) === 'undefined') {
        Api.GetActiveSheet().GetRange("Z1").SetValue("Ошибка: Api не определён.");
        return;
    }

    // 1. Получаем листы: шаблон, рабочий и чек-лист
    let sheetTemplate = Api.GetSheet("Шаблон");
    let sheetWork = Api.GetActiveSheet();
    let sheetCheck = Api.GetSheet("чек_лист");

    if (!sheetTemplate) {
        sheetWork.GetRange("Z1").SetValue("Ошибка: лист 'Шаблон' не найден.");
        return;
    }
    if (!sheetCheck) {
        sheetWork.GetRange("Z1").SetValue("Ошибка: лист 'чек_лист' не найден.");
        return;
    }

    // 2. Копируем данные с шаблона на рабочий лист
    let usedRangeTemplate = sheetTemplate.GetUsedRange();
    if (!usedRangeTemplate) {
        sheetWork.GetRange("Z1").SetValue("Ошибка: на листе 'Шаблон' нет данных.");
        return;
    }

    let targetAddress = usedRangeTemplate.GetAddress();
    let targetRange = sheetWork.GetRange(targetAddress);
    usedRangeTemplate.Copy(targetRange);

    // 3. Получаем значение из ячейки A2 листа "чек_лист" для замены "[РФ]"
    let rangeA2 = sheetCheck.GetRange("A2");
    let replacementRF = rangeA2 ? rangeA2.GetValue() : null;

    // 4. Формируем текущую дату в формате ДД.ММ.ГГГГ
    let today = new Date();
    let day = String(today.getDate()).padStart(2, '0');
    let month = String(today.getMonth() + 1).padStart(2, '0');
    let year = today.getFullYear();
    let currentDate = `${day}.${month}.${year}`;

    // 5. Выполняем замены на рабочем листе
    let usedRangeWork = sheetWork.GetUsedRange();
    if (!usedRangeWork) {
        sheetWork.GetRange("Z1").SetValue("Ошибка: на рабочем листе нет данных для замены.");
        return;
    }

    let logMessage = "";
    if (replacementRF && replacementRF !== "[РФ]") {
        usedRangeWork.Replace("[РФ]", replacementRF, "xlPart", "xlByRows", "xlNext", false, true);
        logMessage += `'[РФ]' → '${replacementRF}'; `;
    } else {
        logMessage += `'[РФ]' не заменён (чек_лист!A2 пусто или равно '[РФ]'); `;
    }
    usedRangeWork.Replace("[ДАТА1]", currentDate, "xlPart", "xlByRows", "xlNext", false, true);
    logMessage += `'[ДАТА1]' → '${currentDate}'`;

    // 6. Записываем результат отладки в ячейку Z1
    sheetWork.GetRange("Z1").SetValue("✅ Готово: " + logMessage);
})();
