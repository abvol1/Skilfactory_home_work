

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Разбить по столбцу А</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 400px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h2 {
            margin-top: 0;
            color: #333;
        }
        p {
            color: #666;
            font-size: 14px;
        }
        button {
            background: #2b7b8c;
            color: white;
            border: none;
            padding: 10px 24px;
            font-size: 16px;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background: #1f5f6e;
        }
        #status {
            margin-top: 15px;
            padding: 10px;
            background: #f0f0f0;
            border-radius: 4px;
            font-size: 13px;
            color: #333;
            display: none;
        }
    </style>
</head>
<body>
<div class="container">
    <h2>📊 Разбить по столбцу А</h2>
    <p>Будут созданы отдельные листы для каждого уникального значения в столбце <strong>A</strong>.</p>
    <button id="runBtn">▶ Выполнить</button>
    <div id="status">Готово! Создано листов: <span id="count"></span></div>
</div>

<script>
    document.getElementById('runBtn').addEventListener('click', function() {
        var btn = this;
        btn.disabled = true;
        btn.textContent = 'Выполняется...';

        window.Asc.plugin.callCommand(function() {
            // ---- Весь код плагина (тот же, что был ранее) ----
            var srcSheet = Api.GetActiveSheet();
            var lastRow = 0;
            var maxRows = 5000;

            for (var i = 1; i <= maxRows; i++) {
                var val = srcSheet.GetRange("A" + i).GetValue();
                if (val !== undefined && val !== null && val !== "") {
                    lastRow = i;
                } else {
                    var empty = 0;
                    for (var j = i; j <= i + 4 && j <= maxRows; j++) {
                        if (!srcSheet.GetRange("A" + j).GetValue()) empty++;
                    }
                    if (empty >= 5) break;
                }
            }

            if (lastRow === 0) {
                srcSheet.GetRange("Z1").SetValue("Нет данных в столбце A");
                window.Asc.plugin.executeCommand("close", "");
                return;
            }

            var maxCols = 1;
            for (var c = 1; c <= 50; c++) {
                var colLetter = String.fromCharCode(64 + c);
                var val = srcSheet.GetRange(colLetter + "1").GetValue();
                if (val !== undefined && val !== null && val !== "") {
                    maxCols = c;
                }
            }

            var uniqueValues = [];
            var headerRow = 1;

            for (var r = 2; r <= lastRow; r++) {
                var val = srcSheet.GetRange("A" + r).GetValue();
                if (val && val.toString().trim() !== "") {
                    var key = val.toString().trim();
                    if (uniqueValues.indexOf(key) === -1) {
                        uniqueValues.push(key);
                    }
                }
            }

            if (uniqueValues.length === 0) {
                srcSheet.GetRange("Z1").SetValue("Нет уникальных значений");
                window.Asc.plugin.executeCommand("close", "");
                return;
            }

            for (var u = 0; u < uniqueValues.length; u++) {
                var currentValue = uniqueValues[u];
                var sheetName = currentValue;
                if (sheetName.length > 31) sheetName = sheetName.substring(0, 31);
                sheetName = sheetName.replace(/[\\\/\?\*\[\]]/g, '_');

                var destSheet = Api.GetSheet(sheetName);
                if (!destSheet) {
                    Api.AddSheet(sheetName);
                    destSheet = Api.GetSheet(sheetName);
                } else {
                    for (var clearR = 1; clearR <= 5000; clearR++) {
                        for (var clearC = 1; clearC <= maxCols; clearC++) {
                            var clearLetter = String.fromCharCode(64 + clearC);
                            destSheet.GetRange(clearLetter + clearR).SetValue("");
                        }
                    }
                }

                if (!destSheet) continue;

                for (var c = 1; c <= maxCols; c++) {
                    var colLetter = String.fromCharCode(64 + c);
                    var headerVal = srcSheet.GetRange(colLetter + headerRow).GetValue();
                    destSheet.GetRange(colLetter + "1").SetValue(headerVal);
                }

                var destRow = 2;
                for (var r = 2; r <= lastRow; r++) {
                    var val = srcSheet.GetRange("A" + r).GetValue();
                    if (val && val.toString().trim() === currentValue) {
                        for (var c = 1; c <= maxCols; c++) {
                            var colLetter = String.fromCharCode(64 + c);
                            var srcVal = srcSheet.GetRange(colLetter + r).GetValue();
                            destSheet.GetRange(colLetter + destRow).SetValue(srcVal);
                        }
                        destRow++;
                    }
                }
            }

            srcSheet.GetRange("Z1").SetValue("Готово! Создано листов: " + uniqueValues.length);

            // Передаём количество в интерфейс
            window.Asc.plugin.executeCommand("close", JSON.stringify({ count: uniqueValues.length }));
        }, false);

        // Обработчик результата (при закрытии окна)
        window.Asc.plugin.onClose = function(result) {
            if (result) {
                try {
                    var data = JSON.parse(result);
                    document.getElementById('count').textContent = data.count;
                    document.getElementById('status').style.display = 'block';
                } catch(e) {}
            }
            btn.disabled = false;
            btn.textContent = '▶ Выполнить';
        };
    });
</script>
</body>
</html>






<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Разбить по столбцу А</title>
    <script>
        window.Asc.plugin.init = function() {
            this.callCommand(function() {
                // -------------------------------------------------------------
                // ВЕСЬ КОД ПЛАГИНА (тот же, что был в pluginCode.js)
                // -------------------------------------------------------------
                var srcSheet = Api.GetActiveSheet();
                var lastRow = 0;
                var maxRows = 5000;

                // ---- 1. Определяем последнюю строку с данными ----
                for (var i = 1; i <= maxRows; i++) {
                    var val = srcSheet.GetRange("A" + i).GetValue();
                    if (val !== undefined && val !== null && val !== "") {
                        lastRow = i;
                    } else {
                        var empty = 0;
                        for (var j = i; j <= i + 4 && j <= maxRows; j++) {
                            if (!srcSheet.GetRange("A" + j).GetValue()) empty++;
                        }
                        if (empty >= 5) break;
                    }
                }

                if (lastRow === 0) {
                    srcSheet.GetRange("Z1").SetValue("Нет данных в столбце A");
                    window.Asc.plugin.executeCommand("close", "");
                    return;
                }

                // ---- 2. Определяем последний столбец с данными ----
                var maxCols = 1;
                for (var c = 1; c <= 50; c++) {
                    var colLetter = String.fromCharCode(64 + c);
                    var val = srcSheet.GetRange(colLetter + "1").GetValue();
                    if (val !== undefined && val !== null && val !== "") {
                        maxCols = c;
                    }
                }

                // ---- 3. Собираем уникальные значения из столбца A (пропускаем заголовок) ----
                var uniqueValues = [];
                var headerRow = 1;

                for (var r = 2; r <= lastRow; r++) {
                    var val = srcSheet.GetRange("A" + r).GetValue();
                    if (val && val.toString().trim() !== "") {
                        var key = val.toString().trim();
                        if (uniqueValues.indexOf(key) === -1) {
                            uniqueValues.push(key);
                        }
                    }
                }

                if (uniqueValues.length === 0) {
                    srcSheet.GetRange("Z1").SetValue("Нет уникальных значений в столбце A");
                    window.Asc.plugin.executeCommand("close", "");
                    return;
                }

                // ---- 4. Для каждого уникального значения создаём лист и копируем данные ----
                for (var u = 0; u < uniqueValues.length; u++) {
                    var currentValue = uniqueValues[u];
                    var sheetName = currentValue;
                    if (sheetName.length > 31) sheetName = sheetName.substring(0, 31);
                    // Заменяем недопустимые символы
                    sheetName = sheetName.replace(/[\\\/\?\*\[\]]/g, '_');

                    var destSheet = Api.GetSheet(sheetName);
                    if (!destSheet) {
                        Api.AddSheet(sheetName);
                        destSheet = Api.GetSheet(sheetName);
                    } else {
                        // Очищаем существующий лист
                        for (var clearR = 1; clearR <= 5000; clearR++) {
                            for (var clearC = 1; clearC <= maxCols; clearC++) {
                                var clearLetter = String.fromCharCode(64 + clearC);
                                destSheet.GetRange(clearLetter + clearR).SetValue("");
                            }
                        }
                    }

                    if (!destSheet) {
                        srcSheet.GetRange("Z1").SetValue("Ошибка создания листа: " + sheetName);
                        continue;
                    }

                    // Копируем заголовок (первая строка)
                    for (var c = 1; c <= maxCols; c++) {
                        var colLetter = String.fromCharCode(64 + c);
                        var headerVal = srcSheet.GetRange(colLetter + headerRow).GetValue();
                        destSheet.GetRange(colLetter + "1").SetValue(headerVal);
                    }

                    // Копируем строки, где в столбце A = currentValue
                    var destRow = 2;
                    for (var r = 2; r <= lastRow; r++) {
                        var val = srcSheet.GetRange("A" + r).GetValue();
                        if (val && val.toString().trim() === currentValue) {
                            for (var c = 1; c <= maxCols; c++) {
                                var colLetter = String.fromCharCode(64 + c);
                                var srcVal = srcSheet.GetRange(colLetter + r).GetValue();
                                destSheet.GetRange(colLetter + destRow).SetValue(srcVal);
                            }
                            destRow++;
                        }
                    }
                }

                // ---- 5. Итог ----
                srcSheet.GetRange("Z1").SetValue("Готово! Создано листов: " + uniqueValues.length);
                window.Asc.plugin.executeCommand("close", "");
            }, false);
        };
    </script>
</head>
<body>
</body>
</html>






Разработка плагина для Р7-Офис действительно отличается от создания макроса. Готовый плагин, который делает именно то, что вам нужно, — ниже.

📁 Структура плагина

Плагин для Р7-Офис — это папка с тремя обязательными файлами:

· config.json — конфигурация (имя, иконка, тип редактора).
· index.html — точка входа, подключающая базовые файлы.
· pluginCode.js — основной код на JavaScript.

Шаг 1. Создайте папку плагина

Создайте папку с названием, например, SplitByColumn.

Шаг 2. Создайте файл config.json

Этот файл сообщает Р7-Офис, как отображать ваш плагин.

```json
{
    "baseUrl": "",
    "guid": "split.by.column.plugin",
    "name": "Разбить по столбцу А",
    "variations": [
        {
            "description": "Создает листы по уникальным значениям в столбце А",
            "EditorsSupport": ["cell"],
            "icons": ["icon.png", "icon@2x.png"],
            "isVisual": false,
            "isViewer": false,
            "url": "index.html"
        }
    ]
}
```

· "EditorsSupport": ["cell"] указывает, что плагин работает только в табличном редакторе.
· "isVisual": false: плагин не открывает отдельное окно, а просто выполняет действие по нажатию кнопки.

Шаг 3. Создайте файл index.html

Это точка входа плагина.

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Разбить по столбцу А</title>
    <script src="pluginCode.js"></script>
</head>
<body>
</body>
</html>
```

Этот файл просто подключает основной скрипт pluginCode.js.

Шаг 4. Создайте файл pluginCode.js (основной код)

Это сердце плагина. Он содержит ту же логику, что и ваш рабочий макрос, но обернутую в структуру плагина.

```javascript
window.Asc.plugin.init = function () {
    this.callCommand(function() {
        var srcSheet = Api.GetActiveSheet();
        var lastRow = 0;
        var maxRows = 5000;

        // ---- 1. Определяем последнюю строку с данными ----
        for (var i = 1; i <= maxRows; i++) {
            var val = srcSheet.GetRange("A" + i).GetValue();
            if (val !== undefined && val !== null && val !== "") {
                lastRow = i;
            } else {
                var empty = 0;
                for (var j = i; j <= i + 4 && j <= maxRows; j++) {
                    if (!srcSheet.GetRange("A" + j).GetValue()) empty++;
                }
                if (empty >= 5) break;
            }
        }

        if (lastRow === 0) {
            srcSheet.GetRange("Z1").SetValue("Нет данных в столбце A");
            return;
        }

        // ---- 2. Определяем последний столбец с данными ----
        var maxCols = 1;
        for (var c = 1; c <= 50; c++) {
            var colLetter = String.fromCharCode(64 + c);
            var val = srcSheet.GetRange(colLetter + "1").GetValue();
            if (val !== undefined && val !== null && val !== "") {
                maxCols = c;
            }
        }

        // ---- 3. Собираем уникальные значения из столбца A (пропускаем заголовок) ----
        var uniqueValues = [];
        var headerRow = 1;

        for (var r = 2; r <= lastRow; r++) {
            var val = srcSheet.GetRange("A" + r).GetValue();
            if (val && val.toString().trim() !== "") {
                var key = val.toString().trim();
                if (uniqueValues.indexOf(key) === -1) {
                    uniqueValues.push(key);
                }
            }
        }

        if (uniqueValues.length === 0) {
            srcSheet.GetRange("Z1").SetValue("Нет уникальных значений в столбце A");
            return;
        }

        // ---- 4. Для каждого уникального значения создаём лист и копируем данные ----
        for (var u = 0; u < uniqueValues.length; u++) {
            var currentValue = uniqueValues[u];
            var sheetName = currentValue;
            if (sheetName.length > 31) sheetName = sheetName.substring(0, 31);

            // Заменяем недопустимые символы в имени листа
            sheetName = sheetName.replace(/[\\\/\?\*\[\]]/g, '_');

            var destSheet = Api.GetSheet(sheetName);
            if (!destSheet) {
                Api.AddSheet(sheetName);
                destSheet = Api.GetSheet(sheetName);
            } else {
                // Очищаем существующий лист
                for (var clearR = 1; clearR <= 5000; clearR++) {
                    for (var clearC = 1; clearC <= maxCols; clearC++) {
                        var clearLetter = String.fromCharCode(64 + clearC);
                        destSheet.GetRange(clearLetter + clearR).SetValue("");
                    }
                }
            }

            if (!destSheet) {
                srcSheet.GetRange("Z1").SetValue("Ошибка создания листа: " + sheetName);
                continue;
            }

            // Копируем заголовок (первая строка)
            for (var c = 1; c <= maxCols; c++) {
                var colLetter = String.fromCharCode(64 + c);
                var headerVal = srcSheet.GetRange(colLetter + headerRow).GetValue();
                destSheet.GetRange(colLetter + "1").SetValue(headerVal);
            }

            // Копируем строки, где в столбце A = currentValue
            var destRow = 2;
            for (var r = 2; r <= lastRow; r++) {
                var val = srcSheet.GetRange("A" + r).GetValue();
                if (val && val.toString().trim() === currentValue) {
                    for (var c = 1; c <= maxCols; c++) {
                        var colLetter = String.fromCharCode(64 + c);
                        var srcVal = srcSheet.GetRange(colLetter + r).GetValue();
                        destSheet.GetRange(colLetter + destRow).SetValue(srcVal);
                    }
                    destRow++;
                }
            }
        }

        // ---- 5. Итог ----
        srcSheet.GetRange("Z1").SetValue("Готово! Создано листов: " + uniqueValues.length);
    }, false);
};
```

🚀 Установка плагина

1. Упакуйте папку SplitByColumn в ZIP-архив.
2. Переименуйте расширение файла с .zip на .plugin.
3. В Р7-Офис откройте вкладку «Плагины» → «Настройки» → «Добавить плагин».
4. Выберите ваш файл SplitByColumn.plugin.

После установки на вкладке «Плагины» появится кнопка «Разбить по столбцу А». Её нажатие запустит весь процесс автоматически.

💡 Важные нюансы

· Имена листов: не могут быть длиннее 31 символа и содержать символы \ / ? * [ или ]. Код автоматически обрезает имя и заменяет их на _.
· Производительность: при большом количестве данных (10 000+ строк) плагин может работать несколько минут.
· Иконка: для красоты можете добавить в папку файлы icon.png и icon@2x.png.









(function() {
    var srcSheet = Api.GetActiveSheet();

    // ---- 1. Получаем или создаём лист "текст" ----
    var destSheet = Api.GetSheet("текст");
    if (!destSheet) {
        // Если лист не найден, создаём его с помощью AddSheet
        Api.AddSheet("текст");
        destSheet = Api.GetSheet("текст");
        if (!destSheet) {
            srcSheet.GetRange("Z1").SetValue("Ошибка: не удалось создать лист");
            return;
        }
        // Возвращаемся на исходный лист, чтобы продолжить работу
        srcSheet.Activate();
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

    // ---- 3. Копирование (столбцы A–T) ----
    var destRow = 1;
    var copiedCount = 0;
    var maxCols = 20;

    for (var r = 1; r <= lastRow; r++) {
        var cellValue = srcSheet.GetRange("A" + r).GetValue();
        if (cellValue && cellValue.toString().toLowerCase().indexOf("проба") !== -1) {
            for (var c = 1; c <= maxCols; c++) {
                var colLetter = String.fromCharCode(64 + c);
                var srcVal = srcSheet.GetRange(colLetter + r).GetValue();
                destSheet.GetRange(colLetter + destRow).SetValue(srcVal);
            }
            destRow++;
            copiedCount++;
        }
    }

    // ---- 4. Итог ----
    srcSheet.GetRange("Z1").SetValue("Готово! Скопировано: " + copiedCount);
})();









(function() {
    var srcSheet = Api.GetActiveSheet();

    // ---- 1. Проверяем лист "текст" ----
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
            // 5 пустых подряд – стоп
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

    // ---- 3. Копирование (столбцы A–T) ----
    var destRow = 1;
    var copiedCount = 0;
    var maxCols = 20; // Можно увеличить до 26 (A–Z) или больше

    for (var r = 1; r <= lastRow; r++) {
        var cellA = srcSheet.GetRange("A" + r);
        var cellValue = cellA.GetValue();

        if (cellValue && cellValue.toString().toLowerCase().indexOf("проба") !== -1) {
            // Копируем столбцы по буквам
            for (var c = 1; c <= maxCols; c++) {
                // Преобразуем номер столбца в букву (A=1, B=2, ...)
                var colLetter = String.fromCharCode(64 + c); // 65 = 'A'
                var srcAddr = colLetter + r;
                var destAddr = colLetter + destRow;

                var srcVal = srcSheet.GetRange(srcAddr).GetValue();
                destSheet.GetRange(destAddr).SetValue(srcVal);
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

    // ---- Получаем лист "текст" ----
    var destSheet = Api.GetSheet("текст");
    if (!destSheet) {
        srcSheet.GetRange("Z1").SetValue("Ошибка: создайте лист 'текст' вручную");
        return;
    }

    // ---- Определяем последнюю строку (до 5000) ----
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

    // ---- Копирование (столбцы 1..20) ----
    var destRow = 1;
    var copiedCount = 0;
    var maxCols = 20; // <- Увеличьте, если нужно больше столбцов

    for (var r = 1; r <= lastRow; r++) {
        var cellValue = srcSheet.GetRange("A" + r).GetValue();
        if (cellValue && cellValue.toString().toLowerCase().indexOf("проба") !== -1) {
            for (var c = 1; c <= maxCols; c++) {
                var srcVal = srcSheet.GetRange(r, c).GetValue();
                destSheet.GetRange(destRow, c).SetValue(srcVal);
            }
            destRow++;
            copiedCount++;
        }
    }

    // ---- Итог ----
    srcSheet.GetRange("Z1").SetValue("Готово! Скопировано строк: " + copiedCount);
})();








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
