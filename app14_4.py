















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
