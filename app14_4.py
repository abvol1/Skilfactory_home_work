



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
