
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
  td.name { text-align:left; font-weight:600; cursor:pointer; }
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
    <button data-dept="Кредиты ФЛ" disabled>Кредиты ФЛ</button>
    <button data-dept="Кредиты ЮЛ" disabled>Кредиты ЮЛ</button>
    <button data-dept="Транзакт" disabled>Транзакт</button>
    <button data-dept="справочник" disabled>📖 Справочник</button>
  </div>
</div>

<div id="deptView">
  <div class="panel">
    <h3 style="margin-top:0">Сотрудники отдела</h3>
    <div style="overflow-x:auto;">
      <table id="empTable">
        <thead>
          <tr>
            <th>ФИО</th><th>Должность</th><th id="th_p1">Р1</th><th id="th_p2">Р2</th>
            <th id="th_p4">П1</th><th id="th_p5">П2</th>
            <th>Ср. Прд.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th></th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <div class="panel">
    <h3 style="margin-top:0; text-align:center;">Карта 9 квадратов (текущий отдел)</h3>
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
    short: 'Самый тяжелый случай.', 
    portrait: 'Сотрудник, который не даёт нужного результата и не показывает потенциала для роста.',
    risks: 'Снижение стандартов команды, нагрузка на других.', 
    decision: 'Честная обратная связь, план улучшения или расставание.' 
  },
  2: { 
    short: 'Сотрудники, которые ментально уже уволились.', 
    portrait: 'Сотрудник, который пока не справляется, но имеет некоторый потенциал.',
    risks: 'Неопределённость для команды, потеря времени.', 
    decision: 'Чёткий план улучшения, наставник; если нет динамики — расставание.' 
  },
  3: { 
    short: 'Мега-опытные «зубры».', 
    portrait: 'Способный сотрудник, который почему-то не даёт результата.',
    risks: 'Ярлык «неудачник»; потеря таланта.', 
    decision: 'Разобраться в причинах, сменить роль, дать поддержку.' 
  },
  4: { 
    short: 'Стараются, не бунтуют, но работают очень медленно.', 
    portrait: 'Выполняет работу на приемлемом уровне, но не проявляет стремления к росту.',
    risks: 'Устаревание навыков.', 
    decision: 'Стандарты, обучение под текущие задачи.' 
  },
  5: { 
    short: 'Костяк бэк-офиса.', 
    portrait: 'Стабильные, обучаемые сотрудники, которые хорошо выполняют свою роль.',
    risks: 'Застой, снижение вовлечённости.', 
    decision: 'Точечное развитие, ротация задач, обратная связь.' 
  },
  6: { 
    short: 'Супер-надежные исполнители с хорошей гибкостью.', 
    portrait: 'Сотрудник с большим потенциалом, но текущие результаты пока средние.',
    risks: 'Фрустрация, если потенциал не реализуется.', 
    decision: 'Сложные задачи, наставник, чёткие цели.' 
  },
  7: { 
    short: 'Активные сотрудники, но регулярно косячат.', 
    portrait: 'Эксперт в своей текущей роли, но не стремится к росту.',
    risks: 'Демотивация и потеря специалиста.', 
    decision: 'Ценить за экспертизу, развивать в глубину.' 
  },
  8: { 
    short: 'Генераторы идей с горящими глазами.', 
    portrait: 'Надёжно и хорошо выполняет работу, может расширять зону ответственности.',
    risks: 'Перегрузка без признания.', 
    decision: 'Развивать в ширину: проекты, наставничество.' 
  },
  9: { 
    short: 'Главная элита.', 
    portrait: 'Лучшие сотрудники: уже дают сильный результат и способны расти дальше.',
    risks: 'Выгорание, потеря мотивации, перехват конкурентами.', 
    decision: 'Удерживать, амбициозные проекты, готовить к повышению.' 
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

    const p = [];
    COLS_PERF.forEach(c => p.push(toNum(getVal(c))));
    COLS_POT.forEach(c => p.push(toNum(getVal(c))));

    list.push({
      fio, position, p,
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
  
  const list = state.employees[dept].filter(e => !e.isDeleted);

  list.forEach((emp, idx) => {
    const p = emp.p;
    const m1 = avg2(p[0],p[1]);
    const m2 = avg2(p[2],p[3]);
    const info = squareInfo(m1, m2);
    const prof = SQUARE_PROFILES[info.num] || { short: '—' };

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:12px;">${escapeHtml(prof.short)}</td>
      <td><span class="del" data-idx="${idx}">удалить</span></td>
    `;
    tr.querySelector('.name').addEventListener('click', () => {
      state.selectedIndex = idx;
      renderTable(); renderGrid(); renderEditForm();
    });
    tr.querySelector('.del').addEventListener('click', (e) => {
      e.stopPropagation();
      if (!confirm(`Удалить сотрудника «${emp.fio}»?`)) return;
      const originalIdx = state.employees[dept].indexOf(emp);
      if (originalIdx > -1) state.employees[dept][originalIdx].isDeleted = true;
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
  
  const list = state.employees[dept].filter(e => !e.isDeleted);

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
        <ul>${members.map(m=>`<li title="${escapeHtml(m.fio)}">${escapeHtml(m.fio)}</li>`).join('')}</ul>
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
  
  const list = state.employees[dept].filter(e => !e.isDeleted);
  
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
  if (!state.currentDept || state.currentDept === 'справочник') return;
  const fio = prompt('ФИО нового сотрудника:');
  if (!fio) return;
  
  const newEmp = {
    fio: fio.trim(),
    position: '',
    p: ['','','',''],
    isNew: true,
    isDeleted: false,
    fioCell: null, posCell: null,
    paramCells: [null,null,null,null],
  };
  
  state.employees[state.currentDept].push(newEmp);
  const activeList = state.employees[state.currentDept].filter(e => !e.isDeleted);
  state.selectedIndex = activeList.length - 1;
  
  renderTable(); renderGrid(); renderEditForm();
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

























После того как изменили количество показателей, наверное нужно изменить расчет квадратов.

Например выше указала все высокие баллы, а он рассчитал как средние показатели у Барановой Иры, хотя если везде высший бал, то это это Мушкетер должен быть. 

2.) Вот в таблицу еще нужно добавить вот это. 
В колонку портрет,в зависимости от квадрата необходимо заполнить вот так:
 
9. Мушкетеры :  Главная элита.
8. Самородки: Генераторы идей с горящими глазами.
7. Фантазеры : Активные сотрудники,но регулярно косячат.
6. Пчелы-труженицы :Супер-надежные исполнители с хорошей гибкостью.
5. Рабочие муравьи: Костяк бэк-офиса. 
4. Улитки: Стараются, не бунтуют, но работают очень медленно.
3. Хранители традиций:Мега-опытные «зубры».
2. Пассажир: Сотрудники, которые ментально уже уволились.
1. Якоря :  Самый тяжелый случай. 

Чтобы в таблице был и квадрат и краткий портрет.

 3.) А вот  уже на квадратах мы расписываем подробно в всплывающих окнах 
ПОРТРЕТ :
9. Мушкетеры :  портрет_мушк
8. Самородки: портрет_сам
7. Фантазеры : портрет_фант
6. Пчелы-труженицы :портрет_пч
5. Рабочие муравьи: портрет_мур
4. Улитки: портрет_ул
3. Хранители традиций:портрет_хр
2. Пассажир: портрет_пас
1. Якоря :  портрет_як

РИСК :
9. Мушкетеры :  риск_мушк
8. Самородки: риск_сам
7. Фантазеры : риск_фант
6. Пчелы-труженицы :риск_пч
5. Рабочие муравьи: риск_мур
4. Улитки: риск_ул
3. Хранители традиций:риск_хр
2. Пассажир: риск_пас
1. Якоря :  риск_як

Решение :
9. Мушкетеры :  реш_мушк
8. Самородки: реш_сам
7. Фантазеры : реш_фант
6. Пчелы-труженицы :реш_пч
5. Рабочие муравьи: реш_мур
4. Улитки: реш_ул
3. Хранители традиций:реш_хр
2. Пассажир: реш_пас
1. Якоря :  реш_як

 
3.) Ср.Эфф нужно заменить на Ср. Прд
