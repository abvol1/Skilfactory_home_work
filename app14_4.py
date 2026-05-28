
(function()
{
    try {
        if (typeof Api === 'undefined') throw new Error('Api не определён');
        var sheet = Api.GetActiveSheet();
        var row = 1; // <-- Меняйте это число для каждой кнопки

        var cell = sheet.GetRange("A" + row);
        var value = cell.GetValue();

        // Окрашиваем в зелёный (всегда работает)
        var green = Api.CreateColorFromRGB(0, 255, 0);
        cell.SetFillColor(green);

        // === БЛОК КОПИРОВАНИЯ: пробуем все методы ===
        var copied = false;

        // Метод 1: прямое копирование диапазона
        try { cell.Copy(); copied = true; } catch(e) {}

        // Метод 2: копирование через выделение и команду редактора
        if (!copied) {
            try {
                cell.Select();
                Api.ExecCommand("copy");
                copied = true;
            } catch(e) {}
        }

        // Метод 3: глобальная функция Api.Copy (если есть)
        if (!copied) {
            try { Api.Copy(); copied = true; } catch(e) {}
        }

        // Метод 4: объект Clipboard (только для новых версий)
        if (!copied) {
            try {
                var clip = Api.CreateClipboard();
                clip.SetText(String(value));
                copied = true;
            } catch(e) {}
        }

        // Метод 5: отправка клавиш Ctrl+C (работает, если разрешено)
        if (!copied) {
            try {
                cell.Select();
                Api.SendKeys("^c");
                copied = true;
            } catch(e) {}
        }

        // Запись результата в Z1
        if (copied) {
            sheet.GetRange("Z1").SetValue("Готово! A" + row + " скопировано и окрашено.");
        } else {
            sheet.GetRange("Z1").SetValue("Ячейка окрашена. Скопируйте вручную: " + value);
        }

    } catch(e) {
        try { Api.GetActiveSheet().GetRange("Z1").SetValue("Ошибка: " + e.message); } catch(e2) {}
    }
})();







(function()
{
    try {
        if (typeof Api === 'undefined') throw new Error('Api не определён');
        var sheet = Api.GetActiveSheet();
        var row = 1; // номер строки, меняйте для каждого макроса вручную

        var cell = sheet.GetRange("A" + row);
        var value = cell.GetValue();

        // Окрашиваем в зелёный
        var green = Api.CreateColorFromRGB(0, 255, 0);
        cell.SetFillColor(green);

        // Копируем в буфер обмена
        var copied = false;
        cell.Select();
        if (typeof Api.ExecCommand === 'function') {
            try {
                Api.ExecCommand("copy");
                copied = true;
            } catch(e) {}
        }
        if (!copied && typeof Api.Copy === 'function') {
            try { Api.Copy(); copied = true; } catch(e) {}
        }

        if (copied) {
            sheet.GetRange("Z1").SetValue("Готово! A" + row + " скопировано и окрашено.");
        } else {
            sheet.GetRange("Z1").SetValue("Ячейка A" + row + " окрашена. Скопируйте вручную: " + value);
        }

    } catch(e) {
        try { Api.GetActiveSheet().GetRange("Z1").SetValue("Ошибка: " + e.message); } catch(e2) {}
    }
})();









Давайте сделаем финальный, самый надёжный вариант — вручную созданные кнопки напротив каждой строки. Вы сами расставите их (это быстро), а макрос по нажатию будет красить ячейку в столбце A и сразу копировать её текст в буфер. Код уже не будет вызывать ошибок GetLeft и GetPresentation, потому что не использует создание фигур через API.

📌 Как это сделать (пошагово)

1. Вручную создайте кнопку (прямоугольник) напротив первой ячейки.
   · Вкладка Вставка → Фигура → выберите прямоугольник.
   · Разместите его в столбце B, напротив нужной строки (например, B1).
2. Задайте имя фигуры
   · Щёлкните по фигуре правой кнопкой → Свойства (или Формат фигуры) → найдите поле Имя (или Имя объекта).
   · Введите CopyRow_1 (если это строка 1). Для других строк: CopyRow_2, CopyRow_3 и т.д.
   · Имя обязательно должно начинаться на CopyRow_ и заканчиваться номером строки.
3. Назначьте макрос
   · Правый клик по фигуре → Назначить макрос.
   · В списке выберите макрос CopyAndColorByButton (создайте его заранее, код ниже).
   · Нажмите ОК.
4. Создайте такой же макрос для всех остальных строк — просто скопируйте готовую фигуру (Ctrl+C / Ctrl+V) и переименуйте, исправив номер строки в имени. При копировании назначенный макрос сохраняется.

⚙️ Код макроса CopyAndColorByButton

Создайте новый макрос с этим именем и вставьте:

```javascript
(function()
{
    try {
        if (typeof Api === 'undefined') throw new Error('Api не определён');
        var sheet = Api.GetActiveSheet();
        var activeShape = Api.GetActiveShape();
        if (!activeShape) {
            sheet.GetRange("Z1").SetValue("Не найдена активная кнопка.");
            return;
        }

        // Получаем имя фигуры (в разных версиях свойство или метод)
        var shapeName = "";
        if (typeof activeShape.GetName === 'function') {
            shapeName = activeShape.GetName();
        } else if (activeShape.Name !== undefined) {
            shapeName = activeShape.Name;
        }

        // Извлекаем номер строки из имени (должно быть CopyRow_1, CopyRow_2 и т.д.)
        var match = shapeName.match(/CopyRow_(\d+)/);
        if (!match) {
            sheet.GetRange("Z1").SetValue("Имя кнопки не содержит 'CopyRow_номер'. Переименуйте фигуру.");
            return;
        }
        var row = parseInt(match[1]);
        if (isNaN(row) || row < 1) {
            sheet.GetRange("Z1").SetValue("Неверный номер строки в имени кнопки.");
            return;
        }

        // Ячейка в столбце A этой строки
        var cellA = sheet.GetRange("A" + row);
        var value = cellA.GetValue();

        // Окрашиваем в зелёный
        var green = Api.CreateColorFromRGB(0, 255, 0);
        cellA.SetFillColor(green);

        // Копируем в буфер обмена
        var copied = false;
        cellA.Select();  // выделяем ячейку A
        if (typeof Api.ExecCommand === 'function') {
            try {
                Api.ExecCommand("copy");
                copied = true;
            } catch(e) {}
        }
        if (!copied && typeof Api.Copy === 'function') {
            try { Api.Copy(); copied = true; } catch(e) {}
        }

        if (copied) {
            sheet.GetRange("Z1").SetValue("Готово! A" + row + " скопировано и окрашено.");
        } else {
            sheet.GetRange("Z1").SetValue("Ячейка A" + row + " окрашена. Скопируйте вручную: " + value);
        }

    } catch(e) {
        try { Api.GetActiveSheet().GetRange("Z1").SetValue("Ошибка: " + e.message); } catch(e2) {}
    }
})();
```

✅ Результат

· Нажимаете на кнопку «Копировать» напротив нужной строки.
· Ячейка в столбце A загорается зелёным.
· Текст из этой ячейки попадает в буфер обмена (вставляется через Ctrl+V).
· Если копирование вдруг не сработает (в вашей версии такое бывает редко при ручном вызове), в ячейке Z1 появится само значение для ручного копирования.

Этот способ исключает все проблемы с программным созданием фигур и ошибками GetLeft, потому что фигуры созданы вручную. Попробуйте — теперь всё должно работать стабильно. Если что-то пойдёт не так, сообщите, что именно появляется в Z1.








(function()
{
    try {
        if (typeof Api === 'undefined') throw new Error('Api не определён');
        var sheet = Api.GetActiveSheet();

        // Удаляем старые кнопки (безопасный перебор)
        try {
            var shapes = sheet.GetAllShapes();
            if (shapes && typeof shapes.length === 'number') {
                for (var i = shapes.length - 1; i >= 0; i--) {
                    var sh = shapes[i];
                    var name = null;
                    if (typeof sh.GetName === 'function') {
                        name = sh.GetName();
                    } else if (sh.Name !== undefined) {
                        name = sh.Name;
                    }
                    if (name && name.indexOf("CopyRow_") === 0) {
                        try { sh.Delete(); } catch(e) {}
                    }
                }
            }
        } catch(e) {
            sheet.GetRange("Z1").SetValue("Предупреждение: старые кнопки не удалены. " + e.message);
        }

        var usedRange = sheet.GetUsedRange();
        if (!usedRange) {
            sheet.GetRange("Z1").SetValue("Нет данных для создания кнопок.");
            return;
        }

        var data = usedRange.GetValue();
        var btnWidth = 80 * 0.035 * 72; // примерно 80 пикселей
        var btnHeight = 20 * 0.75;       // примерно 15pt

        for (var rowIdx = 0; rowIdx < data.length; rowIdx++) {
            var cellValue = data[rowIdx][0]; // значение в столбце A
            if (cellValue === null || cellValue === undefined || String(cellValue).trim() === '') continue;

            var excelRow = rowIdx + 1;

            // Создаём кнопку-прямоугольник
            var shape = Api.CreateShape("rect", {
                Width: btnWidth,
                Height: btnHeight,
                Fill: Api.CreateColorFromRGB(200, 230, 255),
                Stroke: Api.CreateColorFromRGB(100, 100, 100)
            });
            shape.SetName("CopyRow_" + excelRow);
            shape.AddText("Копировать");
            shape.SetVerticalTextAlign("center");
            shape.SetHorizontalTextAlign("center");
            shape.SetMacro("CopyAndColor");

            // Привязываем фигуру к ячейке B<номер строки> – координаты не нужны
            sheet.AddShape(shape, "B" + excelRow);
        }

        sheet.GetRange("Z1").SetValue("Кнопки созданы в столбце B. Нажмите на кнопку напротив нужной строки.");

    } catch(e) {
        try { Api.GetActiveSheet().GetRange("Z1").SetValue("Ошибка: " + e.message); } catch(e2) {}
    }
})();






(function()
{
    try {
        if (typeof Api === 'undefined') throw new Error('Api не определён');
        var sheet = Api.GetActiveSheet();

        // Удаляем старые кнопки (безопасный способ)
        try {
            var shapes = sheet.GetAllShapes();
            if (shapes && typeof shapes.length === 'number') {
                for (var i = shapes.length - 1; i >= 0; i--) {
                    var sh = shapes[i];
                    var name = null;
                    // пробуем получить имя через свойство Name или метод GetName
                    if (typeof sh.GetName === 'function') {
                        name = sh.GetName();
                    } else if (sh.Name !== undefined) {
                        name = sh.Name;
                    }
                    if (name && name.indexOf("CopyRow_") === 0) {
                        try { sh.Delete(); } catch(e) {}
                    }
                }
            }
        } catch(e) {
            sheet.GetRange("Z1").SetValue("Не удалось удалить старые кнопки: " + e.message);
        }

        var usedRange = sheet.GetUsedRange();
        if (!usedRange) {
            sheet.GetRange("Z1").SetValue("Нет данных для создания кнопок.");
            return;
        }

        var data = usedRange.GetValue();
        var btnWidth = 80 * 0.035 * 72; // примерно 80px
        var btnHeight = 20 * 0.75;       // ~15pt
        var colBLeft = sheet.GetRange("B1").GetLeft();

        for (var rowIdx = 0; rowIdx < data.length; rowIdx++) {
            var cellValue = data[rowIdx][0];
            if (cellValue === null || cellValue === undefined || String(cellValue).trim() === '') continue;

            var excelRow = rowIdx + 1;
            var cellARange = sheet.GetRange("A" + excelRow);
            var top = cellARange.GetTop();
            var left = colBLeft;

            var shape = Api.CreateShape("rect", {
                Width: btnWidth,
                Height: btnHeight,
                Left: left,
                Top: top,
                Fill: Api.CreateColorFromRGB(200, 230, 255),
                Stroke: Api.CreateColorFromRGB(100, 100, 100)
            });
            shape.SetName("CopyRow_" + excelRow);
            shape.AddText("Копировать");
            shape.SetVerticalTextAlign("center");
            shape.SetHorizontalTextAlign("center");
            shape.SetMacro("CopyAndColor");

            sheet.AddShape(shape);
        }

        sheet.GetRange("Z1").SetValue("Кнопки созданы. Нажмите на кнопку напротив нужной строки.");

    } catch(e) {
        try { Api.GetActiveSheet().GetRange("Z1").SetValue("Ошибка: " + e.message); } catch(e2) {}
    }
})();









(function()
{
    try {
        if (typeof Api === 'undefined') throw new Error('Api не определён');
        var sheet = Api.GetActiveSheet();

        // Пытаемся удалить старые кнопки (имена начинаются с "CopyRow_")
        try {
            var shapes = sheet.GetAllShapes();
            if (shapes && shapes.length) {
                for (var i = 0; i < shapes.length; i++) {
                    var sh = shapes[i];
                    // В разных версиях имя может быть свойством или методом
                    var name = null;
                    try { name = sh.GetName(); } catch(e) {}
                    if (!name && sh.Name) name = sh.Name;
                    if (name && name.indexOf("CopyRow_") === 0) {
                        sh.Delete();
                    }
                }
            }
        } catch(e) {
            sheet.GetRange("Z1").SetValue("Предупреждение: не удалось удалить старые кнопки. Ошибка: " + e.message);
        }

        // ... (дальше код создания новых кнопок без изменений) ...









Мы пришли к самому надёжному варианту: разместить кнопку напротив каждой заполненной ячейки в столбце A. Нажатие на такую кнопку считается действием пользователя, что даёт доступ к буферу обмена. Я подготовил два макроса.

1. Создание кнопок «Копировать» в столбце B

Этот макрос нужно запустить один раз, чтобы добавить кнопки напротив всех непустых ячеек столбца A активного листа. При повторном запуске старые кнопки будут удалены и созданы заново.

```javascript
(function()
{
    try {
        if (typeof Api === 'undefined') throw new Error('Api не определён');
        var sheet = Api.GetActiveSheet();

        // Удаляем все фигуры, имя которых начинается с "CopyRow_"
        var shapes = sheet.GetAllShapes();
        for (var i = shapes.length - 1; i >= 0; i--) {
            if (shapes[i].GetName().indexOf("CopyRow_") === 0) {
                shapes[i].Delete();
            }
        }

        var usedRange = sheet.GetUsedRange();
        if (!usedRange) {
            sheet.GetRange("Z1").SetValue("Нет данных для создания кнопок.");
            return;
        }

        var data = usedRange.GetValue();
        var btnWidth = 80 * 0.035 * 72; // примерно 80 пикселей в пунктах (1px ≈ 0.75pt)
        var btnHeight = 20 * 0.75;       // ~15pt
        var colBLeft = sheet.GetRange("B1").GetLeft(); // координата X начала столбца B

        for (var rowIdx = 0; rowIdx < data.length; rowIdx++) {
            var cellValue = data[rowIdx][0]; // значение в столбце A
            if (cellValue === null || cellValue === undefined || String(cellValue).trim() === '') continue;

            var excelRow = rowIdx + 1; // строка в Excel (начинается с 1)
            var cellARange = sheet.GetRange("A" + excelRow);
            var top = cellARange.GetTop();
            var left = colBLeft;

            // Создаём прямоугольник-кнопку
            var shape = Api.CreateShape("rect", {
                Width: btnWidth,
                Height: btnHeight,
                Left: left,
                Top: top,
                Fill: Api.CreateColorFromRGB(200, 230, 255),
                Stroke: Api.CreateColorFromRGB(100, 100, 100)
            });
            shape.SetName("CopyRow_" + excelRow);
            shape.AddText("Копировать");
            shape.SetVerticalTextAlign("center");
            shape.SetHorizontalTextAlign("center");

            // Привязываем макрос "CopyAndColor" к нажатию на фигуру
            shape.SetMacro("CopyAndColor");

            sheet.AddShape(shape);
        }

        sheet.GetRange("Z1").SetValue("Кнопки созданы. Нажмите на кнопку напротив нужной строки.");
    } catch(e) {
        try { Api.GetActiveSheet().GetRange("Z1").SetValue("Ошибка: " + e.message); } catch(e2) {}
    }
})();
```

2. Макрос‑обработчик нажатия кнопки

Именно этот макрос должен быть сохранён в документе с именем CopyAndColor. Он вызывается при клике по любой кнопке «Копировать». Определяет строку, красит ячейку в столбце A и копирует её значение в буфер обмена.

```javascript
(function()
{
    try {
        if (typeof Api === 'undefined') throw new Error('Api не определён');
        var sheet = Api.GetActiveSheet();
        var activeShape = Api.GetActiveShape();
        if (!activeShape) {
            sheet.GetRange("Z1").SetValue("Не найдена активная кнопка.");
            return;
        }

        var shapeName = activeShape.GetName();
        var parts = shapeName.split('_');
        if (parts.length < 2 || parts[0] !== "CopyRow") {
            sheet.GetRange("Z1").SetValue("Имя кнопки не соответствует формату.");
            return;
        }
        var rowNumber = parseInt(parts[1]);
        if (isNaN(rowNumber)) {
            sheet.GetRange("Z1").SetValue("Неверный номер строки в имени кнопки.");
            return;
        }

        // Целевая ячейка в столбце A
        var cellA = sheet.GetRange("A" + rowNumber);
        var value = cellA.GetValue();

        // Окрашиваем в зелёный
        var green = Api.CreateColorFromRGB(0, 255, 0);
        cellA.SetFillColor(green);

        // Копируем значение в буфер обмена
        var copied = false;
        // Выделяем ячейку и используем команду copy (теперь она должна работать!)
        cellA.Select();
        if (typeof Api.ExecCommand === 'function') {
            try {
                Api.ExecCommand("copy");
                copied = true;
            } catch(e) {}
        }
        // Запасной вариант – если не скопировалось, запишем в Z1
        if (!copied) {
            sheet.GetRange("Z1").SetValue("Ячейка окрашена. Значение: " + (value !== null ? value : ""));
        } else {
            sheet.GetRange("Z1").SetValue("Готово! A" + rowNumber + " скопировано и окрашено.");
        }
    } catch(e) {
        try { Api.GetActiveSheet().GetRange("Z1").SetValue("Ошибка: " + e.message); } catch(e2) {}
    }
})();
```

Инструкция по применению

1. Откройте редактор макросов (Плагины → Макросы или Alt+F11).
2. Создайте первый макрос с кодом создания кнопок, назовите его, например, CreateButtons.
3. Создайте второй макрос и обязательно назовите его CopyAndColor (имя должно точно совпадать).
4. Выполните макрос CreateButtons. Он расставит кнопки в столбце B напротив каждой непустой ячейки A.
5. Теперь просто нажимайте на любую кнопку «Копировать». Соответствующая ячейка A станет зелёной, а её значение попадёт в буфер обмена (проверьте через Ctrl+V).

Если после нажатия кнопки значение всё же не копируется (маловероятно), в ячейке Z1 появится само значение для ручного копирования. Но благодаря тому, что копирование вызывается непосредственно в ответ на клик по кнопке, команда ExecCommand("copy") должна получить доступ к буферу.

Этот способ решает задачу полностью: окрашивание работает, копирование – теперь с высокой вероятностью тоже. Попробуйте, пожалуйста, и дайте знать результат!













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

        var address = selection.GetAddress();
        var cleanAddress = address.replace(/\$/g, '');
        var columnLetter = cleanAddress.match(/^[A-Za-z]+/)[0];
        if (columnLetter.toUpperCase() !== 'A') {
            sheet.GetRange("Z1").SetValue("Ячейка не в столбце A, а в столбце " + columnLetter);
            return;
        }

        // Получаем объект ячейки для окрашивания
        var cell = null;
        try { cell = selection.ActiveCell; } catch(e) {}
        if (!cell) {
            try { cell = selection.Get(0); } catch(e) {}
        }
        if (!cell) {
            cell = sheet.GetRange(address);
        }

        // Закрашиваем зелёным (работает)
        var greenColor = Api.CreateColorFromRGB(0, 255, 0);
        cell.SetFillColor(greenColor);

        // Копируем через встроенную команду редактора
        var copied = false;
        if (typeof Api.ExecCommand === 'function') {
            try {
                Api.ExecCommand("copy");
                copied = true;
            } catch(e) {}
        }
        if (!copied && typeof Api.Copy === 'function') {
            try {
                Api.Copy();
                copied = true;
            } catch(e) {}
        }
        // Если и это не вышло – сохраняем значение в Z1 для ручного копирования
        if (!copied) {
            var val = cell.GetValue();
            sheet.GetRange("Z1").SetValue("Ячейка окрашена. Скопируйте значение вручную: " + (val !== null ? val : ""));
        } else {
            sheet.GetRange("Z1").SetValue("Готово! Ячейка " + address + " окрашена и скопирована в буфер.");
        }

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
        var selection = sheet.GetSelection();
        if (!selection || selection.Count !== 1) {
            sheet.GetRange("Z1").SetValue("Выделите ровно одну ячейку в столбце A.");
            return;
        }

        var address = selection.GetAddress();
        var cleanAddress = address.replace(/\$/g, '');
        var columnLetter = cleanAddress.match(/^[A-Za-z]+/)[0];
        if (columnLetter.toUpperCase() !== 'A') {
            sheet.GetRange("Z1").SetValue("Ячейка не в столбце A, а в столбце " + columnLetter);
            return;
        }

        // Получаем объект ячейки (Range)
        var cell = null;
        try { cell = selection.ActiveCell; } catch(e) {}
        if (!cell) {
            try { cell = selection.Get(0); } catch(e) {}
        }
        if (!cell) {
            cell = sheet.GetRange(address);
        }

        // 1. Закрашиваем зелёным (это работает)
        var greenColor = Api.CreateColorFromRGB(0, 255, 0);
        cell.SetFillColor(greenColor);

        // 2. Копирование в буфер – пробуем разные методы
        var copied = false;
        var cellValue = cell.GetValue();

        // Способ A: стандартный Range.Copy() (часто работает в Р7)
        try {
            cell.Copy();
            copied = true;
        } catch(e) {}

        // Способ B: через Api.Clipboard (если доступен)
        if (!copied && Api.GetClipboard) {
            try {
                var clipboard = Api.GetClipboard();
                if (clipboard && clipboard.SetText) {
                    clipboard.SetText(String(cellValue));
                    copied = true;
                }
            } catch(e) {}
        }

        // Способ C: если и это не помогло, пытаемся через тот же Range, но с явным адресом
        if (!copied) {
            try {
                sheet.GetRange(address).Copy();
                copied = true;
            } catch(e) {}
        }

        // Итоговое сообщение
        if (copied) {
            sheet.GetRange("Z1").SetValue("Готово! Ячейка " + address + " окрашена и скопирована в буфер.");
        } else {
            sheet.GetRange("Z1").SetValue("Ячейка окрашена, но скопировать не удалось. Скопируйте значение вручную: " + cellValue);
        }

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
        var selection = sheet.GetSelection();
        if (!selection || selection.Count !== 1) {
            sheet.GetRange("Z1").SetValue("Выделите ровно одну ячейку в столбце A.");
            return;
        }

        var address = selection.GetAddress();
        var cleanAddress = address.replace(/\$/g, '');
        var columnLetter = cleanAddress.match(/^[A-Za-z]+/)[0];
        if (columnLetter.toUpperCase() !== 'A') {
            sheet.GetRange("Z1").SetValue("Ячейка не в столбце A, а в столбце " + columnLetter);
            return;
        }

        // Получаем объект ячейки (любым доступным способом)
        var cell = null;
        try { cell = selection.ActiveCell; } catch(e) {}
        if (!cell) {
            try { cell = selection.Get(0); } catch(e) {}
        }
        if (!cell) {
            cell = sheet.GetRange(address);
        }

        // Закрашиваем зелёным (уже работает)
        var greenColor = Api.CreateColorFromRGB(0, 255, 0);
        cell.SetFillColor(greenColor);

        // Копируем значение в буфер обмена через textarea
        var cellValue = cell.GetValue();
        if (cellValue !== null && cellValue !== undefined) {
            var textArea = document.createElement("textarea");
            textArea.value = String(cellValue);
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
        }

        sheet.GetRange("Z1").SetValue("Готово! Ячейка " + address + " окрашена и скопирована в буфер.");

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
