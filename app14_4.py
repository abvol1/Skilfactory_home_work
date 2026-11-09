<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Установить макрос</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        #status { margin-top: 10px; color: green; }
    </style>
</head>
<body>
    <h3>Проверка разницы времени</h3>
    <p>Нажмите кнопку, чтобы добавить макрос в документ.</p>
    <button id="installBtn">Установить макрос</button>
    <div id="status"></div>

    <script>
        // Код макроса, который будет установлен
        var macroCode = `(function() {
    var sheet = Api.GetActiveSheet();
    var maxRows = 5000;
    var lastRow = 1;

    for (var i = 2; i <= maxRows; i++) {
        var v = sheet.GetRange("A" + i).GetValue();
        if (v !== undefined && v !== null && v !== "") {
            lastRow = i;
        } else {
            var empty = 0;
            for (var j = i; j <= i + 4 && j <= maxRows; j++) {
                if (!sheet.GetRange("A" + j).GetValue()) empty++;
            }
            if (empty >= 5) break;
        }
    }

    if (lastRow < 3) {
        sheet.GetRange("Z1").SetValue("Недостаточно данных");
        return;
    }

    function parseDate(str) {
        if (!str) return null;
        var s = str.toString().trim();
        var m = s.match(/^(\\d{4})-(\\d{2})-(\\d{2})[ T](\\d{2}):(\\d{2}):(\\d{2})/);
        if (!m) return null;
        return new Date(parseInt(m[1]), parseInt(m[2])-1, parseInt(m[3]), parseInt(m[4]), parseInt(m[5]), parseInt(m[6]));
    }

    var mismatches = 0;
    for (var r = 3; r <= lastRow; r++) {
        var prevDate = parseDate(sheet.GetRange("A" + (r-1)).GetValue());
        var currDate = parseDate(sheet.GetRange("A" + r).GetValue());
        var cVal = sheet.GetRange("C" + r).GetValue();
        
        if (!prevDate || !currDate) continue;
        
        var diffSec = Math.round((currDate - prevDate) / 1000);
        var expected = parseFloat(cVal);
        
        if (isNaN(expected) || diffSec !== expected) {
            mismatches++;
            for (var c = 1; c <= 20; c++) {
                var colLetter = String.fromCharCode(64 + c);
                sheet.GetRange(colLetter + r).SetFillColor(Api.CreateColorFromRGB(255, 200, 200));
            }
        }
    }
    sheet.GetRange("Z1").SetValue("Расхождений: " + mismatches);
})();`;

        document.getElementById('installBtn').addEventListener('click', function() {
            var status = document.getElementById('status');
            try {
                // Формируем объект для SetMacros
                var macrosData = {
                    "macrosArray": [
                        {
                            "name": "Проверка времени",
                            "value": macroCode
                        }
                    ],
                    "current": 1
                };
                
                // Вызываем метод установки макросов
                window.Asc.plugin.executeMethod("SetMacros", [macrosData], function() {
                    status.textContent = "Макрос установлен! Откройте 'Плагины' -> 'Макросы' и запустите 'Проверка времени'.";
                });
            } catch (e) {
                status.textContent = "Ошибка: " + e.message;
                status.style.color = "red";
            }
        });
    </script>
</body>
</html>













<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Проверка разницы времени</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
        .container { max-width: 450px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h2 { margin-top: 0; color: #333; font-size: 18px; }
        p { color: #666; font-size: 13px; line-height: 1.5; }
        button { background: #2b7b8c; color: white; border: none; padding: 10px 24px; font-size: 16px; border-radius: 4px; cursor: pointer; width: 100%; margin-top: 10px; }
        button:hover { background: #1f5f6e; }
        #status { margin-top: 15px; padding: 10px; background: #f0f0f0; border-radius: 4px; font-size: 13px; display: none; white-space: pre-wrap; }
        .ok { color: #2e7d32; }
        .err { color: #c62828; }
    </style>
</head>
<body>
<div class="container">
    <h2>⏱ Проверка разницы времени</h2>
    <p>Сравнивает разницу между строками в столбце <strong>A</strong> со значением в столбце <strong>C</strong>. Строки с расхождением закрашиваются красным.</p>
    <button id="runBtn">▶ Выполнить проверку</button>
    <div id="status"></div>
</div>

<script>
    document.getElementById('runBtn').addEventListener('click', function() {
        var btn = this;
        var status = document.getElementById('status');
        btn.disabled = true;
        btn.textContent = 'Выполняется...';
        status.style.display = 'block';
        status.textContent = 'Выполняется...';
        status.className = '';

        // Используем callCommand для выполнения в контексте документа
        window.Asc.plugin.callCommand(function() {
            var sheet = Api.GetActiveSheet();
            var maxRows = 5000;
            var lastRow = 1;

            // ---- 1. Определяем последнюю строку по столбцу A ----
            for (var i = 2; i <= maxRows; i++) {
                var v = sheet.GetRange("A" + i).GetValue();
                if (v !== undefined && v !== null && v !== "") {
                    lastRow = i;
                } else {
                    var empty = 0;
                    for (var j = i; j <= i + 4 && j <= maxRows; j++) {
                        if (!sheet.GetRange("A" + j).GetValue()) empty++;
                    }
                    if (empty >= 5) break;
                }
            }

            if (lastRow < 3) {
                sheet.GetRange("Z1").SetValue("Недостаточно данных (нужно минимум 3 строки)");
                window.Asc.plugin.executeCommand("close", JSON.stringify({error: "Мало данных"}));
                return;
            }

            // ---- 2. Функция парсинга даты ----
            function parseDate(str) {
                if (!str) return null;
                var s = str.toString().trim();
                var m = s.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})/);
                if (!m) return null;
                return new Date(
                    parseInt(m[1]), parseInt(m[2])-1, parseInt(m[3]),
                    parseInt(m[4]), parseInt(m[5]), parseInt(m[6])
                );
            }

            var mismatches = 0;
            var totalChecked = 0;

            // ---- 3. Проходим по строкам, начиная с 3-й ----
            for (var r = 3; r <= lastRow; r++) {
                var prevVal = sheet.GetRange("A" + (r-1)).GetValue();
                var currVal = sheet.GetRange("A" + r).GetValue();
                var cVal = sheet.GetRange("C" + r).GetValue();

                var prevDate = parseDate(prevVal);
                var currDate = parseDate(currVal);

                if (!prevDate || !currDate) continue;

                var diffSec = Math.round((currDate - prevDate) / 1000);
                var expected = parseFloat(cVal);
                totalChecked++;

                var isMismatch = false;
                if (isNaN(expected)) {
                    isMismatch = true;
                } else if (diffSec !== expected) {
                    isMismatch = true;
                }

                if (isMismatch) {
                    mismatches++;
                    // Закрашиваем строку (столбцы A..T)
                    for (var c = 1; c <= 20; c++) {
                        var colLetter = String.fromCharCode(64 + c);
                        var cell = sheet.GetRange(colLetter + r);
                        cell.SetFillColor(Api.CreateColorFromRGB(255, 200, 200));
                    }
                }
            }

            // ---- 4. Итог ----
            sheet.GetRange("Z1").SetValue("Проверено строк: " + totalChecked + ", расхождений: " + mismatches);
            window.Asc.plugin.executeCommand("close", JSON.stringify({
                total: totalChecked,
                mismatches: mismatches
            }));
        }, false);
    });

    // Обработчик закрытия (результат)
    window.Asc.plugin.onClose = function(result) {
        var btn = document.getElementById('runBtn');
        var status = document.getElementById('status');
        try {
            var data = JSON.parse(result);
            if (data.error) {
                status.textContent = '⚠️ ' + data.error;
                status.className = 'err';
            } else {
                status.textContent = '✅ Проверено строк: ' + data.total + '\n❌ Расхождений: ' + data.mismatches;
                status.className = data.mismatches > 0 ? 'err' : 'ok';
            }
        } catch(e) {
            status.textContent = 'Готово (результат: ' + result + ')';
        }
        btn.disabled = false;
        btn.textContent = '▶ Выполнить проверку';
    };
</script>
</body>
</html>











Понял задачу. Давайте разберём её формально, чтобы плагин работал именно так, как вы ожидаете.

---

📋 Формализация задачи

Дано:

· Столбец A — дата-время в формате YYYY-MM-DD HH:MM:SS (начиная со строки 2).
· Столбец C — некоторое числовое значение (количество секунд).
· Для каждой строки i (начиная с 3-й):
  · diff = A[i] - A[i-1] (разница в секундах между текущей и предыдущей строкой).
  · Сравниваем diff со значением C[i] (значение в столбце C текущей строки).
  · Если diff !== C[i] → закрашиваем строку (например, красным).

Пример:

Строка A C diff Совпадает?
2 2026-11-05 15:01:44 7 — —
3 2026-11-05 15:01:53 9 9 ✅ да
4 2026-11-05 15:02:01 6 8 ❌ нет → закрасить

---

⚠️ Важное уточнение

В вашем примере: 2026-11-05 15:01:53 минус 2026-11-05 15:01:44 = 9 секунд, а в C стоит 9 — совпадает. ✅

Но что если разница отрицательная или в C стоит не число? Плагин должен:

· Пропускать пустые строки.
· Если C[i] не число — считать расхождением (закрашивать).
· Если формат даты неверный — тоже считать расхождением.

---

🧩 Плагин (полный код)

📄 config.json

```json
{
    "baseUrl": "",
    "guid": "asc.{A1B2C3D4-1111-2222-3333-444455556666}",
    "name": "Проверка разницы времени",
    "variations": [
        {
            "description": "Сравнивает разницу времени в столбце A со значением в столбце C и закрашивает строки с расхождениями",
            "EditorsSupport": ["cell"],
            "icons": [],
            "isVisual": true,
            "isViewer": false,
            "url": "index.html"
        }
    ]
}
```

---

🖥️ index.html (весь код внутри)

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Проверка разницы времени</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
        .container { max-width: 450px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h2 { margin-top: 0; color: #333; font-size: 18px; }
        p { color: #666; font-size: 13px; line-height: 1.5; }
        button { background: #2b7b8c; color: white; border: none; padding: 10px 24px; font-size: 16px; border-radius: 4px; cursor: pointer; width: 100%; margin-top: 10px; }
        button:hover { background: #1f5f6e; }
        #status { margin-top: 15px; padding: 10px; background: #f0f0f0; border-radius: 4px; font-size: 13px; display: none; white-space: pre-wrap; }
        .ok { color: #2e7d32; }
        .err { color: #c62828; }
    </style>
</head>
<body>
<div class="container">
    <h2>⏱ Проверка разницы времени</h2>
    <p>Сравнивает разницу между строками в столбце <strong>A</strong> со значением в столбце <strong>C</strong>. Строки с расхождением закрашиваются красным.</p>
    <button id="runBtn">▶ Выполнить проверку</button>
    <div id="status"></div>
</div>

<script>
    // ===== Код макроса (выполняется внутри редактора, где Api доступен) =====
    var macroCode = `
(function() {
    var sheet = Api.GetActiveSheet();
    var maxRows = 5000;
    var lastRow = 1;

    // ---- 1. Определяем последнюю строку по столбцу A ----
    for (var i = 2; i <= maxRows; i++) {
        var v = sheet.GetRange("A" + i).GetValue();
        if (v !== undefined && v !== null && v !== "") {
            lastRow = i;
        } else {
            var empty = 0;
            for (var j = i; j <= i + 4 && j <= maxRows; j++) {
                if (!sheet.GetRange("A" + j).GetValue()) empty++;
            }
            if (empty >= 5) break;
        }
    }

    if (lastRow < 3) {
        sheet.GetRange("Z1").SetValue("Недостаточно данных (нужно минимум 3 строки)");
        window.Asc.plugin.executeCommand("close", JSON.stringify({error: "Мало данных"}));
        return;
    }

    // ---- 2. Функция парсинга даты формата YYYY-MM-DD HH:MM:SS ----
    function parseDate(str) {
        if (!str) return null;
        var s = str.toString().trim();
        // Поддерживаем форматы: YYYY-MM-DD HH:MM:SS или YYYY-MM-DDTHH:MM:SS
        var m = s.match(/^(\\d{4})-(\\d{2})-(\\d{2})[ T](\\d{2}):(\\d{2}):(\\d{2})/);
        if (!m) return null;
        return new Date(
            parseInt(m[1]), parseInt(m[2])-1, parseInt(m[3]),
            parseInt(m[4]), parseInt(m[5]), parseInt(m[6])
        );
    }

    var mismatches = 0;
    var totalChecked = 0;

    // ---- 3. Проходим по строкам, начиная с 3-й ----
    for (var r = 3; r <= lastRow; r++) {
        var prevVal = sheet.GetRange("A" + (r-1)).GetValue();
        var currVal = sheet.GetRange("A" + r).GetValue();
        var cVal = sheet.GetRange("C" + r).GetValue();

        var prevDate = parseDate(prevVal);
        var currDate = parseDate(currVal);

        // Если даты не парсятся — пропускаем или считаем расхождением
        if (!prevDate || !currDate) {
            continue;
        }

        var diffSec = Math.round((currDate - prevDate) / 1000);
        var expected = parseFloat(cVal);

        totalChecked++;

        var isMismatch = false;
        if (isNaN(expected)) {
            isMismatch = true; // в C не число
        } else if (diffSec !== expected) {
            isMismatch = true;
        }

        if (isMismatch) {
            mismatches++;
            // Закрашиваем всю строку (столбцы A..T)
            for (var c = 1; c <= 20; c++) {
                var colLetter = String.fromCharCode(64 + c);
                var cell = sheet.GetRange(colLetter + r);
                cell.SetFillColor(Api.CreateColorFromRGB(255, 200, 200)); // светло-красный
            }
        }
    }

    // ---- 4. Итог ----
    sheet.GetRange("Z1").SetValue("Проверено строк: " + totalChecked + ", расхождений: " + mismatches);
    window.Asc.plugin.executeCommand("close", JSON.stringify({
        total: totalChecked,
        mismatches: mismatches
    }));
})();
    `;

    // ===== Обработчик кнопки =====
    document.getElementById('runBtn').addEventListener('click', function() {
        var btn = this;
        var status = document.getElementById('status');
        btn.disabled = true;
        btn.textContent = 'Выполняется...';
        status.style.display = 'block';
        status.textContent = 'Выполняется...';
        status.className = '';

        window.Asc.plugin.executeCommand("macro", macroCode);

        window.Asc.plugin.onClose = function(result) {
            try {
                var data = JSON.parse(result);
                if (data.error) {
                    status.textContent = '⚠️ ' + data.error;
                    status.className = 'err';
                } else {
                    status.textContent = '✅ Проверено строк: ' + data.total + '\n❌ Расхождений: ' + data.mismatches;
                    status.className = data.mismatches > 0 ? 'err' : 'ok';
                }
            } catch(e) {
                status.textContent = 'Готово (результат: ' + result + ')';
            }
            btn.disabled = false;
            btn.textContent = '▶ Выполнить проверку';
        };
    });
</script>
</body>
</html>
```

---

🎨 Как работает закрашивание

· Цвет: светло-красный RGB(255, 200, 200).
· Метод: cell.SetFillColor(Api.CreateColorFromRGB(255, 200, 200)).
· Закрашиваются столбцы A–T (20 столбцов). Если нужно больше — увеличьте 20 в цикле for (var c = 1; c <= 20; c++).

---

⚙️ Настройка

Что нужно Как изменить
Другой цвет Измените 255, 200, 200 на нужный RGB.
Красить только ячейку A Уберите цикл for (var c...) и красьте только sheet.GetRange("A" + r).
Красить только ячейку C Аналогично — красьте sheet.GetRange("C" + r).
Больше столбцов Увеличьте 20 в цикле закрашивания.
Другой формат даты Отредактируйте регулярное выражение в parseDate.

---

📌 Важные нюансы

1. Формат даты — плагин ожидает YYYY-MM-DD HH:MM:SS (с пробелом или T между датой и временем). Если у вас другой формат — сообщите, адаптирую регулярное выражение.
2. Первая проверяемая строка — строка 3 (сравнивается со строкой 2). Строка 2 не проверяется, так как у неё нет предыдущей.
3. Если в C не число — строка считается расхождением и закрашивается.
4. Если дата не парсится — строка пропускается (можно изменить на «закрашивать» — скажите, если нужно).

---

🚀 Установка

1. Создайте папку TimeCheckPlugin.
2. Положите туда config.json и index.html.
3. Заархивируйте содержимое → переименуйте в .plugin.
4. В Р7-Офис: Плагины → Настройки → Добавить плагин.
5. Перезапустите Р7.

После нажатия кнопки:

· На листе в Z1 появится итог: «Проверено строк: X, расхождений: Y».
· Строки с расхождением будут закрашены светло-красным.
· В окне плагина отобразится результат.

---

Если формат даты у вас отличается (например, 05.11.2026 15:01:44 или 2026/11/05 15:01:44) — напишите, я поправлю регулярное выражение. Также уточните, нужно ли красить всю строку или только конкретные ячейки (A и C).















Отличная идея! Кнопка «📄 Характеристика» позволит сформировать красивый документ по конкретному сотруднику — с ФИО, должностью, оценками, квадратом, портретом, рисками и решением. Это удобно для печати или отправки руководителю.

Вот точечные изменения (4 шага):

---

Шаг 1. Добавьте кнопку в форму редактирования

Найдите в функции renderEditForm блок с кнопками (там, где поля ФИО, должность, метка). В самом низу формы, сразу после <div class="means" id="meansBox"></div>, добавьте:

```html
    <div class="row" style="margin-top:12px;">
      <button id="btnPrintCharacter" class="primary" style="padding:10px 18px;">📄 Сформировать характеристику</button>
    </div>
```

Итоговый блок в renderEditForm будет выглядеть так (конец):

```javascript
    <div class="means" id="meansBox"></div>

    <div class="row" style="margin-top:12px;">
      <button id="btnPrintCharacter" class="primary" style="padding:10px 18px;">📄 Сформировать характеристику</button>
    </div>
  `;
  updateMeans();
```

---

Шаг 2. Добавьте обработчик кнопки

Сразу после updateMeans(); в renderEditForm (перед box.querySelectorAll('input[type=number]')...) добавьте:

```javascript
  // Обработчик кнопки "Характеристика"
  const printBtn = $('#btnPrintCharacter');
  if (printBtn) {
    printBtn.addEventListener('click', () => {
      printCharacteristic(emp);
    });
  }
```

---

Шаг 3. Добавьте саму функцию printCharacteristic

Вставьте эту функцию в любое место скрипта (например, после renderEditForm):

```javascript
/* ======================= ПЕЧАТЬ ХАРАКТЕРИСТИКИ ======================= */
function printCharacteristic(emp) {
  const p = emp.p;
  const m1 = avg2(p[0], p[1]);
  const m2 = avg2(p[2], p[3]);
  const info = squareInfo(m1, m2);
  const prof = SQUARE_PROFILES[info.num] || {};

  // Формируем красивую HTML-страницу для печати
  const html = `
    <!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="UTF-8">
      <title>Характеристика — ${escapeHtml(emp.fio)}</title>
      <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 30px; color: #222; line-height: 1.5; }
        h1 { font-size: 22px; margin: 0 0 4px 0; }
        h2 { font-size: 14px; color: #666; font-weight: 400; margin: 0 0 20px 0; }
        .section { margin-bottom: 20px; }
        .section h3 { font-size: 14px; text-transform: uppercase; color: #2563eb; margin: 0 0 8px 0; border-bottom: 2px solid #2563eb; padding-bottom: 4px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 12px; }
        th, td { border: 1px solid #ddd; padding: 8px 10px; text-align: left; font-size: 13px; }
        th { background: #f5f6f8; width: 40%; }
        .badge { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }
        .badge.green { background: #d9f2d9; color: #166534; }
        .badge.yellow{ background: #fff4cc; color: #92400e; }
        .badge.red   { background: #fde2e1; color: #991b1b; }
        .badge.dark-green { background: #c1d6c6; color: #2f4a37; }
        .badge.dark-red   { background: #d9b3b3; color: #6b2b2b; }
        .badge.gray  { background: #f3f4f6; color: #4b5563; }
        .portrait { background: #f9fafb; border-left: 4px solid #2563eb; padding: 12px 16px; font-style: italic; margin-bottom: 12px; }
        .footer { margin-top: 40px; font-size: 11px; color: #999; text-align: center; }
        @media print {
          body { margin: 15mm; }
          button { display: none; }
        }
        .no-print { text-align: center; margin-top: 20px; }
        .no-print button { padding: 10px 24px; font-size: 14px; border-radius: 8px; border: 1px solid #2563eb; background: #2563eb; color: white; cursor: pointer; }
      </style>
    </head>
    <body>
      <h1>Характеристика сотрудника</h1>
      <h2>Сформировано: ${new Date().toLocaleDateString('ru-RU')}</h2>

      <div class="section">
        <h3>Общие сведения</h3>
        <table>
          <tr><th>ФИО</th><td>${escapeHtml(emp.fio)}</td></tr>
          <tr><th>Должность</th><td>${escapeHtml(emp.position || '—')}</td></tr>
          <tr><th>Отдел</th><td>${escapeHtml(emp.dept || '—')}</td></tr>
        </table>
      </div>

      <div class="section">
        <h3>Оценки</h3>
        <table>
          <tr><th>Ср. продуктивность</th><td><b>${m1 || '—'}</b></td></tr>
          <tr><th>Ср. потенциал</th><td><b>${m2 || '—'}</b></td></tr>
          <tr><th>Квадрат</th><td><span class="badge ${info.color}">${info.title}</span></td></tr>
        </table>
      </div>

      <div class="section">
        <h3>Управленческий портрет</h3>
        <div class="portrait">${escapeHtml(prof.portrait || '—')}</div>
      </div>

      <div class="section">
        <h3>Риски</h3>
        <p>${escapeHtml(prof.risks || '—')}</p>
      </div>

      <div class="section">
        <h3>Рекомендуемое управленческое решение</h3>
        <p>${escapeHtml(prof.decision || '—')}</p>
      </div>

      <div class="no-print">
        <button onclick="window.print()">🖨 Печать / Сохранить в PDF</button>
      </div>

      <div class="footer">
        Документ сформирован автоматически в системе оценки персонала.
      </div>
    </body>
    </html>
  `;

  // Открываем в новом окне
  const win = window.open('', '_blank');
  if (!win) {
    alert('Браузер заблокировал всплывающее окно. Разрешите всплывающие окна для этого сайта.');
    return;
  }
  win.document.write(html);
  win.document.close();
}
```

---

Шаг 4. Проверка

1. Откройте файл в браузере, загрузите .xlsx.
2. Кликните по любому сотруднику в таблице — откроется форма.
3. Внизу формы появится синяя кнопка «📄 Сформировать характеристику».
4. Нажмите её — откроется новое окно с готовой характеристикой:
   · ФИО, должность, отдел
   · Средние оценки, квадрат
   · Портрет (описание из справочника)
   · Риски
   · Рекомендуемое решение
5. В открывшемся окне можно нажать «🖨 Печать / Сохранить в PDF» — браузер предложит распечатать или сохранить как PDF.

---

Что можно улучшить (по желанию)

· Добавить логотип компании — вставьте <img src="logo.png" ...> в <body> HTML-шаблона.
· Добавить подпись руководителя — внизу добавьте <br><br>_______________ / ________________.
· Поменять цвета под корпоративный стиль — измените #2563eb на ваш фирменный цвет.
· Добавить ФИО руководителя — если он есть в форме оценки, можно передать его в printCharacteristic(emp, manager).

Если нужно — могу доработать: добавить логотип, блок с подписями или сделать кнопку «Скачать в Word» (.docx).












Чтобы под картой 9 квадратов появилась легенда по цветам фамилий (🔴 Красный, 🟡 Жёлтый, 🟢 Зелёный), нужно добавить всего один блок HTML и немного подправить CSS. Вот точечные изменения:

Шаг 1. Добавьте CSS для легенды цветов

В блоке <style> найдите классы .legend (они уже есть для цветов квадратов) и сразу после них добавьте:

```css
  /* Легенда цветов фамилий */
  .name-legend {
    display: flex;
    justify-content: center;
    gap: 24px;
    margin-top: 12px;
    font-size: 13px;
    color: #333;
    flex-wrap: wrap;
  }
  .name-legend .item {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .name-legend .dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
  }
  .name-legend .dot.red { background: #b91c1c; }
  .name-legend .dot.yellow { background: #b45309; }
  .name-legend .dot.green { background: #15803d; }
```

Шаг 2. Добавьте HTML-блок под картой

Найдите в HTML блок с картой 9 квадратов:

```html
  <div class="panel">
    <h3 id="gridTitle" style="margin-top:0; text-align:center;">Карта 9 квадратов (текущий отдел)</h3>
    <div class="grid-wrap" id="grid9"></div>
  </div>
```

Добавьте внутрь этого panel (после <div class="grid-wrap" id="grid9"></div>) новый блок:

```html
  <div class="panel">
    <h3 id="gridTitle" style="margin-top:0; text-align:center;">Карта 9 квадратов (текущий отдел)</h3>
    <div class="grid-wrap" id="grid9"></div>
    
    <!-- ЛЕГЕНДА ЦВЕТОВ ФАМИЛИЙ -->
    <div class="name-legend">
      <div class="item"><span class="dot red"></span> Красный — требует внимания</div>
      <div class="item"><span class="dot yellow"></span> Жёлтый — в процессе</div>
      <div class="item"><span class="dot green"></span> Зелёный — всё отлично</div>
    </div>
    <!-- КОНЕЦ ЛЕГЕНДЫ -->
  </div>
```

Шаг 3. (Опционально) Настроить текст подписей

Текст в легенде (например, «Красный — требует внимания») вы можете изменить на любой свой. Главное — сохранить структуру: <div class="item"><span class="dot red"></span> Ваш текст</div>.

Итог

Под картой 9 квадратов появится строка с тремя цветными кружками и пояснениями:

· 🔴 Красный — ...
· 🟡 Жёлтый — ...
· 🟢 Зелёный — ...

Эта легенда будет видна на всех вкладках отделов (и «Все сотрудники» тоже), потому что она находится внутри блока #deptView, который скрывается только при переходе в «Справочник».




















<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Оценка сотрудников — 9-box grid</title>
<script src="xlsx.full.min.js"></script>
<style>
  :root { --border:#d0d5dd; --accent:#2563eb; }
  * { box-sizing: border-box; }
  body { font-family: system-ui, Segoe UI, Arial, sans-serif; margin:0; padding:20px; background:#f5f6f8; color:#222; }
  h1 { font-size:20px; margin:0 0 12px; }
  .panel { background:#fff; border:1px solid var(--border); border-radius:10px; padding:16px; margin-bottom:14px; }
  .row { display:flex; gap:12px; flex-wrap:wrap; align-items:center; }
  button { padding:8px 14px; border:1px solid var(--border); background:#fff; border-radius:8px; cursor:pointer; font-size:14px; }
  button:hover { border-color:var(--accent); color:var(--accent); }
  button.active { background:var(--accent); color:#fff; border-color:var(--accent); }
  button.primary { background:#2563eb; color:#fff; border-color:#2563eb; }
  button:disabled { opacity:.5; cursor:default; }
  table { width:100%; border-collapse:collapse; }
  th, td { border:1px solid var(--border); padding:6px 8px; text-align:center; font-size:14px; }
  th { background:#f0f2f5; }
  td.name { text-align:left; font-weight:400; cursor:pointer; }
  td.name:hover { background:#eef4ff; }
  tr.selected td { background:#e0ecff; }
  input[type=number] { width:56px; padding:4px; text-align:center; border:1px solid var(--border); border-radius:6px; }
  input[type=text].fio { width:200px; padding:6px; border:1px solid var(--border); border-radius:6px; }
  input[type=text].pos { width:200px; padding:6px; border:1px solid var(--border); border-radius:6px; }

  /* Портрет в форме */
  textarea.portrait {
    width:100%;
    padding:10px;
    border:1px solid var(--border);
    border-radius:6px;
    min-height:80px;
    resize:vertical;
    font-family: ui-monospace, Consolas, monospace;
    font-size:12px;
    line-height:1.5;
    background:#f9fafb;
    white-space:pre-wrap;
    overflow-y:auto;
  }

  /* Карта 9 квадратов (увеличена и по центру) */
  .grid-wrap {
    display:grid;
    grid-template-columns: repeat(3, 1fr);
    gap:12px;
    max-width: 900px;
    margin: 0 auto;
  }

  .cell {
    position: relative;
    border:1px solid var(--border);
    border-radius:12px;
    padding:14px;
    min-height:130px;
    cursor: help;
    transition: transform 0.1s;
  }
  .cell:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

  .cell h4 { margin:0 0 4px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:16px; font-weight:700; color:#1f2937; margin:2px 0 8px; }
  .cell ul { margin:0; padding-left:0; list-style:none; font-size:13px; }
  .cell ul li { margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }

  /* Цвета */
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }
  .cell.dark-green { background:#c1d6c6; border-color:#5c7a64; }
  .cell.dark-red   { background:#d9b3b3; border-color:#8b4545; }

  /* Легенда */
  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:16px; font-size:13px; color:#333; width:100%; justify-content: center; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }
  .legend .swatch.dark-green{ background:#c1d6c6; border-color:#5c7a64; }
  .legend .swatch.dark-red{ background:#d9b3b3; border-color:#8b4545; }

  /* Бейджи */
  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.dark-green { background:#c1d6c6; color:#2f4a37; }
  .badge.dark-red   { background:#d9b3b3; color:#6b2b2b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

  /* Всплывающая подсказка */
  #tooltip {
    position: fixed; background: #1f2937; color: #fff; padding: 12px; border-radius: 8px;
    font-size: 12px; max-width: 320px; line-height: 1.5; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    pointer-events: none; opacity: 0; transition: opacity 0.15s; z-index: 1000; display: none;
  }
  #tooltip.active { opacity: 1; display: block; }
  #tooltip h5 { margin: 0 0 6px 0; font-size: 14px; color: #fff; }
  #tooltip p { margin: 0 0 8px 0; }
  #tooltip .label { color: #9ca3af; font-weight: 600; display: block; margin-bottom: 2px;}

  .hint { color:#666; font-size:13px; }
  .status { font-size:13px; color:#166534; }
  .del { color:#b91c1c; cursor:pointer; font-size:12px; }
  .means { font-size:14px; margin:6px 0; }
  .form-group { margin-bottom: 12px; }
  .form-group label { display:block; font-weight:600; margin-bottom:4px; font-size:13px; color:#475467; }
  .debug { background:#f8f9fa; border:1px solid #ddd; padding:8px; font-size:12px; font-family:monospace; color:#333; max-height:200px; overflow:auto; margin-top:8px; display:none; white-space:pre-wrap; }

  .ref-section { margin-bottom:24px; }
  .ref-title { font-size:16px; font-weight:700; color:#1f2937; margin:0 0 8px; padding:8px 12px; background:#e0ecff; border-left:4px solid var(--accent); border-radius:4px; }
  .ref-table { width:100%; border-collapse:collapse; }
  .ref-table th { background:#f0f2f5; text-align:left; padding:8px 10px; font-size:13px; }
  .ref-table td { text-align:left; vertical-align:top; padding:10px; font-size:13px; line-height:1.4; }
  .ref-table td:first-child { font-weight:600; width:180px; color:#1f2937; }
  .ref-level-1 { background:#fef2f2; }
  .ref-level-2 { background:#fefce8; }
  .ref-level-3 { background:#f0fdf4; }
</style>
</head>
<body>

<h1>Оценка сотрудников — 9-box grid</h1>

<div class="panel">
  <div class="row">
    <input type="file" id="fileInput" accept=".xlsx,.xls">
    <button id="btnSave" class="primary" disabled>💾 Сохранить</button>
    <button id="btnAdd" disabled>➕ Добавить сотрудника</button>
    <button id="btnDebug" style="font-size:12px;">🐞 Диагностика</button>
    <span id="status" class="status"></span>
  </div>
  <div id="debugBox" class="debug"></div>
</div>

<div class="panel">
  <div class="row" id="deptButtons">
    <button data-dept="Кредиты ФЛ" disabled>👤Кредиты ФЛ</button>
    <button data-dept="Кредиты ЮЛ" disabled>👤Кредиты ЮЛ</button>
    <button data-dept="Транзакт" disabled>👤Транзакт</button>
    <button data-dept="Все" disabled>👥 Все сотрудники ЦЗО</button> <!-- НОВАЯ КНОПКА -->
    <button data-dept="справочник" disabled>📖 Справочник</button>
  </div>
</div>

<div id="deptView">
  <div class="panel">
    <h3 style="margin-top:0">🙋🏻‍♂️ Сотрудники отдела</h3>
    <div style="overflow-x:auto;">
      <table id="empTable">
        <thead>
          <tr>
            <th>ФИО</th><th>Отдел</th><th>Должность</th><th id="th_p1">Дедлайн ЗОД</th><th id="th_p2">Качество ЗОД</th>
            <th id="th_p4">Новаторство</th><th id="th_p5">Командность</th>
            <th>Ср. Прд.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th></th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <div class="panel">
    <h3 id="gridTitle" style="margin-top:0; text-align:center;">Карта 9 квадратов (текущий отдел)</h3>
    <div class="grid-wrap" id="grid9"></div>
  </div>

  <div class="panel">
    <h3 style="margin-top:0">Редактирование сотрудника</h3>
    <div id="editForm" class="hint">Выберите сотрудника в таблице.</div>
  </div>
</div>

<div id="refView" style="display:none;">
  <div class="panel">
    <h3 style="margin-top:0">📖 Расширенный справочник критериев и показателей</h3>
    <div id="refContent"></div>
  </div>
</div>

<!-- Тултип -->
<div id="tooltip">
  <h5 id="tt-title"></h5>
  <p><span class="label">Портрет:</span> <span id="tt-portrait"></span></p>
  <p><span class="label">Риски:</span> <span id="tt-risks"></span></p>
  <p><span class="label">Решение:</span> <span id="tt-decision"></span></p>
</div>

<script>
/* ======================= КОНСТАНТЫ ======================= */
let COL_FIO = 1;
let COL_POS = 2;
let COLS_PERF = [3,4];
let COL_AVG_PERF = 5;
let COLS_POT  = [6,7];
let COL_AVG_POT  = 8;
let COL_SQUARE   = 9;
let COL_PORTRAIT = 10;

const DEPTS = ['Кредиты ФЛ', 'Кредиты ЮЛ', 'Транзакт'];

let SQUARE_NAMES = {
  1: '1. Якорь',
  2: '2. Пассажир',
  3: '3. Хранители традиций',
  4: '4. Улитки',
  5: '5. Рабочие муравьи',
  6: '6. Пчелы-труженицы',
  7: '7. Фантазеры',
  8: '8. Самородки',
  9: '9. Мушкетеры'
};

let PERF_NAMES = ['Дедлайн ЗОД', 'Качество ЗОД'];
let POT_NAMES = ['Новаторство', 'Командность'];

// Профили: короткий портрет (для таблицы), подробный (для тултипа), риски, решения
const SQUARE_PROFILES = {
  1: {
    short: 'Самый тяжелый случай. ',
    portrait: 'Баланс стабильно завален, дедлайн 12:00 сорван, ошибок куча. При этом учиться не хотят, на любые замечания отвечают агрессией или токсичным нытьем: «За такую зарплату скажите спасибо, что вообще прихожу».',
    risks: 'Тянут весь отдел на дно, демотивируют абсолютно всех вокруг.',
    decision: 'План повышения эффективности (испытательный срок) на 3–4 недели. Четко под подпись: «Вот чек-лист. Сдача до 12:00. Максимум 2 ошибки за месяц. Если не выполняешь — мы расстаемся». В вашей ситуации их увольнение — это благо: на их оклад можно догрузить или удержать «Мушкетеров».'
  },
  2: {
    short: 'Сотрудники, которые ментально уже уволились.',
    portrait: 'Делают необходимый минимум, чтобы не уволили прямо сегодня. Шаг влево, шаг вправо — отказ. Никаких идей, полная апатия.',
    risks: 'Заражают коллектив своим пофигизмом («А зачем напрягаться за эти деньги?»). При малейшем увеличении объемов завалят дедлайн.',
    decision: 'Прямой разговор по душам. «Я вижу, что ты выполняешь норму, но огонь пропал. Что происходит? Ты устал от бэк-офиса? Давай определимся, как мы работаем дальше, потому что мне нужна включенность в процесс закрытия».'
  },
  3: {
    short: 'Мега-опытные «зубры».',
    portrait: 'Ручную проверку знают наизусть, баланс у них всегда идеален. Но потенциал нулевой: любые изменения в софте или чек-листах встречают в штыки («Мы 10 лет так проверяли, зачем вы придумываете ерунду?!»).',
    risks: 'Могут тормозить автоматизацию отдела и ворчанием демотивировать новичков.',
    decision: 'Встреча-уважение. Не пытаться их переделать. Сказать: «Вы наш главный щит от ошибок, ваш опыт бесценен». При внедрении нового контроля просить их стать «главными критиками»: «Посмотрите своим опытным взглядом, где в этой новой схеме могут быть слабые места?» (это снизит их сопротивление).'
  },
  4: {
    short: 'Стараются, не бунтуют, но работают очень медленно.',
    portrait: 'До 12:00 вечно не успевают, из-за спешки в последний момент начинают совершать глупые ошибки. При этом готовы учиться, но темп мышления/работы не позволяет ускориться.',
    risks: 'Будут постоянно тянуть время закрытия дня всего филиала.',
    decision: 'Разбор хронометража. Сесть вместе и посмотреть, на каких именно пунктах чек-листа «Улитка» зависает. Возможно, закрепить за ней на неделю «Пчелу-труженицу», чтобы та показала свои лайфхаки по скорости.'
  },
  5: {
    short: 'Костяк бэк-офиса.',
    portrait: 'Работают стабильно, баланс сдают вовремя в 95% случаев, ошибки редкие. Чужие идеи принимают, работают строго по инструкции.',
    risks: 'Завязнуть в рутине, устать от монотонности и начать потихоньку снижать показатели до уровня «Пассажиров».',
    decision: 'Плановая беседа-сверка. Спросить: «Как дела? На каком этапе чек-листа чаще всего спотыкаешься? Какая помощь нужна от меня, чтобы закрываться еще легче?»Оказывать поддержку.'
  },
  6: {
    short: 'Супер-надежные исполнители с хорошей гибкостью.',
    portrait: 'До 12:00 всё закрывают идеально. Сами новые макросы не пишут, но если «Мушкетеры» придумали новую Excel-таблицу для контроля — «Пчелы» первыми без ворчания внедряют её в свою работу.',
    risks: 'Относиться к ним как к должному и забывать хвалить. Без поддержки они могут загрустить и снизить планку.',
    decision: 'Встреча-благодарность. Закрепить их стабильность, похвалить за легкую адаптацию к изменениям: «Нам очень ценно, что ты так быстро подхватываешь новые правила».'
  },
  7: {
    short: 'Активные сотрудники, но регулярно косячат.',
    portrait: 'Очень активные сотрудники, постоянно фонтанируют идеями: «А давайте всё переделаем!». Но при этом сами регулярно косячат в балансе и сдают его после 12:00, потому что отвлекаются от чек-листа на свои «воздушные замки».',
    risks: 'Могут дезорганизовать работу отдела своими бесконечными разговорами об улучшениях при полном отсутствии личного результата.',
    decision: 'Жесткое заземление. «Твои идеи классные, но давай договоримся: сначала мы выходим на 100% сдачу баланса до 12:00 без ошибок в течение месяца. Как только подтянешь базу — мы сядем обсуждать твои предложения».'
  },
  8: {
    short: 'Генераторы идей с горящими глазами.',
    portrait: 'Предлагают отличные инструменты контроля, но в текущей рутине из-за невнимательности могут сдать баланс в 11:58 или допустить пару мелких ошибок.',
    risks: 'Если забивать их идеи и заставлять только механически кликать по чек-листу, они потеряют интерес, перестанут предлагать улучшения и скатятся в «Пассажиров».',
    decision: 'Направить их потенциал на исправление их же продуктивности. «У тебя отличные идеи, давай ты применишь свой инструмент контроля, чтобы у тебя самого было 0 ошибок в балансе?»'
  },
  9: {
    short: 'Главная элита.',
    portrait: 'Баланс сдают до 12:00 без единой ошибки. Постоянно предлагают, как автоматизировать ручную проверку, пишут макросы, оптимизируют чек-листы.',
    risks: 'Поскольку должностей и прибавок нет, им быстро станет скучно перемалывать рутину. Они уйдут туда, где платят больше.',
    decision: ' Сказать честно: «Я вижу твой уровень, ты перерос рутину». Вовлечь в проектную работу — дать им задачу возглавить мини-автоматизацию процесса. Сделать наставниками.'
  }
};

let referenceData = null;

// ИСПРАВЛЕННЫЙ РАСЧЕТ (делим на 2)
const avg2 = (a,b) => {
  const n1 = Number(a) || 0;
  const n2 = Number(b) || 0;
  if (a === '' && b === '') return 0;
  return +((n1 + n2) / 2).toFixed(2);
};

function squareInfoForLevels(x, y){
  const map = {
    high: { low:['yellow',     7], mid:['green',        8], high:['dark-green', 9] },
    mid:  { low:['red',        4], mid:['yellow',       5], high:['green',       6] },
    low:  { low:['dark-red',   1], mid:['red',          2], high:['yellow',      3] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

/* ======================= СОСТОЯНИЕ ======================= */
const state = {
  workbook: null,
  fileName: 'employees.xlsx',
  fileHandle: null,
  currentDept: null,
  employees: {},
  selectedIndex: null,
};

DEPTS.forEach(d => state.employees[d] = []);

const $ = sel => document.querySelector(sel);

function toNum(v){
  if (v === '' || v === null || v === undefined) return '';
  const n = Number(String(v).replace(',', '.'));
  if (isNaN(n)) return '';
  return Math.min(3, Math.max(1, Math.round(n)));
}
function escapeHtml(s){
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function setStatus(msg, warn){
  const el = $('#status');
  el.textContent = msg;
  el.style.color = warn ? '#92400e' : '#166534';
  setTimeout(()=>{ if (el.textContent === msg) el.textContent=''; }, 6000);
}
function logDebug(msg) {
  const box = $('#debugBox');
  box.style.display = 'block';
  box.textContent += msg + '\n';
}

function findSheet(wb, name) {
  const target = name.toLowerCase().replace(/[\s_\-]/g,'');
  for (const sn of wb.SheetNames) {
    if (sn.toLowerCase().replace(/[\s_\-]/g,'') === target) return sn;
  }
  for (const sn of wb.SheetNames) {
    if (sn.toLowerCase().includes(target)) return sn;
  }
  return null;
}

/* ======================= ДИАГНОСТИКА ======================= */
$('#btnDebug').addEventListener('click', () => {
  const box = $('#debugBox');
  if (box.style.display === 'block') { box.style.display = 'none'; return; }
  box.style.display = 'block';
  box.textContent = '--- ДИАГНОСТИКА ---\n';
  if (!state.workbook) { logDebug('Файл не загружен.'); return; }
  logDebug('Листы: ' + state.workbook.SheetNames.join(', '));

  DEPTS.forEach(dept => {
    const realName = findSheet(state.workbook, dept);
    logDebug(`\n[${dept}] -> "${realName || 'НЕ НАЙДЕН'}"`);
    if (realName) logDebug(`  Прочитано: ${state.employees[dept].length}`);
  });
});

/* ======================= ЧТЕНИЕ ФАЙЛА ======================= */
$('#fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  state.fileName = file.name;
  state.fileHandle = null;
  $('#debugBox').textContent = '';

  COL_FIO = 1; COL_POS = 2;
  COLS_PERF = [3,4]; COL_AVG_PERF = 5;
  COLS_POT  = [6,7]; COL_AVG_POT = 8;
  COL_SQUARE = 9; COL_PORTRAIT = 10;

  try {
    if (typeof XLSX === 'undefined') throw new Error('Библиотека SheetJS не загружена.');
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
    state.workbook = wb;

    detectColumnsFromHeader(wb);
    readReferenceSheet(wb);

    DEPTS.forEach(dept => { state.employees[dept] = readDeptSheet(wb, dept); });

    document.querySelectorAll('#deptButtons button').forEach(b => b.disabled = false);
    $('#btnSave').disabled = false;
    $('#btnAdd').disabled = false;

    const total = DEPTS.reduce((s,d) => s + state.employees[d].length, 0);
    setStatus(total === 0 ? 'Сотрудники не найдены.' : `Файл загружен. Всего: ${total}.`, total === 0);
    selectDept(DEPTS[0]);
  } catch (err) {
    setStatus('Ошибка: ' + err.message, true);
    logDebug('ОШИБКА: ' + err.stack);
  }
});

function detectColumnsFromHeader(wb) {
  let sheetName = null;
  for (const d of DEPTS) { const s = findSheet(wb, d); if (s) { sheetName = s; break; } }
  if (!sheetName) return;

  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'', raw:false });

  let headerRow = -1;
  for (let r = 0; r < Math.min(15, aoa.length); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (String(row[c]).toLowerCase().includes('фио')) { headerRow = r; break; }
    }
    if (headerRow !== -1) break;
  }
  if (headerRow === -1) return;

  const headerText = {};
  for (let r = headerRow; r <= Math.min(headerRow + 3, aoa.length - 1); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (row[c]) headerText[c] = (headerText[c] || '') + ' ' + String(row[c]).toLowerCase();
    }
  }

  const found = {};
  for (let c in headerText) {
    const text = headerText[c]; const cNum = parseInt(c);
    if (text.includes('фио')) found.fio = cNum;
    else if (text.includes('должност')) found.pos = cNum;
    else if (text.includes('дедлайн')) found.p1 = cNum;
    else if (text.includes('качество')) found.p2 = cNum;
    else if (text.includes('новаторство')) found.p3 = cNum;
    else if (text.includes('командность')) found.p4 = cNum;
    else if (text.includes('ср. балл') && text.includes('эффектив')) found.avg1 = cNum;
    else if (text.includes('ср. балл') && text.includes('потенциал')) found.avg2 = cNum;
    else if (text.includes('итоговый квадрат') || text.includes('квадрат')) found.sq = cNum;
    else if (text.includes('портрет')) found.portrait = cNum;
  }

  if (found.fio !== undefined) COL_FIO = found.fio;
  if (found.pos !== undefined) COL_POS = found.pos;
  if (found.p1 !== undefined && found.p2 !== undefined) COLS_PERF = [found.p1, found.p2];
  if (found.p3 !== undefined && found.p4 !== undefined) COLS_POT = [found.p3, found.p4];
  if (found.avg1 !== undefined) COL_AVG_PERF = found.avg1;
  if (found.avg2 !== undefined) COL_AVG_POT = found.avg2;
  if (found.sq !== undefined) COL_SQUARE = found.sq;
  if (found.portrait !== undefined) COL_PORTRAIT = found.portrait;
}

function readReferenceSheet(wb) {
  const sheetName = findSheet(wb, 'справочник');
  if (!sheetName) return;

  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'', raw:false });

  const sections = [];
  let currentSection = null;
  let currentCriterion = null;

  for (let r = 0; r < aoa.length; r++) {
    const row = aoa[r] || [];
    const col0 = String(row[0] || '').trim();
    const col1 = String(row[1] || '').trim();
    const col2 = String(row[2] || '').trim();
    const col3 = String(row[3] || '').trim();

    if (col0.includes('Ось Эффективности') || col0.includes('Ось Потенциала')) {
      currentSection = { title: col0, criteria: [] };
      sections.push(currentSection);
      currentCriterion = null;
      continue;
    }

    if (col0 === 'Показатель' || col1 === '1 балл (Низкий уровень)') continue;

    if (currentSection && col0) {
      if (col1 || col2 || col3) {
        currentCriterion = { name: col0, level1: col1, level2: col2, level3: col3 };
        currentSection.criteria.push(currentCriterion);
      } else if (currentCriterion && !col1 && !col2 && !col3) {
        currentCriterion.name += ' ' + col0;
      }
    }
  }

  referenceData = sections;
  renderReferenceView();
}

function renderReferenceView() {
  const container = $('#refContent');
  if (!referenceData || referenceData.length === 0) {
    container.innerHTML = '<p class="hint">Справочник не загружен или пуст.</p>';
    return;
  }

  let html = '';
  referenceData.forEach(sec => {
    html += `<div class="ref-section">
      <div class="ref-title">${escapeHtml(sec.title)}</div>
      <table class="ref-table">
        <thead>
          <tr>
            <th>Показатель</th>
            <th>1 балл (Низкий)</th>
            <th>2 балла (Средний)</th>
            <th>3 балла (Высокий)</th>
          </tr>
        </thead>
        <tbody>`;

    sec.criteria.forEach(c => {
      html += `<tr>
        <td>${escapeHtml(c.name)}</td>
        <td class="ref-level-1">${escapeHtml(c.level1 || '—')}</td>
        <td class="ref-level-2">${escapeHtml(c.level2 || '—')}</td>
        <td class="ref-level-3">${escapeHtml(c.level3 || '—')}</td>
      </tr>`;
    });

    html += `</tbody></table></div>`;
  });

  container.innerHTML = html;
}

function readDeptSheet(wb, sheetName){
  const realName = findSheet(wb, sheetName);
  if (!realName) return [];

  const ws = wb.Sheets[realName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'', raw:false });
  const list = [];

  let startRow = -1;
  for (let r = 0; r < Math.min(15, aoa.length); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (String(row[c]).toLowerCase().includes('фио')) { startRow = r + 1; break; }
    }
    if (startRow !== -1) break;
  }

  if (startRow === -1) return [];

  for (let r = startRow; r < aoa.length; r++) {
    const row = aoa[r] || [];
    const fio = String(row[COL_FIO] || '').trim();
    if (!fio || fio.toLowerCase() === 'фио' || fio.toLowerCase().includes('сотрудник')) continue;

    const getVal = (c) => {
      const addr = XLSX.utils.encode_cell({ r, c });
      const cell = ws[addr];
      if (!cell) return '';
      if (cell.v !== undefined && cell.v !== null) return cell.v;
      if (cell.w !== undefined && cell.w !== null) return cell.w;
      return '';
    };

    const position = String(getVal(COL_POS) || '').trim();
    const markVal = String(getVal(COL_MARK) || '').trim(); // COL_MARK - индекс колонки

    const p = [];
    COLS_PERF.forEach(c => p.push(toNum(getVal(c))));
    COLS_POT.forEach(c => p.push(toNum(getVal(c))));

    list.push({
      fio, position, p,
      dept: sheetName, // <-- ДОБАВИТЬ ЭТУ СТРОКУ
      mark: markVal,
      fioCell: XLSX.utils.encode_cell({ r, c: COL_FIO }),
      posCell: XLSX.utils.encode_cell({ r, c: COL_POS }),
      paramCells: [
        ...COLS_PERF.map(c => XLSX.utils.encode_cell({ r, c })),
        ...COLS_POT.map(c => XLSX.utils.encode_cell({ r, c }))
      ],
      isNew: false, isDeleted: false, row: r
    });
  }
  return list;
}

/* ======================= НАВИГАЦИЯ ======================= */
document.querySelectorAll('#deptButtons button').forEach(btn => {
  btn.addEventListener('click', () => selectDept(btn.dataset.dept));
});
function selectDept(dept){
  state.currentDept = dept;
  state.selectedIndex = null;

  document.querySelectorAll('#deptButtons button').forEach(b =>
    b.classList.toggle('active', b.dataset.dept === dept));

  // --- ИЗМЕНЕНИЕ НАЧАЛО ---
  const titleEl = $('#gridTitle');
  if (dept === 'Все') {
    titleEl.textContent = 'Карта 9 квадратов (весь ЦЗО)';
  } else if (dept === 'справочник') {
    titleEl.textContent = 'Справочник'; // скроется вместе с deptView, но на всякий случай
  } else {
    titleEl.textContent = `Карта 9 квадратов (${dept})`;
  }
  // --- ИЗМЕНЕНИЕ КОНЕЦ ---

  if (dept === 'справочник') {
    $('#deptView').style.display = 'none';
    $('#refView').style.display = 'block';
    renderReferenceView();
  } else {
    $('#deptView').style.display = 'block';
    $('#refView').style.display = 'none';
    renderTable(); renderGrid(); renderEditForm();
  }
}

/* ======================= ТАБЛИЦА ======================= */
function renderTable(){
  const tbody = $('#empTable tbody');
  tbody.innerHTML = '';
  const dept = state.currentDept;
  if (!dept || dept === 'справочник') return;

  // --- ИЗМЕНЕНИЕ НАЧАЛО ---
  let list = [];
  if (dept === 'Все') {
    // Собираем сотрудников из всех отделов
    DEPTS.forEach(d => {
      const emps = state.employees[d].filter(e => !e.isDeleted);
      list.push(...emps);
    });
    // Сортируем по алфавиту (по ФИО)
    list.sort((a,b) => a.fio.localeCompare(b.fio));
  } else {
    list = state.employees[dept].filter(e => !e.isDeleted);
  }
  // --- ИЗМЕНЕНИЕ КОНЕЦ ---



  list.forEach((emp, idx) => {
    const p = emp.p;
    const m1 = avg2(p[0],p[1]);
    const m2 = avg2(p[2],p[3]);
    const info = squareInfo(m1, m2);
    const prof = SQUARE_PROFILES[info.num] || { short: '—' };

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name" style="${emp.mark === 'red' ? 'color:#b91c1c' : emp.mark === 'yellow' ? 'color:#b45309' : emp.mark === 'green' ? 'color:#15803d' : ''}">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.dept || '—')}</td> <!-- ДОБАВЛЕНА КОЛОНКА ОТДЕЛА -->
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:12px;">${escapeHtml(prof.short)}</td>
      <td><span class="del" data-idx="${idx}">❌удалить</span></td>
    `;
    tr.querySelector('.name').addEventListener('click', () => {
      state.selectedIndex = idx;
      renderTable(); renderGrid(); renderEditForm();
    });
    tr.querySelector('.del').addEventListener('click', (e) => {
      e.stopPropagation();
      if (!confirm(`Удалить сотрудника «${emp.fio}»?`)) return;
  // --- ИЗМЕНЕНИЕ ---
      const targetDept = emp.dept || dept;
      const originalIdx = state.employees[targetDept].indexOf(emp);
      if (originalIdx > -1) state.employees[targetDept][originalIdx].isDeleted = true;
      // -----------------

      if (state.selectedIndex === idx) state.selectedIndex = null;
      else if (state.selectedIndex > idx) state.selectedIndex--;
      renderTable(); renderGrid(); renderEditForm();
    });
    tbody.appendChild(tr);
  });
}

/* ======================= 9 КВАДРАТОВ ======================= */

function renderGrid(){
  const wrap = $('#grid9');
  wrap.innerHTML = '';
  const dept = state.currentDept;
  if (!dept || dept === 'справочник') return;

  let list = [];
  if (dept === 'Все') {
    DEPTS.forEach(d => list.push(...state.employees[d].filter(e => !e.isDeleted)));
    list.sort((a,b) => a.fio.localeCompare(b.fio));
  } else {
    list = state.employees[dept].filter(e => !e.isDeleted);
  }

  const rows = ['high','mid','low'];
  const cols = ['low','mid','high'];
  const rowLabel = { high:'высокий', mid:'средний', low:'низкий' };
  const colLabel = { low:'низкий', mid:'средний', high:'высокий' };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');

  for (const y of rows){
    for (const x of cols){
      const info = squareInfoForLevels(x, y);
      const cell = document.createElement('div');
      cell.className = 'cell ' + info.color;
      cell.setAttribute('data-num', info.num);

      const members = list.filter(emp => {
        const m1 = avg2(emp.p[0],emp.p[1]);
        const m2 = avg2(emp.p[2],emp.p[3]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m => {
          let colorStyle = '';
          if (m.mark === 'red') colorStyle = 'color: #b91c1c; font-weight: 700;';
          if (m.mark === 'yellow') colorStyle = 'color: #b45309; font-weight: 700;';
          if (m.mark === 'green') colorStyle = 'color: #15803d; font-weight: 700;';
          return `<li style="${colorStyle}" title="${escapeHtml(m.fio)}">${escapeHtml(m.fio)}</li>`;
        }).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');

      // Тултип
      cell.addEventListener('mouseenter', (e) => {
        const prof = SQUARE_PROFILES[info.num];
        if (!prof) return;

        $('#tt-title').textContent = info.title;
        $('#tt-portrait').textContent = prof.portrait;
        $('#tt-risks').textContent = prof.risks;
        $('#tt-decision').textContent = prof.decision;

        const tt = $('#tooltip');
        tt.classList.add('active');

        const rect = e.target.getBoundingClientRect();
        tt.style.left = Math.min(window.innerWidth - 340, rect.left + 20) + 'px';
        tt.style.top = (rect.top + 20) + 'px';
      });

      cell.addEventListener('mouseleave', () => {
        $('#tooltip').classList.remove('active');
      });

      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
    <div class="item"><span class="swatch dark-green"></span> Главная элита (Мушкетеры)</div>
    <div class="item"><span class="swatch dark-red"></span> Самый тяжелый случай (Якорь)</div>
  `;
  wrap.appendChild(legend);
}

/* ======================= ФОРМА РЕДАКТИРОВАНИЯ ======================= */
function renderEditForm(){
  const box = $('#editForm');
  const dept = state.currentDept;
  if (!dept || dept === 'справочник') return;

  let list = [];
  if (dept === 'Все') {
    DEPTS.forEach(d => list.push(...state.employees[d].filter(e => !e.isDeleted)));
  } else {
    list = state.employees[dept].filter(e => !e.isDeleted);
  }

  if (state.selectedIndex === null || !list[state.selectedIndex]){
    box.innerHTML = '<span class="hint">Выберите сотрудника в таблице.</span>';
    return;
  }
  const emp = list[state.selectedIndex];

  const m1 = avg2(emp.p[0],emp.p[1]);
  const m2 = avg2(emp.p[2],emp.p[3]);
  const info = squareInfo(m1, m2);
  const prof = SQUARE_PROFILES[info.num] || { portrait: '—' };

  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
      <label>Метка:
        <select id="editMark" style="padding:6px; border-radius:6px; border:1px solid #ccc;">
          <option value="none" ${emp.mark === 'none' || !emp.mark ? 'selected' : ''}>— Нет —</option>
          <option value="red" ${emp.mark === 'red' ? 'selected' : ''}>🔴 Красный</option>
          <option value="yellow" ${emp.mark === 'yellow' ? 'selected' : ''}>🟡 Жёлтый</option>
          <option value="green" ${emp.mark === 'green' ? 'selected' : ''}>🟢 Зелёный</option>
        </select>
      </label>
    </div>

    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[2,3].map(i=>`<label title="${POT_NAMES[i-2]}">${POT_NAMES[i-2]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="form-group">
      <label>Управленческий портрет:</label>
      <textarea id="editPortrait" class="portrait" readonly>${escapeHtml(prof.portrait)}</textarea>
    </div>

    <div class="means" id="meansBox"></div>
  `;
  updateMeans();

  box.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('input', () => {
      const v = toNum(inp.value);
      emp.p[+inp.dataset.param] = v;
      if (v !== '') inp.value = v;

      const newM1 = avg2(emp.p[0],emp.p[1]);
      const newM2 = avg2(emp.p[2],emp.p[3]);
      const newInfo = squareInfo(newM1, newM2);
      const newProf = SQUARE_PROFILES[newInfo.num] || { portrait: '—' };

      $('#editPortrait').value = newProf.portrait;

      updateMeans(); renderTable(); renderGrid();
      const rows = document.querySelectorAll('#empTable tbody tr');
      rows.forEach((tr,i)=>tr.classList.toggle('selected', i===state.selectedIndex));
    });
  });

  $('#editFio').addEventListener('input', e => {
    emp.fio = e.target.value;
    renderTable(); renderGrid();
    document.querySelectorAll('#empTable tbody tr')
      .forEach((tr,i)=>tr.classList.toggle('selected', i===state.selectedIndex));
  });
  $('#editPos').addEventListener('input', e => {
    emp.position = e.target.value;
    renderTable();
  });

  $('#editMark').addEventListener('change', e => {
    emp.mark = e.target.value;
    renderTable(); renderGrid();
  });

  function updateMeans(){
    const m1 = avg2(emp.p[0],emp.p[1]);
    const m2 = avg2(emp.p[2],emp.p[3]);
    const info = (m1 && m2) ? squareInfo(m1, m2) : null;
    $('#meansBox').innerHTML = `Ср. Прд.: <b>${m1||'—'}</b> &nbsp;|&nbsp;
      Ср. Пот.: <b>${m2||'—'}</b> &nbsp;|&nbsp;
      Квадрат: ${info ? `<span class="badge ${info.color}">${info.title}</span>` : '—'}`;
  }
}


/* ======================= ДОБАВЛЕНИЕ СОТРУДНИКА ======================= */
$('#btnAdd').addEventListener('click', () => {
  // 1. Проверяем, выбран ли конкретный отдел
  if (!state.currentDept || state.currentDept === 'справочник' || state.currentDept === 'Все') {
    alert('Чтобы добавить сотрудника, выберите конкретный отдел (Кредиты ФЛ, Кредиты ЮЛ или Транзакт).');
    return;
  }

  const fio = prompt('ФИО нового сотрудника:');
  if (!fio) return;

  // 2. Создаем сотрудника
  const newEmp = {
    fio: fio.trim(),
    position: '',
    p: ['','','',''], // 4 оценки
    isNew: true,
    isDeleted: false,
    dept: state.currentDept, // Привязываем к текущему отделу
    fioCell: null, posCell: null,
    paramCells: [null,null,null,null],
  };

  // 3. Добавляем в массив выбранного отдела
  state.employees[state.currentDept].push(newEmp);

  // 4. Сбрасываем фильтры, чтобы новый сотрудник точно появился в таблице
  state.searchQuery = '';
  state.filterSquare = 'all';
  if ($('#searchFio')) $('#searchFio').value = '';
  if ($('#filterSquare')) $('#filterSquare').value = 'all';

  // 5. Выделяем нового сотрудника в форме
  state._editDept = state.currentDept;
  // Индекс берем из полного массива (без фильтров)
  state.selectedIndex = state.employees[state.currentDept].length - 1;

  // 6. Перерисовываем интерфейс
  renderTable();
  renderGrid();
  renderEditForm();
});

/* ======================= СОХРАНЕНИЕ ======================= */
$('#btnSave').addEventListener('click', async () => {
  if (!state.workbook) return;
  let updated = 0, deleted = 0;

  DEPTS.forEach(dept => {
    const realName = findSheet(state.workbook, dept);
    if (!realName) return;

    const ws = state.workbook.Sheets[realName];
    const allList = state.employees[dept];

    deleted += allList.filter(e => e.isDeleted).length;
    const activeList = allList.filter(e => !e.isDeleted);

    let startRow = 4;
    const oldEmp = allList.find(e => !e.isNew && !e.isDeleted);
    if (oldEmp && oldEmp.row !== undefined) startRow = oldEmp.row;

    const maxCol = Math.max(COL_PORTRAIT, COL_SQUARE, COL_AVG_POT, 15);

    const headerAOA = [];
    for (let r = 0; r < startRow; r++) {
      const row = new Array(maxCol + 1).fill('');
      for (let c = 0; c <= maxCol; c++) {
        const addr = XLSX.utils.encode_cell({ r, c });
        const cell = ws[addr];
        if (cell && cell.v !== undefined) row[c] = cell.v;
      }
      headerAOA.push(row);
    }

    const dataAOA = [];
    activeList.forEach(emp => {
      const p = emp.p;
      const m1 = avg2(p[0], p[1]);
      const m2 = avg2(p[2], p[3]);
      const info = squareInfo(m1, m2);
      const prof = SQUARE_PROFILES[info.num] || { short: '—', portrait: '—' };

      const rowData = new Array(maxCol + 1).fill('');
      rowData[0] = '';
      rowData[COL_FIO] = emp.fio;
      rowData[COL_POS] = emp.position;

      COLS_PERF.forEach((c, i) => { rowData[c] = p[i] === '' ? '' : Number(p[i]); });
      COLS_POT.forEach((c, i) => { rowData[c] = p[i+2] === '' ? '' : Number(p[i+2]); });

      rowData[COL_AVG_PERF] = m1 || '';
      rowData[COL_AVG_POT] = m2 || '';
      rowData[COL_SQUARE] = info.title;
      rowData[COL_PORTRAIT] = prof.short; // Сохраняем КОРОТКИЙ портрет в файл
      rowData[COL_MARK] = emp.mark || 'none';

      dataAOA.push(rowData);
      updated++;
    });

    const finalAOA = headerAOA.concat(dataAOA);
    const newWs = XLSX.utils.aoa_to_sheet(finalAOA, { origin: 'A1' });

    const range = {
      s: { r: 0, c: 0 },
      e: { r: finalAOA.length - 1, c: maxCol }
    };
    newWs['!ref'] = XLSX.utils.encode_range(range);

    for (let r = 0; r < startRow; r++) {
      for (let c = 0; c <= maxCol; c++) {
        const oldAddr = XLSX.utils.encode_cell({ r, c });
        const newAddr = XLSX.utils.encode_cell({ r, c });
        if (ws[oldAddr] && ws[oldAddr].s) {
          if (!newWs[newAddr]) newWs[newAddr] = { t:'s', v:'' };
          newWs[newAddr].s = ws[oldAddr].s;
        }
      }
    }

    for (let r = startRow; r < startRow + activeList.length; r++) {
      const addr = XLSX.utils.encode_cell({ r, c: COL_PORTRAIT });
      if (!newWs[addr]) newWs[addr] = { t:'s', v:'' };
      newWs[addr].s = { alignment: { wrapText: true, vertical: 'top' } };
    }

    if (ws['!cols']) newWs['!cols'] = ws['!cols'];
    if (ws['!merges']) newWs['!merges'] = ws['!merges'];
    if (ws['!rows']) newWs['!rows'] = ws['!rows'];

    state.workbook.Sheets[realName] = newWs;
  });

  DEPTS.forEach(dept => {
    state.employees[dept] = state.employees[dept].filter(e => !e.isDeleted);
    state.employees[dept].forEach((emp, idx) => {
      emp.row = 4 + idx;
      emp.isNew = false;
      emp.isDeleted = false;
    });
  });

  const wbout = XLSX.write(state.workbook, { bookType:'xlsx', type:'array' });

  if (window.showSaveFilePicker) {
    try {
      if (!state.fileHandle) {
        state.fileHandle = await window.showSaveFilePicker({
          suggestedName: state.fileName,
          types: [{
            description: 'Excel Files',
            accept: {'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']}
          }]
        });
      }

      const writable = await state.fileHandle.createWritable();
      await writable.write(wbout);
      await writable.close();

      setStatus(`✅ Файл перезаписан. Обновлено: ${updated}, удалено: ${deleted}.`);
      renderTable(); renderGrid(); renderEditForm();
      return;
    } catch (err) {
      if (err.name === 'AbortError') {
        setStatus('Сохранение отменено пользователем.', true);
        return;
      }
    }
  }

  const blob = new Blob([wbout], { type: 'application/octet-stream' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = state.fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  setStatus(`Скачано: ${state.fileName}. Обновлено: ${updated}, удалено: ${deleted}.`);
  renderTable(); renderGrid(); renderEditForm();
});
</script>
</body>
</html>












<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Оценка сотрудников — 9-box grid</title>
<script src="xlsx.full.min.js"></script>
<style>
  :root { --border:#d0d5dd; --accent:#2563eb; }
  * { box-sizing: border-box; }
  body { font-family: system-ui, Segoe UI, Arial, sans-serif; margin:0; padding:20px; background:#f5f6f8; color:#222; }
  h1 { font-size:20px; margin:0 0 12px; }
  .panel { background:#fff; border:1px solid var(--border); border-radius:10px; padding:16px; margin-bottom:14px; }
  .row { display:flex; gap:12px; flex-wrap:wrap; align-items:center; }
  button { padding:8px 14px; border:1px solid var(--border); background:#fff; border-radius:8px; cursor:pointer; font-size:14px; }
  button:hover { border-color:var(--accent); color:var(--accent); }
  button.active { background:var(--accent); color:#fff; border-color:var(--accent); }
  button.primary { background:#2563eb; color:#fff; border-color:#2563eb; }
  button:disabled { opacity:.5; cursor:default; }
  table { width:100%; border-collapse:collapse; }
  th, td { border:1px solid var(--border); padding:6px 8px; text-align:center; font-size:14px; }
  th { background:#f0f2f5; }
  td.name { text-align:left; font-weight:400; cursor:pointer; }
  td.name:hover { background:#eef4ff; }
  tr.selected td { background:#e0ecff; }
  input[type=number] { width:56px; padding:4px; text-align:center; border:1px solid var(--border); border-radius:6px; }
  input[type=text].fio { width:200px; padding:6px; border:1px solid var(--border); border-radius:6px; }
  input[type=text].pos { width:200px; padding:6px; border:1px solid var(--border); border-radius:6px; }

  /* Портрет в форме */
  textarea.portrait {
    width:100%;
    padding:10px;
    border:1px solid var(--border);
    border-radius:6px;
    min-height:80px;
    resize:vertical;
    font-family: ui-monospace, Consolas, monospace;
    font-size:12px;
    line-height:1.5;
    background:#f9fafb;
    white-space:pre-wrap;
    overflow-y:auto;
  }

  /* Карта 9 квадратов (увеличена и по центру) */
  .grid-wrap {
    display:grid;
    grid-template-columns: repeat(3, 1fr);
    gap:12px;
    max-width: 900px;
    margin: 0 auto;
  }

  .cell {
    position: relative;
    border:1px solid var(--border);
    border-radius:12px;
    padding:14px;
    min-height:130px;
    cursor: help;
    transition: transform 0.1s;
  }
  .cell:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

  .cell h4 { margin:0 0 4px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:16px; font-weight:700; color:#1f2937; margin:2px 0 8px; }
  .cell ul { margin:0; padding-left:0; list-style:none; font-size:13px; }
  .cell ul li { margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }

  /* Цвета */
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }
  .cell.dark-green { background:#c1d6c6; border-color:#5c7a64; }
  .cell.dark-red   { background:#d9b3b3; border-color:#8b4545; }

  /* Легенда */
  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:16px; font-size:13px; color:#333; width:100%; justify-content: center; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }
  .legend .swatch.dark-green{ background:#c1d6c6; border-color:#5c7a64; }
  .legend .swatch.dark-red{ background:#d9b3b3; border-color:#8b4545; }

  /* Бейджи */
  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.dark-green { background:#c1d6c6; color:#2f4a37; }
  .badge.dark-red   { background:#d9b3b3; color:#6b2b2b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

  /* Всплывающая подсказка */
  #tooltip {
    position: fixed; background: #1f2937; color: #fff; padding: 12px; border-radius: 8px;
    font-size: 12px; max-width: 320px; line-height: 1.5; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    pointer-events: none; opacity: 0; transition: opacity 0.15s; z-index: 1000; display: none;
  }
  #tooltip.active { opacity: 1; display: block; }
  #tooltip h5 { margin: 0 0 6px 0; font-size: 14px; color: #fff; }
  #tooltip p { margin: 0 0 8px 0; }
  #tooltip .label { color: #9ca3af; font-weight: 600; display: block; margin-bottom: 2px;}

  .hint { color:#666; font-size:13px; }
  .status { font-size:13px; color:#166534; }
  .del { color:#b91c1c; cursor:pointer; font-size:12px; }
  .means { font-size:14px; margin:6px 0; }
  .form-group { margin-bottom: 12px; }
  .form-group label { display:block; font-weight:600; margin-bottom:4px; font-size:13px; color:#475467; }
  .debug { background:#f8f9fa; border:1px solid #ddd; padding:8px; font-size:12px; font-family:monospace; color:#333; max-height:200px; overflow:auto; margin-top:8px; display:none; white-space:pre-wrap; }

  .ref-section { margin-bottom:24px; }
  .ref-title { font-size:16px; font-weight:700; color:#1f2937; margin:0 0 8px; padding:8px 12px; background:#e0ecff; border-left:4px solid var(--accent); border-radius:4px; }
  .ref-table { width:100%; border-collapse:collapse; }
  .ref-table th { background:#f0f2f5; text-align:left; padding:8px 10px; font-size:13px; }
  .ref-table td { text-align:left; vertical-align:top; padding:10px; font-size:13px; line-height:1.4; }
  .ref-table td:first-child { font-weight:600; width:180px; color:#1f2937; }
  .ref-level-1 { background:#fef2f2; }
  .ref-level-2 { background:#fefce8; }
  .ref-level-3 { background:#f0fdf4; }
</style>
</head>
<body>

<h1>Оценка сотрудников — 9-box grid</h1>

<div class="panel">
  <div class="row">
    <input type="file" id="fileInput" accept=".xlsx,.xls">
    <button id="btnSave" class="primary" disabled>💾 Сохранить</button>
    <button id="btnAdd" disabled>➕ Добавить сотрудника</button>
    <button id="btnDebug" style="font-size:12px;">🐞 Диагностика</button>
    <span id="status" class="status"></span>
  </div>
  <div id="debugBox" class="debug"></div>
</div>

<div class="panel">
  <div class="row" id="deptButtons">
    <button data-dept="Кредиты ФЛ" disabled>👤Кредиты ФЛ</button>
    <button data-dept="Кредиты ЮЛ" disabled>👤Кредиты ЮЛ</button>
    <button data-dept="Транзакт" disabled>👤Транзакт</button>
    <button data-dept="Все" disabled>👥 Все сотрудники ЦЗО</button> <!-- НОВАЯ КНОПКА -->
    <button data-dept="справочник" disabled>📖 Справочник</button>
  </div>
</div>

<div id="deptView">
  <div class="panel">
    <h3 style="margin-top:0">🙋🏻‍♂️ Сотрудники отдела</h3>
    <div style="overflow-x:auto;">
      <table id="empTable">
        <thead>
          <tr>
            <th>ФИО</th><th>Отдел</th><th>Должность</th><th id="th_p1">Дедлайн ЗОД</th><th id="th_p2">Качество ЗОД</th>
            <th id="th_p4">Новаторство</th><th id="th_p5">Командность</th>
            <th>Ср. Прд.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th></th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <div class="panel">
    <h3 id="gridTitle" style="margin-top:0; text-align:center;">Карта 9 квадратов (текущий отдел)</h3>
    <div class="grid-wrap" id="grid9"></div>
  </div>

  <div class="panel">
    <h3 style="margin-top:0">Редактирование сотрудника</h3>
    <div id="editForm" class="hint">Выберите сотрудника в таблице.</div>
  </div>
</div>

<div id="refView" style="display:none;">
  <div class="panel">
    <h3 style="margin-top:0">📖 Расширенный справочник критериев и показателей</h3>
    <div id="refContent"></div>
  </div>
</div>

<!-- Тултип -->
<div id="tooltip">
  <h5 id="tt-title"></h5>
  <p><span class="label">Портрет:</span> <span id="tt-portrait"></span></p>
  <p><span class="label">Риски:</span> <span id="tt-risks"></span></p>
  <p><span class="label">Решение:</span> <span id="tt-decision"></span></p>
</div>

<script>
/* ======================= КОНСТАНТЫ ======================= */
let COL_FIO = 1;
let COL_POS = 2;
let COLS_PERF = [3,4];
let COL_AVG_PERF = 5;
let COLS_POT  = [6,7];
let COL_AVG_POT  = 8;
let COL_SQUARE   = 9;
let COL_PORTRAIT = 10;

const DEPTS = ['Кредиты ФЛ', 'Кредиты ЮЛ', 'Транзакт'];

let SQUARE_NAMES = {
  1: '1. Якорь',
  2: '2. Пассажир',
  3: '3. Хранители традиций',
  4: '4. Улитки',
  5: '5. Рабочие муравьи',
  6: '6. Пчелы-труженицы',
  7: '7. Фантазеры',
  8: '8. Самородки',
  9: '9. Мушкетеры'
};

let PERF_NAMES = ['Дедлайн ЗОД', 'Качество ЗОД'];
let POT_NAMES = ['Новаторство', 'Командность'];

// Профили: короткий портрет (для таблицы), подробный (для тултипа), риски, решения
const SQUARE_PROFILES = {
  1: {
    short: 'Самый тяжелый случай. ',
    portrait: 'Баланс стабильно завален, дедлайн 12:00 сорван, ошибок куча. При этом учиться не хотят, на любые замечания отвечают агрессией или токсичным нытьем: «За такую зарплату скажите спасибо, что вообще прихожу».',
    risks: 'Тянут весь отдел на дно, демотивируют абсолютно всех вокруг.',
    decision: 'План повышения эффективности (испытательный срок) на 3–4 недели. Четко под подпись: «Вот чек-лист. Сдача до 12:00. Максимум 2 ошибки за месяц. Если не выполняешь — мы расстаемся». В вашей ситуации их увольнение — это благо: на их оклад можно догрузить или удержать «Мушкетеров».'
  },
  2: {
    short: 'Сотрудники, которые ментально уже уволились.',
    portrait: 'Делают необходимый минимум, чтобы не уволили прямо сегодня. Шаг влево, шаг вправо — отказ. Никаких идей, полная апатия.',
    risks: 'Заражают коллектив своим пофигизмом («А зачем напрягаться за эти деньги?»). При малейшем увеличении объемов завалят дедлайн.',
    decision: 'Прямой разговор по душам. «Я вижу, что ты выполняешь норму, но огонь пропал. Что происходит? Ты устал от бэк-офиса? Давай определимся, как мы работаем дальше, потому что мне нужна включенность в процесс закрытия».'
  },
  3: {
    short: 'Мега-опытные «зубры».',
    portrait: 'Ручную проверку знают наизусть, баланс у них всегда идеален. Но потенциал нулевой: любые изменения в софте или чек-листах встречают в штыки («Мы 10 лет так проверяли, зачем вы придумываете ерунду?!»).',
    risks: 'Могут тормозить автоматизацию отдела и ворчанием демотивировать новичков.',
    decision: 'Встреча-уважение. Не пытаться их переделать. Сказать: «Вы наш главный щит от ошибок, ваш опыт бесценен». При внедрении нового контроля просить их стать «главными критиками»: «Посмотрите своим опытным взглядом, где в этой новой схеме могут быть слабые места?» (это снизит их сопротивление).'
  },
  4: {
    short: 'Стараются, не бунтуют, но работают очень медленно.',
    portrait: 'До 12:00 вечно не успевают, из-за спешки в последний момент начинают совершать глупые ошибки. При этом готовы учиться, но темп мышления/работы не позволяет ускориться.',
    risks: 'Будут постоянно тянуть время закрытия дня всего филиала.',
    decision: 'Разбор хронометража. Сесть вместе и посмотреть, на каких именно пунктах чек-листа «Улитка» зависает. Возможно, закрепить за ней на неделю «Пчелу-труженицу», чтобы та показала свои лайфхаки по скорости.'
  },
  5: {
    short: 'Костяк бэк-офиса.',
    portrait: 'Работают стабильно, баланс сдают вовремя в 95% случаев, ошибки редкие. Чужие идеи принимают, работают строго по инструкции.',
    risks: 'Завязнуть в рутине, устать от монотонности и начать потихоньку снижать показатели до уровня «Пассажиров».',
    decision: 'Плановая беседа-сверка. Спросить: «Как дела? На каком этапе чек-листа чаще всего спотыкаешься? Какая помощь нужна от меня, чтобы закрываться еще легче?»Оказывать поддержку.'
  },
  6: {
    short: 'Супер-надежные исполнители с хорошей гибкостью.',
    portrait: 'До 12:00 всё закрывают идеально. Сами новые макросы не пишут, но если «Мушкетеры» придумали новую Excel-таблицу для контроля — «Пчелы» первыми без ворчания внедряют её в свою работу.',
    risks: 'Относиться к ним как к должному и забывать хвалить. Без поддержки они могут загрустить и снизить планку.',
    decision: 'Встреча-благодарность. Закрепить их стабильность, похвалить за легкую адаптацию к изменениям: «Нам очень ценно, что ты так быстро подхватываешь новые правила».'
  },
  7: {
    short: 'Активные сотрудники, но регулярно косячат.',
    portrait: 'Очень активные сотрудники, постоянно фонтанируют идеями: «А давайте всё переделаем!». Но при этом сами регулярно косячат в балансе и сдают его после 12:00, потому что отвлекаются от чек-листа на свои «воздушные замки».',
    risks: 'Могут дезорганизовать работу отдела своими бесконечными разговорами об улучшениях при полном отсутствии личного результата.',
    decision: 'Жесткое заземление. «Твои идеи классные, но давай договоримся: сначала мы выходим на 100% сдачу баланса до 12:00 без ошибок в течение месяца. Как только подтянешь базу — мы сядем обсуждать твои предложения».'
  },
  8: {
    short: 'Генераторы идей с горящими глазами.',
    portrait: 'Предлагают отличные инструменты контроля, но в текущей рутине из-за невнимательности могут сдать баланс в 11:58 или допустить пару мелких ошибок.',
    risks: 'Если забивать их идеи и заставлять только механически кликать по чек-листу, они потеряют интерес, перестанут предлагать улучшения и скатятся в «Пассажиров».',
    decision: 'Направить их потенциал на исправление их же продуктивности. «У тебя отличные идеи, давай ты применишь свой инструмент контроля, чтобы у тебя самого было 0 ошибок в балансе?»'
  },
  9: {
    short: 'Главная элита.',
    portrait: 'Баланс сдают до 12:00 без единой ошибки. Постоянно предлагают, как автоматизировать ручную проверку, пишут макросы, оптимизируют чек-листы.',
    risks: 'Поскольку должностей и прибавок нет, им быстро станет скучно перемалывать рутину. Они уйдут туда, где платят больше.',
    decision: ' Сказать честно: «Я вижу твой уровень, ты перерос рутину». Вовлечь в проектную работу — дать им задачу возглавить мини-автоматизацию процесса. Сделать наставниками.'
  }
};

let referenceData = null;

// ИСПРАВЛЕННЫЙ РАСЧЕТ (делим на 2)
const avg2 = (a,b) => {
  const n1 = Number(a) || 0;
  const n2 = Number(b) || 0;
  if (a === '' && b === '') return 0;
  return +((n1 + n2) / 2).toFixed(2);
};

function squareInfoForLevels(x, y){
  const map = {
    high: { low:['yellow',     7], mid:['green',        8], high:['dark-green', 9] },
    mid:  { low:['red',        4], mid:['yellow',       5], high:['green',       6] },
    low:  { low:['dark-red',   1], mid:['red',          2], high:['yellow',      3] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

/* ======================= СОСТОЯНИЕ ======================= */
const state = {
  workbook: null,
  fileName: 'employees.xlsx',
  fileHandle: null,
  currentDept: null,
  employees: {},
  selectedIndex: null,
};

DEPTS.forEach(d => state.employees[d] = []);

const $ = sel => document.querySelector(sel);

function toNum(v){
  if (v === '' || v === null || v === undefined) return '';
  const n = Number(String(v).replace(',', '.'));
  if (isNaN(n)) return '';
  return Math.min(3, Math.max(1, Math.round(n)));
}
function escapeHtml(s){
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function setStatus(msg, warn){
  const el = $('#status');
  el.textContent = msg;
  el.style.color = warn ? '#92400e' : '#166534';
  setTimeout(()=>{ if (el.textContent === msg) el.textContent=''; }, 6000);
}
function logDebug(msg) {
  const box = $('#debugBox');
  box.style.display = 'block';
  box.textContent += msg + '\n';
}

function findSheet(wb, name) {
  const target = name.toLowerCase().replace(/[\s_\-]/g,'');
  for (const sn of wb.SheetNames) {
    if (sn.toLowerCase().replace(/[\s_\-]/g,'') === target) return sn;
  }
  for (const sn of wb.SheetNames) {
    if (sn.toLowerCase().includes(target)) return sn;
  }
  return null;
}

/* ======================= ДИАГНОСТИКА ======================= */
$('#btnDebug').addEventListener('click', () => {
  const box = $('#debugBox');
  if (box.style.display === 'block') { box.style.display = 'none'; return; }
  box.style.display = 'block';
  box.textContent = '--- ДИАГНОСТИКА ---\n';
  if (!state.workbook) { logDebug('Файл не загружен.'); return; }
  logDebug('Листы: ' + state.workbook.SheetNames.join(', '));

  DEPTS.forEach(dept => {
    const realName = findSheet(state.workbook, dept);
    logDebug(`\n[${dept}] -> "${realName || 'НЕ НАЙДЕН'}"`);
    if (realName) logDebug(`  Прочитано: ${state.employees[dept].length}`);
  });
});

/* ======================= ЧТЕНИЕ ФАЙЛА ======================= */
$('#fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  state.fileName = file.name;
  state.fileHandle = null;
  $('#debugBox').textContent = '';

  COL_FIO = 1; COL_POS = 2;
  COLS_PERF = [3,4]; COL_AVG_PERF = 5;
  COLS_POT  = [6,7]; COL_AVG_POT = 8;
  COL_SQUARE = 9; COL_PORTRAIT = 10;

  try {
    if (typeof XLSX === 'undefined') throw new Error('Библиотека SheetJS не загружена.');
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
    state.workbook = wb;

    detectColumnsFromHeader(wb);
    readReferenceSheet(wb);

    DEPTS.forEach(dept => { state.employees[dept] = readDeptSheet(wb, dept); });

    document.querySelectorAll('#deptButtons button').forEach(b => b.disabled = false);
    $('#btnSave').disabled = false;
    $('#btnAdd').disabled = false;

    const total = DEPTS.reduce((s,d) => s + state.employees[d].length, 0);
    setStatus(total === 0 ? 'Сотрудники не найдены.' : `Файл загружен. Всего: ${total}.`, total === 0);
    selectDept(DEPTS[0]);
  } catch (err) {
    setStatus('Ошибка: ' + err.message, true);
    logDebug('ОШИБКА: ' + err.stack);
  }
});

function detectColumnsFromHeader(wb) {
  let sheetName = null;
  for (const d of DEPTS) { const s = findSheet(wb, d); if (s) { sheetName = s; break; } }
  if (!sheetName) return;

  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'', raw:false });

  let headerRow = -1;
  for (let r = 0; r < Math.min(15, aoa.length); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (String(row[c]).toLowerCase().includes('фио')) { headerRow = r; break; }
    }
    if (headerRow !== -1) break;
  }
  if (headerRow === -1) return;

  const headerText = {};
  for (let r = headerRow; r <= Math.min(headerRow + 3, aoa.length - 1); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (row[c]) headerText[c] = (headerText[c] || '') + ' ' + String(row[c]).toLowerCase();
    }
  }

  const found = {};
  for (let c in headerText) {
    const text = headerText[c]; const cNum = parseInt(c);
    if (text.includes('фио')) found.fio = cNum;
    else if (text.includes('должност')) found.pos = cNum;
    else if (text.includes('дедлайн')) found.p1 = cNum;
    else if (text.includes('качество')) found.p2 = cNum;
    else if (text.includes('новаторство')) found.p3 = cNum;
    else if (text.includes('командность')) found.p4 = cNum;
    else if (text.includes('ср. балл') && text.includes('эффектив')) found.avg1 = cNum;
    else if (text.includes('ср. балл') && text.includes('потенциал')) found.avg2 = cNum;
    else if (text.includes('итоговый квадрат') || text.includes('квадрат')) found.sq = cNum;
    else if (text.includes('портрет')) found.portrait = cNum;
  }

  if (found.fio !== undefined) COL_FIO = found.fio;
  if (found.pos !== undefined) COL_POS = found.pos;
  if (found.p1 !== undefined && found.p2 !== undefined) COLS_PERF = [found.p1, found.p2];
  if (found.p3 !== undefined && found.p4 !== undefined) COLS_POT = [found.p3, found.p4];
  if (found.avg1 !== undefined) COL_AVG_PERF = found.avg1;
  if (found.avg2 !== undefined) COL_AVG_POT = found.avg2;
  if (found.sq !== undefined) COL_SQUARE = found.sq;
  if (found.portrait !== undefined) COL_PORTRAIT = found.portrait;
}

function readReferenceSheet(wb) {
  const sheetName = findSheet(wb, 'справочник');
  if (!sheetName) return;

  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'', raw:false });

  const sections = [];
  let currentSection = null;
  let currentCriterion = null;

  for (let r = 0; r < aoa.length; r++) {
    const row = aoa[r] || [];
    const col0 = String(row[0] || '').trim();
    const col1 = String(row[1] || '').trim();
    const col2 = String(row[2] || '').trim();
    const col3 = String(row[3] || '').trim();

    if (col0.includes('Ось Эффективности') || col0.includes('Ось Потенциала')) {
      currentSection = { title: col0, criteria: [] };
      sections.push(currentSection);
      currentCriterion = null;
      continue;
    }

    if (col0 === 'Показатель' || col1 === '1 балл (Низкий уровень)') continue;

    if (currentSection && col0) {
      if (col1 || col2 || col3) {
        currentCriterion = { name: col0, level1: col1, level2: col2, level3: col3 };
        currentSection.criteria.push(currentCriterion);
      } else if (currentCriterion && !col1 && !col2 && !col3) {
        currentCriterion.name += ' ' + col0;
      }
    }
  }

  referenceData = sections;
  renderReferenceView();
}

function renderReferenceView() {
  const container = $('#refContent');
  if (!referenceData || referenceData.length === 0) {
    container.innerHTML = '<p class="hint">Справочник не загружен или пуст.</p>';
    return;
  }

  let html = '';
  referenceData.forEach(sec => {
    html += `<div class="ref-section">
      <div class="ref-title">${escapeHtml(sec.title)}</div>
      <table class="ref-table">
        <thead>
          <tr>
            <th>Показатель</th>
            <th>1 балл (Низкий)</th>
            <th>2 балла (Средний)</th>
            <th>3 балла (Высокий)</th>
          </tr>
        </thead>
        <tbody>`;

    sec.criteria.forEach(c => {
      html += `<tr>
        <td>${escapeHtml(c.name)}</td>
        <td class="ref-level-1">${escapeHtml(c.level1 || '—')}</td>
        <td class="ref-level-2">${escapeHtml(c.level2 || '—')}</td>
        <td class="ref-level-3">${escapeHtml(c.level3 || '—')}</td>
      </tr>`;
    });

    html += `</tbody></table></div>`;
  });

  container.innerHTML = html;
}

function readDeptSheet(wb, sheetName){
  const realName = findSheet(wb, sheetName);
  if (!realName) return [];

  const ws = wb.Sheets[realName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'', raw:false });
  const list = [];

  let startRow = -1;
  for (let r = 0; r < Math.min(15, aoa.length); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (String(row[c]).toLowerCase().includes('фио')) { startRow = r + 1; break; }
    }
    if (startRow !== -1) break;
  }

  if (startRow === -1) return [];

  for (let r = startRow; r < aoa.length; r++) {
    const row = aoa[r] || [];
    const fio = String(row[COL_FIO] || '').trim();
    if (!fio || fio.toLowerCase() === 'фио' || fio.toLowerCase().includes('сотрудник')) continue;

    const getVal = (c) => {
      const addr = XLSX.utils.encode_cell({ r, c });
      const cell = ws[addr];
      if (!cell) return '';
      if (cell.v !== undefined && cell.v !== null) return cell.v;
      if (cell.w !== undefined && cell.w !== null) return cell.w;
      return '';
    };

    const position = String(getVal(COL_POS) || '').trim();
    const markVal = String(getVal(COL_MARK) || '').trim(); // COL_MARK - индекс колонки

    const p = [];
    COLS_PERF.forEach(c => p.push(toNum(getVal(c))));
    COLS_POT.forEach(c => p.push(toNum(getVal(c))));

    list.push({
      fio, position, p,
      dept: sheetName, // <-- ДОБАВИТЬ ЭТУ СТРОКУ
      mark: markVal,
      fioCell: XLSX.utils.encode_cell({ r, c: COL_FIO }),
      posCell: XLSX.utils.encode_cell({ r, c: COL_POS }),
      paramCells: [
        ...COLS_PERF.map(c => XLSX.utils.encode_cell({ r, c })),
        ...COLS_POT.map(c => XLSX.utils.encode_cell({ r, c }))
      ],
      isNew: false, isDeleted: false, row: r
    });
  }
  return list;
}

/* ======================= НАВИГАЦИЯ ======================= */
document.querySelectorAll('#deptButtons button').forEach(btn => {
  btn.addEventListener('click', () => selectDept(btn.dataset.dept));
});
function selectDept(dept){
  state.currentDept = dept;
  state.selectedIndex = null;

  document.querySelectorAll('#deptButtons button').forEach(b =>
    b.classList.toggle('active', b.dataset.dept === dept));

  // --- ИЗМЕНЕНИЕ НАЧАЛО ---
  const titleEl = $('#gridTitle');
  if (dept === 'Все') {
    titleEl.textContent = 'Карта 9 квадратов (весь ЦЗО)';
  } else if (dept === 'справочник') {
    titleEl.textContent = 'Справочник'; // скроется вместе с deptView, но на всякий случай
  } else {
    titleEl.textContent = `Карта 9 квадратов (${dept})`;
  }
  // --- ИЗМЕНЕНИЕ КОНЕЦ ---

  if (dept === 'справочник') {
    $('#deptView').style.display = 'none';
    $('#refView').style.display = 'block';
    renderReferenceView();
  } else {
    $('#deptView').style.display = 'block';
    $('#refView').style.display = 'none';
    renderTable(); renderGrid(); renderEditForm();
  }
}

/* ======================= ТАБЛИЦА ======================= */
function renderTable(){
  const tbody = $('#empTable tbody');
  tbody.innerHTML = '';
  const dept = state.currentDept;
  if (!dept || dept === 'справочник') return;

  // --- ИЗМЕНЕНИЕ НАЧАЛО ---
  let list = [];
  if (dept === 'Все') {
    // Собираем сотрудников из всех отделов
    DEPTS.forEach(d => {
      const emps = state.employees[d].filter(e => !e.isDeleted);
      list.push(...emps);
    });
    // Сортируем по алфавиту (по ФИО)
    list.sort((a,b) => a.fio.localeCompare(b.fio));
  } else {
    list = state.employees[dept].filter(e => !e.isDeleted);
  }
  // --- ИЗМЕНЕНИЕ КОНЕЦ ---



  list.forEach((emp, idx) => {
    const p = emp.p;
    const m1 = avg2(p[0],p[1]);
    const m2 = avg2(p[2],p[3]);
    const info = squareInfo(m1, m2);
    const prof = SQUARE_PROFILES[info.num] || { short: '—' };

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name" style="${emp.mark === 'red' ? 'color:#b91c1c' : emp.mark === 'yellow' ? 'color:#b45309' : emp.mark === 'green' ? 'color:#15803d' : ''}">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.dept || '—')}</td> <!-- ДОБАВЛЕНА КОЛОНКА ОТДЕЛА -->
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:12px;">${escapeHtml(prof.short)}</td>
      <td><span class="del" data-idx="${idx}">❌удалить</span></td>
    `;
    tr.querySelector('.name').addEventListener('click', () => {
      state.selectedIndex = idx;
      renderTable(); renderGrid(); renderEditForm();
    });
    tr.querySelector('.del').addEventListener('click', (e) => {
      e.stopPropagation();
      if (!confirm(`Удалить сотрудника «${emp.fio}»?`)) return;
  // --- ИЗМЕНЕНИЕ ---
      const targetDept = emp.dept || dept;
      const originalIdx = state.employees[targetDept].indexOf(emp);
      if (originalIdx > -1) state.employees[targetDept][originalIdx].isDeleted = true;
      // -----------------

      if (state.selectedIndex === idx) state.selectedIndex = null;
      else if (state.selectedIndex > idx) state.selectedIndex--;
      renderTable(); renderGrid(); renderEditForm();
    });
    tbody.appendChild(tr);
  });
}

/* ======================= 9 КВАДРАТОВ ======================= */

function renderGrid(){
  const wrap = $('#grid9');
  wrap.innerHTML = '';
  const dept = state.currentDept;
  if (!dept || dept === 'справочник') return;

  let list = [];
  if (dept === 'Все') {
    DEPTS.forEach(d => list.push(...state.employees[d].filter(e => !e.isDeleted)));
    list.sort((a,b) => a.fio.localeCompare(b.fio));
  } else {
    list = state.employees[dept].filter(e => !e.isDeleted);
  }

  const rows = ['high','mid','low'];
  const cols = ['low','mid','high'];
  const rowLabel = { high:'высокий', mid:'средний', low:'низкий' };
  const colLabel = { low:'низкий', mid:'средний', high:'высокий' };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');

  for (const y of rows){
    for (const x of cols){
      const info = squareInfoForLevels(x, y);
      const cell = document.createElement('div');
      cell.className = 'cell ' + info.color;
      cell.setAttribute('data-num', info.num);

      const members = list.filter(emp => {
        const m1 = avg2(emp.p[0],emp.p[1]);
        const m2 = avg2(emp.p[2],emp.p[3]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m => {
          let colorStyle = '';
          if (m.mark === 'red') colorStyle = 'color: #b91c1c; font-weight: 700;';
          if (m.mark === 'yellow') colorStyle = 'color: #b45309; font-weight: 700;';
          if (m.mark === 'green') colorStyle = 'color: #15803d; font-weight: 700;';
          return `<li style="${colorStyle}" title="${escapeHtml(m.fio)}">${escapeHtml(m.fio)}</li>`;
        }).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');

      // Тултип
      cell.addEventListener('mouseenter', (e) => {
        const prof = SQUARE_PROFILES[info.num];
        if (!prof) return;

        $('#tt-title').textContent = info.title;
        $('#tt-portrait').textContent = prof.portrait;
        $('#tt-risks').textContent = prof.risks;
        $('#tt-decision').textContent = prof.decision;

        const tt = $('#tooltip');
        tt.classList.add('active');

        const rect = e.target.getBoundingClientRect();
        tt.style.left = Math.min(window.innerWidth - 340, rect.left + 20) + 'px';
        tt.style.top = (rect.top + 20) + 'px';
      });

      cell.addEventListener('mouseleave', () => {
        $('#tooltip').classList.remove('active');
      });

      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
    <div class="item"><span class="swatch dark-green"></span> Главная элита (Мушкетеры)</div>
    <div class="item"><span class="swatch dark-red"></span> Самый тяжелый случай (Якорь)</div>
  `;
  wrap.appendChild(legend);
}

/* ======================= ФОРМА РЕДАКТИРОВАНИЯ ======================= */
function renderEditForm(){
  const box = $('#editForm');
  const dept = state.currentDept;
  if (!dept || dept === 'справочник') return;

  let list = [];
  if (dept === 'Все') {
    DEPTS.forEach(d => list.push(...state.employees[d].filter(e => !e.isDeleted)));
  } else {
    list = state.employees[dept].filter(e => !e.isDeleted);
  }

  if (state.selectedIndex === null || !list[state.selectedIndex]){
    box.innerHTML = '<span class="hint">Выберите сотрудника в таблице.</span>';
    return;
  }
  const emp = list[state.selectedIndex];

  const m1 = avg2(emp.p[0],emp.p[1]);
  const m2 = avg2(emp.p[2],emp.p[3]);
  const info = squareInfo(m1, m2);
  const prof = SQUARE_PROFILES[info.num] || { portrait: '—' };

  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
      <label>Метка:
        <select id="editMark" style="padding:6px; border-radius:6px; border:1px solid #ccc;">
          <option value="none" ${emp.mark === 'none' || !emp.mark ? 'selected' : ''}>— Нет —</option>
          <option value="red" ${emp.mark === 'red' ? 'selected' : ''}>🔴 Красный</option>
          <option value="yellow" ${emp.mark === 'yellow' ? 'selected' : ''}>🟡 Жёлтый</option>
          <option value="green" ${emp.mark === 'green' ? 'selected' : ''}>🟢 Зелёный</option>
        </select>
      </label>
    </div>

    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[2,3].map(i=>`<label title="${POT_NAMES[i-2]}">${POT_NAMES[i-2]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="form-group">
      <label>Управленческий портрет:</label>
      <textarea id="editPortrait" class="portrait" readonly>${escapeHtml(prof.portrait)}</textarea>
    </div>

    <div class="means" id="meansBox"></div>
  `;
  updateMeans();

  box.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('input', () => {
      const v = toNum(inp.value);
      emp.p[+inp.dataset.param] = v;
      if (v !== '') inp.value = v;

      const newM1 = avg2(emp.p[0],emp.p[1]);
      const newM2 = avg2(emp.p[2],emp.p[3]);
      const newInfo = squareInfo(newM1, newM2);
      const newProf = SQUARE_PROFILES[newInfo.num] || { portrait: '—' };

      $('#editPortrait').value = newProf.portrait;

      updateMeans(); renderTable(); renderGrid();
      const rows = document.querySelectorAll('#empTable tbody tr');
      rows.forEach((tr,i)=>tr.classList.toggle('selected', i===state.selectedIndex));
    });
  });

  $('#editFio').addEventListener('input', e => {
    emp.fio = e.target.value;
    renderTable(); renderGrid();
    document.querySelectorAll('#empTable tbody tr')
      .forEach((tr,i)=>tr.classList.toggle('selected', i===state.selectedIndex));
  });
  $('#editPos').addEventListener('input', e => {
    emp.position = e.target.value;
    renderTable();
  });

  $('#editMark').addEventListener('change', e => {
    emp.mark = e.target.value;
    renderTable(); renderGrid();
  });

  function updateMeans(){
    const m1 = avg2(emp.p[0],emp.p[1]);
    const m2 = avg2(emp.p[2],emp.p[3]);
    const info = (m1 && m2) ? squareInfo(m1, m2) : null;
    $('#meansBox').innerHTML = `Ср. Прд.: <b>${m1||'—'}</b> &nbsp;|&nbsp;
      Ср. Пот.: <b>${m2||'—'}</b> &nbsp;|&nbsp;
      Квадрат: ${info ? `<span class="badge ${info.color}">${info.title}</span>` : '—'}`;
  }
}


/* ======================= ДОБАВЛЕНИЕ СОТРУДНИКА ======================= */
$('#btnAdd').addEventListener('click', () => {
  // 1. Проверяем, выбран ли конкретный отдел
  if (!state.currentDept || state.currentDept === 'справочник' || state.currentDept === 'Все') {
    alert('Чтобы добавить сотрудника, выберите конкретный отдел (Кредиты ФЛ, Кредиты ЮЛ или Транзакт).');
    return;
  }

  const fio = prompt('ФИО нового сотрудника:');
  if (!fio) return;

  // 2. Создаем сотрудника
  const newEmp = {
    fio: fio.trim(),
    position: '',
    p: ['','','',''], // 4 оценки
    isNew: true,
    isDeleted: false,
    dept: state.currentDept, // Привязываем к текущему отделу
    fioCell: null, posCell: null,
    paramCells: [null,null,null,null],
  };

  // 3. Добавляем в массив выбранного отдела
  state.employees[state.currentDept].push(newEmp);

  // 4. Сбрасываем фильтры, чтобы новый сотрудник точно появился в таблице
  state.searchQuery = '';
  state.filterSquare = 'all';
  if ($('#searchFio')) $('#searchFio').value = '';
  if ($('#filterSquare')) $('#filterSquare').value = 'all';

  // 5. Выделяем нового сотрудника в форме
  state._editDept = state.currentDept;
  // Индекс берем из полного массива (без фильтров)
  state.selectedIndex = state.employees[state.currentDept].length - 1;

  // 6. Перерисовываем интерфейс
  renderTable();
  renderGrid();
  renderEditForm();
});

/* ======================= СОХРАНЕНИЕ ======================= */
$('#btnSave').addEventListener('click', async () => {
  if (!state.workbook) return;
  let updated = 0, deleted = 0;

  DEPTS.forEach(dept => {
    const realName = findSheet(state.workbook, dept);
    if (!realName) return;

    const ws = state.workbook.Sheets[realName];
    const allList = state.employees[dept];

    deleted += allList.filter(e => e.isDeleted).length;
    const activeList = allList.filter(e => !e.isDeleted);

    let startRow = 4;
    const oldEmp = allList.find(e => !e.isNew && !e.isDeleted);
    if (oldEmp && oldEmp.row !== undefined) startRow = oldEmp.row;

    const maxCol = Math.max(COL_PORTRAIT, COL_SQUARE, COL_AVG_POT, 15);

    const headerAOA = [];
    for (let r = 0; r < startRow; r++) {
      const row = new Array(maxCol + 1).fill('');
      for (let c = 0; c <= maxCol; c++) {
        const addr = XLSX.utils.encode_cell({ r, c });
        const cell = ws[addr];
        if (cell && cell.v !== undefined) row[c] = cell.v;
      }
      headerAOA.push(row);
    }

    const dataAOA = [];
    activeList.forEach(emp => {
      const p = emp.p;
      const m1 = avg2(p[0], p[1]);
      const m2 = avg2(p[2], p[3]);
      const info = squareInfo(m1, m2);
      const prof = SQUARE_PROFILES[info.num] || { short: '—', portrait: '—' };

      const rowData = new Array(maxCol + 1).fill('');
      rowData[0] = '';
      rowData[COL_FIO] = emp.fio;
      rowData[COL_POS] = emp.position;

      COLS_PERF.forEach((c, i) => { rowData[c] = p[i] === '' ? '' : Number(p[i]); });
      COLS_POT.forEach((c, i) => { rowData[c] = p[i+2] === '' ? '' : Number(p[i+2]); });

      rowData[COL_AVG_PERF] = m1 || '';
      rowData[COL_AVG_POT] = m2 || '';
      rowData[COL_SQUARE] = info.title;
      rowData[COL_PORTRAIT] = prof.short; // Сохраняем КОРОТКИЙ портрет в файл
      rowData[COL_MARK] = emp.mark || 'none';

      dataAOA.push(rowData);
      updated++;
    });

    const finalAOA = headerAOA.concat(dataAOA);
    const newWs = XLSX.utils.aoa_to_sheet(finalAOA, { origin: 'A1' });

    const range = {
      s: { r: 0, c: 0 },
      e: { r: finalAOA.length - 1, c: maxCol }
    };
    newWs['!ref'] = XLSX.utils.encode_range(range);

    for (let r = 0; r < startRow; r++) {
      for (let c = 0; c <= maxCol; c++) {
        const oldAddr = XLSX.utils.encode_cell({ r, c });
        const newAddr = XLSX.utils.encode_cell({ r, c });
        if (ws[oldAddr] && ws[oldAddr].s) {
          if (!newWs[newAddr]) newWs[newAddr] = { t:'s', v:'' };
          newWs[newAddr].s = ws[oldAddr].s;
        }
      }
    }

    for (let r = startRow; r < startRow + activeList.length; r++) {
      const addr = XLSX.utils.encode_cell({ r, c: COL_PORTRAIT });
      if (!newWs[addr]) newWs[addr] = { t:'s', v:'' };
      newWs[addr].s = { alignment: { wrapText: true, vertical: 'top' } };
    }

    if (ws['!cols']) newWs['!cols'] = ws['!cols'];
    if (ws['!merges']) newWs['!merges'] = ws['!merges'];
    if (ws['!rows']) newWs['!rows'] = ws['!rows'];

    state.workbook.Sheets[realName] = newWs;
  });

  DEPTS.forEach(dept => {
    state.employees[dept] = state.employees[dept].filter(e => !e.isDeleted);
    state.employees[dept].forEach((emp, idx) => {
      emp.row = 4 + idx;
      emp.isNew = false;
      emp.isDeleted = false;
    });
  });

  const wbout = XLSX.write(state.workbook, { bookType:'xlsx', type:'array' });

  if (window.showSaveFilePicker) {
    try {
      if (!state.fileHandle) {
        state.fileHandle = await window.showSaveFilePicker({
          suggestedName: state.fileName,
          types: [{
            description: 'Excel Files',
            accept: {'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']}
          }]
        });
      }

      const writable = await state.fileHandle.createWritable();
      await writable.write(wbout);
      await writable.close();

      setStatus(`✅ Файл перезаписан. Обновлено: ${updated}, удалено: ${deleted}.`);
      renderTable(); renderGrid(); renderEditForm();
      return;
    } catch (err) {
      if (err.name === 'AbortError') {
        setStatus('Сохранение отменено пользователем.', true);
        return;
      }
    }
  }

  const blob = new Blob([wbout], { type: 'application/octet-stream' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = state.fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  setStatus(`Скачано: ${state.fileName}. Обновлено: ${updated}, удалено: ${deleted}.`);
  renderTable(); renderGrid(); renderEditForm();
});
</script>
</body>
</html>
