Чтобы нажать на кнопку-крестик, можно использовать несколько надёжных локаторов. Вот лучшие варианты:

1. По aria-label="Удалить" (самый надёжный)

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Удалить']"))
)
button.click()
```

2. По иконке mdi-close (если несколько кнопок "Удалить")

```python
# Ищем кнопку, внутри которой есть span с классом mdi-close
button = driver.find_element(By.XPATH, "//button[.//span[contains(@class, 'mdi-close')]]")
button.click()
```

3. По классу ds-icon-button и атрибуту aria-label

```python
button = driver.find_element(By.XPATH, "//button[@aria-label='Удалить' and contains(@class, 'ds-icon-button')]")
button.click()
```

4. Комбинация с родительским контейнером (если нужно найти конкретную)

```python
# Если нужно найти крестик внутри определённого блока
container = driver.find_element(By.XPATH, "//div[@class='ui-tabs-item__text']/..")
button = container.find_element(By.XPATH, ".//button[@aria-label='Удалить']")
button.click()
```

Полный пример с прокруткой и ожиданием

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

try:
    # Ждём появления кнопки
    button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Удалить']"))
    )
    # Прокручиваем к кнопке (на случай, если она вне экрана)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
    # Ждём кликабельности
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(button))
    button.click()
    print("Крестик нажат")
except TimeoutException:
    print("Кнопка не найдена или не кликабельна")
```

Если кнопка появляется после наведения

```python
from selenium.webdriver.common.action_chains import ActionChains

# Наводим на родительский элемент, чтобы кнопка стала видимой
parent = driver.find_element(By.XPATH, "//div[@class='ui-tabs-item__text']")
ActionChains(driver).move_to_element(parent).perform()
time.sleep(0.5)

# Теперь кликаем
button = driver.find_element(By.XPATH, "//button[@aria-label='Удалить']")
button.click()
```

Выбирайте способ, который лучше всего подходит к вашей странице. aria-label="Удалить" — самый надёжный, если он уникален. Если на странице несколько таких кнопок, уточните контекст через родительский элемент.




<div data-v-3d7="" class="ui-tabs-item__text"><span data-v-3d7=""> Фактическая операция по договору (Полный список) Из: </span></div>
<button data-v-d16="" data-v-3d7="" type="button" aria-label="Удалить" tabindex="0" class="non-draggable ds-icon-button ds-icon-button__type-transparent ds-icon-button__size-s ds-icon-button__color-secondary ds-icon-button__square ds-icon-button__icon-only ds-icon-button__no-padding"><span data-v-cf273d10="" data-v-d16abfc0="" class="ds-icon mdi mdi-close" style="font-size: var(--ds-icon-size-s); height: var(--ds-icon-size-s); width: var(--ds-icon-size-s); color: var(--ds-color-secondary); z-index: 1;"><!----></span><!----></button>






<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; padding: 12px; background: #f5f5f5; margin: 0; }
        button {
            width: 100%; padding: 12px; margin: 8px 0;
            border: none; border-radius: 6px; font-size: 14px; font-weight: bold;
            cursor: pointer; color: white; background: #4CAF50;
        }
        .status {
            margin-top: 15px; padding: 10px; background: #fff; border-radius: 4px;
            font-size: 12px; color: #333; min-height: 40px; white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <h3>🔄 Двойная обработка (линейный код с комментариями)</h3>
    <p style="font-size:12px; color:#666;">
        1) 60323_iskhod (Z) → 60323_ОБОРОТ (A)<br>
        2) 60324_iskhod (Z) → 60324_ОБОРОТ (A)<br>
        Замена: "," → "" (удаление), "." → ","
    </p>
    <button onclick="processAll()">⚡ Выполнить всё</button>
    <div class="status" id="status">Готов к работе</div>

    <script>
        // ------------------------------------------------------------
        // Вспомогательные мини-функции (только для удобства,
        // они не содержат бизнес-логики)
        // ------------------------------------------------------------

        // Быстрый доступ к API редактора (находится в родительском окне)
        function editor() { return window.parent.Asc.editor; }

        // Вывод сообщения в интерфейс плагина
        function setStatus(msg) { document.getElementById('status').textContent = msg; }

        // Принудительное обновление книги (если метод доступен)
        function refresh() {
            try {
                if (typeof editor().asc_Recalculate === 'function') {
                    editor().asc_Recalculate();
                }
            } catch(e) {}
        }

        // ------------------------------------------------------------
        // Основная линейная процедура – вызывается при нажатии кнопки
        // ------------------------------------------------------------
        function processAll() {
            setStatus('⏳ Начинаю обработку...');
            try {
                // Получаем объект редактора
                var ed = editor();

                // ================================================
                // ПЕРВАЯ ПАРА: 60323_iskhod → 60323_ОБОРОТ
                // ================================================

                // --- Получение листа-источника (60323_iskhod) ---
                var src1 = null;
                // Пробуем получить лист прямым методом GetSheet (если есть)
                if (typeof ed.GetSheet === 'function') {
                    src1 = ed.GetSheet('60323_iskhod');
                } else {
                    // Иначе перебираем все листы и сравниваем имена
                    var sheets = ed.GetSheets();
                    for (var i = 0; i < sheets.GetCount(); i++) {
                        var sh = sheets.GetSheet(i);
                        if (sh && sh.GetName && sh.GetName() === '60323_iskhod') {
                            src1 = sh;
                            break;
                        }
                    }
                }

                // --- Получение листа-приёмника (60323_ОБОРОТ) ---
                var dst1 = null;
                if (typeof ed.GetSheet === 'function') {
                    dst1 = ed.GetSheet('60323_ОБОРОТ');
                } else {
                    var sheets = ed.GetSheets();
                    for (var i = 0; i < sheets.GetCount(); i++) {
                        var sh = sheets.GetSheet(i);
                        if (sh && sh.GetName && sh.GetName() === '60323_ОБОРОТ') {
                            dst1 = sh;
                            break;
                        }
                    }
                }

                // Если хотя бы один лист не найден – останавливаемся
                if (!src1 || !dst1) throw 'Не найдены листы 60323_iskhod или 60323_ОБОРОТ';

                // --- Поиск последней непустой строки в столбце Z ---
                var lastRow1 = 0;
                var used1 = src1.GetUsedRange();               // весь используемый диапазон
                if (used1) {
                    // Последняя строка диапазона (даже если там пусто)
                    var lastUsedRow1 = used1.GetRow() + used1.GetRows().GetCount() - 1;
                    // Идём снизу вверх, пока не встретим непустую ячейку в Z
                    for (var r = lastUsedRow1; r >= 1; r--) {
                        var val = src1.GetRange('Z' + r).GetValue();
                        if (val !== null && val !== undefined && String(val).trim() !== '') {
                            lastRow1 = r;                      // нашли последнюю заполненную
                            break;
                        }
                    }
                }
                if (lastRow1 === 0) throw 'Столбец Z пуст на 60323_iskhod';

                // --- Замена символов в столбце Z (60323_iskhod) ---
                for (var r = 1; r <= lastRow1; r++) {
                    var cell = src1.GetRange('Z' + r);         // ячейка в строке r
                    var value = cell.GetValue();               // читаем значение
                    if (value !== null && value !== undefined) {
                        var strValue = String(value);          // приводим к строке
                        // Удаляем все запятые (разделители тысяч)
                        // и заменяем точку (десятичный разделитель) на запятую
                        var newStr = strValue.replace(/,/g, '').replace(/\./g, ',');
                        if (newStr !== strValue) {
                            cell.SetValue(newStr);             // записываем обратно, если изменилось
                        }
                    }
                }
                refresh();                                     // обновляем лист

                // --- Копирование Z → A на лист 60323_ОБОРОТ ---
                src1.GetRange('Z1:Z' + lastRow1).Copy(dst1.GetRange('A1'));
                refresh();
                setStatus('✅ Первая пара готова: ' + lastRow1 + ' строк');

                // ================================================
                // ВТОРАЯ ПАРА: 60324_iskhod → 60324_ОБОРОТ
                // ================================================

                // --- Получение листа-источника (60324_iskhod) ---
                var src2 = null;
                if (typeof ed.GetSheet === 'function') {
                    src2 = ed.GetSheet('60324_iskhod');
                } else {
                    var sheets = ed.GetSheets();
                    for (var i = 0; i < sheets.GetCount(); i++) {
                        var sh = sheets.GetSheet(i);
                        if (sh && sh.GetName && sh.GetName() === '60324_iskhod') {
                            src2 = sh;
                            break;
                        }
                    }
                }

                // --- Получение листа-приёмника (60324_ОБОРОТ) ---
                var dst2 = null;
                if (typeof ed.GetSheet === 'function') {
                    dst2 = ed.GetSheet('60324_ОБОРОТ');
                } else {
                    var sheets = ed.GetSheets();
                    for (var i = 0; i < sheets.GetCount(); i++) {
                        var sh = sheets.GetSheet(i);
                        if (sh && sh.GetName && sh.GetName() === '60324_ОБОРОТ') {
                            dst2 = sh;
                            break;
                        }
                    }
                }

                if (!src2 || !dst2) throw 'Не найдены листы 60324_iskhod или 60324_ОБОРОТ';

                // --- Поиск последней непустой строки в столбце Z (60324_iskhod) ---
                var lastRow2 = 0;
                var used2 = src2.GetUsedRange();
                if (used2) {
                    var lastUsedRow2 = used2.GetRow() + used2.GetRows().GetCount() - 1;
                    for (var r = lastUsedRow2; r >= 1; r--) {
                        var val = src2.GetRange('Z' + r).GetValue();
                        if (val !== null && val !== undefined && String(val).trim() !== '') {
                            lastRow2 = r;
                            break;
                        }
                    }
                }
                if (lastRow2 === 0) throw 'Столбец Z пуст на 60324_iskhod';

                // --- Замена символов в столбце Z (60324_iskhod) ---
                for (var r = 1; r <= lastRow2; r++) {
                    var cell = src2.GetRange('Z' + r);
                    var value = cell.GetValue();
                    if (value !== null && value !== undefined) {
                        var strValue = String(value);
                        var newStr = strValue.replace(/,/g, '').replace(/\./g, ',');
                        if (newStr !== strValue) {
                            cell.SetValue(newStr);
                        }
                    }
                }
                refresh();

                // --- Копирование Z → A на лист 60324_ОБОРОТ ---
                src2.GetRange('Z1:Z' + lastRow2).Copy(dst2.GetRange('A1'));
                refresh();

                // Итоговое сообщение с количеством строк в каждой паре
                setStatus('✅ Готово! 60323: ' + lastRow1 + ' строк, 60324: ' + lastRow2 + ' строк.');
            } catch(e) {
                setStatus('❌ Ошибка: ' + (e.message || e));
            }
        }
    </script>
</body>
</html>
