
(function()
{
    if (typeof(Api) === 'undefined') {
        console.log("Ошибка: Api не определён.");
        return;
    }

    // 1. Получаем лист-шаблон и активный лист (рабочий)
    let sheetTemplate = Api.GetSheetByName("Шаблон");
    let sheetWork = Api.GetActiveSheet();

    if (!sheetTemplate) {
        console.log("Ошибка: лист с именем 'Шаблон' не найден.");
        return;
    }
    if (!sheetWork) {
        console.log("Ошибка: активный лист не получен.");
        return;
    }

    // 2. Копируем все использованные ячейки с шаблона на рабочий лист
    let usedRangeTemplate = sheetTemplate.GetUsedRange();
    if (!usedRangeTemplate) {
        console.log("На листе 'Шаблон' нет данных.");
        return;
    }

    let targetAddress = usedRangeTemplate.GetAddress();
    let targetRange = sheetWork.GetRange(targetAddress);
    usedRangeTemplate.Copy(targetRange);
    console.log("Данные скопированы с листа 'Шаблон'.");

    // 3. Получаем замену для ВСП из ячейки A1 рабочего листа (после копирования)
    let oRangeA1 = sheetWork.GetRange("A1");
    let replacementVSP = oRangeA1 ? oRangeA1.GetValue() : null;
    if (!replacementVSP || replacementVSP === "") {
        console.log("Предупреждение: ячейка A1 пуста. Замена 'ВСП' не будет выполнена.");
        replacementVSP = null;
    }

    // 4. Текущая дата
    let today = new Date();
    let day = String(today.getDate()).padStart(2, '0');
    let month = String(today.getMonth() + 1).padStart(2, '0');
    let year = today.getFullYear();
    let currentDate = `${day}.${month}.${year}`;

    // 5. Заменяем маркеры на рабочем листе
    let usedRangeWork = sheetWork.GetUsedRange();
    if (usedRangeWork) {
        if (replacementVSP && replacementVSP !== "ВСП") {
            usedRangeWork.Replace("ВСП", replacementVSP, "xlPart", "xlByRows", "xlNext", false, true);
            console.log(`Замена 'ВСП' → '${replacementVSP}'`);
        }
        usedRangeWork.Replace("ДАТА1", currentDate, "xlPart", "xlByRows", "xlNext", false, true);
        console.log(`Замена 'ДАТА1' → '${currentDate}'`);
    } else {
        console.log("Не удалось получить диапазон на рабочем листе.");
        return;
    }

    console.log("✅ Макрос успешно выполнен. Шаблон сохранён.");
})();
