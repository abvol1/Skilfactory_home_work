
(function() {
    var srcSheet = Api.GetActiveSheet();

    // ---- 1. Получаем лист "текст" (должен существовать) ----
    var destSheet = Api.GetSheet("текст");
    if (!destSheet) {
        srcSheet.GetRange("Z1").SetValue("Ошибка: создайте лист 'текст' вручную");
        return;
    }

    // ---- 2. Определяем последнюю строку с данными (до 5000) ----
    var lastRow = 0;
    for (var i = 1; i <= 5000; i++) {
        var val = srcSheet.GetRange("A" + i).GetValue();
        if (val !== undefined && val !== null && val !== "") {
            lastRow = i;
        } else {
            var emptyCount = 0;
            for (var j = i; j <= i + 4 && j <= 5000; j++) {
                if (!srcSheet.GetRange("A" + j).GetValue()) emptyCount++;
            }
            if (emptyCount >= 5) break;
        }
    }

    if (lastRow === 0) {
        srcSheet.GetRange("Z1").SetValue("Нет данных в столбце A");
        return;
    }

    // ---- 3. Копирование строк (столбцы A–T, можно увеличить) ----
    var destRow = 1;
    var copiedCount = 0;
    var maxCols = 20; // если нужно больше – измените

    for (var r = 1; r <= lastRow; r++) {
        var cellValue = srcSheet.GetRange("A" + r).GetValue();
        if (cellValue && cellValue.toString().toLowerCase().indexOf("проба") !== -1) {
            // Копируем столбцы от 1 до maxCols
            for (var c = 1; c <= maxCols; c++) {
                var srcVal = srcSheet.GetRange(r, c).GetValue();
                destSheet.GetRange(destRow, c).SetValue(srcVal);
            }
            destRow++;
            copiedCount++;
        }
    }

    // ---- 4. Итог ----
    srcSheet.GetRange("Z1").SetValue("Готово! Скопировано строк: " + copiedCount);
    destSheet.GetRange("A1").SetValue("Скопировано строк: " + copiedCount);
})();







(function() {
    var srcSheet = Api.GetActiveSheet();

    // ---- Получаем лист "текст" (он должен существовать) ----
    var destSheet = Api.GetSheet("текст");
    if (!destSheet) {
        // Если листа нет — пишем сообщение в ячейку и выходим
        srcSheet.GetRange("Z1").SetValue("Ошибка: создайте лист 'текст' вручную и запустите макрос снова");
        return;
    }

    // ---- Определяем последнюю строку с данными (до 10 000) ----
    var lastRow = 0;
    for (var i = 1; i <= 10000; i++) {
        var val = srcSheet.GetRange("A" + i).GetValue();
        if (val !== undefined && val !== null && val !== "") {
            lastRow = i;
        } else {
            // Если 5 пустых подряд – считаем, что данные кончились
            var emptyCount = 0;
            for (var j = i; j <= i + 4 && j <= 10000; j++) {
                if (!srcSheet.GetRange("A" + j).GetValue()) emptyCount++;
            }
            if (emptyCount >= 5) break;
        }
    }

    if (lastRow === 0) {
        srcSheet.GetRange("Z1").SetValue("Нет данных в столбце A");
        return;
    }

    // ---- Определяем последний столбец с данными (максимум 50) ----
    var lastCol = 1;
    for (var c = 1; c <= 50; c++) {
        var colVal = srcSheet.GetRange(1, c).GetValue();
        if (colVal !== undefined && colVal !== null && colVal !== "") {
            lastCol = c;
        }
    }

    // ---- Очищаем лист назначения (только данные, не форматирование) ----
    // для безопасности очищаем только столбцы, которые будем заполнять
    for (var r = 1; r <= 10000; r++) {
        for (var c = 1; c <= lastCol; c++) {
            destSheet.GetRange(r, c).SetValue("");
        }
    }

    // ---- Копирование строк со словом "проба" ----
    var destRow = 1;
    var copiedCount = 0;

    for (var r = 1; r <= lastRow; r++) {
        var cellValue = srcSheet.GetRange("A" + r).GetValue();
        if (cellValue && cellValue.toString().toLowerCase().indexOf("проба") !== -1) {
            // Копируем все столбцы от 1 до lastCol
            for (var c = 1; c <= lastCol; c++) {
                var srcVal = srcSheet.GetRange(r, c).GetValue();
                destSheet.GetRange(destRow, c).SetValue(srcVal);
            }
            destRow++;
            copiedCount++;
        }
    }

    // ---- Итоговое сообщение ----
    srcSheet.GetRange("Z1").SetValue("Готово! Скопировано строк: " + copiedCount);
    destSheet.GetRange("A1").SetValue("Скопировано строк: " + copiedCount);
})();



















(function() {
    var srcSheet = Api.GetActiveSheet();
    srcSheet.GetRange("Z1").SetValue("1. Старт");

    // ---- Получение листа "текст" (предполагаем, что он уже создан) ----
    var destSheet = Api.GetSheet("текст");
    srcSheet.GetRange("Z2").SetValue("2. Лист 'текст' получен: " + (destSheet ? "да" : "нет"));
    if (!destSheet) {
        srcSheet.GetRange("Z1").SetValue("Ошибка: лист 'текст' не найден");
        return;
    }

    // ---- Определяем последнюю строку (упрощённо, до 100) ----
    var lastRow = 0;
    for (var i = 1; i <= 100; i++) {
        var val = srcSheet.GetRange("A" + i).GetValue();
        if (val !== undefined && val !== null && val !== "") {
            lastRow = i;
        } else {
            // Если 3 пустые подряд – стоп
            var empty = 0;
            for (var j = i; j <= i + 2 && j <= 100; j++) {
                if (!srcSheet.GetRange("A" + j).GetValue()) empty++;
            }
            if (empty >= 3) break;
        }
    }
    srcSheet.GetRange("Z3").SetValue("3. Последняя строка: " + lastRow);
    if (lastRow === 0) {
        srcSheet.GetRange("Z1").SetValue("Нет данных");
        return;
    }

    // ---- Очищаем лист назначения перед копированием ----
    srcSheet.GetRange("Z4").SetValue("4. Очистка листа 'текст'...");
    destSheet.GetUsedRange().Clear();  // если зависнет – удалим эту строку

    // ---- Цикл копирования с записью прогресса ----
    var destRow = 1;
    var copiedCount = 0;
    srcSheet.GetRange("Z5").SetValue("5. Начинаем копирование...");

    for (var r = 1; r <= lastRow; r++) {
        // Записываем номер текущей строки в ячейку Z10 (обновляется каждую итерацию)
        srcSheet.GetRange("Z10").SetValue("Обработка строки " + r);

        var cellA = srcSheet.GetRange("A" + r);
        var cellValue = cellA.GetValue();

        if (cellValue && cellValue.toString().toLowerCase().indexOf("проба") !== -1) {
            // Копируем только столбец A для теста
            var srcVal = srcSheet.GetRange("A" + r).GetValue();
            destSheet.GetRange("A" + destRow).SetValue(srcVal);
            destRow++;
            copiedCount++;
            // Записываем количество найденных на данный момент
            srcSheet.GetRange("Z11").SetValue("Найдено: " + copiedCount);
        }
    }

    // ---- Итог ----
    srcSheet.GetRange("Z6").SetValue("6. Скопировано строк: " + copiedCount);
    destSheet.GetRange("A1").SetValue("Скопировано строк: " + copiedCount);
    srcSheet.GetRange("Z1").SetValue("Готово!");
})();








· Второй макрос открывает файл, берёт данные с листа «Лист1» (или первого листа) и добавляет их в конец листа «текст».
· Оба макроса обрабатывают ошибки (например, отсутствие листа, отмена выбора файла).
