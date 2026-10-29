
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
  input[type=text].decision { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; margin-top:4px; }
  
  /* Красивое отображение портрета в форме */
  textarea.portrait { 
    width:100%; 
    padding:10px; 
    border:1px solid var(--border); 
    border-radius:6px; 
    min-height:120px; 
    resize:vertical; 
    font-family: ui-monospace, Consolas, monospace;
    font-size:12px; 
    line-height:1.5; 
    background:#f9fafb; 
    white-space:pre-wrap; 
    overflow-y:auto;
  }
  
  .grid-wrap { display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; max-width:460px; }
  .cell { position: relative; border:1px solid var(--border); border-radius:10px; padding:10px; min-height:110px; }
  .cell h4 { margin:0 0 2px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:14px; font-weight:700; color:#1f2937; margin:2px 0 6px; }
  .cell ul { margin:0; padding-left:16px; font-size:12px; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }
  
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }

  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:12px; font-size:13px; color:#333; width:100%; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }

  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

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
            <th>ФИО</th><th>Должность</th><th id="th_p1">Р1</th><th id="th_p2">Р2</th><th id="th_p3">Р3</th>
            <th id="th_p4">П1</th><th id="th_p5">П2</th><th id="th_p6">П3</th>
            <th>Ср. Эфф.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th>Риски</th><th>Решение</th><th></th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <div class="panel">
    <h3 style="margin-top:0">Карта 9 квадратов (текущий отдел)</h3>
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

<script>
/* ======================= КОНСТАНТЫ ======================= */
let COL_FIO = 1;
let COL_POS = 2;
let COLS_PERF = [3,4,5];
let COL_AVG_PERF = 6;
let COLS_POT  = [7,8,9];
let COL_AVG_POT  = 10;
let COL_SQUARE   = 11;
let COL_PORTRAIT = 12;
let COL_RISKS    = 13;
let COL_DECISION = 14; // Сдвинули на 1, чтобы вставить Риски

const DEPTS = ['Кредиты ФЛ', 'Кредиты ЮЛ', 'Транзакт'];

// НОВЫЕ НАЗВАНИЯ КВАДРАТОВ (по вашей методике)
let SQUARE_NAMES = {
  1: '1. Якорь', 
  2: '2. Пассажир', 
  3: '3. Хранители традиций',
  4: '4. Улитки', 
  5: '5. Рабочие муравьи', 
  6: '6. Пчелы-труженицы',
  7: '7. Фантазеры', 
  8: '8. Алмазы неограненные', 
  9: '9. Мушкетеры'
};

let PERF_NAMES = ['Дедлайн ЗОД', 'Качество операц. контроля', 'Дисциплина'];
let POT_NAMES = ['Оптимизация процессов', 'Наставничество', 'Стрессоустойчивость'];

// ПОЛНЫЕ ПРОФИЛИ ДЛЯ КАЖДОГО КВАДРАТА
const SQUARE_PROFILES = {
  1: {
    portrait: 'Сотрудник, который не даёт нужного результата и не показывает потенциала для роста в текущих условиях.',
    risks: 'Снижение стандартов команды, нагрузка на других, демотивация сильных.',
    decision: 'Честная обратная связь, формальный план улучшения; если он не работает — перевод на другую роль или расставание.'
  },
  2: {
    portrait: 'Сотрудник, который пока не справляется, но имеет некоторый потенциал и может вырасти при правильной поддержке.',
    risks: 'Долго терпеть низкий результат; неопределённость для команды.',
    decision: 'Чёткий план улучшения, обучение, наставник, контроль промежуточных результатов; если динамики нет — рассматривать перевод или расставание.'
  },
  3: {
    portrait: 'Способный сотрудник, который почему-то не даёт результата. Причины могут быть разными: не та роль, конфликт, отсутствие мотивации, проблемы с ресурсами, личные обстоятельства.',
    risks: 'Ярлык «неудачник» при недооценке причин; потеря таланта.',
    decision: 'Разобраться в причинах, сменить роль или задачи, дать поддержку и чёткие ожидания; установить срок для улучшения.'
  },
  4: {
    portrait: 'Выполняет работу на приемлемом уровне, но не проявляет стремления к росту и не имеет выраженного потенциала для более сложных ролей.',
    risks: 'Терпимость к «среднему» результату; постепенное устаревание навыков.',
    decision: 'Удерживать на текущей роли, обеспечивать понятные стандарты и обучение под текущие задачи; не строить долгосрочные планы на повышение.'
  },
  5: {
    portrait: 'Основная рабочая сила: стабильные, обучаемые сотрудники, которые хорошо выполняют свою роль, но пока без выраженного взлёта.',
    risks: 'Застой; если не развивать, могут постепенно снизить вовлечённость.',
    decision: 'Развивать по точечным навыкам, давать обратную связь, ротацию или расширение задач; искать, что может усилить результативность.'
  },
  6: {
    portrait: 'Сотрудник с большим потенциалом, но текущие результаты пока средние — возможно, из-за новизны роли, нехватки опыта или неправильных задач.',
    risks: 'Если не помочь, потенциал останется нереализованным; возможна фрустрация.',
    decision: 'Инвестировать в развитие, давать сложные, но посильные задачи, наставника, чёткие цели и обратную связь.'
  },
  7: {
    portrait: 'Эксперт в своей текущей роли, стабильно даёт результат, но не стремится или объективно ограничен в росте на более высокую должность.',
    risks: 'Воспринимать как «неперспективного» и демотивировать; потерять ценного специалиста.',
    decision: 'Ценить за экспертизу, удерживать, поддерживать статус и условия; развивать не вверх, а в глубину — углубление экспертизы, передача опыта.'
  },
  8: {
    portrait: 'Надёжно и хорошо выполняет работу, может расширять зону ответственности, но не обязательно готов к резкому карьерному скачку.',
    risks: 'Недооценить и потерять; перегрузить дополнительными задачами без признания.',
    decision: 'Развивать в ширину — новые проекты, наставничество, кросс-функциональные задачи; поощрять и удерживать.'
  },
  9: {
    portrait: 'Лучшие сотрудники: уже дают сильный результат и способны расти дальше — до эксперта или руководителя.',
    risks: 'Выгорание, потеря мотивации, если не давать развития; их легко «перехватывают» конкуренты.',
    decision: 'Удерживать, давать амбициозные проекты, готовить к повышению, обсуждать индивидуальный план развития и преемственность.'
  }
};

// Будем хранить справочник для генерации портретов (если понадобится)
let REF_CRITERIA = { perf: {}, pot: {} };
let referenceData = null;

function squareInfoForLevels(x, y){
  // Логика раскраски (светофор)
  const map = {
    high: { low:['yellow', 7], mid:['green', 8], high:['green', 9] },
    mid:  { low:['red',    4], mid:['yellow',5], high:['green', 6] },
    low:  { low:['red',    1], mid:['red',   2], high:['yellow',3] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

// ГЕНЕРАЦИЯ ПРОФИЛЯ (Портрет, Риски, Решение)
function getProfile(emp) {
  const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
  const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
  if (!m1 || !m2) return { portrait: 'Оценки не выставлены.', risks: '—', decision: '—' };
  
  const info = squareInfo(m1, m2);
  return SQUARE_PROFILES[info.num] || { portrait: 'Нет данных.', risks: '—', decision: '—' };
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
const avg3 = (a,b,c)=> +(((a||0)+(b||0)+(c||0))/3).toFixed(2);

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
  box.textContent = '--- ДИАГНОСТИКА (SheetJS ' + (window.XLSX ? XLSX.version : '?') + ') ---\n';
  if (!state.workbook) { logDebug('Файл не загружен.'); return; }
  logDebug('Листы: ' + state.workbook.SheetNames.join(', '));
  logDebug(`Индексы: ФИО=${COL_FIO}, Должн=${COL_POS}, Портрет=${COL_PORTRAIT}, Риски=${COL_RISKS}, Решение=${COL_DECISION}`);
  
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

  // Сброс индексов (теперь 15 колонок)
  COL_FIO = 1; COL_POS = 2;
  COLS_PERF = [3,4,5]; COL_AVG_PERF = 6;
  COLS_POT  = [7,8,9]; COL_AVG_POT = 10;
  COL_SQUARE = 11; COL_PORTRAIT = 12; COL_RISKS = 13; COL_DECISION = 14;

  try {
    if (typeof XLSX === 'undefined') throw new Error('Библиотека SheetJS не загружена.');
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
    state.workbook = wb;
    logDebug('Файл загружен: ' + file.name);

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
    else if (text.includes('дисциплин')) found.p3 = cNum;
    else if (text.includes('оптимизац')) found.p4 = cNum;
    else if (text.includes('наставнич')) found.p5 = cNum;
    else if (text.includes('стрессоуст')) found.p6 = cNum;
    else if (text.includes('ср. балл') && text.includes('эффектив')) found.avg1 = cNum;
    else if (text.includes('ср. балл') && text.includes('потенциал')) found.avg2 = cNum;
    else if (text.includes('итоговый квадрат') || text.includes('квадрат')) found.sq = cNum;
    else if (text.includes('портрет')) found.portrait = cNum;
    else if (text.includes('риск')) found.risks = cNum;
    else if (text.includes('решение')) found.decision = cNum;
  }
  
  if (found.fio !== undefined) COL_FIO = found.fio;
  if (found.pos !== undefined) COL_POS = found.pos;
  if (found.p1 !== undefined && found.p2 !== undefined && found.p3 !== undefined) COLS_PERF = [found.p1, found.p2, found.p3];
  if (found.p4 !== undefined && found.p5 !== undefined && found.p6 !== undefined) COLS_POT = [found.p4, found.p5, found.p6];
  if (found.avg1 !== undefined) COL_AVG_PERF = found.avg1;
  if (found.avg2 !== undefined) COL_AVG_POT = found.avg2;
  if (found.sq !== undefined) COL_SQUARE = found.sq;
  if (found.portrait !== undefined) COL_PORTRAIT = found.portrait;
  if (found.risks !== undefined) COL_RISKS = found.risks;
  if (found.decision !== undefined) COL_DECISION = found.decision;
}

function readReferenceSheet(wb) {
  const sheetName = findSheet(wb, 'справочник');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'', raw:false });
  
  const sections = [];
  let currentSection = null;
  let currentCriterion = null;
  let currentMode = ''; 

  for (let r = 0; r < aoa.length; r++) {
    const row = aoa[r] || [];
    const col0 = String(row[0] || '').trim();
    const col1 = String(row[1] || '').trim();
    const col2 = String(row[2] || '').trim();
    const col3 = String(row[3] || '').trim();
    
    if (col0.includes('Ось Эффективности')) {
      currentSection = { title: col0, criteria: [] };
      sections.push(currentSection);
      currentCriterion = null;
      currentMode = 'perf';
      continue;
    }
    if (col0.includes('Ось Потенциала')) {
      currentSection = { title: col0, criteria: [] };
      sections.push(currentSection);
      currentCriterion = null;
      currentMode = 'pot';
      continue;
    }
    
    if (col0 === 'Показатель' || col1 === '1 балл (Низкий уровень)') continue;
    
    if (currentSection && col0) {
      if (col1 || col2 || col3) {
        currentCriterion = { name: col0, level1: col1, level2: col2, level3: col3 };
        currentSection.criteria.push(currentCriterion);
        
        if (currentMode === 'perf') REF_CRITERIA.perf[col0] = { 1: col1, 2: col2, 3: col3 };
        else if (currentMode === 'pot') REF_CRITERIA.pot[col0] = { 1: col1, 2: col2, 3: col3 };
      } else if (currentCriterion && !col1 && !col2 && !col3) {
        currentCriterion.name += ' ' + col0;
      }
    }
  }
  
  referenceData = sections;
  
  let perfParams = [], potParams = [];
  sections.forEach(sec => {
    if (sec.title.includes('Эффективности')) sec.criteria.forEach(c => perfParams.push(c.name));
    else if (sec.title.includes('Потенциала')) sec.criteria.forEach(c => potParams.push(c.name));
  });
  
  if (perfParams.length >= 3) PERF_NAMES = perfParams.slice(0, 3);
  if (potParams.length >= 3) POT_NAMES = potParams.slice(0, 3);
  
  setTimeout(() => {
    $('#th_p1').textContent = PERF_NAMES[0];
    $('#th_p2').textContent = PERF_NAMES[1];
    $('#th_p3').textContent = PERF_NAMES[2];
    $('#th_p4').textContent = POT_NAMES[0];
    $('#th_p5').textContent = POT_NAMES[1];
    $('#th_p6').textContent = POT_NAMES[2];
  }, 50);
  
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
    
    // Читаем Портрет, Риски, Решение из файла (если там уже есть), иначе они сгенерируются
    const portrait = String(getVal(COL_PORTRAIT) || '').trim();
    const risks = String(getVal(COL_RISKS) || '').trim();
    const decision = String(getVal(COL_DECISION) || '').trim();

    const p = [];
    COLS_PERF.forEach(c => p.push(toNum(getVal(c))));
    COLS_POT.forEach(c => p.push(toNum(getVal(c))));

    list.push({
      fio, position, portrait, risks, decision, p,
      fioCell: XLSX.utils.encode_cell({ r, c: COL_FIO }),
      posCell: XLSX.utils.encode_cell({ r, c: COL_POS }),
      portraitCell: XLSX.utils.encode_cell({ r, c: COL_PORTRAIT }),
      risksCell: XLSX.utils.encode_cell({ r, c: COL_RISKS }),
      decisionCell: XLSX.utils.encode_cell({ r, c: COL_DECISION }),
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
    const m1 = avg3(p[0],p[1],p[2]);
    const m2 = avg3(p[3],p[4],p[5]);
    const info = squareInfo(m1, m2);
    
    // Подтягиваем профиль (портрет, риски, решение)
    const prof = getProfile(emp);
    emp.portrait = prof.portrait;
    emp.risks = prof.risks;
    emp.decision = prof.decision;

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:11px;white-space:pre-wrap;">${escapeHtml(prof.portrait)}</td>
      <td style="max-width:200px;text-align:left;font-size:11px;white-space:pre-wrap;">${escapeHtml(prof.risks)}</td>
      <td style="max-width:200px;text-align:left;font-size:11px;white-space:pre-wrap;">${escapeHtml(prof.decision)}</td>
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

      const members = list.filter(emp => {
        const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
        const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m=>`<li>${escapeHtml(m.fio)}</li>`).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');
      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
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
  const prof = getProfile(emp);
  
  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1,2].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[3,4,5].map(i=>`<label title="${POT_NAMES[i-3]}">${POT_NAMES[i-3]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="form-group">
      <label>Управленческий портрет (авто):</label>
      <textarea id="editPortrait" class="portrait" readonly>${escapeHtml(prof.portrait)}</textarea>
    </div>

    <div class="form-group">
      <label>Риски (авто):</label>
      <textarea id="editRisks" class="portrait" readonly>${escapeHtml(prof.risks)}</textarea>
    </div>

    <div class="form-group">
      <label>Управленческое решение (авто):</label>
      <textarea id="editDecision" class="portrait" readonly>${escapeHtml(prof.decision)}</textarea>
    </div>

    <div class="means" id="meansBox"></div>
  `;
  updateMeans();

  box.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('input', () => {
      const v = toNum(inp.value);
      emp.p[+inp.dataset.param] = v;
      if (v !== '') inp.value = v;
      
      const newProf = getProfile(emp);
      $('#editPortrait').value = newProf.portrait;
      $('#editRisks').value = newProf.risks;
      $('#editDecision').value = newProf.decision;
      
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
    const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
    const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
    const info = (m1 && m2) ? squareInfo(m1, m2) : null;
    $('#meansBox').innerHTML = `Средняя по разделу 1: <b>${m1||'—'}</b> &nbsp;|&nbsp;
      Средняя по разделу 2: <b>${m2||'—'}</b> &nbsp;|&nbsp;
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
    portrait: '',
    risks: '',
    decision: '',
    p: ['','','','','',''],
    isNew: true,
    isDeleted: false,
    fioCell: null, posCell: null, portraitCell: null, risksCell: null, decisionCell: null,
    paramCells: [null,null,null,null,null,null],
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

    // Теперь 15 колонок (0-14)
    const maxCol = Math.max(COL_DECISION, COL_RISKS, COL_PORTRAIT, COL_SQUARE, COL_AVG_POT, 15);

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
      const m1 = avg3(p[0], p[1], p[2]);
      const m2 = avg3(p[3], p[4], p[5]);
      const info = squareInfo(m1, m2);
      const prof = getProfile(emp);

      const rowData = new Array(maxCol + 1).fill('');
      rowData[0] = '';
      rowData[COL_FIO] = emp.fio;
      rowData[COL_POS] = emp.position;
      
      COLS_PERF.forEach((c, i) => { rowData[c] = p[i] === '' ? '' : Number(p[i]); });
      COLS_POT.forEach((c, i) => { rowData[c] = p[i+3] === '' ? '' : Number(p[i+3]); });
      
      rowData[COL_AVG_PERF] = m1 || '';
      rowData[COL_AVG_POT] = m2 || '';
      rowData[COL_SQUARE] = info.title;
      rowData[COL_PORTRAIT] = prof.portrait;
      rowData[COL_RISKS] = prof.risks;
      rowData[COL_DECISION] = prof.decision;

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
    
    // Копируем стили шапки и добавляем перенос текста
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
    
    // Включаем перенос текста для колонок Портрет (M), Риски (N), Решение (O)
    for (let r = startRow; r < startRow + activeList.length; r++) {
      [COL_PORTRAIT, COL_RISKS, COL_DECISION].forEach(c => {
        const addr = XLSX.utils.encode_cell({ r, c });
        if (!newWs[addr]) newWs[addr] = { t:'s', v:'' };
        newWs[addr].s = { alignment: { wrapText: true, vertical: 'top' } };
      });
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





















если квадрат 9.Мушкетеры , то в Управленческий портрет должно подтянуться:"Лучшие сотрудники: уже дают сильный результат и способны расти дальше — до эксперта или руководителя."

Плюс еще можно добавить столбец "Риски" (добавить его после столбца Управленческий портрет и перед "Управленческое решение") и туда бы подтянулось "Выгорание, потеря мотивации, если не давать развития; их легко «перехватывают» конкуренты."

И в столбец "Управленческое решение" подтянуться должно "Удерживать, давать амбициозные проекты, готовить к повышению, обсуждать индивидуальный план развития и преемственность."

И так по каждому квадрату. У каждого свой портрет,риски и решение.

9. Мушкетеры — высокая результативность + высокий потенциал

Управленческий портрет: Лучшие сотрудники: уже дают сильный результат и способны расти дальше — до эксперта или руководителя.
Риски: Выгорание, потеря мотивации, если не давать развития; их легко «перехватывают» конкуренты.
Управленческое решение: Удерживать, давать амбициозные проекты, готовить к повышению, обсуждать индивидуальный план развития и преемственность.

8. Алмазы неограненные — высокая результативность + средний потенциал

Управленческий портрет: Надёжно и хорошо выполняет работу, может расширять зону ответственности, но не обязательно готов к резкому карьерному скачку.
Риски: Недооценить и потерять; перегрузить дополнительными задачами без признания.
Управленческое решение: Развивать в ширину — новые проекты, наставничество, кросс-функциональные задачи; поощрять и удерживать.

7. Фантазеры — высокая результативность + низкий потенциал

Управленческий портрет: Эксперт в своей текущей роли, стабильно даёт результат, но не стремится или объективно ограничен в росте на более высокую должность.
Риски: Воспринимать как «неперспективного» и демотивировать; потерять ценного специалиста.
Управленческое решение: Ценить за экспертизу, удерживать, поддерживать статус и условия; развивать не вверх, а в глубину — углубление экспертизы, передача опыта.

6. Пчелы-труженицы — средняя результативность + высокий потенциал

Управленческий портрет: Сотрудник с большим потенциалом, но текущие результаты пока средние — возможно, из-за новизны роли, нехватки опыта или неправильных задач.
Риски: Если не помочь, потенциал останется нереализованным; возможна фрустрация.
Управленческое решение: Инвестировать в развитие, давать сложные, но посильные задачи, наставника, чёткие цели и обратную связь.

5. Рабочие муравьи — средняя результативность + средний потенциал

Управленческий портрет: Основная рабочая сила: стабильные, обучаемые сотрудники, которые хорошо выполняют свою роль, но пока без выраженного взлёта.
Риски: Застой; если не развивать, могут постепенно снизить вовлечённость.
Управленческое решение: Развивать по точечным навыкам, давать обратную связь, ротацию или расширение задач; искать, что может усилить результативность.

4. Улитки — средняя результативность + низкий потенциал

Управленческий портрет: Выполняет работу на приемлемом уровне, но не проявляет стремления к росту и не имеет выраженного потенциала для более сложных ролей.
Риски: Терпимость к «среднему» результату; постепенное устаревание навыков.
Управленческое решение: Удерживать на текущей роли, обеспечивать понятные стандарты и обучение под текущие задачи; не строить долгосрочные планы на повышение.

3. Хранители традиций  — низкая результативность + высокий потенциал

Управленческий портрет: Способный сотрудник, который почему-то не даёт результата. Причины могут быть разными: не та роль, конфликт, отсутствие мотивации, проблемы с ресурсами, личные обстоятельства.
Риски: Ярлык «неудачник» при недооценке причин; потеря таланта.
Управленческое решение: Разобраться в причинах, сменить роль или задачи, дать поддержку и чёткие ожидания; установить срок для улучшения.

2. Пассажир — низкая результативность + средний потенциал

Управленческий портрет: Сотрудник, который пока не справляется, но имеет некоторый потенциал и может вырасти при правильной поддержке.
Риски: Долго терпеть низкий результат; неопределённость для команды.
Управленческое решение: Чёткий план улучшения, обучение, наставник, контроль промежуточных результатов; если динамики нет — рассматривать перевод или расставание.

1. Якорь — низкая результативность + низкий потенциал

Управленческий портрет: Сотрудник, который не даёт нужного результата и не показывает потенциала для роста в текущих условиях.
Риски: Снижение стандартов команды, нагрузка на других, демотивация сильных.
Управленческое решение: Честная обратная связь, формальный план улучшения; если он не работает — перевод на другую роль или расставание.




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
  input[type=text].decision { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; margin-top:4px; }
  textarea.portrait { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; min-height:80px; resize:vertical; font-family:inherit; font-size:13px; background:#f9fafb; line-height: 1.4;}
  
  .grid-wrap { display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; max-width:460px; }
  .cell { position: relative; border:1px solid var(--border); border-radius:10px; padding:10px; min-height:110px; }
  .cell h4 { margin:0 0 2px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:14px; font-weight:700; color:#1f2937; margin:2px 0 6px; }
  .cell ul { margin:0; padding-left:16px; font-size:12px; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }
  
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }

  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:12px; font-size:13px; color:#333; width:100%; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }

  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

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
            <th>ФИО</th><th>Должность</th><th id="th_p1">Р1</th><th id="th_p2">Р2</th><th id="th_p3">Р3</th>
            <th id="th_p4">П1</th><th id="th_p5">П2</th><th id="th_p6">П3</th>
            <th>Ср. Эфф.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th>Решение</th><th></th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <div class="panel">
    <h3 style="margin-top:0">Карта 9 квадратов (текущий отдел)</h3>
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

<script>
/* ======================= КОНСТАНТЫ ======================= */
let COL_FIO = 1;
let COL_POS = 2;
let COLS_PERF = [3,4,5];
let COL_AVG_PERF = 6;
let COLS_POT  = [7,8,9];
let COL_AVG_POT  = 10;
let COL_SQUARE   = 11;
let COL_PORTRAIT = 12;
let COL_DECISION = 13;

const DEPTS = ['Кредиты ФЛ', 'Кредиты ЮЛ', 'Транзакт'];

// НОВЫЕ НАЗВАНИЯ КВАДРАТОВ
let SQUARE_NAMES = {
  1: '1. Якорь', 
  2: '2. Пассажир', 
  3: '3. Хранители традиций',
  4: '4. Улитки', 
  5: '5. Рабочие муравьи', 
  6: '6. Пчелы-труженицы',
  7: '7. Фантазеры', 
  8: '8. Алмазы неограненные', 
  9: '9. Мушкетеры'
};

let PERF_NAMES = ['Дедлайн ЗОД', 'Качество операц. контроля', 'Дисциплина'];
let POT_NAMES = ['Оптимизация процессов', 'Наставничество', 'Стрессоустойчивость'];

// Будем хранить справочник для генерации портретов
let REF_CRITERIA = {
  perf: {}, 
  pot: {}   
};

function squareInfoForLevels(x, y){
  // Логика раскраски (светофор)
  const map = {
    high: { low:['yellow', 7], mid:['green', 8], high:['green', 9] },
    mid:  { low:['red',    4], mid:['yellow',5], high:['green', 6] },
    low:  { low:['red',    1], mid:['red',   2], high:['yellow',3] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

// УМНАЯ ГЕНЕРАЦИЯ ПОРТРЕТА НА ОСНОВЕ СПРАВОЧНИКА
function generatePortrait(emp) {
  const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
  const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
  if (!m1 || !m2) return 'Оценки не выставлены.';
  
  const info = squareInfo(m1, m2);
  let text = `Сотрудник соответствует квадрату «${info.title}».\n`;
  
  const strengths = [];
  const weaknesses = [];
  
  for (let i=0; i<6; i++) {
    const val = Number(emp.p[i]);
    const isPerf = i < 3;
    const name = isPerf ? PERF_NAMES[i] : POT_NAMES[i-3];
    const dict = isPerf ? REF_CRITERIA.perf : REF_CRITERIA.pot;
    
    if (val === 3) {
      const desc = dict[name] && dict[name][3] ? ` (${dict[name][3]})` : '';
      strengths.push(`${name}${desc}`);
    }
    if (val === 1) {
      const desc = dict[name] && dict[name][1] ? ` (${dict[name][1]})` : '';
      weaknesses.push(`${name}${desc}`);
    }
  }
  
  if (strengths.length > 0) text += `\n✅ Сильные стороны:\n— ` + strengths.join('\n— ');
  if (weaknesses.length > 0) text += `\n\n⚠️ Зоны развития:\n— ` + weaknesses.join('\n— ');
  
  return text;
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
const avg3 = (a,b,c)=> +(((a||0)+(b||0)+(c||0))/3).toFixed(2);

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
  box.textContent = '--- ДИАГНОСТИКА (SheetJS ' + (window.XLSX ? XLSX.version : '?') + ') ---\n';
  if (!state.workbook) { logDebug('Файл не загружен.'); return; }
  logDebug('Листы: ' + state.workbook.SheetNames.join(', '));
  logDebug(`Индексы: ФИО=${COL_FIO}, Должн=${COL_POS}, Перф=${COLS_PERF}, Пот=${COLS_POT}`);
  
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
  COLS_PERF = [3,4,5]; COL_AVG_PERF = 6;
  COLS_POT  = [7,8,9]; COL_AVG_POT = 10;
  COL_SQUARE = 11; COL_PORTRAIT = 12; COL_DECISION = 13;

  try {
    if (typeof XLSX === 'undefined') throw new Error('Библиотека SheetJS не загружена.');
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
    state.workbook = wb;
    logDebug('Файл загружен: ' + file.name);

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
    else if (text.includes('дисциплин')) found.p3 = cNum;
    else if (text.includes('оптимизац')) found.p4 = cNum;
    else if (text.includes('наставнич')) found.p5 = cNum;
    else if (text.includes('стрессоуст')) found.p6 = cNum;
    else if (text.includes('ср. балл') && text.includes('эффектив')) found.avg1 = cNum;
    else if (text.includes('ср. балл') && text.includes('потенциал')) found.avg2 = cNum;
    else if (text.includes('итоговый квадрат') || text.includes('квадрат')) found.sq = cNum;
    else if (text.includes('управленческий портрет')) found.portrait = cNum;
    else if (text.includes('управленческое решение')) found.decision = cNum;
  }
  
  if (found.fio !== undefined) COL_FIO = found.fio;
  if (found.pos !== undefined) COL_POS = found.pos;
  if (found.p1 !== undefined && found.p2 !== undefined && found.p3 !== undefined) COLS_PERF = [found.p1, found.p2, found.p3];
  if (found.p4 !== undefined && found.p5 !== undefined && found.p6 !== undefined) COLS_POT = [found.p4, found.p5, found.p6];
  if (found.avg1 !== undefined) COL_AVG_PERF = found.avg1;
  if (found.avg2 !== undefined) COL_AVG_POT = found.avg2;
  if (found.sq !== undefined) COL_SQUARE = found.sq;
  if (found.portrait !== undefined) COL_PORTRAIT = found.portrait;
  if (found.decision !== undefined) COL_DECISION = found.decision;
}

function readReferenceSheet(wb) {
  const sheetName = findSheet(wb, 'справочник');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'', raw:false });
  
  const sections = [];
  let currentSection = null;
  let currentCriterion = null;
  let currentMode = ''; 

  for (let r = 0; r < aoa.length; r++) {
    const row = aoa[r] || [];
    const col0 = String(row[0] || '').trim();
    const col1 = String(row[1] || '').trim();
    const col2 = String(row[2] || '').trim();
    const col3 = String(row[3] || '').trim();
    
    if (col0.includes('Ось Эффективности')) {
      currentSection = { title: col0, criteria: [] };
      sections.push(currentSection);
      currentCriterion = null;
      currentMode = 'perf';
      continue;
    }
    if (col0.includes('Ось Потенциала')) {
      currentSection = { title: col0, criteria: [] };
      sections.push(currentSection);
      currentCriterion = null;
      currentMode = 'pot';
      continue;
    }
    
    if (col0 === 'Показатель' || col1 === '1 балл (Низкий уровень)') continue;
    
    if (currentSection && col0) {
      if (col1 || col2 || col3) {
        currentCriterion = { name: col0, level1: col1, level2: col2, level3: col3 };
        currentSection.criteria.push(currentCriterion);
        
        if (currentMode === 'perf') REF_CRITERIA.perf[col0] = { 1: col1, 2: col2, 3: col3 };
        else if (currentMode === 'pot') REF_CRITERIA.pot[col0] = { 1: col1, 2: col2, 3: col3 };
      } else if (currentCriterion && !col1 && !col2 && !col3) {
        currentCriterion.name += ' ' + col0;
      }
    }
  }
  
  referenceData = sections;
  
  let perfParams = [], potParams = [];
  sections.forEach(sec => {
    if (sec.title.includes('Эффективности')) sec.criteria.forEach(c => perfParams.push(c.name));
    else if (sec.title.includes('Потенциала')) sec.criteria.forEach(c => potParams.push(c.name));
  });
  
  if (perfParams.length >= 3) PERF_NAMES = perfParams.slice(0, 3);
  if (potParams.length >= 3) POT_NAMES = potParams.slice(0, 3);
  
  setTimeout(() => {
    $('#th_p1').textContent = PERF_NAMES[0];
    $('#th_p2').textContent = PERF_NAMES[1];
    $('#th_p3').textContent = PERF_NAMES[2];
    $('#th_p4').textContent = POT_NAMES[0];
    $('#th_p5').textContent = POT_NAMES[1];
    $('#th_p6').textContent = POT_NAMES[2];
  }, 50);
  
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
    const portrait = String(getVal(COL_PORTRAIT) || '').trim();
    const decision = String(getVal(COL_DECISION) || '').trim();

    const p = [];
    COLS_PERF.forEach(c => p.push(toNum(getVal(c))));
    COLS_POT.forEach(c => p.push(toNum(getVal(c))));

    list.push({
      fio, position, portrait, decision, p,
      fioCell: XLSX.utils.encode_cell({ r, c: COL_FIO }),
      posCell: XLSX.utils.encode_cell({ r, c: COL_POS }),
      portraitCell: XLSX.utils.encode_cell({ r, c: COL_PORTRAIT }),
      decisionCell: XLSX.utils.encode_cell({ r, c: COL_DECISION }),
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
    const m1 = avg3(p[0],p[1],p[2]);
    const m2 = avg3(p[3],p[4],p[5]);
    const info = squareInfo(m1, m2);
    
    const portraitText = generatePortrait(emp);
    emp.portrait = portraitText;

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:11px;white-space:pre-wrap;">${escapeHtml(portraitText)}</td>
      <td style="max-width:150px;text-align:left;font-size:11px;">${escapeHtml(emp.decision)}</td>
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

      const members = list.filter(emp => {
        const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
        const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m=>`<li>${escapeHtml(m.fio)}</li>`).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');
      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
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
  
  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1,2].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[3,4,5].map(i=>`<label title="${POT_NAMES[i-3]}">${POT_NAMES[i-3]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="form-group">
      <label>Управленческий портрет (генерируется на основе справочника):</label>
      <textarea id="editPortrait" class="portrait" readonly>${escapeHtml(generatePortrait(emp))}</textarea>
    </div>

    <div class="form-group">
      <label>Управленческое решение:</label>
      <input type="text" id="editDecision" class="decision" value="${escapeHtml(emp.decision || '')}">
    </div>

    <div class="means" id="meansBox"></div>
  `;
  updateMeans();

  box.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('input', () => {
      const v = toNum(inp.value);
      emp.p[+inp.dataset.param] = v;
      if (v !== '') inp.value = v;
      
      $('#editPortrait').value = generatePortrait(emp);
      
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
  $('#editDecision').addEventListener('input', e => {
    emp.decision = e.target.value;
    renderTable();
  });

  function updateMeans(){
    const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
    const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
    const info = (m1 && m2) ? squareInfo(m1, m2) : null;
    $('#meansBox').innerHTML = `Средняя по разделу 1: <b>${m1||'—'}</b> &nbsp;|&nbsp;
      Средняя по разделу 2: <b>${m2||'—'}</b> &nbsp;|&nbsp;
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
    portrait: '',
    decision: '',
    p: ['','','','','',''],
    isNew: true,
    isDeleted: false,
    fioCell: null, posCell: null, portraitCell: null, decisionCell: null,
    paramCells: [null,null,null,null,null,null],
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

    const maxCol = Math.max(COL_DECISION, COL_PORTRAIT, COL_SQUARE, COL_AVG_POT, 15);

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
      const m1 = avg3(p[0], p[1], p[2]);
      const m2 = avg3(p[3], p[4], p[5]);
      const info = squareInfo(m1, m2);
      const portrait = generatePortrait(emp);

      const rowData = new Array(maxCol + 1).fill('');
      rowData[0] = '';
      rowData[COL_FIO] = emp.fio;
      rowData[COL_POS] = emp.position;
      
      COLS_PERF.forEach((c, i) => { rowData[c] = p[i] === '' ? '' : Number(p[i]); });
      COLS_POT.forEach((c, i) => { rowData[c] = p[i+3] === '' ? '' : Number(p[i+3]); });
      
      rowData[COL_AVG_PERF] = m1 || '';
      rowData[COL_AVG_POT] = m2 || '';
      rowData[COL_SQUARE] = info.title;
      rowData[COL_PORTRAIT] = portrait;
      rowData[COL_DECISION] = emp.decision;

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
  td.name { text-align:left; font-weight:600; cursor:pointer; }
  td.name:hover { background:#eef4ff; }
  tr.selected td { background:#e0ecff; }
  input[type=number] { width:56px; padding:4px; text-align:center; border:1px solid var(--border); border-radius:6px; }
  input[type=text].fio { width:200px; padding:6px; border:1px solid var(--border); border-radius:6px; }
  input[type=text].pos { width:200px; padding:6px; border:1px solid var(--border); border-radius:6px; }
  input[type=text].decision { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; margin-top:4px; }
  textarea.portrait { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; min-height:60px; resize:vertical; font-family:inherit; font-size:13px;}
  
  .grid-wrap { display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; max-width:460px; }
  .cell { position: relative; border:1px solid var(--border); border-radius:10px; padding:10px; min-height:110px; }
  .cell h4 { margin:0 0 2px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:14px; font-weight:700; color:#1f2937; margin:2px 0 6px; }
  .cell ul { margin:0; padding-left:16px; font-size:12px; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }
  
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }

  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:12px; font-size:13px; color:#333; width:100%; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }

  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

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
            <th>ФИО</th><th>Должность</th><th id="th_p1">Р1</th><th id="th_p2">Р2</th><th id="th_p3">Р3</th>
            <th id="th_p4">П1</th><th id="th_p5">П2</th><th id="th_p6">П3</th>
            <th>Ср. Эфф.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th>Решение</th><th></th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <div class="panel">
    <h3 style="margin-top:0">Карта 9 квадратов (текущий отдел)</h3>
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

<script>
/* ======================= КОНСТАНТЫ ======================= */
let COL_FIO = 1;
let COL_POS = 2;
let COLS_PERF = [3,4,5];
let COL_AVG_PERF = 6;
let COLS_POT  = [7,8,9];
let COL_AVG_POT  = 10;
let COL_SQUARE   = 11;
let COL_PORTRAIT = 12;
let COL_DECISION = 13;

const DEPTS = ['Кредиты ФЛ', 'Кредиты ЮЛ', 'Транзакт'];

let SQUARE_NAMES = {
  1: '1. Якорь', 2: '2. Пассажир', 3: '3. Звезда',
  4: '4. Проблемный', 5: '5. Стабильный', 6: '6. Результативный',
  7: '7. Аутсайдер', 8: '8. Исполнитель', 9: '9. Профессионал'
};
let PERF_NAMES = ['Дедлайн ЗОД', 'Качество операц. контроля', 'Дисциплина'];
let POT_NAMES = ['Оптимизация процессов', 'Наставничество', 'Стрессоустойчивость'];

let PORTRAIT_TEMPLATES = {
  1: 'Лидер. Максимальная эффективность и высокий потенциал. Готов к повышению.',
  2: 'Исполнитель с потенциалом. Показывает результат, но нужно развивать инициативность.',
  3: 'Перспективный сотрудник. Высокий потенциал, но пока не дотягивает до нужных результатов.',
  4: 'Проблемная зона. Низкая эффективность при среднем потенциале. Требуется контроль.',
  5: 'Стабильный сотрудник. Надежно выполняет работу, но не стремится к росту.',
  6: 'Результативный. Отлично справляется с задачами, но потенциал ограничен.',
  7: 'Зона риска. Высокий потенциал, но крайне низкие результаты.',
  8: 'Аутсайдер. Низкие показатели по обоим направлениям.',
  9: 'Специалист. Высокие результаты, но низкий потенциал (достиг потолка).'
};

let referenceData = null;

function squareInfoForLevels(x, y){
  const map = {
    high: { low:['yellow', 7], mid:['green', 3], high:['green', 1] },
    mid:  { low:['red',    4], mid:['yellow',5], high:['green', 6] },
    low:  { low:['red',    8], mid:['red',   2], high:['yellow',9] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

function generatePortrait(emp) {
  const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
  const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
  if (!m1 || !m2) return 'Оценки не выставлены.';
  
  const info = squareInfo(m1, m2);
  const base = PORTRAIT_TEMPLATES[info.num] || `Квадрат: ${info.title}.`;
  
  const strengths = [];
  const weaknesses = [];
  
  for (let i=0; i<6; i++) {
    const val = Number(emp.p[i]);
    const name = i < 3 ? PERF_NAMES[i] : POT_NAMES[i-3];
    if (val === 3) strengths.push(name);
    if (val === 1) weaknesses.push(name);
  }
  
  let text = base;
  if (strengths.length > 0) text += ` Сильные стороны: ${strengths.join(', ')}.`;
  if (weaknesses.length > 0) text += ` Зоны развития: ${weaknesses.join(', ')}.`;
  return text;
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
const avg3 = (a,b,c)=> +(((a||0)+(b||0)+(c||0))/3).toFixed(2);

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
  box.textContent = '--- ДИАГНОСТИКА (SheetJS ' + (window.XLSX ? XLSX.version : '?') + ') ---\n';
  if (!state.workbook) { logDebug('Файл не загружен.'); return; }
  logDebug('Листы в файле: ' + state.workbook.SheetNames.map(s=>`"${s}"`).join(', '));
  logDebug(`Индексы: ФИО=${COL_FIO}, Должн=${COL_POS}, Перф=${COLS_PERF}, Пот=${COLS_POT}`);
  
  DEPTS.forEach(dept => {
    const realName = findSheet(state.workbook, dept);
    logDebug(`\n[${dept}] -> "${realName || 'НЕ НАЙДЕН'}"`);
    if (realName) {
      logDebug(`  Прочитано: ${state.employees[dept].length}`);
      if (state.employees[dept][0]) {
        const e = state.employees[dept][0];
        logDebug(`  Первый: "${e.fio}", оценки: [${e.p.join(',')}]`);
      }
    }
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
  COLS_PERF = [3,4,5]; COL_AVG_PERF = 6;
  COLS_POT  = [7,8,9]; COL_AVG_POT = 10;
  COL_SQUARE = 11; COL_PORTRAIT = 12; COL_DECISION = 13;

  try {
    if (typeof XLSX === 'undefined') {
      throw new Error('Библиотека SheetJS не загружена. Положите xlsx.full.min.js рядом с index.html.');
    }
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
    state.workbook = wb;
    logDebug('Файл загружен: ' + file.name);
    logDebug('Версия SheetJS: ' + XLSX.version);

    detectColumnsFromHeader(wb);
    readReferenceSheet(wb);

    DEPTS.forEach(dept => {
      state.employees[dept] = readDeptSheet(wb, dept);
    });

    document.querySelectorAll('#deptButtons button').forEach(b => b.disabled = false);
    $('#btnSave').disabled = false;
    $('#btnAdd').disabled = false;

    const total = DEPTS.reduce((s,d) => s + state.employees[d].length, 0);
    if (total === 0) {
      setStatus('Сотрудники не найдены. Откройте 🐞 Диагностику.', true);
    } else {
      setStatus(`Файл загружен. Всего сотрудников: ${total}.`);
    }
    selectDept(DEPTS[0]);
  } catch (err) {
    setStatus('Ошибка чтения файла: ' + err.message, true);
    logDebug('ОШИБКА: ' + err.stack);
  }
});

function detectColumnsFromHeader(wb) {
  let sheetName = null;
  for (const d of DEPTS) {
    const s = findSheet(wb, d);
    if (s) { sheetName = s; break; }
  }
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
  
  if (headerRow === -1) { logDebug('Шапка не найдена.'); return; }
  
  const headerText = {};
  for (let r = headerRow; r <= Math.min(headerRow + 3, aoa.length - 1); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (row[c]) headerText[c] = (headerText[c] || '') + ' ' + String(row[c]).toLowerCase();
    }
  }
  
  const found = {};
  for (let c in headerText) {
    const text = headerText[c];
    const cNum = parseInt(c);
    if (text.includes('фио')) found.fio = cNum;
    else if (text.includes('должност')) found.pos = cNum;
    else if (text.includes('дедлайн')) found.p1 = cNum;
    else if (text.includes('качество')) found.p2 = cNum;
    else if (text.includes('дисциплин')) found.p3 = cNum;
    else if (text.includes('оптимизац')) found.p4 = cNum;
    else if (text.includes('наставнич')) found.p5 = cNum;
    else if (text.includes('стрессоуст')) found.p6 = cNum;
    else if (text.includes('ср. балл') && text.includes('эффектив')) found.avg1 = cNum;
    else if (text.includes('ср. балл') && text.includes('потенциал')) found.avg2 = cNum;
    else if (text.includes('итоговый квадрат') || text.includes('квадрат')) found.sq = cNum;
    else if (text.includes('управленческий портрет')) found.portrait = cNum;
    else if (text.includes('управленческое решение')) found.decision = cNum;
  }
  
  if (found.fio !== undefined) COL_FIO = found.fio;
  if (found.pos !== undefined) COL_POS = found.pos;
  if (found.p1 !== undefined && found.p2 !== undefined && found.p3 !== undefined) COLS_PERF = [found.p1, found.p2, found.p3];
  if (found.p4 !== undefined && found.p5 !== undefined && found.p6 !== undefined) COLS_POT = [found.p4, found.p5, found.p6];
  if (found.avg1 !== undefined) COL_AVG_PERF = found.avg1;
  if (found.avg2 !== undefined) COL_AVG_POT = found.avg2;
  if (found.sq !== undefined) COL_SQUARE = found.sq;
  if (found.portrait !== undefined) COL_PORTRAIT = found.portrait;
  if (found.decision !== undefined) COL_DECISION = found.decision;
  
  logDebug(`Индексы (из шапки): ФИО=${COL_FIO}, Должн=${COL_POS}, Перф=${COLS_PERF}, Пот=${COLS_POT}`);
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
  
  let perfParams = [], potParams = [];
  sections.forEach(sec => {
    if (sec.title.includes('Эффективности')) {
      sec.criteria.forEach(c => perfParams.push(c.name));
    } else if (sec.title.includes('Потенциала')) {
      sec.criteria.forEach(c => potParams.push(c.name));
    }
  });
  
  if (perfParams.length >= 3) PERF_NAMES = perfParams.slice(0, 3);
  if (potParams.length >= 3) POT_NAMES = potParams.slice(0, 3);
  
  setTimeout(() => {
    $('#th_p1').textContent = PERF_NAMES[0];
    $('#th_p2').textContent = PERF_NAMES[1];
    $('#th_p3').textContent = PERF_NAMES[2];
    $('#th_p4').textContent = POT_NAMES[0];
    $('#th_p5').textContent = POT_NAMES[1];
    $('#th_p6').textContent = POT_NAMES[2];
  }, 50);
  
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
  if (!realName) { logDebug(`${sheetName}: лист не найден`); return []; }
  
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
  
  if (startRow === -1) { logDebug(`${sheetName}: шапка не найдена`); return []; }
  
  for (let r = startRow; r < aoa.length; r++) {
    const row = aoa[r] || [];
    const fio = String(row[COL_FIO] || '').trim();
    if (!fio) continue;
    if (fio.toLowerCase() === 'фио' || fio.toLowerCase().includes('сотрудник')) continue;

    // Универсальный геттер для 0.20.3 (иногда .v === undefined)
    const getVal = (c) => {
      const addr = XLSX.utils.encode_cell({ r, c });
      const cell = ws[addr];
      if (!cell) return '';
      if (cell.v !== undefined && cell.v !== null) return cell.v;
      if (cell.w !== undefined && cell.w !== null) return cell.w;
      return '';
    };

    const position = String(getVal(COL_POS) || '').trim();
    const portrait = String(getVal(COL_PORTRAIT) || '').trim();
    const decision = String(getVal(COL_DECISION) || '').trim();

    const p = [];
    COLS_PERF.forEach(c => p.push(toNum(getVal(c))));
    COLS_POT.forEach(c => p.push(toNum(getVal(c))));

    list.push({
      fio, position, portrait, decision, p,
      fioCell: XLSX.utils.encode_cell({ r, c: COL_FIO }),
      posCell: XLSX.utils.encode_cell({ r, c: COL_POS }),
      portraitCell: XLSX.utils.encode_cell({ r, c: COL_PORTRAIT }),
      decisionCell: XLSX.utils.encode_cell({ r, c: COL_DECISION }),
      paramCells: [
        ...COLS_PERF.map(c => XLSX.utils.encode_cell({ r, c })),
        ...COLS_POT.map(c => XLSX.utils.encode_cell({ r, c }))
      ],
      isNew: false, isDeleted: false, row: r
    });
  }

  logDebug(`${sheetName}: прочитано ${list.length} сотрудников`);
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
    const m1 = avg3(p[0],p[1],p[2]);
    const m2 = avg3(p[3],p[4],p[5]);
    const info = squareInfo(m1, m2);
    
    const portraitText = generatePortrait(emp);
    emp.portrait = portraitText;

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:11px;">${escapeHtml(portraitText)}</td>
      <td style="max-width:150px;text-align:left;font-size:11px;">${escapeHtml(emp.decision)}</td>
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

      const members = list.filter(emp => {
        const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
        const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m=>`<li>${escapeHtml(m.fio)}</li>`).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');
      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
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
  
  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1,2].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[3,4,5].map(i=>`<label title="${POT_NAMES[i-3]}">${POT_NAMES[i-3]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="form-group">
      <label>Управленческий портрет (генерируется автоматически):</label>
      <textarea id="editPortrait" class="portrait" readonly>${escapeHtml(generatePortrait(emp))}</textarea>
    </div>

    <div class="form-group">
      <label>Управленческое решение:</label>
      <input type="text" id="editDecision" class="decision" value="${escapeHtml(emp.decision || '')}">
    </div>

    <div class="means" id="meansBox"></div>
  `;
  updateMeans();

  box.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('input', () => {
      const v = toNum(inp.value);
      emp.p[+inp.dataset.param] = v;
      if (v !== '') inp.value = v;
      
      $('#editPortrait').value = generatePortrait(emp);
      
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
  $('#editDecision').addEventListener('input', e => {
    emp.decision = e.target.value;
    renderTable();
  });

  function updateMeans(){
    const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
    const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
    const info = (m1 && m2) ? squareInfo(m1, m2) : null;
    $('#meansBox').innerHTML = `Средняя по разделу 1: <b>${m1||'—'}</b> &nbsp;|&nbsp;
      Средняя по разделу 2: <b>${m2||'—'}</b> &nbsp;|&nbsp;
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
    portrait: '',
    decision: '',
    p: ['','','','','',''],
    isNew: true,
    isDeleted: false,
    fioCell: null, posCell: null, portraitCell: null, decisionCell: null,
    paramCells: [null,null,null,null,null,null],
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

    const maxCol = Math.max(COL_DECISION, COL_PORTRAIT, COL_SQUARE, COL_AVG_POT, 15);

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
      const m1 = avg3(p[0], p[1], p[2]);
      const m2 = avg3(p[3], p[4], p[5]);
      const info = squareInfo(m1, m2);
      const portrait = generatePortrait(emp);

      const rowData = new Array(maxCol + 1).fill('');
      rowData[0] = '';
      rowData[COL_FIO] = emp.fio;
      rowData[COL_POS] = emp.position;
      
      COLS_PERF.forEach((c, i) => { rowData[c] = p[i] === '' ? '' : Number(p[i]); });
      COLS_POT.forEach((c, i) => { rowData[c] = p[i+3] === '' ? '' : Number(p[i+3]); });
      
      rowData[COL_AVG_PERF] = m1 || '';
      rowData[COL_AVG_POT] = m2 || '';
      rowData[COL_SQUARE] = info.title;
      rowData[COL_PORTRAIT] = portrait;
      rowData[COL_DECISION] = emp.decision;

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
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
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
  input[type=text].decision { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; margin-top:4px; }
  textarea.portrait { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; min-height:60px; resize:vertical; font-family:inherit; font-size:13px;}
  
  .grid-wrap { display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; max-width:460px; }
  .cell { position: relative; border:1px solid var(--border); border-radius:10px; padding:10px; min-height:110px; }
  .cell h4 { margin:0 0 2px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:14px; font-weight:700; color:#1f2937; margin:2px 0 6px; }
  .cell ul { margin:0; padding-left:16px; font-size:12px; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }
  
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }

  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:12px; font-size:13px; color:#333; width:100%; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }

  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

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
            <th>ФИО</th><th>Должность</th><th id="th_p1">Р1</th><th id="th_p2">Р2</th><th id="th_p3">Р3</th>
            <th id="th_p4">П1</th><th id="th_p5">П2</th><th id="th_p6">П3</th>
            <th>Ср. Эфф.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th>Решение</th><th></th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <div class="panel">
    <h3 style="margin-top:0">Карта 9 квадратов (текущий отдел)</h3>
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

<script>
/* ======================= КОНСТАНТЫ ======================= */
let COL_FIO = 1;
let COL_POS = 2;
let COLS_PERF = [3,4,5];
let COL_AVG_PERF = 6;
let COLS_POT  = [7,8,9];
let COL_AVG_POT  = 10;
let COL_SQUARE   = 11;
let COL_PORTRAIT = 12;
let COL_DECISION = 13;

// Список отделов (ключи). Можете добавлять/менять
const DEPTS = ['Кредиты ФЛ', 'Кредиты ЮЛ', 'Транзакт'];

let SQUARE_NAMES = {
  1: '1. Якорь', 2: '2. Пассажир', 3: '3. Звезда',
  4: '4. Проблемный', 5: '5. Стабильный', 6: '6. Результативный',
  7: '7. Аутсайдер', 8: '8. Исполнитель', 9: '9. Профессионал'
};
let PERF_NAMES = ['Дедлайн ЗОД', 'Качество операц. контроля', 'Дисциплина'];
let POT_NAMES = ['Оптимизация процессов', 'Наставничество', 'Стрессоустойчивость'];

let PORTRAIT_TEMPLATES = {
  1: 'Лидер. Максимальная эффективность и высокий потенциал. Готов к повышению.',
  2: 'Исполнитель с потенциалом. Показывает результат, но нужно развивать инициативность.',
  3: 'Перспективный сотрудник. Высокий потенциал, но пока не дотягивает до нужных результатов.',
  4: 'Проблемная зона. Низкая эффективность при среднем потенциале. Требуется контроль.',
  5: 'Стабильный сотрудник. Надежно выполняет работу, но не стремится к росту.',
  6: 'Результативный. Отлично справляется с задачами, но потенциал ограничен.',
  7: 'Зона риска. Высокий потенциал, но крайне низкие результаты.',
  8: 'Аутсайдер. Низкие показатели по обоим направлениям.',
  9: 'Специалист. Высокие результаты, но низкий потенциал (достиг потолка).'
};

let referenceData = null;

function squareInfoForLevels(x, y){
  const map = {
    high: { low:['yellow', 7], mid:['green', 3], high:['green', 1] },
    mid:  { low:['red',    4], mid:['yellow',5], high:['green', 6] },
    low:  { low:['red',    8], mid:['red',   2], high:['yellow',9] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

function generatePortrait(emp) {
  const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
  const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
  if (!m1 || !m2) return 'Оценки не выставлены.';
  
  const info = squareInfo(m1, m2);
  const base = PORTRAIT_TEMPLATES[info.num] || `Квадрат: ${info.title}.`;
  
  const strengths = [];
  const weaknesses = [];
  
  for (let i=0; i<6; i++) {
    const val = Number(emp.p[i]);
    const name = i < 3 ? PERF_NAMES[i] : POT_NAMES[i-3];
    if (val === 3) strengths.push(name);
    if (val === 1) weaknesses.push(name);
  }
  
  let text = base;
  if (strengths.length > 0) text += ` Сильные стороны: ${strengths.join(', ')}.`;
  if (weaknesses.length > 0) text += ` Зоны развития: ${weaknesses.join(', ')}.`;
  return text;
}

/* ======================= СОСТОЯНИЕ ======================= */
const state = {
  workbook: null,
  fileName: 'employees.xlsx',
  fileHandle: null,
  currentDept: null,
  employees: {}, // ключи — DEPTS
  selectedIndex: null,
};

DEPTS.forEach(d => state.employees[d] = []);

const $ = sel => document.querySelector(sel);
const avg3 = (a,b,c)=> +(((a||0)+(b||0)+(c||0))/3).toFixed(2);

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

// Универсальный поиск листа по подстроке (без учёта регистра/пробелов)
function findSheet(wb, name) {
  const target = name.toLowerCase().replace(/[\s_\-]/g,'');
  // 1. Точное совпадение
  for (const sn of wb.SheetNames) {
    if (sn.toLowerCase().replace(/[\s_\-]/g,'') === target) return sn;
  }
  // 2. Вхождение подстроки
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
  logDebug('Листы в файле: ' + state.workbook.SheetNames.map(s=>`"${s}"`).join(', '));
  logDebug(`Используемые индексы: ФИО=${COL_FIO}, Должн=${COL_POS}, Перф=${COLS_PERF}, Пот=${COLS_POT}`);
  
  DEPTS.forEach(dept => {
    const realName = findSheet(state.workbook, dept);
    logDebug(`\n[${dept}] -> лист "${realName || 'НЕ НАЙДЕН'}"`);
    if (realName) {
      logDebug(`  Прочитано сотрудников: ${state.employees[dept].length}`);
    }
  });
});

/* ======================= ЧТЕНИЕ ФАЙЛА ======================= */
$('#fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  state.fileName = file.name;
  state.fileHandle = null;
  $('#debugBox').textContent = '';

  // Сброс индексов
  COL_FIO = 1; COL_POS = 2;
  COLS_PERF = [3,4,5]; COL_AVG_PERF = 6;
  COLS_POT  = [7,8,9]; COL_AVG_POT = 10;
  COL_SQUARE = 11; COL_PORTRAIT = 12; COL_DECISION = 13;

  try {
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
    state.workbook = wb;
    logDebug('Файл загружен: ' + file.name);

    detectColumnsFromHeader(wb);
    readReferenceSheet(wb);

    DEPTS.forEach(dept => {
      state.employees[dept] = readDeptSheet(wb, dept);
    });

    document.querySelectorAll('#deptButtons button').forEach(b => b.disabled = false);
    $('#btnSave').disabled = false;
    $('#btnAdd').disabled = false;

    const total = DEPTS.reduce((s,d) => s + state.employees[d].length, 0);
    if (total === 0) {
      setStatus('Сотрудники не найдены. Откройте 🐞 Диагностику.', true);
    } else {
      setStatus(`Файл загружен. Всего сотрудников: ${total}.`);
    }
    selectDept(DEPTS[0]);
  } catch (err) {
    setStatus('Ошибка чтения файла: ' + err.message, true);
    logDebug('ОШИБКА: ' + err.stack);
  }
});

function detectColumnsFromHeader(wb) {
  // Ищем шапку в первом найденном отделе
  let sheetName = null;
  for (const d of DEPTS) {
    const s = findSheet(wb, d);
    if (s) { sheetName = s; break; }
  }
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let headerRow = -1;
  for (let r = 0; r < Math.min(15, aoa.length); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (String(row[c]).toLowerCase().includes('фио')) {
        headerRow = r;
        break;
      }
    }
    if (headerRow !== -1) break;
  }
  
  if (headerRow === -1) { logDebug('Шапка не найдена, используем дефолтные индексы.'); return; }
  
  const headerText = {};
  for (let r = headerRow; r <= Math.min(headerRow + 3, aoa.length - 1); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (row[c]) headerText[c] = (headerText[c] || '') + ' ' + String(row[c]).toLowerCase();
    }
  }
  
  const found = {};
  for (let c in headerText) {
    const text = headerText[c];
    const cNum = parseInt(c);
    if (text.includes('фио')) found.fio = cNum;
    else if (text.includes('должност')) found.pos = cNum;
    else if (text.includes('дедлайн')) found.p1 = cNum;
    else if (text.includes('качество')) found.p2 = cNum;
    else if (text.includes('дисциплин')) found.p3 = cNum;
    else if (text.includes('оптимизац')) found.p4 = cNum;
    else if (text.includes('наставнич')) found.p5 = cNum;
    else if (text.includes('стрессоуст')) found.p6 = cNum;
    else if (text.includes('ср. балл') && text.includes('эффектив')) found.avg1 = cNum;
    else if (text.includes('ср. балл') && text.includes('потенциал')) found.avg2 = cNum;
    else if (text.includes('итоговый квадрат') || text.includes('квадрат')) found.sq = cNum;
    else if (text.includes('управленческий портрет')) found.portrait = cNum;
    else if (text.includes('управленческое решение')) found.decision = cNum;
  }
  
  if (found.fio !== undefined) COL_FIO = found.fio;
  if (found.pos !== undefined) COL_POS = found.pos;
  if (found.p1 !== undefined && found.p2 !== undefined && found.p3 !== undefined) COLS_PERF = [found.p1, found.p2, found.p3];
  if (found.p4 !== undefined && found.p5 !== undefined && found.p6 !== undefined) COLS_POT = [found.p4, found.p5, found.p6];
  if (found.avg1 !== undefined) COL_AVG_PERF = found.avg1;
  if (found.avg2 !== undefined) COL_AVG_POT = found.avg2;
  if (found.sq !== undefined) COL_SQUARE = found.sq;
  if (found.portrait !== undefined) COL_PORTRAIT = found.portrait;
  if (found.decision !== undefined) COL_DECISION = found.decision;
  
  logDebug(`Индексы (из шапки): ФИО=${COL_FIO}, Должн=${COL_POS}, Перф=${COLS_PERF}, Пот=${COLS_POT}`);
}

function readReferenceSheet(wb) {
  const sheetName = findSheet(wb, 'справочник');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
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
  
  let perfParams = [], potParams = [];
  sections.forEach(sec => {
    if (sec.title.includes('Эффективности')) {
      sec.criteria.forEach(c => perfParams.push(c.name));
    } else if (sec.title.includes('Потенциала')) {
      sec.criteria.forEach(c => potParams.push(c.name));
    }
  });
  
  if (perfParams.length >= 3) PERF_NAMES = perfParams.slice(0, 3);
  if (potParams.length >= 3) POT_NAMES = potParams.slice(0, 3);
  
  setTimeout(() => {
    $('#th_p1').textContent = PERF_NAMES[0];
    $('#th_p2').textContent = PERF_NAMES[1];
    $('#th_p3').textContent = PERF_NAMES[2];
    $('#th_p4').textContent = POT_NAMES[0];
    $('#th_p5').textContent = POT_NAMES[1];
    $('#th_p6').textContent = POT_NAMES[2];
  }, 50);
  
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
  if (!realName) { logDebug(`${sheetName}: лист не найден`); return []; }
  
  const ws = wb.Sheets[realName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  const list = [];

  let startRow = -1;
  for (let r = 0; r < Math.min(15, aoa.length); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (String(row[c]).toLowerCase().includes('фио')) {
        startRow = r + 1;
        break;
      }
    }
    if (startRow !== -1) break;
  }
  
  if (startRow === -1) { logDebug(`${sheetName}: шапка не найдена`); return []; }
  
  for (let r = startRow; r < aoa.length; r++) {
    const row = aoa[r] || [];
    const fio = String(row[COL_FIO] || '').trim();
    if (!fio) continue;
    if (fio.toLowerCase() === 'фио' || fio.toLowerCase().includes('сотрудник')) continue;

    const position = String(row[COL_POS] || '').trim();
    const portrait = String(row[COL_PORTRAIT] || '').trim();
    const decision = String(row[COL_DECISION] || '').trim();

    const p = [];
    COLS_PERF.forEach(c => { p.push(toNum(row[c])); });
    COLS_POT.forEach(c => { p.push(toNum(row[c])); });

    const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
    const posAddr = XLSX.utils.encode_cell({ r, c: COL_POS });
    const portraitAddr = XLSX.utils.encode_cell({ r, c: COL_PORTRAIT });
    const decisionAddr = XLSX.utils.encode_cell({ r, c: COL_DECISION });
    
    const paramCells = [
      ...COLS_PERF.map(c => XLSX.utils.encode_cell({ r, c })),
      ...COLS_POT.map(c => XLSX.utils.encode_cell({ r, c }))
    ];

    list.push({
      fio, position, portrait, decision, p,
      fioCell: fioAddr, posCell: posAddr,
      portraitCell: portraitAddr, decisionCell: decisionAddr,
      paramCells, isNew: false, isDeleted: false, row: r
    });
  }

  logDebug(`${sheetName}: прочитано ${list.length} сотрудников`);
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
    const m1 = avg3(p[0],p[1],p[2]);
    const m2 = avg3(p[3],p[4],p[5]);
    const info = squareInfo(m1, m2);
    
    const portraitText = generatePortrait(emp);
    emp.portrait = portraitText;

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:11px;">${escapeHtml(portraitText)}</td>
      <td style="max-width:150px;text-align:left;font-size:11px;">${escapeHtml(emp.decision)}</td>
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

      const members = list.filter(emp => {
        const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
        const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m=>`<li>${escapeHtml(m.fio)}</li>`).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');
      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
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
  
  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1,2].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[3,4,5].map(i=>`<label title="${POT_NAMES[i-3]}">${POT_NAMES[i-3]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="form-group">
      <label>Управленческий портрет (генерируется автоматически):</label>
      <textarea id="editPortrait" class="portrait" readonly>${escapeHtml(generatePortrait(emp))}</textarea>
    </div>

    <div class="form-group">
      <label>Управленческое решение:</label>
      <input type="text" id="editDecision" class="decision" value="${escapeHtml(emp.decision || '')}">
    </div>

    <div class="means" id="meansBox"></div>
  `;
  updateMeans();

  box.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('input', () => {
      const v = toNum(inp.value);
      emp.p[+inp.dataset.param] = v;
      if (v !== '') inp.value = v;
      
      $('#editPortrait').value = generatePortrait(emp);
      
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
  $('#editDecision').addEventListener('input', e => {
    emp.decision = e.target.value;
    renderTable();
  });

  function updateMeans(){
    const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
    const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
    const info = (m1 && m2) ? squareInfo(m1, m2) : null;
    $('#meansBox').innerHTML = `Средняя по разделу 1: <b>${m1||'—'}</b> &nbsp;|&nbsp;
      Средняя по разделу 2: <b>${m2||'—'}</b> &nbsp;|&nbsp;
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
    portrait: '',
    decision: '',
    p: ['','','','','',''],
    isNew: true,
    isDeleted: false,
    fioCell: null, posCell: null, portraitCell: null, decisionCell: null,
    paramCells: [null,null,null,null,null,null],
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

    const maxCol = Math.max(COL_DECISION, COL_PORTRAIT, COL_SQUARE, COL_AVG_POT, 15);

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
      const m1 = avg3(p[0], p[1], p[2]);
      const m2 = avg3(p[3], p[4], p[5]);
      const info = squareInfo(m1, m2);
      const portrait = generatePortrait(emp);

      const rowData = new Array(maxCol + 1).fill('');
      rowData[0] = '';
      rowData[COL_FIO] = emp.fio;
      rowData[COL_POS] = emp.position;
      
      COLS_PERF.forEach((c, i) => { rowData[c] = p[i] === '' ? '' : Number(p[i]); });
      COLS_POT.forEach((c, i) => { rowData[c] = p[i+3] === '' ? '' : Number(p[i+3]); });
      
      rowData[COL_AVG_PERF] = m1 || '';
      rowData[COL_AVG_POT] = m2 || '';
      rowData[COL_SQUARE] = info.title;
      rowData[COL_PORTRAIT] = portrait;
      rowData[COL_DECISION] = emp.decision;

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
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
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
  input[type=text].decision { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; margin-top:4px; }
  textarea.portrait { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; min-height:60px; resize:vertical; font-family:inherit; font-size:13px;}
  
  .grid-wrap { display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; max-width:460px; }
  .cell { position: relative; border:1px solid var(--border); border-radius:10px; padding:10px; min-height:110px; }
  .cell h4 { margin:0 0 2px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:14px; font-weight:700; color:#1f2937; margin:2px 0 6px; }
  .cell ul { margin:0; padding-left:16px; font-size:12px; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }
  
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }

  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:12px; font-size:13px; color:#333; width:100%; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }

  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

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
  <p class="hint" style="margin-top:8px;">
    * В Chrome/Edge при первом сохранении выберите ваш файл — далее он будет перезаписываться без создания копий.
  </p>
</div>

<div class="panel">
  <div class="row" id="deptButtons">
    <button data-dept="отдел1" disabled>Отдел 1</button>
    <button data-dept="отдел2" disabled>Отдел 2</button>
    <button data-dept="отдел3" disabled>Отдел 3</button>
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
            <th>ФИО</th><th>Должность</th><th id="th_p1">Р1</th><th id="th_p2">Р2</th><th id="th_p3">Р3</th>
            <th id="th_p4">П1</th><th id="th_p5">П2</th><th id="th_p6">П3</th>
            <th>Ср. Эфф.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th>Решение</th><th></th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <div class="panel">
    <h3 style="margin-top:0">Карта 9 квадратов (текущий отдел)</h3>
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

<script>
/* ======================= ЖЕСТКИЕ КОНСТАНТЫ ======================= */
// Все индексы 0-based. НЕ МЕНЯЮТСЯ при чтении.
const COL_FIO = 1;         // B
const COL_POS = 2;         // C
const COLS_PERF = [3,4,5]; // D,E,F
const COL_AVG_PERF = 6;    // G
const COLS_POT  = [7,8,9]; // H,I,J
const COL_AVG_POT  = 10;   // K
const COL_SQUARE   = 11;   // L
const COL_PORTRAIT = 12;   // M
const COL_DECISION = 13;   // N

// Жесткая строка начала данных: 5-я строка Excel = индекс 4.
// Если в вашем файле данные начинаются с 6-й строки — поставьте 5.
const DATA_START_ROW = 4;

let SQUARE_NAMES = {
  1: '1. Якорь', 2: '2. Пассажир', 3: '3. Звезда',
  4: '4. Проблемный', 5: '5. Стабильный', 6: '6. Результативный',
  7: '7. Аутсайдер', 8: '8. Исполнитель', 9: '9. Профессионал'
};
let PERF_NAMES = ['Дедлайн ЗОД', 'Качество операц. контроля', 'Дисциплина'];
let POT_NAMES = ['Оптимизация процессов', 'Наставничество', 'Стрессоустойчивость'];

let PORTRAIT_TEMPLATES = {
  1: 'Лидер. Максимальная эффективность и высокий потенциал. Готов к повышению.',
  2: 'Исполнитель с потенциалом. Показывает результат, но нужно развивать инициативность.',
  3: 'Перспективный сотрудник. Высокий потенциал, но пока не дотягивает до нужных результатов.',
  4: 'Проблемная зона. Низкая эффективность при среднем потенциале. Требуется контроль.',
  5: 'Стабильный сотрудник. Надежно выполняет работу, но не стремится к росту.',
  6: 'Результативный. Отлично справляется с задачами, но потенциал ограничен.',
  7: 'Зона риска. Высокий потенциал, но крайне низкие результаты.',
  8: 'Аутсайдер. Низкие показатели по обоим направлениям.',
  9: 'Специалист. Высокие результаты, но низкий потенциал (достиг потолка).'
};

let referenceData = null;

function squareInfoForLevels(x, y){
  const map = {
    high: { low:['yellow', 7], mid:['green', 3], high:['green', 1] },
    mid:  { low:['red',    4], mid:['yellow',5], high:['green', 6] },
    low:  { low:['red',    8], mid:['red',   2], high:['yellow',9] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

function generatePortrait(emp) {
  const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
  const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
  if (!m1 || !m2) return 'Оценки не выставлены.';
  
  const info = squareInfo(m1, m2);
  const base = PORTRAIT_TEMPLATES[info.num] || `Квадрат: ${info.title}.`;
  
  const strengths = [];
  const weaknesses = [];
  
  for (let i=0; i<6; i++) {
    const val = Number(emp.p[i]);
    const name = i < 3 ? PERF_NAMES[i] : POT_NAMES[i-3];
    if (val === 3) strengths.push(name);
    if (val === 1) weaknesses.push(name);
  }
  
  let text = base;
  if (strengths.length > 0) text += ` Сильные стороны: ${strengths.join(', ')}.`;
  if (weaknesses.length > 0) text += ` Зоны развития: ${weaknesses.join(', ')}.`;
  return text;
}

/* ======================= СОСТОЯНИЕ ======================= */
const state = {
  workbook: null,
  fileName: 'employees.xlsx',
  fileHandle: null,
  currentDept: null,
  employees: { 'отдел1': [], 'отдел2': [], 'отдел3': [] },
  selectedIndex: null,
};

const $ = sel => document.querySelector(sel);
const avg3 = (a,b,c)=> +(((a||0)+(b||0)+(c||0))/3).toFixed(2);

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
  logDebug('Листы в файле: ' + state.workbook.SheetNames.map(s=>`"${s}"`).join(', '));
  logDebug(`Использую жесткие индексы: ФИО=${COL_FIO}(B), Должн=${COL_POS}(C), Перф=${COLS_PERF}(D,E,F), Пот=${COLS_POT}(H,I,J), Стартовая строка (0-based)=${DATA_START_ROW} (стр ${DATA_START_ROW+1})`);
  
  ['отдел1','отдел2','отдел3'].forEach(dept => {
    const realName = findSheet(state.workbook, dept);
    if (!realName) { logDebug(`\n[${dept}] лист не найден`); return; }
    const ws = state.workbook.Sheets[realName];
    logDebug(`\n[${dept}] -> "${realName}", ref=${ws['!ref']}`);
    logDebug(`  Прочитано сотрудников: ${state.employees[dept].length}`);
    
    // Показываем первые 5 строк начиная с DATA_START_ROW
    const range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
    for (let r = DATA_START_ROW; r <= Math.min(DATA_START_ROW + 5, range.e.r); r++) {
      const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
      const fioCell = ws[fioAddr];
      const fioVal = fioCell ? fioCell.v : '(пусто)';
      
      const p1Addr = XLSX.utils.encode_cell({ r, c: COLS_PERF[0] });
      const p1Cell = ws[p1Addr];
      const p1Val = p1Cell ? p1Cell.v : '(пусто)';
      
      logDebug(`  Строка ${r+1}: ФИО(B)="${fioVal}", Перф1(D)="${p1Val}"`);
    }
  });
});

/* ======================= ЧТЕНИЕ ФАЙЛА ======================= */
$('#fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  state.fileName = file.name;
  state.fileHandle = null;
  $('#debugBox').textContent = '';

  try {
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
    state.workbook = wb;
    logDebug('Файл загружен: ' + file.name);
    logDebug('Листы: ' + wb.SheetNames.join(', '));

    // 1. Читаем справочник (для отображения, не влияет на индексы)
    readReferenceSheet(wb);

    // 2. Читаем данные отделов (по жестким индексам)
    ['отдел1','отдел2','отдел3'].forEach(dept => {
      state.employees[dept] = readDeptSheet(wb, dept);
    });

    document.querySelectorAll('#deptButtons button').forEach(b => b.disabled = false);
    $('#btnSave').disabled = false;
    $('#btnAdd').disabled = false;

    const total = state.employees['отдел1'].length + state.employees['отдел2'].length + state.employees['отдел3'].length;
    if (total === 0) {
      setStatus('Сотрудники не найдены. Нажмите 🐞 Диагностику.', true);
      // Автоматически открываем диагностику
      $('#debugBox').style.display = 'block';
      $('#btnDebug').click();
    } else {
      setStatus(`Файл загружен. Всего сотрудников: ${total}.`);
    }
    selectDept('отдел1');
  } catch (err) {
    setStatus('Ошибка чтения файла: ' + err.message, true);
    logDebug('ОШИБКА: ' + err.stack);
  }
});

function readReferenceSheet(wb) {
  const sheetName = findSheet(wb, 'справочник');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
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
  
  let perfParams = [], potParams = [];
  sections.forEach(sec => {
    if (sec.title.includes('Эффективности')) {
      sec.criteria.forEach(c => perfParams.push(c.name));
    } else if (sec.title.includes('Потенциала')) {
      sec.criteria.forEach(c => potParams.push(c.name));
    }
  });
  
  if (perfParams.length >= 3) PERF_NAMES = perfParams.slice(0, 3);
  if (potParams.length >= 3) POT_NAMES = potParams.slice(0, 3);
  
  setTimeout(() => {
    $('#th_p1').textContent = PERF_NAMES[0];
    $('#th_p2').textContent = PERF_NAMES[1];
    $('#th_p3').textContent = PERF_NAMES[2];
    $('#th_p4').textContent = POT_NAMES[0];
    $('#th_p5').textContent = POT_NAMES[1];
    $('#th_p6').textContent = POT_NAMES[2];
  }, 50);
  
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

/* ======================= ЧТЕНИЕ ОТДЕЛА (ЖЕСТКО) ======================= */
function readDeptSheet(wb, sheetName){
  const realName = findSheet(wb, sheetName);
  if (!realName) { logDebug(`${sheetName}: лист не найден`); return []; }
  
  const ws = wb.Sheets[realName];
  const range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
  const list = [];

  // Жестко начинаем с DATA_START_ROW
  for (let r = DATA_START_ROW; r <= range.e.r; r++) {
    const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
    const fioCell = ws[fioAddr];
    const fio = fioCell ? String(fioCell.v || '').trim() : '';
    if (!fio) continue;
    if (fio.toLowerCase() === 'фио') continue;

    const posAddr = XLSX.utils.encode_cell({ r, c: COL_POS });
    const posCell = ws[posAddr];
    const position = posCell ? String(posCell.v || '').trim() : '';

    const portraitAddr = XLSX.utils.encode_cell({ r, c: COL_PORTRAIT });
    const portraitCell = ws[portraitAddr];
    const portrait = portraitCell ? String(portraitCell.v || '').trim() : '';

    const decisionAddr = XLSX.utils.encode_cell({ r, c: COL_DECISION });
    const decisionCell = ws[decisionAddr];
    const decision = decisionCell ? String(decisionCell.v || '').trim() : '';

    const p = [];
    COLS_PERF.forEach(c => {
      const addr = XLSX.utils.encode_cell({ r, c });
      const cell = ws[addr];
      p.push(cell ? toNum(cell.v) : '');
    });
    COLS_POT.forEach(c => {
      const addr = XLSX.utils.encode_cell({ r, c });
      const cell = ws[addr];
      p.push(cell ? toNum(cell.v) : '');
    });

    const paramCells = [
      ...COLS_PERF.map(c => XLSX.utils.encode_cell({ r, c })),
      ...COLS_POT.map(c => XLSX.utils.encode_cell({ r, c }))
    ];

    list.push({
      fio, position, portrait, decision, p,
      fioCell: fioAddr, posCell: posAddr,
      portraitCell: portraitAddr, decisionCell: decisionAddr,
      paramCells, isNew: false, isDeleted: false, row: r
    });
  }

  logDebug(`${sheetName}: прочитано ${list.length} сотрудников (с строки ${DATA_START_ROW+1})`);
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
    const m1 = avg3(p[0],p[1],p[2]);
    const m2 = avg3(p[3],p[4],p[5]);
    const info = squareInfo(m1, m2);
    
    const portraitText = generatePortrait(emp);
    emp.portrait = portraitText;

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:11px;">${escapeHtml(portraitText)}</td>
      <td style="max-width:150px;text-align:left;font-size:11px;">${escapeHtml(emp.decision)}</td>
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

      const members = list.filter(emp => {
        const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
        const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m=>`<li>${escapeHtml(m.fio)}</li>`).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');
      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
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
  
  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1,2].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[3,4,5].map(i=>`<label title="${POT_NAMES[i-3]}">${POT_NAMES[i-3]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="form-group">
      <label>Управленческий портрет (генерируется автоматически):</label>
      <textarea id="editPortrait" class="portrait" readonly>${escapeHtml(generatePortrait(emp))}</textarea>
    </div>

    <div class="form-group">
      <label>Управленческое решение:</label>
      <input type="text" id="editDecision" class="decision" value="${escapeHtml(emp.decision || '')}">
    </div>

    <div class="means" id="meansBox"></div>
  `;
  updateMeans();

  box.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('input', () => {
      const v = toNum(inp.value);
      emp.p[+inp.dataset.param] = v;
      if (v !== '') inp.value = v;
      
      $('#editPortrait').value = generatePortrait(emp);
      
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
  $('#editDecision').addEventListener('input', e => {
    emp.decision = e.target.value;
    renderTable();
  });

  function updateMeans(){
    const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
    const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
    const info = (m1 && m2) ? squareInfo(m1, m2) : null;
    $('#meansBox').innerHTML = `Средняя по разделу 1: <b>${m1||'—'}</b> &nbsp;|&nbsp;
      Средняя по разделу 2: <b>${m2||'—'}</b> &nbsp;|&nbsp;
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
    portrait: '',
    decision: '',
    p: ['','','','','',''],
    isNew: true,
    isDeleted: false,
    fioCell: null, posCell: null, portraitCell: null, decisionCell: null,
    paramCells: [null,null,null,null,null,null],
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

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    const realName = findSheet(state.workbook, dept);
    if (!realName) return;
    
    const ws = state.workbook.Sheets[realName];
    const allList = state.employees[dept];
    
    deleted += allList.filter(e => e.isDeleted).length;
    const activeList = allList.filter(e => !e.isDeleted);
    
    // Шапка = все строки до DATA_START_ROW
    const startRow = DATA_START_ROW;
    const maxCol = Math.max(COL_DECISION, COL_PORTRAIT, COL_SQUARE, COL_AVG_POT, 15);

    const headerAOA = [];
    for (let r = 0; r < startRow; r++) {
      const row = new Array(maxCol + 1).fill('');
      for (let c = 0; c <= maxCol; c++) {
        const addr = XLSX.utils.encode_cell({ r, c });
        const cell = ws[addr];
        if (cell && cell.v !== undefined) {
          row[c] = cell.v;
        }
      }
      headerAOA.push(row);
    }

    const dataAOA = [];
    activeList.forEach(emp => {
      const p = emp.p;
      const m1 = avg3(p[0], p[1], p[2]);
      const m2 = avg3(p[3], p[4], p[5]);
      const info = squareInfo(m1, m2);
      const portrait = generatePortrait(emp);

      const rowData = new Array(maxCol + 1).fill('');
      rowData[0] = '';
      rowData[COL_FIO] = emp.fio;
      rowData[COL_POS] = emp.position;
      
      COLS_PERF.forEach((c, i) => { rowData[c] = p[i] === '' ? '' : Number(p[i]); });
      COLS_POT.forEach((c, i) => { rowData[c] = p[i+3] === '' ? '' : Number(p[i+3]); });
      
      rowData[COL_AVG_PERF] = m1 || '';
      rowData[COL_AVG_POT] = m2 || '';
      rowData[COL_SQUARE] = info.title;
      rowData[COL_PORTRAIT] = portrait;
      rowData[COL_DECISION] = emp.decision;

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
    
    if (ws['!cols']) newWs['!cols'] = ws['!cols'];
    if (ws['!merges']) newWs['!merges'] = ws['!merges'];
    if (ws['!rows']) newWs['!rows'] = ws['!rows'];
    
    state.workbook.Sheets[realName] = newWs;
  });

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    state.employees[dept] = state.employees[dept].filter(e => !e.isDeleted);
    
    state.employees[dept].forEach((emp, idx) => {
      emp.row = DATA_START_ROW + idx;
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
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
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
  input[type=text].decision { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; margin-top:4px; }
  textarea.portrait { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; min-height:60px; resize:vertical; font-family:inherit; font-size:13px;}
  
  .grid-wrap { display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; max-width:460px; }
  .cell { position: relative; border:1px solid var(--border); border-radius:10px; padding:10px; min-height:110px; }
  .cell h4 { margin:0 0 2px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:14px; font-weight:700; color:#1f2937; margin:2px 0 6px; }
  .cell ul { margin:0; padding-left:16px; font-size:12px; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }
  
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }

  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:12px; font-size:13px; color:#333; width:100%; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }

  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

  .hint { color:#666; font-size:13px; }
  .status { font-size:13px; color:#166534; }
  .del { color:#b91c1c; cursor:pointer; font-size:12px; }
  .means { font-size:14px; margin:6px 0; }
  .form-group { margin-bottom: 12px; }
  .form-group label { display:block; font-weight:600; margin-bottom:4px; font-size:13px; color:#475467; }
  .debug { background:#f8f9fa; border:1px solid #ddd; padding:8px; font-size:12px; font-family:monospace; color:#333; max-height:150px; overflow:auto; margin-top:8px; display:none; white-space:pre-wrap; }

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
  <p class="hint" style="margin-top:8px;">
    * В Chrome/Edge при первом сохранении выберите ваш файл — далее он будет перезаписываться без создания копий.
  </p>
</div>

<div class="panel">
  <div class="row" id="deptButtons">
    <button data-dept="отдел1" disabled>Отдел 1</button>
    <button data-dept="отдел2" disabled>Отдел 2</button>
    <button data-dept="отдел3" disabled>Отдел 3</button>
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
            <th>ФИО</th><th>Должность</th><th id="th_p1">Р1</th><th id="th_p2">Р2</th><th id="th_p3">Р3</th>
            <th id="th_p4">П1</th><th id="th_p5">П2</th><th id="th_p6">П3</th>
            <th>Ср. Эфф.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th>Решение</th><th></th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <div class="panel">
    <h3 style="margin-top:0">Карта 9 квадратов (текущий отдел)</h3>
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

<script>
/* ======================= КОНСТАНТЫ ======================= */
// Жестко заданные индексы (0-based)
const FIXED_COL_FIO = 1;       // B
const FIXED_COL_POS = 2;       // C
const FIXED_COLS_PERF = [3,4,5]; // D,E,F
const FIXED_COLS_POT  = [7,8,9]; // H,I,J
const FIXED_COL_AVG_PERF = 6;   // G
const FIXED_COL_AVG_POT  = 10;  // K
const FIXED_COL_SQUARE   = 11;  // L
const FIXED_COL_PORTRAIT = 12;  // M
const FIXED_COL_DECISION = 13;  // N

// Переменные, которые могут быть переопределены, если шапка нестандартная
let COL_FIO = FIXED_COL_FIO;
let COL_POS = FIXED_COL_POS;
let COLS_PERF = [...FIXED_COLS_PERF];
let COLS_POT  = [...FIXED_COLS_POT];
let COL_AVG_PERF = FIXED_COL_AVG_PERF;
let COL_AVG_POT  = FIXED_COL_AVG_POT;
let COL_SQUARE   = FIXED_COL_SQUARE;
let COL_PORTRAIT = FIXED_COL_PORTRAIT;
let COL_DECISION = FIXED_COL_DECISION;

let SQUARE_NAMES = {
  1: '1. Якорь', 2: '2. Пассажир', 3: '3. Звезда',
  4: '4. Проблемный', 5: '5. Стабильный', 6: '6. Результативный',
  7: '7. Аутсайдер', 8: '8. Исполнитель', 9: '9. Профессионал'
};
let PERF_NAMES = ['Дедлайн ЗОД', 'Качество операц. контроля', 'Дисциплина'];
let POT_NAMES = ['Оптимизация процессов', 'Наставничество', 'Стрессоустойчивость'];

let PORTRAIT_TEMPLATES = {
  1: 'Лидер. Максимальная эффективность и высокий потенциал. Готов к повышению.',
  2: 'Исполнитель с потенциалом. Показывает результат, но нужно развивать инициативность.',
  3: 'Перспективный сотрудник. Высокий потенциал, но пока не дотягивает до нужных результатов.',
  4: 'Проблемная зона. Низкая эффективность при среднем потенциале. Требуется контроль.',
  5: 'Стабильный сотрудник. Надежно выполняет работу, но не стремится к росту.',
  6: 'Результативный. Отлично справляется с задачами, но потенциал ограничен.',
  7: 'Зона риска. Высокий потенциал, но крайне низкие результаты.',
  8: 'Аутсайдер. Низкие показатели по обоим направлениям.',
  9: 'Специалист. Высокие результаты, но низкий потенциал (достиг потолка).'
};

let referenceData = null;

function squareInfoForLevels(x, y){
  const map = {
    high: { low:['yellow', 7], mid:['green', 3], high:['green', 1] },
    mid:  { low:['red',    4], mid:['yellow',5], high:['green', 6] },
    low:  { low:['red',    8], mid:['red',   2], high:['yellow',9] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

function generatePortrait(emp) {
  const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
  const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
  if (!m1 || !m2) return 'Оценки не выставлены.';
  
  const info = squareInfo(m1, m2);
  const base = PORTRAIT_TEMPLATES[info.num] || `Квадрат: ${info.title}.`;
  
  const strengths = [];
  const weaknesses = [];
  
  for (let i=0; i<6; i++) {
    const val = Number(emp.p[i]);
    const name = i < 3 ? PERF_NAMES[i] : POT_NAMES[i-3];
    if (val === 3) strengths.push(name);
    if (val === 1) weaknesses.push(name);
  }
  
  let text = base;
  if (strengths.length > 0) text += ` Сильные стороны: ${strengths.join(', ')}.`;
  if (weaknesses.length > 0) text += ` Зоны развития: ${weaknesses.join(', ')}.`;
  return text;
}

/* ======================= СОСТОЯНИЕ ======================= */
const state = {
  workbook: null,
  fileName: 'employees.xlsx',
  fileHandle: null,
  currentDept: null,
  employees: { 'отдел1': [], 'отдел2': [], 'отдел3': [] },
  selectedIndex: null,
};

const $ = sel => document.querySelector(sel);
const avg3 = (a,b,c)=> +(((a||0)+(b||0)+(c||0))/3).toFixed(2);

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
  logDebug('Листы в файле: ' + state.workbook.SheetNames.map(s=>`"${s}"`).join(', '));
  
  const testDept = findSheet(state.workbook, 'отдел1');
  if (testDept) {
    const ws = state.workbook.Sheets[testDept];
    const range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
    logDebug(`\nАнализ листа "${testDept}" (диапазон: ${ws['!ref']}):`);
    logDebug(`Используемые индексы: ФИО=${COL_FIO}, Должн=${COL_POS}, Перф=${COLS_PERF}, Пот=${COLS_POT}`);
    
    for (let r = 0; r <= Math.min(8, range.e.r); r++) {
      let rowStr = `Стр ${r+1}: `;
      for (let c = 0; c <= Math.min(15, range.e.c); c++) {
        const addr = XLSX.utils.encode_cell({ r, c });
        const cell = ws[addr];
        if (cell && cell.v !== undefined && String(cell.v).trim() !== '') {
          rowStr += `[${XLSX.utils.encode_col(c)}: "${cell.v}"] `;
        }
      }
      logDebug(rowStr);
    }
  }
  
  ['отдел1','отдел2','отдел3'].forEach(dept => {
    logDebug(`\n[${dept}] прочитано сотрудников: ${state.employees[dept].length}`);
  });
});

/* ======================= ЧТЕНИЕ ФАЙЛА ======================= */
$('#fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  state.fileName = file.name;
  state.fileHandle = null;
  $('#debugBox').textContent = '';

  // Сбрасываем индексы на дефолтные
  COL_FIO = FIXED_COL_FIO;
  COL_POS = FIXED_COL_POS;
  COLS_PERF = [...FIXED_COLS_PERF];
  COLS_POT  = [...FIXED_COLS_POT];
  COL_AVG_PERF = FIXED_COL_AVG_PERF;
  COL_AVG_POT  = FIXED_COL_AVG_POT;
  COL_SQUARE   = FIXED_COL_SQUARE;
  COL_PORTRAIT = FIXED_COL_PORTRAIT;
  COL_DECISION = FIXED_COL_DECISION;

  try {
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
    state.workbook = wb;
    logDebug('Файл загружен: ' + file.name);

    // 1. Пытаемся найти шапку в листе отдела и уточнить индексы
    detectColumnsFromHeader(wb);
    
    // 2. Читаем справочник (только для отображения, НЕ меняет индексы)
    readReferenceSheet(wb);

    // 3. Читаем данные отделов
    ['отдел1','отдел2','отдел3'].forEach(dept => {
      state.employees[dept] = readDeptSheet(wb, dept);
    });

    document.querySelectorAll('#deptButtons button').forEach(b => b.disabled = false);
    $('#btnSave').disabled = false;
    $('#btnAdd').disabled = false;

    const total = state.employees['отдел1'].length + state.employees['отдел2'].length + state.employees['отдел3'].length;
    if (total === 0) {
      setStatus('Сотрудники не найдены. Откройте 🐞 Диагностику.', true);
    } else {
      setStatus(`Файл загружен. Всего сотрудников: ${total}.`);
    }
    selectDept('отдел1');
  } catch (err) {
    setStatus('Ошибка чтения файла: ' + err.message, true);
    logDebug('ОШИБКА: ' + err.stack);
  }
});

function detectColumnsFromHeader(wb) {
  const sheetName = findSheet(wb, 'отдел1') || findSheet(wb, 'отдел2') || findSheet(wb, 'отдел3');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let headerRow = -1;
  for (let r = 0; r < Math.min(15, aoa.length); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (String(row[c]).toLowerCase().includes('фио')) {
        headerRow = r;
        break;
      }
    }
    if (headerRow !== -1) break;
  }
  
  if (headerRow === -1) { logDebug('Строка с "ФИО" не найдена, используем дефолтные индексы.'); return; }
  
  const headerText = {};
  for (let r = headerRow; r <= Math.min(headerRow + 3, aoa.length - 1); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (row[c]) headerText[c] = (headerText[c] || '') + ' ' + String(row[c]).toLowerCase();
    }
  }
  
  const found = {};
  for (let c in headerText) {
    const text = headerText[c];
    const cNum = parseInt(c);
    if (text.includes('фио')) found.fio = cNum;
    else if (text.includes('должност')) found.pos = cNum;
    else if (text.includes('дедлайн')) found.p1 = cNum;
    else if (text.includes('качество')) found.p2 = cNum;
    else if (text.includes('дисциплин')) found.p3 = cNum;
    else if (text.includes('оптимизац')) found.p4 = cNum;
    else if (text.includes('наставнич')) found.p5 = cNum;
    else if (text.includes('стрессоуст')) found.p6 = cNum;
    else if (text.includes('ср. балл') && text.includes('эффектив')) found.avg1 = cNum;
    else if (text.includes('ср. балл') && text.includes('потенциал')) found.avg2 = cNum;
    else if (text.includes('итоговый квадрат') || text.includes('квадрат')) found.sq = cNum;
    else if (text.includes('управленческий портрет')) found.portrait = cNum;
    else if (text.includes('управленческое решение')) found.decision = cNum;
  }
  
  if (found.fio !== undefined) COL_FIO = found.fio;
  if (found.pos !== undefined) COL_POS = found.pos;
  if (found.p1 !== undefined && found.p2 !== undefined && found.p3 !== undefined) COLS_PERF = [found.p1, found.p2, found.p3];
  if (found.p4 !== undefined && found.p5 !== undefined && found.p6 !== undefined) COLS_POT = [found.p4, found.p5, found.p6];
  if (found.avg1 !== undefined) COL_AVG_PERF = found.avg1;
  if (found.avg2 !== undefined) COL_AVG_POT = found.avg2;
  if (found.sq !== undefined) COL_SQUARE = found.sq;
  if (found.portrait !== undefined) COL_PORTRAIT = found.portrait;
  if (found.decision !== undefined) COL_DECISION = found.decision;
  
  logDebug(`Индексы (из шапки): ФИО=${COL_FIO}, Должн=${COL_POS}, Перф=${COLS_PERF}, Пот=${COLS_POT}`);
}

function readReferenceSheet(wb) {
  const sheetName = findSheet(wb, 'справочник');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
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
  
  // Обновляем названия параметров для таблицы (только отображаемые имена, не индексы!)
  let perfParams = [], potParams = [];
  sections.forEach(sec => {
    if (sec.title.includes('Эффективности')) {
      sec.criteria.forEach(c => perfParams.push(c.name));
    } else if (sec.title.includes('Потенциала')) {
      sec.criteria.forEach(c => potParams.push(c.name));
    }
  });
  
  if (perfParams.length >= 3) PERF_NAMES = perfParams.slice(0, 3);
  if (potParams.length >= 3) POT_NAMES = potParams.slice(0, 3);
  
  setTimeout(() => {
    $('#th_p1').textContent = PERF_NAMES[0];
    $('#th_p2').textContent = PERF_NAMES[1];
    $('#th_p3').textContent = PERF_NAMES[2];
    $('#th_p4').textContent = POT_NAMES[0];
    $('#th_p5').textContent = POT_NAMES[1];
    $('#th_p6').textContent = POT_NAMES[2];
  }, 50);
  
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
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  const list = [];

  let startRow = -1;
  for (let r = 0; r < Math.min(15, aoa.length); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (String(row[c]).toLowerCase().includes('фио')) {
        startRow = r + 1;
        break;
      }
    }
    if (startRow !== -1) break;
  }
  
  if (startRow === -1) { logDebug(`${sheetName}: шапка не найдена`); return []; }
  
  for (let r = startRow; r < aoa.length; r++) {
    const row = aoa[r] || [];
    const fio = String(row[COL_FIO] || '').trim();
    if (!fio) continue;
    if (fio.toLowerCase() === 'фио' || fio.toLowerCase().includes('сотрудник')) continue;

    const position = String(row[COL_POS] || '').trim();
    const portrait = String(row[COL_PORTRAIT] || '').trim();
    const decision = String(row[COL_DECISION] || '').trim();

    const p = [];
    COLS_PERF.forEach(c => { p.push(toNum(row[c])); });
    COLS_POT.forEach(c => { p.push(toNum(row[c])); });

    const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
    const posAddr = XLSX.utils.encode_cell({ r, c: COL_POS });
    const portraitAddr = XLSX.utils.encode_cell({ r, c: COL_PORTRAIT });
    const decisionAddr = XLSX.utils.encode_cell({ r, c: COL_DECISION });
    
    const paramCells = [
      ...COLS_PERF.map(c => XLSX.utils.encode_cell({ r, c })),
      ...COLS_POT.map(c => XLSX.utils.encode_cell({ r, c }))
    ];

    list.push({
      fio, position, portrait, decision, p,
      fioCell: fioAddr, posCell: posAddr,
      portraitCell: portraitAddr, decisionCell: decisionAddr,
      paramCells, isNew: false, isDeleted: false, row: r
    });
  }

  logDebug(`${sheetName}: прочитано ${list.length} сотрудников`);
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
    const m1 = avg3(p[0],p[1],p[2]);
    const m2 = avg3(p[3],p[4],p[5]);
    const info = squareInfo(m1, m2);
    
    const portraitText = generatePortrait(emp);
    emp.portrait = portraitText;

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:11px;">${escapeHtml(portraitText)}</td>
      <td style="max-width:150px;text-align:left;font-size:11px;">${escapeHtml(emp.decision)}</td>
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

      const members = list.filter(emp => {
        const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
        const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m=>`<li>${escapeHtml(m.fio)}</li>`).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');
      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
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
  
  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1,2].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[3,4,5].map(i=>`<label title="${POT_NAMES[i-3]}">${POT_NAMES[i-3]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="form-group">
      <label>Управленческий портрет (генерируется автоматически):</label>
      <textarea id="editPortrait" class="portrait" readonly>${escapeHtml(generatePortrait(emp))}</textarea>
    </div>

    <div class="form-group">
      <label>Управленческое решение:</label>
      <input type="text" id="editDecision" class="decision" value="${escapeHtml(emp.decision || '')}">
    </div>

    <div class="means" id="meansBox"></div>
  `;
  updateMeans();

  box.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('input', () => {
      const v = toNum(inp.value);
      emp.p[+inp.dataset.param] = v;
      if (v !== '') inp.value = v;
      
      $('#editPortrait').value = generatePortrait(emp);
      
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
  $('#editDecision').addEventListener('input', e => {
    emp.decision = e.target.value;
    renderTable();
  });

  function updateMeans(){
    const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
    const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
    const info = (m1 && m2) ? squareInfo(m1, m2) : null;
    $('#meansBox').innerHTML = `Средняя по разделу 1: <b>${m1||'—'}</b> &nbsp;|&nbsp;
      Средняя по разделу 2: <b>${m2||'—'}</b> &nbsp;|&nbsp;
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
    portrait: '',
    decision: '',
    p: ['','','','','',''],
    isNew: true,
    isDeleted: false,
    fioCell: null, posCell: null, portraitCell: null, decisionCell: null,
    paramCells: [null,null,null,null,null,null],
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

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    const realName = findSheet(state.workbook, dept);
    if (!realName) return;
    
    const ws = state.workbook.Sheets[realName];
    const allList = state.employees[dept];
    
    deleted += allList.filter(e => e.isDeleted).length;
    const activeList = allList.filter(e => !e.isDeleted);
    
    let startRow = 4;
    const oldEmp = allList.find(e => !e.isNew && !e.isDeleted);
    if (oldEmp && oldEmp.row !== undefined) {
      startRow = oldEmp.row;
    }

    const maxCol = Math.max(COL_DECISION, COL_PORTRAIT, COL_SQUARE, COL_AVG_POT, 15);

    const headerAOA = [];
    for (let r = 0; r < startRow; r++) {
      const row = new Array(maxCol + 1).fill('');
      for (let c = 0; c <= maxCol; c++) {
        const addr = XLSX.utils.encode_cell({ r, c });
        const cell = ws[addr];
        if (cell && cell.v !== undefined) {
          row[c] = cell.v;
        }
      }
      headerAOA.push(row);
    }

    const dataAOA = [];
    activeList.forEach(emp => {
      const p = emp.p;
      const m1 = avg3(p[0], p[1], p[2]);
      const m2 = avg3(p[3], p[4], p[5]);
      const info = squareInfo(m1, m2);
      const portrait = generatePortrait(emp);

      const rowData = new Array(maxCol + 1).fill('');
      rowData[0] = '';
      rowData[COL_FIO] = emp.fio;
      rowData[COL_POS] = emp.position;
      
      COLS_PERF.forEach((c, i) => { rowData[c] = p[i] === '' ? '' : Number(p[i]); });
      COLS_POT.forEach((c, i) => { rowData[c] = p[i+3] === '' ? '' : Number(p[i+3]); });
      
      rowData[COL_AVG_PERF] = m1 || '';
      rowData[COL_AVG_POT] = m2 || '';
      rowData[COL_SQUARE] = info.title;
      rowData[COL_PORTRAIT] = portrait;
      rowData[COL_DECISION] = emp.decision;

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
    
    if (ws['!cols']) newWs['!cols'] = ws['!cols'];
    if (ws['!merges']) newWs['!merges'] = ws['!merges'];
    if (ws['!rows']) newWs['!rows'] = ws['!rows'];
    
    state.workbook.Sheets[realName] = newWs;
  });

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    state.employees[dept] = state.employees[dept].filter(e => !e.isDeleted);
    
    const startRow = 4;
    state.employees[dept].forEach((emp, idx) => {
      emp.row = startRow + idx;
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
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
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
  input[type=text].decision { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; margin-top:4px; }
  textarea.portrait { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; min-height:60px; resize:vertical; font-family:inherit; font-size:13px;}
  
  .grid-wrap { display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; max-width:460px; }
  .cell { position: relative; border:1px solid var(--border); border-radius:10px; padding:10px; min-height:110px; }
  .cell h4 { margin:0 0 2px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:14px; font-weight:700; color:#1f2937; margin:2px 0 6px; }
  .cell ul { margin:0; padding-left:16px; font-size:12px; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }
  
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }

  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:12px; font-size:13px; color:#333; width:100%; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }

  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

  .hint { color:#666; font-size:13px; }
  .status { font-size:13px; color:#166534; }
  .del { color:#b91c1c; cursor:pointer; font-size:12px; }
  .means { font-size:14px; margin:6px 0; }
  .form-group { margin-bottom: 12px; }
  .form-group label { display:block; font-weight:600; margin-bottom:4px; font-size:13px; color:#475467; }
  .debug { background:#f8f9fa; border:1px solid #ddd; padding:8px; font-size:12px; font-family:monospace; color:#333; max-height:150px; overflow:auto; margin-top:8px; display:none; white-space:pre-wrap; }

  /* Стили для просмотра справочника */
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
  <p class="hint" style="margin-top:8px;">
    * В Chrome/Edge при первом сохранении выберите ваш файл — далее он будет перезаписываться без создания копий.
  </p>
</div>

<div class="panel">
  <div class="row" id="deptButtons">
    <button data-dept="отдел1" disabled>Отдел 1</button>
    <button data-dept="отдел2" disabled>Отдел 2</button>
    <button data-dept="отдел3" disabled>Отдел 3</button>
    <button data-dept="справочник" disabled>📖 Справочник</button>
  </div>
</div>

<!-- Основной контейнер для блоков отделов -->
<div id="deptView">
  <div class="panel">
    <h3 style="margin-top:0">Сотрудники отдела</h3>
    <div style="overflow-x:auto;">
      <table id="empTable">
        <thead>
          <tr>
            <th>ФИО</th><th>Должность</th><th id="th_p1">Р1</th><th id="th_p2">Р2</th><th id="th_p3">Р3</th>
            <th id="th_p4">П1</th><th id="th_p5">П2</th><th id="th_p6">П3</th>
            <th>Ср. Эфф.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th>Решение</th><th></th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
  </div>

  <div class="panel">
    <h3 style="margin-top:0">Карта 9 квадратов (текущий отдел)</h3>
    <div class="grid-wrap" id="grid9"></div>
  </div>

  <div class="panel">
    <h3 style="margin-top:0">Редактирование сотрудника</h3>
    <div id="editForm" class="hint">Выберите сотрудника в таблице.</div>
  </div>
</div>

<!-- Контейнер для отображения справочника -->
<div id="refView" style="display:none;">
  <div class="panel">
    <h3 style="margin-top:0">📖 Расширенный справочник критериев и показателей</h3>
    <div id="refContent"></div>
  </div>
</div>

<script>
/* ======================= КОНСТАНТЫ ======================= */
let COL_FIO = 1;
let COL_POS = 2;
let COLS_PERF = [3,4,5];
let COLS_POT  = [7,8,9];
let COL_AVG_PERF = 6;
let COL_AVG_POT  = 10;
let COL_SQUARE   = 11;
let COL_PORTRAIT = 12;
let COL_DECISION = 13;

let SQUARE_NAMES = {
  1: '1. Якорь', 2: '2. Пассажир', 3: '3. Звезда',
  4: '4. Проблемный', 5: '5. Стабильный', 6: '6. Результативный',
  7: '7. Аутсайдер', 8: '8. Исполнитель', 9: '9. Профессионал'
};
let PERF_NAMES = ['Дедлайн ЗОД', 'Качество операц. контроля', 'Дисциплина'];
let POT_NAMES = ['Оптимизация процессов', 'Наставничество', 'Стрессоустойчивость'];

let PORTRAIT_TEMPLATES = {
  1: 'Лидер. Максимальная эффективность и высокий потенциал. Готов к повышению.',
  2: 'Исполнитель с потенциалом. Показывает результат, но нужно развивать инициативность.',
  3: 'Перспективный сотрудник. Высокий потенциал, но пока не дотягивает до нужных результатов.',
  4: 'Проблемная зона. Низкая эффективность при среднем потенциале. Требуется контроль.',
  5: 'Стабильный сотрудник. Надежно выполняет работу, но не стремится к росту.',
  6: 'Результативный. Отлично справляется с задачами, но потенциал ограничен.',
  7: 'Зона риска. Высокий потенциал, но крайне низкие результаты.',
  8: 'Аутсайдер. Низкие показатели по обоим направлениям.',
  9: 'Специалист. Высокие результаты, но низкий потенциал (достиг потолка).'
};

// Данные справочника для отображения (сохраняются при загрузке)
let referenceData = null;

function squareInfoForLevels(x, y){
  const map = {
    high: { low:['yellow', 7], mid:['green', 3], high:['green', 1] },
    mid:  { low:['red',    4], mid:['yellow',5], high:['green', 6] },
    low:  { low:['red',    8], mid:['red',   2], high:['yellow',9] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

function generatePortrait(emp) {
  const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
  const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
  if (!m1 || !m2) return 'Оценки не выставлены.';
  
  const info = squareInfo(m1, m2);
  const base = PORTRAIT_TEMPLATES[info.num] || `Квадрат: ${info.title}.`;
  
  const strengths = [];
  const weaknesses = [];
  
  for (let i=0; i<6; i++) {
    const val = Number(emp.p[i]);
    const name = i < 3 ? PERF_NAMES[i] : POT_NAMES[i-3];
    if (val === 3) strengths.push(name);
    if (val === 1) weaknesses.push(name);
  }
  
  let text = base;
  if (strengths.length > 0) text += ` Сильные стороны: ${strengths.join(', ')}.`;
  if (weaknesses.length > 0) text += ` Зоны развития: ${weaknesses.join(', ')}.`;
  return text;
}

/* ======================= СОСТОЯНИЕ ======================= */
const state = {
  workbook: null,
  fileName: 'employees.xlsx',
  fileHandle: null,
  currentDept: null,
  employees: { 'отдел1': [], 'отдел2': [], 'отдел3': [] },
  selectedIndex: null,
};

const $ = sel => document.querySelector(sel);
const avg3 = (a,b,c)=> +(((a||0)+(b||0)+(c||0))/3).toFixed(2);

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
  logDebug('Листы в файле: ' + state.workbook.SheetNames.map(s=>`"${s}"`).join(', '));
  
  const testDept = findSheet(state.workbook, 'отдел1');
  if (testDept) {
    const ws = state.workbook.Sheets[testDept];
    const range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
    logDebug(`\nАнализ листа "${testDept}" (диапазон: ${ws['!ref']}):`);
    
    for (let r = 0; r <= Math.min(8, range.e.r); r++) {
      let rowStr = `Стр ${r+1}: `;
      for (let c = 0; c <= Math.min(15, range.e.c); c++) {
        const addr = XLSX.utils.encode_cell({ r, c });
        const cell = ws[addr];
        if (cell && cell.v !== undefined && String(cell.v).trim() !== '') {
          rowStr += `[${XLSX.utils.encode_col(c)}: "${cell.v}"] `;
        }
      }
      logDebug(rowStr);
    }
  }
  
  ['отдел1','отдел2','отдел3'].forEach(dept => {
    logDebug(`\n[${dept}] прочитано сотрудников: ${state.employees[dept].length}`);
  });
});

/* ======================= ЧТЕНИЕ ФАЙЛА ======================= */
$('#fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  state.fileName = file.name;
  state.fileHandle = null;
  $('#debugBox').textContent = '';

  try {
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
    state.workbook = wb;
    logDebug('Файл загружен: ' + file.name);

    detectColumnsFromHeader(wb);
    readReferenceSheet(wb);

    ['отдел1','отдел2','отдел3'].forEach(dept => {
      state.employees[dept] = readDeptSheet(wb, dept);
    });

    document.querySelectorAll('#deptButtons button').forEach(b => b.disabled = false);
    $('#btnSave').disabled = false;
    $('#btnAdd').disabled = false;

    const total = state.employees['отдел1'].length + state.employees['отдел2'].length + state.employees['отдел3'].length;
    if (total === 0) {
      setStatus('Сотрудники не найдены. Откройте 🐞 Диагностику.', true);
    } else {
      setStatus(`Файл загружен. Всего сотрудников: ${total}.`);
    }
    selectDept('отдел1');
  } catch (err) {
    setStatus('Ошибка чтения файла: ' + err.message, true);
    logDebug('ОШИБКА: ' + err.stack);
  }
});

function detectColumnsFromHeader(wb) {
  const sheetName = findSheet(wb, 'отдел1') || findSheet(wb, 'отдел2') || findSheet(wb, 'отдел3');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let headerRow = -1;
  for (let r = 0; r < Math.min(15, aoa.length); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (String(row[c]).toLowerCase().includes('фио')) {
        headerRow = r;
        break;
      }
    }
    if (headerRow !== -1) break;
  }
  
  if (headerRow === -1) { logDebug('Строка с "ФИО" не найдена.'); return; }
  
  const headerText = {};
  for (let r = headerRow; r <= Math.min(headerRow + 3, aoa.length - 1); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (row[c]) headerText[c] = (headerText[c] || '') + ' ' + String(row[c]).toLowerCase();
    }
  }
  
  const found = {};
  for (let c in headerText) {
    const text = headerText[c];
    const cNum = parseInt(c);
    if (text.includes('фио')) found.fio = cNum;
    else if (text.includes('должност')) found.pos = cNum;
    else if (text.includes('дедлайн')) found.p1 = cNum;
    else if (text.includes('качество')) found.p2 = cNum;
    else if (text.includes('дисциплин')) found.p3 = cNum;
    else if (text.includes('оптимизац')) found.p4 = cNum;
    else if (text.includes('наставнич')) found.p5 = cNum;
    else if (text.includes('стрессоуст')) found.p6 = cNum;
    else if (text.includes('ср. балл') && text.includes('эффектив')) found.avg1 = cNum;
    else if (text.includes('ср. балл') && text.includes('потенциал')) found.avg2 = cNum;
    else if (text.includes('итоговый квадрат') || text.includes('квадрат')) found.sq = cNum;
    else if (text.includes('управленческий портрет')) found.portrait = cNum;
    else if (text.includes('управленческое решение')) found.decision = cNum;
  }
  
  if (found.fio !== undefined) COL_FIO = found.fio;
  if (found.pos !== undefined) COL_POS = found.pos;
  if (found.p1 !== undefined && found.p2 !== undefined && found.p3 !== undefined) COLS_PERF = [found.p1, found.p2, found.p3];
  if (found.p4 !== undefined && found.p5 !== undefined && found.p6 !== undefined) COLS_POT = [found.p4, found.p5, found.p6];
  if (found.avg1 !== undefined) COL_AVG_PERF = found.avg1;
  if (found.avg2 !== undefined) COL_AVG_POT = found.avg2;
  if (found.sq !== undefined) COL_SQUARE = found.sq;
  if (found.portrait !== undefined) COL_PORTRAIT = found.portrait;
  if (found.decision !== undefined) COL_DECISION = found.decision;
  
  logDebug(`Индексы: ФИО=${COL_FIO}, Должн=${COL_POS}, Перф=${COLS_PERF}, Пот=${COLS_POT}, Avg1=${COL_AVG_PERF}, Avg2=${COL_AVG_POT}, Sq=${COL_SQUARE}`);
}

function readReferenceSheet(wb) {
  const sheetName = findSheet(wb, 'справочник');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  // Парсим справочник в структурированном виде
  const sections = [];
  let currentSection = null;
  let currentCriterion = null;
  
  for (let r = 0; r < aoa.length; r++) {
    const row = aoa[r] || [];
    const col0 = String(row[0] || '').trim();
    const col1 = String(row[1] || '').trim();
    const col2 = String(row[2] || '').trim();
    const col3 = String(row[3] || '').trim();
    const col4 = String(row[4] || '').trim();
    
    // Заголовки осей
    if (col0.includes('Ось Эффективности') || col0.includes('Ось Потенциала')) {
      currentSection = { title: col0, criteria: [] };
      sections.push(currentSection);
      currentCriterion = null;
      continue;
    }
    
    // Заголовок таблицы критериев (Показатель | 1 балл | 2 балла | 3 балла)
    if (col0 === 'Показатель' || col1 === '1 балл (Низкий уровень)') {
      continue; // пропускаем строку заголовка
    }
    
    // Строка критерия
    if (currentSection && col0) {
      // Если заполнены 1, 2, 3 балл — это новый критерий
      if (col1 || col2 || col3) {
        currentCriterion = {
          name: col0,
          level1: col1,
          level2: col2,
          level3: col3
        };
        currentSection.criteria.push(currentCriterion);
      } else if (currentCriterion && !col1 && !col2 && !col3) {
        // Продолжение названия критерия (многострочное)
        currentCriterion.name += ' ' + col0;
      }
    }
  }
  
  referenceData = sections;
  
  // Обновляем названия параметров для таблицы
  let perfParams = [], potParams = [];
  sections.forEach(sec => {
    if (sec.title.includes('Эффективности')) {
      sec.criteria.forEach(c => perfParams.push(c.name));
    } else if (sec.title.includes('Потенциала')) {
      sec.criteria.forEach(c => potParams.push(c.name));
    }
  });
  
  if (perfParams.length >= 3) PERF_NAMES = perfParams.slice(0, 3);
  if (potParams.length >= 3) POT_NAMES = potParams.slice(0, 3);
  
  setTimeout(() => {
    $('#th_p1').textContent = PERF_NAMES[0];
    $('#th_p2').textContent = PERF_NAMES[1];
    $('#th_p3').textContent = PERF_NAMES[2];
    $('#th_p4').textContent = POT_NAMES[0];
    $('#th_p5').textContent = POT_NAMES[1];
    $('#th_p6').textContent = POT_NAMES[2];
  }, 50);
  
  // Отрисовываем справочник
  renderReferenceView();
}

// Отрисовка справочника
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
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  const list = [];

  let startRow = -1;
  for (let r = 0; r < Math.min(15, aoa.length); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (String(row[c]).toLowerCase().includes('фио')) {
        startRow = r + 1;
        break;
      }
    }
    if (startRow !== -1) break;
  }
  
  if (startRow === -1) { logDebug(`${sheetName}: шапка не найдена`); return []; }
  
  for (let r = startRow; r < aoa.length; r++) {
    const row = aoa[r] || [];
    const fio = String(row[COL_FIO] || '').trim();
    if (!fio) continue;
    if (fio.toLowerCase() === 'фио' || fio.toLowerCase().includes('сотрудник')) continue;

    const position = String(row[COL_POS] || '').trim();
    const portrait = String(row[COL_PORTRAIT] || '').trim();
    const decision = String(row[COL_DECISION] || '').trim();

    const p = [];
    COLS_PERF.forEach(c => { p.push(toNum(row[c])); });
    COLS_POT.forEach(c => { p.push(toNum(row[c])); });

    const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
    const posAddr = XLSX.utils.encode_cell({ r, c: COL_POS });
    const portraitAddr = XLSX.utils.encode_cell({ r, c: COL_PORTRAIT });
    const decisionAddr = XLSX.utils.encode_cell({ r, c: COL_DECISION });
    
    const paramCells = [
      ...COLS_PERF.map(c => XLSX.utils.encode_cell({ r, c })),
      ...COLS_POT.map(c => XLSX.utils.encode_cell({ r, c }))
    ];

    list.push({
      fio, position, portrait, decision, p,
      fioCell: fioAddr, posCell: posAddr,
      portraitCell: portraitAddr, decisionCell: decisionAddr,
      paramCells, isNew: false, isDeleted: false, row: r
    });
  }

  logDebug(`${sheetName}: прочитано ${list.length} сотрудников`);
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
  
  // Переключаем видимость
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
    const m1 = avg3(p[0],p[1],p[2]);
    const m2 = avg3(p[3],p[4],p[5]);
    const info = squareInfo(m1, m2);
    
    const portraitText = generatePortrait(emp);
    emp.portrait = portraitText;

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:11px;">${escapeHtml(portraitText)}</td>
      <td style="max-width:150px;text-align:left;font-size:11px;">${escapeHtml(emp.decision)}</td>
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

      const members = list.filter(emp => {
        const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
        const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m=>`<li>${escapeHtml(m.fio)}</li>`).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');
      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
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
  
  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1,2].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[3,4,5].map(i=>`<label title="${POT_NAMES[i-3]}">${POT_NAMES[i-3]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="form-group">
      <label>Управленческий портрет (генерируется автоматически):</label>
      <textarea id="editPortrait" class="portrait" readonly>${escapeHtml(generatePortrait(emp))}</textarea>
    </div>

    <div class="form-group">
      <label>Управленческое решение:</label>
      <input type="text" id="editDecision" class="decision" value="${escapeHtml(emp.decision || '')}">
    </div>

    <div class="means" id="meansBox"></div>
  `;
  updateMeans();

  box.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('input', () => {
      const v = toNum(inp.value);
      emp.p[+inp.dataset.param] = v;
      if (v !== '') inp.value = v;
      
      $('#editPortrait').value = generatePortrait(emp);
      
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
  $('#editDecision').addEventListener('input', e => {
    emp.decision = e.target.value;
    renderTable();
  });

  function updateMeans(){
    const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
    const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
    const info = (m1 && m2) ? squareInfo(m1, m2) : null;
    $('#meansBox').innerHTML = `Средняя по разделу 1: <b>${m1||'—'}</b> &nbsp;|&nbsp;
      Средняя по разделу 2: <b>${m2||'—'}</b> &nbsp;|&nbsp;
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
    portrait: '',
    decision: '',
    p: ['','','','','',''],
    isNew: true,
    isDeleted: false,
    fioCell: null, posCell: null, portraitCell: null, decisionCell: null,
    paramCells: [null,null,null,null,null,null],
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

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    const realName = findSheet(state.workbook, dept);
    if (!realName) return;
    
    const ws = state.workbook.Sheets[realName];
    const allList = state.employees[dept];
    
    deleted += allList.filter(e => e.isDeleted).length;
    const activeList = allList.filter(e => !e.isDeleted);
    
    let startRow = 4;
    const oldEmp = allList.find(e => !e.isNew && !e.isDeleted);
    if (oldEmp && oldEmp.row !== undefined) {
      startRow = oldEmp.row;
    }

    const maxCol = Math.max(COL_DECISION, COL_PORTRAIT, COL_SQUARE, COL_AVG_POT, 15);

    const headerAOA = [];
    for (let r = 0; r < startRow; r++) {
      const row = new Array(maxCol + 1).fill('');
      for (let c = 0; c <= maxCol; c++) {
        const addr = XLSX.utils.encode_cell({ r, c });
        const cell = ws[addr];
        if (cell && cell.v !== undefined) {
          row[c] = cell.v;
        }
      }
      headerAOA.push(row);
    }

    const dataAOA = [];
    activeList.forEach(emp => {
      const p = emp.p;
      const m1 = avg3(p[0], p[1], p[2]);
      const m2 = avg3(p[3], p[4], p[5]);
      const info = squareInfo(m1, m2);
      const portrait = generatePortrait(emp);

      const rowData = new Array(maxCol + 1).fill('');
      rowData[0] = '';
      rowData[COL_FIO] = emp.fio;
      rowData[COL_POS] = emp.position;
      
      COLS_PERF.forEach((c, i) => { rowData[c] = p[i] === '' ? '' : Number(p[i]); });
      COLS_POT.forEach((c, i) => { rowData[c] = p[i+3] === '' ? '' : Number(p[i+3]); });
      
      rowData[COL_AVG_PERF] = m1 || '';
      rowData[COL_AVG_POT] = m2 || '';
      rowData[COL_SQUARE] = info.title;
      rowData[COL_PORTRAIT] = portrait;
      rowData[COL_DECISION] = emp.decision;

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
    
    if (ws['!cols']) newWs['!cols'] = ws['!cols'];
    if (ws['!merges']) newWs['!merges'] = ws['!merges'];
    if (ws['!rows']) newWs['!rows'] = ws['!rows'];
    
    state.workbook.Sheets[realName] = newWs;
  });

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    state.employees[dept] = state.employees[dept].filter(e => !e.isDeleted);
    
    const startRow = 4;
    state.employees[dept].forEach((emp, idx) => {
      emp.row = startRow + idx;
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
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
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
  input[type=text].decision { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; margin-top:4px; }
  textarea.portrait { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; min-height:60px; resize:vertical; font-family:inherit; font-size:13px;}
  
  .grid-wrap { display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; max-width:460px; }
  .cell { position: relative; border:1px solid var(--border); border-radius:10px; padding:10px; min-height:110px; }
  .cell h4 { margin:0 0 2px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:14px; font-weight:700; color:#1f2937; margin:2px 0 6px; }
  .cell ul { margin:0; padding-left:16px; font-size:12px; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }
  
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }

  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:12px; font-size:13px; color:#333; width:100%; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }

  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

  .hint { color:#666; font-size:13px; }
  .status { font-size:13px; color:#166534; }
  .del { color:#b91c1c; cursor:pointer; font-size:12px; }
  .means { font-size:14px; margin:6px 0; }
  .form-group { margin-bottom: 12px; }
  .form-group label { display:block; font-weight:600; margin-bottom:4px; font-size:13px; color:#475467; }
  .debug { background:#f8f9fa; border:1px solid #ddd; padding:8px; font-size:12px; font-family:monospace; color:#333; max-height:150px; overflow:auto; margin-top:8px; display:none; white-space:pre-wrap; }
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
  <p class="hint" style="margin-top:8px;">
    * В Chrome/Edge при первом сохранении выберите ваш файл — далее он будет перезаписываться без создания копий.
  </p>
</div>

<div class="panel">
  <div class="row" id="deptButtons">
    <button data-dept="отдел1" disabled>Отдел 1</button>
    <button data-dept="отдел2" disabled>Отдел 2</button>
    <button data-dept="отдел3" disabled>Отдел 3</button>
  </div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Сотрудники отдела</h3>
  <div style="overflow-x:auto;">
    <table id="empTable">
      <thead>
        <tr>
          <th>ФИО</th><th>Должность</th><th id="th_p1">Р1</th><th id="th_p2">Р2</th><th id="th_p3">Р3</th>
          <th id="th_p4">П1</th><th id="th_p5">П2</th><th id="th_p6">П3</th>
          <th>Ср. Эфф.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th>Решение</th><th></th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Карта 9 квадратов (текущий отдел)</h3>
  <div class="grid-wrap" id="grid9"></div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Редактирование сотрудника</h3>
  <div id="editForm" class="hint">Выберите сотрудника в таблице.</div>
</div>

<script>
/* ======================= КОНСТАНТЫ ======================= */
let COL_FIO = 1;
let COL_POS = 2;
let COLS_PERF = [3,4,5];
let COLS_POT  = [7,8,9];
let COL_AVG_PERF = 6;
let COL_AVG_POT  = 10;
let COL_SQUARE   = 11;
let COL_PORTRAIT = 12;
let COL_DECISION = 13;

let SQUARE_NAMES = {
  1: '1. Якорь', 2: '2. Пассажир', 3: '3. Звезда',
  4: '4. Проблемный', 5: '5. Стабильный', 6: '6. Результативный',
  7: '7. Аутсайдер', 8: '8. Исполнитель', 9: '9. Профессионал'
};
let PERF_NAMES = ['Дедлайн ЗОД', 'Качество операц. контроля', 'Дисциплина'];
let POT_NAMES = ['Оптимизация процессов', 'Наставничество', 'Стрессоустойчивость'];

let PORTRAIT_TEMPLATES = {
  1: 'Лидер. Максимальная эффективность и высокий потенциал. Готов к повышению.',
  2: 'Исполнитель с потенциалом. Показывает результат, но нужно развивать инициативность.',
  3: 'Перспективный сотрудник. Высокий потенциал, но пока не дотягивает до нужных результатов.',
  4: 'Проблемная зона. Низкая эффективность при среднем потенциале. Требуется контроль.',
  5: 'Стабильный сотрудник. Надежно выполняет работу, но не стремится к росту.',
  6: 'Результативный. Отлично справляется с задачами, но потенциал ограничен.',
  7: 'Зона риска. Высокий потенциал, но крайне низкие результаты.',
  8: 'Аутсайдер. Низкие показатели по обоим направлениям.',
  9: 'Специалист. Высокие результаты, но низкий потенциал (достиг потолка).'
};

function squareInfoForLevels(x, y){
  const map = {
    high: { low:['yellow', 7], mid:['green', 3], high:['green', 1] },
    mid:  { low:['red',    4], mid:['yellow',5], high:['green', 6] },
    low:  { low:['red',    8], mid:['red',   2], high:['yellow',9] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

function generatePortrait(emp) {
  const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
  const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
  if (!m1 || !m2) return 'Оценки не выставлены.';
  
  const info = squareInfo(m1, m2);
  const base = PORTRAIT_TEMPLATES[info.num] || `Квадрат: ${info.title}.`;
  
  const strengths = [];
  const weaknesses = [];
  
  for (let i=0; i<6; i++) {
    const val = Number(emp.p[i]);
    const name = i < 3 ? PERF_NAMES[i] : POT_NAMES[i-3];
    if (val === 3) strengths.push(name);
    if (val === 1) weaknesses.push(name);
  }
  
  let text = base;
  if (strengths.length > 0) text += ` Сильные стороны: ${strengths.join(', ')}.`;
  if (weaknesses.length > 0) text += ` Зоны развития: ${weaknesses.join(', ')}.`;
  return text;
}

/* ======================= СОСТОЯНИЕ ======================= */
const state = {
  workbook: null,
  fileName: 'employees.xlsx',
  fileHandle: null,
  currentDept: null,
  employees: { 'отдел1': [], 'отдел2': [], 'отдел3': [] },
  selectedIndex: null,
};

const $ = sel => document.querySelector(sel);
const avg3 = (a,b,c)=> +(((a||0)+(b||0)+(c||0))/3).toFixed(2);

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
  logDebug('Листы в файле: ' + state.workbook.SheetNames.map(s=>`"${s}"`).join(', '));
  
  const testDept = findSheet(state.workbook, 'отдел1');
  if (testDept) {
    const ws = state.workbook.Sheets[testDept];
    const range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
    logDebug(`\nАнализ листа "${testDept}" (диапазон: ${ws['!ref']}):`);
    
    for (let r = 0; r <= Math.min(8, range.e.r); r++) {
      let rowStr = `Стр ${r+1}: `;
      for (let c = 0; c <= Math.min(15, range.e.c); c++) {
        const addr = XLSX.utils.encode_cell({ r, c });
        const cell = ws[addr];
        if (cell && cell.v !== undefined && String(cell.v).trim() !== '') {
          rowStr += `[${XLSX.utils.encode_col(c)}: "${cell.v}"] `;
        }
      }
      logDebug(rowStr);
    }
  }
  
  ['отдел1','отдел2','отдел3'].forEach(dept => {
    logDebug(`\n[${dept}] прочитано сотрудников: ${state.employees[dept].length}`);
  });
});

/* ======================= ЧТЕНИЕ ФАЙЛА ======================= */
$('#fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  state.fileName = file.name;
  state.fileHandle = null;
  $('#debugBox').textContent = '';

  try {
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
    state.workbook = wb;
    logDebug('Файл загружен: ' + file.name);

    detectColumnsFromHeader(wb);
    readReferenceSheet(wb);

    ['отдел1','отдел2','отдел3'].forEach(dept => {
      state.employees[dept] = readDeptSheet(wb, dept);
    });

    document.querySelectorAll('#deptButtons button').forEach(b => b.disabled = false);
    $('#btnSave').disabled = false;
    $('#btnAdd').disabled = false;

    const total = state.employees['отдел1'].length + state.employees['отдел2'].length + state.employees['отдел3'].length;
    if (total === 0) {
      setStatus('Сотрудники не найдены. Откройте 🐞 Диагностику.', true);
    } else {
      setStatus(`Файл загружен. Всего сотрудников: ${total}.`);
    }
    selectDept('отдел1');
  } catch (err) {
    setStatus('Ошибка чтения файла: ' + err.message, true);
    logDebug('ОШИБКА: ' + err.stack);
  }
});

function detectColumnsFromHeader(wb) {
  const sheetName = findSheet(wb, 'отдел1') || findSheet(wb, 'отдел2') || findSheet(wb, 'отдел3');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let headerRow = -1;
  for (let r = 0; r < Math.min(15, aoa.length); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (String(row[c]).toLowerCase().includes('фио')) {
        headerRow = r;
        break;
      }
    }
    if (headerRow !== -1) break;
  }
  
  if (headerRow === -1) { logDebug('Строка с "ФИО" не найдена.'); return; }
  
  const headerText = {};
  for (let r = headerRow; r <= Math.min(headerRow + 3, aoa.length - 1); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (row[c]) headerText[c] = (headerText[c] || '') + ' ' + String(row[c]).toLowerCase();
    }
  }
  
  const found = {};
  for (let c in headerText) {
    const text = headerText[c];
    const cNum = parseInt(c);
    if (text.includes('фио')) found.fio = cNum;
    else if (text.includes('должност')) found.pos = cNum;
    else if (text.includes('дедлайн')) found.p1 = cNum;
    else if (text.includes('качество')) found.p2 = cNum;
    else if (text.includes('дисциплин')) found.p3 = cNum;
    else if (text.includes('оптимизац')) found.p4 = cNum;
    else if (text.includes('наставнич')) found.p5 = cNum;
    else if (text.includes('стрессоуст')) found.p6 = cNum;
    else if (text.includes('ср. балл') && text.includes('эффектив')) found.avg1 = cNum;
    else if (text.includes('ср. балл') && text.includes('потенциал')) found.avg2 = cNum;
    else if (text.includes('итоговый квадрат') || text.includes('квадрат')) found.sq = cNum;
    else if (text.includes('управленческий портрет')) found.portrait = cNum;
    else if (text.includes('управленческое решение')) found.decision = cNum;
  }
  
  if (found.fio !== undefined) COL_FIO = found.fio;
  if (found.pos !== undefined) COL_POS = found.pos;
  if (found.p1 !== undefined && found.p2 !== undefined && found.p3 !== undefined) COLS_PERF = [found.p1, found.p2, found.p3];
  if (found.p4 !== undefined && found.p5 !== undefined && found.p6 !== undefined) COLS_POT = [found.p4, found.p5, found.p6];
  if (found.avg1 !== undefined) COL_AVG_PERF = found.avg1;
  if (found.avg2 !== undefined) COL_AVG_POT = found.avg2;
  if (found.sq !== undefined) COL_SQUARE = found.sq;
  if (found.portrait !== undefined) COL_PORTRAIT = found.portrait;
  if (found.decision !== undefined) COL_DECISION = found.decision;
  
  logDebug(`Индексы: ФИО=${COL_FIO}, Должн=${COL_POS}, Перф=${COLS_PERF}, Пот=${COLS_POT}, Avg1=${COL_AVG_PERF}, Avg2=${COL_AVG_POT}, Sq=${COL_SQUARE}`);
}

function readReferenceSheet(wb) {
  const sheetName = findSheet(wb, 'справочник');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let perfParams = [], potParams = [], currentMode = '';

  for (let r = 0; r < aoa.length; r++) {
    const row = aoa[r];
    const col0 = String(row[0] || '').trim();
    
    if (col0.includes('Ось Эффективности')) { currentMode = 'perf'; continue; }
    if (col0.includes('Ось Потенциала')) { currentMode = 'pot'; continue; }

    if (currentMode === 'perf' && col0 && col0 !== 'Показатель') perfParams.push(col0);
    if (currentMode === 'pot' && col0 && col0 !== 'Показатель') potParams.push(col0);
  }

  if (perfParams.length >= 3) PERF_NAMES = perfParams.slice(0, 3);
  if (potParams.length >= 3) POT_NAMES = potParams.slice(0, 3);
  
  setTimeout(() => {
    $('#th_p1').textContent = PERF_NAMES[0];
    $('#th_p2').textContent = PERF_NAMES[1];
    $('#th_p3').textContent = PERF_NAMES[2];
    $('#th_p4').textContent = POT_NAMES[0];
    $('#th_p5').textContent = POT_NAMES[1];
    $('#th_p6').textContent = POT_NAMES[2];
  }, 50);
}

function readDeptSheet(wb, sheetName){
  const realName = findSheet(wb, sheetName);
  if (!realName) return [];
  
  const ws = wb.Sheets[realName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  const list = [];

  let startRow = -1;
  for (let r = 0; r < Math.min(15, aoa.length); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (String(row[c]).toLowerCase().includes('фио')) {
        startRow = r + 1;
        break;
      }
    }
    if (startRow !== -1) break;
  }
  
  if (startRow === -1) { logDebug(`${sheetName}: шапка не найдена`); return []; }
  
  for (let r = startRow; r < aoa.length; r++) {
    const row = aoa[r] || [];
    const fio = String(row[COL_FIO] || '').trim();
    if (!fio) continue;
    if (fio.toLowerCase() === 'фио' || fio.toLowerCase().includes('сотрудник')) continue;

    const position = String(row[COL_POS] || '').trim();
    const portrait = String(row[COL_PORTRAIT] || '').trim();
    const decision = String(row[COL_DECISION] || '').trim();

    const p = [];
    COLS_PERF.forEach(c => { p.push(toNum(row[c])); });
    COLS_POT.forEach(c => { p.push(toNum(row[c])); });

    const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
    const posAddr = XLSX.utils.encode_cell({ r, c: COL_POS });
    const portraitAddr = XLSX.utils.encode_cell({ r, c: COL_PORTRAIT });
    const decisionAddr = XLSX.utils.encode_cell({ r, c: COL_DECISION });
    
    const paramCells = [
      ...COLS_PERF.map(c => XLSX.utils.encode_cell({ r, c })),
      ...COLS_POT.map(c => XLSX.utils.encode_cell({ r, c }))
    ];

    list.push({
      fio, position, portrait, decision, p,
      fioCell: fioAddr, posCell: posAddr,
      portraitCell: portraitAddr, decisionCell: decisionAddr,
      paramCells, isNew: false, isDeleted: false, row: r
    });
  }

  logDebug(`${sheetName}: прочитано ${list.length} сотрудников`);
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
  renderTable(); renderGrid(); renderEditForm();
}

/* ======================= ТАБЛИЦА ======================= */
function renderTable(){
  const tbody = $('#empTable tbody');
  tbody.innerHTML = '';
  const dept = state.currentDept;
  if (!dept) return;
  
  const list = state.employees[dept].filter(e => !e.isDeleted);

  list.forEach((emp, idx) => {
    const p = emp.p;
    const m1 = avg3(p[0],p[1],p[2]);
    const m2 = avg3(p[3],p[4],p[5]);
    const info = squareInfo(m1, m2);
    
    const portraitText = generatePortrait(emp);
    emp.portrait = portraitText;

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:11px;">${escapeHtml(portraitText)}</td>
      <td style="max-width:150px;text-align:left;font-size:11px;">${escapeHtml(emp.decision)}</td>
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
  if (!dept) return;
  
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

      const members = list.filter(emp => {
        const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
        const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m=>`<li>${escapeHtml(m.fio)}</li>`).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');
      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
  `;
  wrap.appendChild(legend);
}

/* ======================= ФОРМА РЕДАКТИРОВАНИЯ ======================= */
function renderEditForm(){
  const box = $('#editForm');
  const dept = state.currentDept;
  if (!dept) { box.innerHTML = '<span class="hint">Выберите отдел.</span>'; return; }
  
  const list = state.employees[dept].filter(e => !e.isDeleted);
  
  if (state.selectedIndex === null || !list[state.selectedIndex]){
    box.innerHTML = '<span class="hint">Выберите сотрудника в таблице.</span>';
    return;
  }
  const emp = list[state.selectedIndex];
  
  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1,2].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[3,4,5].map(i=>`<label title="${POT_NAMES[i-3]}">${POT_NAMES[i-3]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="form-group">
      <label>Управленческий портрет (генерируется автоматически):</label>
      <textarea id="editPortrait" class="portrait" readonly>${escapeHtml(generatePortrait(emp))}</textarea>
    </div>

    <div class="form-group">
      <label>Управленческое решение:</label>
      <input type="text" id="editDecision" class="decision" value="${escapeHtml(emp.decision || '')}">
    </div>

    <div class="means" id="meansBox"></div>
  `;
  updateMeans();

  box.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('input', () => {
      const v = toNum(inp.value);
      emp.p[+inp.dataset.param] = v;
      if (v !== '') inp.value = v;
      
      $('#editPortrait').value = generatePortrait(emp);
      
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
  $('#editDecision').addEventListener('input', e => {
    emp.decision = e.target.value;
    renderTable();
  });

  function updateMeans(){
    const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
    const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
    const info = (m1 && m2) ? squareInfo(m1, m2) : null;
    $('#meansBox').innerHTML = `Средняя по разделу 1: <b>${m1||'—'}</b> &nbsp;|&nbsp;
      Средняя по разделу 2: <b>${m2||'—'}</b> &nbsp;|&nbsp;
      Квадрат: ${info ? `<span class="badge ${info.color}">${info.title}</span>` : '—'}`;
  }
}

/* ======================= ДОБАВЛЕНИЕ СОТРУДНИКА ======================= */
$('#btnAdd').addEventListener('click', () => {
  if (!state.currentDept) return;
  const fio = prompt('ФИО нового сотрудника:');
  if (!fio) return;
  
  const newEmp = {
    fio: fio.trim(),
    position: '',
    portrait: '',
    decision: '',
    p: ['','','','','',''],
    isNew: true,
    isDeleted: false,
    fioCell: null, posCell: null, portraitCell: null, decisionCell: null,
    paramCells: [null,null,null,null,null,null],
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

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    const realName = findSheet(state.workbook, dept);
    if (!realName) return;
    
    const ws = state.workbook.Sheets[realName];
    const allList = state.employees[dept];
    
    deleted += allList.filter(e => e.isDeleted).length;
    const activeList = allList.filter(e => !e.isDeleted);
    
    // Определяем строку начала данных
    let startRow = 4;
    const oldEmp = allList.find(e => !e.isNew && !e.isDeleted);
    if (oldEmp && oldEmp.row !== undefined) {
      startRow = oldEmp.row;
    }

    // Максимальный индекс колонки (с запасом)
    const maxCol = Math.max(COL_DECISION, COL_PORTRAIT, COL_SQUARE, COL_AVG_POT, 15);

    // 1. Копируем шапку
    const headerAOA = [];
    for (let r = 0; r < startRow; r++) {
      const row = new Array(maxCol + 1).fill('');
      for (let c = 0; c <= maxCol; c++) {
        const addr = XLSX.utils.encode_cell({ r, c });
        const cell = ws[addr];
        if (cell && cell.v !== undefined) {
          row[c] = cell.v;
        }
      }
      headerAOA.push(row);
    }

    // 2. Формируем данные
    const dataAOA = [];
    activeList.forEach(emp => {
      const p = emp.p;
      const m1 = avg3(p[0], p[1], p[2]);
      const m2 = avg3(p[3], p[4], p[5]);
      const info = squareInfo(m1, m2);
      const portrait = generatePortrait(emp);

      const rowData = new Array(maxCol + 1).fill('');
      rowData[0] = ''; // Пустая колонка A
      rowData[COL_FIO] = emp.fio;
      rowData[COL_POS] = emp.position;
      
      COLS_PERF.forEach((c, i) => { rowData[c] = p[i] === '' ? '' : Number(p[i]); });
      COLS_POT.forEach((c, i) => { rowData[c] = p[i+3] === '' ? '' : Number(p[i+3]); });
      
      rowData[COL_AVG_PERF] = m1 || '';
      rowData[COL_AVG_POT] = m2 || '';
      rowData[COL_SQUARE] = info.title;
      rowData[COL_PORTRAIT] = portrait;
      rowData[COL_DECISION] = emp.decision;

      dataAOA.push(rowData);
      updated++;
    });

    // 3. Собираем массив
    const finalAOA = headerAOA.concat(dataAOA);
    
    // 4. Создаем лист
    const newWs = XLSX.utils.aoa_to_sheet(finalAOA, { origin: 'A1' });
    
    // Принудительный диапазон
    const range = {
      s: { r: 0, c: 0 },
      e: { r: finalAOA.length - 1, c: maxCol }
    };
    newWs['!ref'] = XLSX.utils.encode_range(range);
    
    // 5. Копируем стили шапки
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
    
    if (ws['!cols']) newWs['!cols'] = ws['!cols'];
    if (ws['!merges']) newWs['!merges'] = ws['!merges'];
    if (ws['!rows']) newWs['!rows'] = ws['!rows'];
    
    state.workbook.Sheets[realName] = newWs;
  });

  // Очищаем память
  ['отдел1','отдел2','отдел3'].forEach(dept => {
    state.employees[dept] = state.employees[dept].filter(e => !e.isDeleted);
    
    const startRow = 4;
    state.employees[dept].forEach((emp, idx) => {
      emp.row = startRow + idx;
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
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
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
  input[type=text].decision { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; margin-top:4px; }
  textarea.portrait { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; min-height:60px; resize:vertical; font-family:inherit; font-size:13px;}
  
  .grid-wrap { display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; max-width:460px; }
  .cell { position: relative; border:1px solid var(--border); border-radius:10px; padding:10px; min-height:110px; }
  .cell h4 { margin:0 0 2px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:14px; font-weight:700; color:#1f2937; margin:2px 0 6px; }
  .cell ul { margin:0; padding-left:16px; font-size:12px; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }
  
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }

  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:12px; font-size:13px; color:#333; width:100%; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }

  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

  .hint { color:#666; font-size:13px; }
  .status { font-size:13px; color:#166534; }
  .del { color:#b91c1c; cursor:pointer; font-size:12px; }
  .means { font-size:14px; margin:6px 0; }
  .form-group { margin-bottom: 12px; }
  .form-group label { display:block; font-weight:600; margin-bottom:4px; font-size:13px; color:#475467; }
  .debug { background:#f8f9fa; border:1px solid #ddd; padding:8px; font-size:12px; font-family:monospace; color:#333; max-height:150px; overflow:auto; margin-top:8px; display:none; white-space:pre-wrap; }
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
  <p class="hint" style="margin-top:8px;">
    * В Chrome/Edge при первом сохранении выберите ваш файл — далее он будет перезаписываться без создания копий.
  </p>
</div>

<div class="panel">
  <div class="row" id="deptButtons">
    <button data-dept="отдел1" disabled>Отдел 1</button>
    <button data-dept="отдел2" disabled>Отдел 2</button>
    <button data-dept="отдел3" disabled>Отдел 3</button>
  </div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Сотрудники отдела</h3>
  <div style="overflow-x:auto;">
    <table id="empTable">
      <thead>
        <tr>
          <th>ФИО</th><th>Должность</th><th id="th_p1">Р1</th><th id="th_p2">Р2</th><th id="th_p3">Р3</th>
          <th id="th_p4">П1</th><th id="th_p5">П2</th><th id="th_p6">П3</th>
          <th>Ср. Эфф.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th>Решение</th><th></th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Карта 9 квадратов (текущий отдел)</h3>
  <div class="grid-wrap" id="grid9"></div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Редактирование сотрудника</h3>
  <div id="editForm" class="hint">Выберите сотрудника в таблице.</div>
</div>

<script>
/* ======================= КОНСТАНТЫ ======================= */
let COL_FIO = 1;
let COL_POS = 2;
let COLS_PERF = [3,4,5];
let COLS_POT  = [7,8,9];
let COL_AVG_PERF = 6;
let COL_AVG_POT  = 10;
let COL_SQUARE   = 11;
let COL_PORTRAIT = 12;
let COL_DECISION = 13;

let SQUARE_NAMES = {
  1: '1. Якорь', 2: '2. Пассажир', 3: '3. Звезда',
  4: '4. Проблемный', 5: '5. Стабильный', 6: '6. Результативный',
  7: '7. Аутсайдер', 8: '8. Исполнитель', 9: '9. Профессионал'
};
let PERF_NAMES = ['Дедлайн ЗОД', 'Качество операц. контроля', 'Дисциплина'];
let POT_NAMES = ['Оптимизация процессов', 'Наставничество', 'Стрессоустойчивость'];

let PORTRAIT_TEMPLATES = {
  1: 'Лидер. Максимальная эффективность и высокий потенциал. Готов к повышению.',
  2: 'Исполнитель с потенциалом. Показывает результат, но нужно развивать инициативность.',
  3: 'Перспективный сотрудник. Высокий потенциал, но пока не дотягивает до нужных результатов.',
  4: 'Проблемная зона. Низкая эффективность при среднем потенциале. Требуется контроль.',
  5: 'Стабильный сотрудник. Надежно выполняет работу, но не стремится к росту.',
  6: 'Результативный. Отлично справляется с задачами, но потенциал ограничен.',
  7: 'Зона риска. Высокий потенциал, но крайне низкие результаты.',
  8: 'Аутсайдер. Низкие показатели по обоим направлениям.',
  9: 'Специалист. Высокие результаты, но низкий потенциал (достиг потолка).'
};

function squareInfoForLevels(x, y){
  const map = {
    high: { low:['yellow', 7], mid:['green', 3], high:['green', 1] },
    mid:  { low:['red',    4], mid:['yellow',5], high:['green', 6] },
    low:  { low:['red',    8], mid:['red',   2], high:['yellow',9] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

function generatePortrait(emp) {
  const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
  const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
  if (!m1 || !m2) return 'Оценки не выставлены.';
  
  const info = squareInfo(m1, m2);
  const base = PORTRAIT_TEMPLATES[info.num] || `Квадрат: ${info.title}.`;
  
  const strengths = [];
  const weaknesses = [];
  
  for (let i=0; i<6; i++) {
    const val = Number(emp.p[i]);
    const name = i < 3 ? PERF_NAMES[i] : POT_NAMES[i-3];
    if (val === 3) strengths.push(name);
    if (val === 1) weaknesses.push(name);
  }
  
  let text = base;
  if (strengths.length > 0) text += ` Сильные стороны: ${strengths.join(', ')}.`;
  if (weaknesses.length > 0) text += ` Зоны развития: ${weaknesses.join(', ')}.`;
  return text;
}

/* ======================= СОСТОЯНИЕ ======================= */
const state = {
  workbook: null,
  fileName: 'employees.xlsx',
  fileHandle: null,
  currentDept: null,
  employees: { 'отдел1': [], 'отдел2': [], 'отдел3': [] },
  selectedIndex: null,
};

const $ = sel => document.querySelector(sel);
const avg3 = (a,b,c)=> +(((a||0)+(b||0)+(c||0))/3).toFixed(2);

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
  logDebug('Листы в файле: ' + state.workbook.SheetNames.map(s=>`"${s}"`).join(', '));
  
  const testDept = findSheet(state.workbook, 'отдел1');
  if (testDept) {
    const ws = state.workbook.Sheets[testDept];
    const range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
    logDebug(`\nАнализ листа "${testDept}" (диапазон: ${ws['!ref']}):`);
    
    for (let r = 0; r <= Math.min(8, range.e.r); r++) {
      let rowStr = `Стр ${r+1}: `;
      for (let c = 0; c <= Math.min(15, range.e.c); c++) {
        const addr = XLSX.utils.encode_cell({ r, c });
        const cell = ws[addr];
        if (cell && cell.v !== undefined && String(cell.v).trim() !== '') {
          rowStr += `[${XLSX.utils.encode_col(c)}: "${cell.v}"] `;
        }
      }
      logDebug(rowStr);
    }
  }
  
  ['отдел1','отдел2','отдел3'].forEach(dept => {
    logDebug(`\n[${dept}] прочитано сотрудников: ${state.employees[dept].length}`);
  });
});

/* ======================= ЧТЕНИЕ ФАЙЛА ======================= */
$('#fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  state.fileName = file.name;
  state.fileHandle = null;
  $('#debugBox').textContent = '';

  try {
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
    state.workbook = wb;
    logDebug('Файл загружен: ' + file.name);

    detectColumnsFromHeader(wb);
    readReferenceSheet(wb);

    ['отдел1','отдел2','отдел3'].forEach(dept => {
      state.employees[dept] = readDeptSheet(wb, dept);
    });

    document.querySelectorAll('#deptButtons button').forEach(b => b.disabled = false);
    $('#btnSave').disabled = false;
    $('#btnAdd').disabled = false;

    const total = state.employees['отдел1'].length + state.employees['отдел2'].length + state.employees['отдел3'].length;
    if (total === 0) {
      setStatus('Сотрудники не найдены. Откройте 🐞 Диагностику.', true);
    } else {
      setStatus(`Файл загружен. Всего сотрудников: ${total}.`);
    }
    selectDept('отдел1');
  } catch (err) {
    setStatus('Ошибка чтения файла: ' + err.message, true);
    logDebug('ОШИБКА: ' + err.stack);
  }
});

function detectColumnsFromHeader(wb) {
  const sheetName = findSheet(wb, 'отдел1') || findSheet(wb, 'отдел2') || findSheet(wb, 'отдел3');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let headerRow = -1;
  for (let r = 0; r < Math.min(15, aoa.length); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (String(row[c]).toLowerCase().includes('фио')) {
        headerRow = r;
        break;
      }
    }
    if (headerRow !== -1) break;
  }
  
  if (headerRow === -1) { logDebug('Строка с "ФИО" не найдена.'); return; }
  
  const headerText = {};
  for (let r = headerRow; r <= Math.min(headerRow + 3, aoa.length - 1); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (row[c]) headerText[c] = (headerText[c] || '') + ' ' + String(row[c]).toLowerCase();
    }
  }
  
  const found = {};
  for (let c in headerText) {
    const text = headerText[c];
    const cNum = parseInt(c);
    if (text.includes('фио')) found.fio = cNum;
    else if (text.includes('должност')) found.pos = cNum;
    else if (text.includes('дедлайн')) found.p1 = cNum;
    else if (text.includes('качество')) found.p2 = cNum;
    else if (text.includes('дисциплин')) found.p3 = cNum;
    else if (text.includes('оптимизац')) found.p4 = cNum;
    else if (text.includes('наставнич')) found.p5 = cNum;
    else if (text.includes('стрессоуст')) found.p6 = cNum;
    else if (text.includes('ср. балл') && text.includes('эффектив')) found.avg1 = cNum;
    else if (text.includes('ср. балл') && text.includes('потенциал')) found.avg2 = cNum;
    else if (text.includes('итоговый квадрат') || text.includes('квадрат')) found.sq = cNum;
    else if (text.includes('управленческий портрет')) found.portrait = cNum;
    else if (text.includes('управленческое решение')) found.decision = cNum;
  }
  
  if (found.fio !== undefined) COL_FIO = found.fio;
  if (found.pos !== undefined) COL_POS = found.pos;
  if (found.p1 !== undefined && found.p2 !== undefined && found.p3 !== undefined) COLS_PERF = [found.p1, found.p2, found.p3];
  if (found.p4 !== undefined && found.p5 !== undefined && found.p6 !== undefined) COLS_POT = [found.p4, found.p5, found.p6];
  if (found.avg1 !== undefined) COL_AVG_PERF = found.avg1;
  if (found.avg2 !== undefined) COL_AVG_POT = found.avg2;
  if (found.sq !== undefined) COL_SQUARE = found.sq;
  if (found.portrait !== undefined) COL_PORTRAIT = found.portrait;
  if (found.decision !== undefined) COL_DECISION = found.decision;
  
  logDebug(`Индексы: ФИО=${COL_FIO}, Должн=${COL_POS}, Перф=${COLS_PERF}, Пот=${COLS_POT}, Avg1=${COL_AVG_PERF}, Avg2=${COL_AVG_POT}, Sq=${COL_SQUARE}`);
}

function readReferenceSheet(wb) {
  const sheetName = findSheet(wb, 'справочник');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let perfParams = [], potParams = [], currentMode = '';

  for (let r = 0; r < aoa.length; r++) {
    const row = aoa[r];
    const col0 = String(row[0] || '').trim();
    
    if (col0.includes('Ось Эффективности')) { currentMode = 'perf'; continue; }
    if (col0.includes('Ось Потенциала')) { currentMode = 'pot'; continue; }

    if (currentMode === 'perf' && col0 && col0 !== 'Показатель') perfParams.push(col0);
    if (currentMode === 'pot' && col0 && col0 !== 'Показатель') potParams.push(col0);
  }

  if (perfParams.length >= 3) PERF_NAMES = perfParams.slice(0, 3);
  if (potParams.length >= 3) POT_NAMES = potParams.slice(0, 3);
  
  setTimeout(() => {
    $('#th_p1').textContent = PERF_NAMES[0];
    $('#th_p2').textContent = PERF_NAMES[1];
    $('#th_p3').textContent = PERF_NAMES[2];
    $('#th_p4').textContent = POT_NAMES[0];
    $('#th_p5').textContent = POT_NAMES[1];
    $('#th_p6').textContent = POT_NAMES[2];
  }, 50);
}

function readDeptSheet(wb, sheetName){
  const realName = findSheet(wb, sheetName);
  if (!realName) return [];
  
  const ws = wb.Sheets[realName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  const list = [];

  let startRow = -1;
  for (let r = 0; r < Math.min(15, aoa.length); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (String(row[c]).toLowerCase().includes('фио')) {
        startRow = r + 1;
        break;
      }
    }
    if (startRow !== -1) break;
  }
  
  if (startRow === -1) { logDebug(`${sheetName}: шапка не найдена`); return []; }
  
  for (let r = startRow; r < aoa.length; r++) {
    const row = aoa[r] || [];
    const fio = String(row[COL_FIO] || '').trim();
    if (!fio) continue;
    if (fio.toLowerCase() === 'фио' || fio.toLowerCase().includes('сотрудник')) continue;

    const position = String(row[COL_POS] || '').trim();
    const portrait = String(row[COL_PORTRAIT] || '').trim();
    const decision = String(row[COL_DECISION] || '').trim();

    const p = [];
    COLS_PERF.forEach(c => { p.push(toNum(row[c])); });
    COLS_POT.forEach(c => { p.push(toNum(row[c])); });

    const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
    const posAddr = XLSX.utils.encode_cell({ r, c: COL_POS });
    const portraitAddr = XLSX.utils.encode_cell({ r, c: COL_PORTRAIT });
    const decisionAddr = XLSX.utils.encode_cell({ r, c: COL_DECISION });
    
    const paramCells = [
      ...COLS_PERF.map(c => XLSX.utils.encode_cell({ r, c })),
      ...COLS_POT.map(c => XLSX.utils.encode_cell({ r, c }))
    ];

    list.push({
      fio, position, portrait, decision, p,
      fioCell: fioAddr, posCell: posAddr,
      portraitCell: portraitAddr, decisionCell: decisionAddr,
      paramCells, isNew: false, isDeleted: false, row: r
    });
  }

  logDebug(`${sheetName}: прочитано ${list.length} сотрудников`);
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
  renderTable(); renderGrid(); renderEditForm();
}

/* ======================= ТАБЛИЦА ======================= */
function renderTable(){
  const tbody = $('#empTable tbody');
  tbody.innerHTML = '';
  const dept = state.currentDept;
  if (!dept) return;
  
  const list = state.employees[dept].filter(e => !e.isDeleted);

  list.forEach((emp, idx) => {
    const p = emp.p;
    const m1 = avg3(p[0],p[1],p[2]);
    const m2 = avg3(p[3],p[4],p[5]);
    const info = squareInfo(m1, m2);
    
    const portraitText = generatePortrait(emp);
    emp.portrait = portraitText;

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:11px;">${escapeHtml(portraitText)}</td>
      <td style="max-width:150px;text-align:left;font-size:11px;">${escapeHtml(emp.decision)}</td>
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
  if (!dept) return;
  
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

      const members = list.filter(emp => {
        const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
        const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m=>`<li>${escapeHtml(m.fio)}</li>`).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');
      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
  `;
  wrap.appendChild(legend);
}

/* ======================= ФОРМА РЕДАКТИРОВАНИЯ ======================= */
function renderEditForm(){
  const box = $('#editForm');
  const dept = state.currentDept;
  if (!dept) { box.innerHTML = '<span class="hint">Выберите отдел.</span>'; return; }
  
  const list = state.employees[dept].filter(e => !e.isDeleted);
  
  if (state.selectedIndex === null || !list[state.selectedIndex]){
    box.innerHTML = '<span class="hint">Выберите сотрудника в таблице.</span>';
    return;
  }
  const emp = list[state.selectedIndex];
  
  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1,2].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[3,4,5].map(i=>`<label title="${POT_NAMES[i-3]}">${POT_NAMES[i-3]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="form-group">
      <label>Управленческий портрет (генерируется автоматически):</label>
      <textarea id="editPortrait" class="portrait" readonly>${escapeHtml(generatePortrait(emp))}</textarea>
    </div>

    <div class="form-group">
      <label>Управленческое решение:</label>
      <input type="text" id="editDecision" class="decision" value="${escapeHtml(emp.decision || '')}">
    </div>

    <div class="means" id="meansBox"></div>
  `;
  updateMeans();

  box.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('input', () => {
      const v = toNum(inp.value);
      emp.p[+inp.dataset.param] = v;
      if (v !== '') inp.value = v;
      
      $('#editPortrait').value = generatePortrait(emp);
      
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
  $('#editDecision').addEventListener('input', e => {
    emp.decision = e.target.value;
    renderTable();
  });

  function updateMeans(){
    const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
    const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
    const info = (m1 && m2) ? squareInfo(m1, m2) : null;
    $('#meansBox').innerHTML = `Средняя по разделу 1: <b>${m1||'—'}</b> &nbsp;|&nbsp;
      Средняя по разделу 2: <b>${m2||'—'}</b> &nbsp;|&nbsp;
      Квадрат: ${info ? `<span class="badge ${info.color}">${info.title}</span>` : '—'}`;
  }
}

/* ======================= ДОБАВЛЕНИЕ СОТРУДНИКА ======================= */
$('#btnAdd').addEventListener('click', () => {
  if (!state.currentDept) return;
  const fio = prompt('ФИО нового сотрудника:');
  if (!fio) return;
  
  const newEmp = {
    fio: fio.trim(),
    position: '',
    portrait: '',
    decision: '',
    p: ['','','','','',''],
    isNew: true,
    isDeleted: false,
    fioCell: null, posCell: null, portraitCell: null, decisionCell: null,
    paramCells: [null,null,null,null,null,null],
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

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    const realName = findSheet(state.workbook, dept);
    if (!realName) return;
    
    const ws = state.workbook.Sheets[realName];
    const allList = state.employees[dept];
    
    // Считаем, сколько было удалено
    deleted += allList.filter(e => e.isDeleted).length;
    
    // Берем только активных
    const activeList = allList.filter(e => !e.isDeleted);
    
    // Определяем, с какой строки начинаются данные (сохраняем шапку как есть)
    // Если есть хотя бы один "старый" сотрудник, берем его row
    let startRow = 4;
    const oldEmp = allList.find(e => !e.isNew && !e.isDeleted);
    if (oldEmp && oldEmp.row !== undefined) {
      startRow = oldEmp.row;
    }

    // Сохраняем шапку: копируем все строки до startRow (индекс 0..startRow-1)
    const headerAOA = [];
    const maxCol = Math.max(COL_DECISION, COL_PORTRAIT, COL_SQUARE, COL_AVG_POT) + 2;
    for (let r = 0; r < startRow; r++) {
      const row = [];
      for (let c = 0; c <= maxCol; c++) {
        const addr = XLSX.utils.encode_cell({ r, c });
        const cell = ws[addr];
        row.push(cell ? cell.v : '');
      }
      headerAOA.push(row);
    }

    // Формируем данные активных
    const dataAOA = [];
    activeList.forEach(emp => {
      const p = emp.p;
      const m1 = avg3(p[0], p[1], p[2]);
      const m2 = avg3(p[3], p[4], p[5]);
      const info = squareInfo(m1, m2);
      const portrait = generatePortrait(emp);

      const rowData = new Array(maxCol + 1).fill('');
      rowData[COL_FIO] = emp.fio;
      rowData[COL_POS] = emp.position;
      
      COLS_PERF.forEach((c, i) => { rowData[c] = p[i] === '' ? '' : Number(p[i]); });
      COLS_POT.forEach((c, i) => { rowData[c] = p[i+3] === '' ? '' : Number(p[i+3]); });
      
      rowData[COL_AVG_PERF] = m1 || '';
      rowData[COL_AVG_POT] = m2 || '';
      rowData[COL_SQUARE] = info.title;
      rowData[COL_PORTRAIT] = portrait;
      rowData[COL_DECISION] = emp.decision;

      dataAOA.push(rowData);
      updated++;
    });

    // Собираем итоговый массив
    const finalAOA = headerAOA.concat(dataAOA);
    
    // Создаем новый лист
    const newWs = XLSX.utils.aoa_to_sheet(finalAOA);
    
    // Пытаемся перенести стили шапки
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
    
    // Копируем ширины колонок и объединения
    if (ws['!cols']) newWs['!cols'] = ws['!cols'];
    if (ws['!merges']) newWs['!merges'] = ws['!merges'];
    if (ws['!rows']) newWs['!rows'] = ws['!rows'];
    
    // Заменяем лист
    state.workbook.Sheets[realName] = newWs;
  });

  // Очищаем память от удаленных и обновляем индексы строк
  ['отдел1','отдел2','отдел3'].forEach(dept => {
    state.employees[dept] = state.employees[dept].filter(e => !e.isDeleted);
    
    // Пересчитываем индексы строк
    const startRow = 4; // Данные начинаются с 5-й строки Excel
    state.employees[dept].forEach((emp, idx) => {
      emp.row = startRow + idx;
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
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
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
  input[type=text].decision { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; margin-top:4px; }
  textarea.portrait { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; min-height:60px; resize:vertical; font-family:inherit; font-size:13px;}
  
  .grid-wrap { display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; max-width:460px; }
  .cell { position: relative; border:1px solid var(--border); border-radius:10px; padding:10px; min-height:110px; }
  .cell h4 { margin:0 0 2px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:14px; font-weight:700; color:#1f2937; margin:2px 0 6px; }
  .cell ul { margin:0; padding-left:16px; font-size:12px; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }
  
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }

  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:12px; font-size:13px; color:#333; width:100%; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }

  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

  .hint { color:#666; font-size:13px; }
  .status { font-size:13px; color:#166534; }
  .del { color:#b91c1c; cursor:pointer; font-size:12px; }
  .means { font-size:14px; margin:6px 0; }
  .form-group { margin-bottom: 12px; }
  .form-group label { display:block; font-weight:600; margin-bottom:4px; font-size:13px; color:#475467; }
  .debug { background:#f8f9fa; border:1px solid #ddd; padding:8px; font-size:12px; font-family:monospace; color:#333; max-height:150px; overflow:auto; margin-top:8px; display:none; white-space:pre-wrap; }
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
  <p class="hint" style="margin-top:8px;">
    * В Chrome/Edge при первом сохранении выберите ваш файл — далее он будет перезаписываться без создания копий.
  </p>
</div>

<div class="panel">
  <div class="row" id="deptButtons">
    <button data-dept="отдел1" disabled>Отдел 1</button>
    <button data-dept="отдел2" disabled>Отдел 2</button>
    <button data-dept="отдел3" disabled>Отдел 3</button>
  </div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Сотрудники отдела</h3>
  <div style="overflow-x:auto;">
    <table id="empTable">
      <thead>
        <tr>
          <th>ФИО</th><th>Должность</th><th id="th_p1">Р1</th><th id="th_p2">Р2</th><th id="th_p3">Р3</th>
          <th id="th_p4">П1</th><th id="th_p5">П2</th><th id="th_p6">П3</th>
          <th>Ср. Эфф.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th>Решение</th><th></th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Карта 9 квадратов (текущий отдел)</h3>
  <div class="grid-wrap" id="grid9"></div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Редактирование сотрудника</h3>
  <div id="editForm" class="hint">Выберите сотрудника в таблице.</div>
</div>

<script>
/* ======================= КОНСТАНТЫ ======================= */
let COL_FIO = 1;
let COL_POS = 2;
let COLS_PERF = [3,4,5];
let COLS_POT  = [7,8,9];
let COL_AVG_PERF = 6;
let COL_AVG_POT  = 10;
let COL_SQUARE   = 11;
let COL_PORTRAIT = 12;
let COL_DECISION = 13;

let SQUARE_NAMES = {
  1: '1. Якорь', 2: '2. Пассажир', 3: '3. Звезда',
  4: '4. Проблемный', 5: '5. Стабильный', 6: '6. Результативный',
  7: '7. Аутсайдер', 8: '8. Исполнитель', 9: '9. Профессионал'
};
let PERF_NAMES = ['Дедлайн ЗОД', 'Качество операц. контроля', 'Дисциплина'];
let POT_NAMES = ['Оптимизация процессов', 'Наставничество', 'Стрессоустойчивость'];

let PORTRAIT_TEMPLATES = {
  1: 'Лидер. Максимальная эффективность и высокий потенциал. Готов к повышению.',
  2: 'Исполнитель с потенциалом. Показывает результат, но нужно развивать инициативность.',
  3: 'Перспективный сотрудник. Высокий потенциал, но пока не дотягивает до нужных результатов.',
  4: 'Проблемная зона. Низкая эффективность при среднем потенциале. Требуется контроль.',
  5: 'Стабильный сотрудник. Надежно выполняет работу, но не стремится к росту.',
  6: 'Результативный. Отлично справляется с задачами, но потенциал ограничен.',
  7: 'Зона риска. Высокий потенциал, но крайне низкие результаты.',
  8: 'Аутсайдер. Низкие показатели по обоим направлениям.',
  9: 'Специалист. Высокие результаты, но низкий потенциал (достиг потолка).'
};

function squareInfoForLevels(x, y){
  const map = {
    high: { low:['yellow', 7], mid:['green', 3], high:['green', 1] },
    mid:  { low:['red',    4], mid:['yellow',5], high:['green', 6] },
    low:  { low:['red',    8], mid:['red',   2], high:['yellow',9] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

function generatePortrait(emp) {
  const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
  const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
  if (!m1 || !m2) return 'Оценки не выставлены.';
  
  const info = squareInfo(m1, m2);
  const base = PORTRAIT_TEMPLATES[info.num] || `Квадрат: ${info.title}.`;
  
  const strengths = [];
  const weaknesses = [];
  
  for (let i=0; i<6; i++) {
    const val = Number(emp.p[i]);
    const name = i < 3 ? PERF_NAMES[i] : POT_NAMES[i-3];
    if (val === 3) strengths.push(name);
    if (val === 1) weaknesses.push(name);
  }
  
  let text = base;
  if (strengths.length > 0) text += ` Сильные стороны: ${strengths.join(', ')}.`;
  if (weaknesses.length > 0) text += ` Зоны развития: ${weaknesses.join(', ')}.`;
  return text;
}

/* ======================= СОСТОЯНИЕ ======================= */
const state = {
  workbook: null,
  fileName: 'employees.xlsx',
  fileHandle: null,
  currentDept: null,
  employees: { 'отдел1': [], 'отдел2': [], 'отдел3': [] },
  selectedIndex: null,
};

const $ = sel => document.querySelector(sel);
const avg3 = (a,b,c)=> +(((a||0)+(b||0)+(c||0))/3).toFixed(2);

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
  logDebug('Листы в файле: ' + state.workbook.SheetNames.map(s=>`"${s}"`).join(', '));
  
  const testDept = findSheet(state.workbook, 'отдел1');
  if (testDept) {
    const ws = state.workbook.Sheets[testDept];
    const range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
    logDebug(`\nАнализ листа "${testDept}" (диапазон: ${ws['!ref']}):`);
    
    // Выведем первые 8 строк
    for (let r = 0; r <= Math.min(8, range.e.r); r++) {
      let rowStr = `Стр ${r+1}: `;
      for (let c = 0; c <= Math.min(15, range.e.c); c++) {
        const addr = XLSX.utils.encode_cell({ r, c });
        const cell = ws[addr];
        if (cell && cell.v !== undefined && String(cell.v).trim() !== '') {
          rowStr += `[${XLSX.utils.encode_col(c)}: "${cell.v}"] `;
        }
      }
      logDebug(rowStr);
    }
  }
  
  ['отдел1','отдел2','отдел3'].forEach(dept => {
    logDebug(`\n[${dept}] прочитано сотрудников: ${state.employees[dept].length}`);
  });
});

/* ======================= ЧТЕНИЕ ФАЙЛА ======================= */
$('#fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  state.fileName = file.name;
  state.fileHandle = null;
  $('#debugBox').textContent = '';

  try {
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
    state.workbook = wb;
    logDebug('Файл загружен: ' + file.name);

    // 1. Пытаемся найти шапку и определить колонки
    detectColumnsFromHeader(wb);
    
    // 2. Читаем справочник (названия показателей)
    readReferenceSheet(wb);

    // 3. Читаем данные отделов
    ['отдел1','отдел2','отдел3'].forEach(dept => {
      state.employees[dept] = readDeptSheet(wb, dept);
    });

    document.querySelectorAll('#deptButtons button').forEach(b => b.disabled = false);
    $('#btnSave').disabled = false;
    $('#btnAdd').disabled = false;

    const total = state.employees['отдел1'].length + state.employees['отдел2'].length + state.employees['отдел3'].length;
    if (total === 0) {
      setStatus('Сотрудники не найдены. Откройте 🐞 Диагностику.', true);
    } else {
      setStatus(`Файл загружен. Всего сотрудников: ${total}.`);
    }
    selectDept('отдел1');
  } catch (err) {
    setStatus('Ошибка чтения файла: ' + err.message, true);
    logDebug('ОШИБКА: ' + err.stack);
  }
});

// Жесткое определение колонок по шапке (ищет строку с "ФИО")
function detectColumnsFromHeader(wb) {
  const sheetName = findSheet(wb, 'отдел1') || findSheet(wb, 'отдел2') || findSheet(wb, 'отдел3');
  if (!sheetName) { logDebug('Листы отделов не найдены для анализа шапки'); return; }
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let headerRow = -1;
  // Ищем строку, где есть слово "ФИО"
  for (let r = 0; r < Math.min(15, aoa.length); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (String(row[c]).toLowerCase().includes('фио')) {
        headerRow = r;
        break;
      }
    }
    if (headerRow !== -1) break;
  }
  
  if (headerRow === -1) {
    logDebug('Строка с "ФИО" не найдена. Используем индексы по умолчанию.');
    return;
  }
  
  // Собираем весь текст шапки (включая возможные подзаголовки в следующих строках)
  const headerText = {};
  for (let r = headerRow; r <= Math.min(headerRow + 3, aoa.length - 1); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (row[c]) {
        headerText[c] = (headerText[c] || '') + ' ' + String(row[c]).toLowerCase();
      }
    }
  }
  
  logDebug(`Шапка найдена в строке ${headerRow + 1}. Анализ колонок:`);
  
  const found = {};
  for (let c in headerText) {
    const text = headerText[c];
    const cNum = parseInt(c);
    logDebug(`  Колонка ${XLSX.utils.encode_col(cNum)}: "${text.trim()}"`);
    
    if (text.includes('фио')) found.fio = cNum;
    else if (text.includes('должност')) found.pos = cNum;
    else if (text.includes('дедлайн')) found.p1 = cNum;
    else if (text.includes('качество')) found.p2 = cNum;
    else if (text.includes('дисциплин')) found.p3 = cNum;
    else if (text.includes('оптимизац')) found.p4 = cNum;
    else if (text.includes('наставнич')) found.p5 = cNum;
    else if (text.includes('стрессоуст')) found.p6 = cNum;
    else if (text.includes('ср. балл') && text.includes('эффектив')) found.avg1 = cNum;
    else if (text.includes('ср. балл') && text.includes('потенциал')) found.avg2 = cNum;
    else if (text.includes('итоговый квадрат') || text.includes('квадрат')) found.sq = cNum;
    else if (text.includes('управленческий портрет')) found.portrait = cNum;
    else if (text.includes('управленческое решение')) found.decision = cNum;
  }
  
  if (found.fio !== undefined) COL_FIO = found.fio;
  if (found.pos !== undefined) COL_POS = found.pos;
  
  // Если нашли явно параметры по названиям — используем их
  if (found.p1 !== undefined && found.p2 !== undefined && found.p3 !== undefined) {
    COLS_PERF = [found.p1, found.p2, found.p3];
  }
  if (found.p4 !== undefined && found.p5 !== undefined && found.p6 !== undefined) {
    COLS_POT = [found.p4, found.p5, found.p6];
  }
  
  if (found.avg1 !== undefined) COL_AVG_PERF = found.avg1;
  if (found.avg2 !== undefined) COL_AVG_POT = found.avg2;
  if (found.sq !== undefined) COL_SQUARE = found.sq;
  if (found.portrait !== undefined) COL_PORTRAIT = found.portrait;
  if (found.decision !== undefined) COL_DECISION = found.decision;
  
  logDebug(`Итоговые индексы: ФИО=${COL_FIO}, Должн=${COL_POS}, Перф=${COLS_PERF}, Пот=${COLS_POT}`);
}

function readReferenceSheet(wb) {
  const sheetName = findSheet(wb, 'справочник');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let perfParams = [], potParams = [], currentMode = '';

  for (let r = 0; r < aoa.length; r++) {
    const row = aoa[r];
    const col0 = String(row[0] || '').trim();
    
    if (col0.includes('Ось Эффективности')) { currentMode = 'perf'; continue; }
    if (col0.includes('Ось Потенциала')) { currentMode = 'pot'; continue; }

    if (currentMode === 'perf' && col0 && col0 !== 'Показатель') perfParams.push(col0);
    if (currentMode === 'pot' && col0 && col0 !== 'Показатель') potParams.push(col0);
  }

  if (perfParams.length >= 3) PERF_NAMES = perfParams.slice(0, 3);
  if (potParams.length >= 3) POT_NAMES = potParams.slice(0, 3);
  
  setTimeout(() => {
    $('#th_p1').textContent = PERF_NAMES[0];
    $('#th_p2').textContent = PERF_NAMES[1];
    $('#th_p3').textContent = PERF_NAMES[2];
    $('#th_p4').textContent = POT_NAMES[0];
    $('#th_p5').textContent = POT_NAMES[1];
    $('#th_p6').textContent = POT_NAMES[2];
  }, 50);
}

function readDeptSheet(wb, sheetName){
  const realName = findSheet(wb, sheetName);
  if (!realName) return [];
  
  const ws = wb.Sheets[realName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  const list = [];

  // Ищем строку, где находится "ФИО"
  let startRow = -1;
  for (let r = 0; r < Math.min(15, aoa.length); r++) {
    const row = aoa[r] || [];
    for (let c = 0; c < row.length; c++) {
      if (String(row[c]).toLowerCase().includes('фио')) {
        startRow = r + 1; // данные начинаются со следующей строки после заголовка
        break;
      }
    }
    if (startRow !== -1) break;
  }
  
  if (startRow === -1) {
    logDebug(`${sheetName}: не найдена строка "ФИО"`);
    return [];
  }
  
  // Читаем данные начиная со следующей строки после шапки
  for (let r = startRow; r < aoa.length; r++) {
    const row = aoa[r] || [];
    const fio = String(row[COL_FIO] || '').trim();
    if (!fio) continue; // пропускаем пустые строки
    
    // Пропускаем строки, где ФИО повторяет заголовки или является мусором
    if (fio.toLowerCase() === 'фио' || fio.toLowerCase().includes('сотрудник')) continue;

    const position = String(row[COL_POS] || '').trim();
    const portrait = String(row[COL_PORTRAIT] || '').trim();
    const decision = String(row[COL_DECISION] || '').trim();

    // Извлекаем оценки
    const p = [];
    COLS_PERF.forEach(c => {
      p.push(toNum(row[c]));
    });
    COLS_POT.forEach(c => {
      p.push(toNum(row[c]));
    });

    // Формируем адреса ячеек
    const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
    const posAddr = XLSX.utils.encode_cell({ r, c: COL_POS });
    const portraitAddr = XLSX.utils.encode_cell({ r, c: COL_PORTRAIT });
    const decisionAddr = XLSX.utils.encode_cell({ r, c: COL_DECISION });
    
    const paramCells = [
      ...COLS_PERF.map(c => XLSX.utils.encode_cell({ r, c })),
      ...COLS_POT.map(c => XLSX.utils.encode_cell({ r, c }))
    ];

    list.push({
      fio, position, portrait, decision, p,
      fioCell: fioAddr, posCell: posAddr,
      portraitCell: portraitAddr, decisionCell: decisionAddr,
      paramCells, isNew: false, isDeleted: false, row: r
    });
  }

  logDebug(`${sheetName}: прочитано ${list.length} сотрудников (данные с строки ${startRow + 1})`);
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
  renderTable(); renderGrid(); renderEditForm();
}

/* ======================= ТАБЛИЦА ======================= */
function renderTable(){
  const tbody = $('#empTable tbody');
  tbody.innerHTML = '';
  const dept = state.currentDept;
  if (!dept) return;
  
  const list = state.employees[dept].filter(e => !e.isDeleted);

  list.forEach((emp, idx) => {
    const p = emp.p;
    const m1 = avg3(p[0],p[1],p[2]);
    const m2 = avg3(p[3],p[4],p[5]);
    const info = squareInfo(m1, m2);
    
    const portraitText = generatePortrait(emp);
    emp.portrait = portraitText;

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:11px;">${escapeHtml(portraitText)}</td>
      <td style="max-width:150px;text-align:left;font-size:11px;">${escapeHtml(emp.decision)}</td>
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
      if (originalIdx > -1) {
        state.employees[dept][originalIdx].isDeleted = true;
      }
      
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
  if (!dept) return;
  
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

      const members = list.filter(emp => {
        const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
        const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m=>`<li>${escapeHtml(m.fio)}</li>`).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');
      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
  `;
  wrap.appendChild(legend);
}

/* ======================= ФОРМА РЕДАКТИРОВАНИЯ ======================= */
function renderEditForm(){
  const box = $('#editForm');
  const dept = state.currentDept;
  if (!dept) { box.innerHTML = '<span class="hint">Выберите отдел.</span>'; return; }
  
  const list = state.employees[dept].filter(e => !e.isDeleted);
  
  if (state.selectedIndex === null || !list[state.selectedIndex]){
    box.innerHTML = '<span class="hint">Выберите сотрудника в таблице.</span>';
    return;
  }
  const emp = list[state.selectedIndex];
  
  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1,2].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[3,4,5].map(i=>`<label title="${POT_NAMES[i-3]}">${POT_NAMES[i-3]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="form-group">
      <label>Управленческий портрет (генерируется автоматически):</label>
      <textarea id="editPortrait" class="portrait" readonly>${escapeHtml(generatePortrait(emp))}</textarea>
    </div>

    <div class="form-group">
      <label>Управленческое решение:</label>
      <input type="text" id="editDecision" class="decision" value="${escapeHtml(emp.decision || '')}">
    </div>

    <div class="means" id="meansBox"></div>
  `;
  updateMeans();

  box.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('input', () => {
      const v = toNum(inp.value);
      emp.p[+inp.dataset.param] = v;
      if (v !== '') inp.value = v;
      
      $('#editPortrait').value = generatePortrait(emp);
      
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
  $('#editDecision').addEventListener('input', e => {
    emp.decision = e.target.value;
    renderTable();
  });

  function updateMeans(){
    const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
    const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
    const info = (m1 && m2) ? squareInfo(m1, m2) : null;
    $('#meansBox').innerHTML = `Средняя по разделу 1: <b>${m1||'—'}</b> &nbsp;|&nbsp;
      Средняя по разделу 2: <b>${m2||'—'}</b> &nbsp;|&nbsp;
      Квадрат: ${info ? `<span class="badge ${info.color}">${info.title}</span>` : '—'}`;
  }
}

/* ======================= ДОБАВЛЕНИЕ СОТРУДНИКА ======================= */
$('#btnAdd').addEventListener('click', () => {
  if (!state.currentDept) return;
  const fio = prompt('ФИО нового сотрудника:');
  if (!fio) return;
  
  const newEmp = {
    fio: fio.trim(),
    position: '',
    portrait: '',
    decision: '',
    p: ['','','','','',''],
    isNew: true,
    isDeleted: false,
    fioCell: null, posCell: null, portraitCell: null, decisionCell: null,
    paramCells: [null,null,null,null,null,null],
  };
  
  state.employees[state.currentDept].push(newEmp);
  const activeList = state.employees[state.currentDept].filter(e => !e.isDeleted);
  state.selectedIndex = activeList.length - 1;
  
  renderTable(); renderGrid(); renderEditForm();
});

/* ======================= СОХРАНЕНИЕ ======================= */
$('#btnSave').addEventListener('click', async () => {
  if (!state.workbook) return;
  let updated = 0, added = 0, deleted = 0;

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    const realName = findSheet(state.workbook, dept);
    if (!realName) return;
    
    const ws = state.workbook.Sheets[realName];
    const list = state.employees[dept];

    list.forEach(emp => {
      if (emp.isDeleted) {
         clearCell(ws, emp.fioCell);
         clearCell(ws, emp.posCell);
         clearCell(ws, emp.portraitCell);
         clearCell(ws, emp.decisionCell);
         emp.paramCells.forEach(addr => clearCell(ws, addr));
         clearCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_AVG_PERF }));
         clearCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_AVG_POT }));
         clearCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_SQUARE }));
         deleted++;
         return;
      }
      
      if (emp.isNew) return;

      emp.portrait = generatePortrait(emp);
      const m1 = avg3(emp.p[0], emp.p[1], emp.p[2]);
      const m2 = avg3(emp.p[3], emp.p[4], emp.p[5]);
      const info = squareInfo(m1, m2);

      writeCell(ws, emp.fioCell, emp.fio);
      writeCell(ws, emp.posCell, emp.position);
      writeCell(ws, emp.portraitCell, emp.portrait);
      writeCell(ws, emp.decisionCell, emp.decision);
      
      for (let i=0; i<6; i++){
        writeCell(ws, emp.paramCells[i], emp.p[i] === '' ? '' : Number(emp.p[i]));
      }

      writeCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_AVG_PERF }), m1 || '');
      writeCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_AVG_POT }), m2 || '');
      writeCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_SQUARE }), info.title);

      updated++;
    });

    const newOnes = list.filter(e => e.isNew && !e.isDeleted);
    if (newOnes.length) {
      let range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
      let lastRow = 4;
      for (let r = range.e.r; r >= 4; r--) {
        const addr = XLSX.utils.encode_cell({ r, c: COL_FIO });
        const cell = ws[addr];
        if (cell && String(cell.v||'').trim() !== '') {
          lastRow = r;
          break;
        }
      }

      newOnes.forEach((emp, k) => {
        const row = lastRow + 1 + k;
        const fioAddr = XLSX.utils.encode_cell({ r: row, c: COL_FIO });
        const posAddr = XLSX.utils.encode_cell({ r: row, c: COL_POS });
        const portAddr = XLSX.utils.encode_cell({ r: row, c: COL_PORTRAIT });
        const decAddr = XLSX.utils.encode_cell({ r: row, c: COL_DECISION });
        
        emp.portrait = generatePortrait(emp);
        const m1 = avg3(emp.p[0], emp.p[1], emp.p[2]);
        const m2 = avg3(emp.p[3], emp.p[4], emp.p[5]);
        const info = squareInfo(m1, m2);
        
        writeCell(ws, fioAddr, emp.fio);
        writeCell(ws, posAddr, emp.position);
        writeCell(ws, portAddr, emp.portrait);
        writeCell(ws, decAddr, emp.decision);
        emp.fioCell = fioAddr;
        emp.posCell = posAddr;
        emp.portraitCell = portAddr;
        emp.decisionCell = decAddr;

        const addresses = [];
        COLS_PERF.forEach((c, i) => {
          const addr = XLSX.utils.encode_cell({ r: row, c });
          writeCell(ws, addr, emp.p[i] === '' ? '' : Number(emp.p[i]));
          addresses.push(addr);
        });
        COLS_POT.forEach((c, i) => {
          const addr = XLSX.utils.encode_cell({ r: row, c });
          writeCell(ws, addr, emp.p[i+3] === '' ? '' : Number(emp.p[i+3]));
          addresses.push(addr);
        });
        emp.paramCells = addresses;

        writeCell(ws, XLSX.utils.encode_cell({ r: row, c: COL_AVG_PERF }), m1 || '');
        writeCell(ws, XLSX.utils.encode_cell({ r: row, c: COL_AVG_POT }), m2 || '');
        writeCell(ws, XLSX.utils.encode_cell({ r: row, c: COL_SQUARE }), info.title);

        emp.isNew = false;
        emp.row = row;
        added++;
      });

      range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
      const maxRow = lastRow + newOnes.length;
      if (range.e.r < maxRow) {
        range.e.r = maxRow;
        ws['!ref'] = XLSX.utils.encode_range(range);
      }
    }
  });

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    state.employees[dept] = state.employees[dept].filter(e => !e.isDeleted);
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
      
      setStatus(`✅ Файл перезаписан на диске. Обновлено: ${updated}, добавлено: ${added}, удалено: ${deleted}.`);
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

  setStatus(`Скачано: ${state.fileName}. Обновлено: ${updated}, добавлено: ${added}, удалено: ${deleted}.`);
  renderTable(); renderGrid(); renderEditForm();
});

function writeCell(ws, addr, value){
  if (!addr) return;
  if (value === '' || value === null || value === undefined){
    if (ws[addr]) { ws[addr].v = ''; ws[addr].t = 's'; }
    else { ws[addr] = { t:'s', v:'' }; }
  } else {
    if (ws[addr]) { ws[addr].v = value; ws[addr].t = typeof value === 'number' ? 'n' : 's'; }
    else { ws[addr] = { t: typeof value === 'number' ? 'n' : 's', v: value }; }
  }
}

function clearCell(ws, addr) {
  if (!addr) return;
  if (ws[addr]) { ws[addr].v = ''; ws[addr].t = 's'; }
}
</script>
</body>
</html>



















<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Оценка сотрудников — 9-box grid</title>
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
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
  input[type=text].decision { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; margin-top:4px; }
  textarea.portrait { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; min-height:60px; resize:vertical; font-family:inherit; font-size:13px;}
  
  .grid-wrap { display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; max-width:460px; }
  .cell { position: relative; border:1px solid var(--border); border-radius:10px; padding:10px; min-height:110px; }
  .cell h4 { margin:0 0 2px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:14px; font-weight:700; color:#1f2937; margin:2px 0 6px; }
  .cell ul { margin:0; padding-left:16px; font-size:12px; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }
  
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }

  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:12px; font-size:13px; color:#333; width:100%; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }

  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

  .hint { color:#666; font-size:13px; }
  .status { font-size:13px; color:#166534; }
  .del { color:#b91c1c; cursor:pointer; font-size:12px; }
  .means { font-size:14px; margin:6px 0; }
  .form-group { margin-bottom: 12px; }
  .form-group label { display:block; font-weight:600; margin-bottom:4px; font-size:13px; color:#475467; }
  .debug { background:#f8f9fa; border:1px solid #ddd; padding:8px; font-size:12px; font-family:monospace; color:#333; max-height:150px; overflow:auto; margin-top:8px; display:none; white-space:pre-wrap; }
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
  <p class="hint" style="margin-top:8px;">
    * В Chrome/Edge при первом сохранении выберите ваш файл — далее он будет перезаписываться без создания копий.
  </p>
</div>

<div class="panel">
  <div class="row" id="deptButtons">
    <button data-dept="отдел1" disabled>Отдел 1</button>
    <button data-dept="отдел2" disabled>Отдел 2</button>
    <button data-dept="отдел3" disabled>Отдел 3</button>
  </div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Сотрудники отдела</h3>
  <div style="overflow-x:auto;">
    <table id="empTable">
      <thead>
        <tr>
          <th>ФИО</th><th>Должность</th><th id="th_p1">Р1</th><th id="th_p2">Р2</th><th id="th_p3">Р3</th>
          <th id="th_p4">П1</th><th id="th_p5">П2</th><th id="th_p6">П3</th>
          <th>Ср. Эфф.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th>Решение</th><th></th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Карта 9 квадратов (текущий отдел)</h3>
  <div class="grid-wrap" id="grid9"></div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Редактирование сотрудника</h3>
  <div id="editForm" class="hint">Выберите сотрудника в таблице.</div>
</div>

<script>
/* ======================= КОНСТАНТЫ ======================= */
let COL_FIO = 1;
let COL_POS = 2;
let COLS_PERF = [3,4,5];
let COLS_POT  = [7,8,9];
let COL_PORTRAIT = 12;
let COL_DECISION = 13;

const COL_AVG_PERF = 6;
const COL_AVG_POT  = 10;
const COL_SQUARE   = 11;

let SQUARE_NAMES = {
  1: '1. Якорь', 2: '2. Пассажир', 3: '3. Звезда',
  4: '4. Проблемный', 5: '5. Стабильный', 6: '6. Результативный',
  7: '7. Аутсайдер', 8: '8. Исполнитель', 9: '9. Профессионал'
};
let PERF_NAMES = ['Дедлайн ЗОД', 'Качество операц. контроля', 'Дисциплина'];
let POT_NAMES = ['Оптимизация процессов', 'Наставничество', 'Стрессоустойчивость'];

let PORTRAIT_TEMPLATES = {
  1: 'Лидер. Максимальная эффективность и высокий потенциал. Готов к повышению.',
  2: 'Исполнитель с потенциалом. Показывает результат, но нужно развивать инициативность.',
  3: 'Перспективный сотрудник. Высокий потенциал, но пока не дотягивает до нужных результатов.',
  4: 'Проблемная зона. Низкая эффективность при среднем потенциале. Требуется контроль.',
  5: 'Стабильный сотрудник. Надежно выполняет работу, но не стремится к росту.',
  6: 'Результативный. Отлично справляется с задачами, но потенциал ограничен.',
  7: 'Зона риска. Высокий потенциал, но крайне низкие результаты.',
  8: 'Аутсайдер. Низкие показатели по обоим направлениям.',
  9: 'Специалист. Высокие результаты, но низкий потенциал (достиг потолка).'
};

function squareInfoForLevels(x, y){
  const map = {
    high: { low:['yellow', 7], mid:['green', 3], high:['green', 1] },
    mid:  { low:['red',    4], mid:['yellow',5], high:['green', 6] },
    low:  { low:['red',    8], mid:['red',   2], high:['yellow',9] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

function generatePortrait(emp) {
  const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
  const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
  if (!m1 || !m2) return 'Оценки не выставлены.';
  
  const info = squareInfo(m1, m2);
  const base = PORTRAIT_TEMPLATES[info.num] || `Квадрат: ${info.title}.`;
  
  const strengths = [];
  const weaknesses = [];
  
  for (let i=0; i<6; i++) {
    const val = Number(emp.p[i]);
    const name = i < 3 ? PERF_NAMES[i] : POT_NAMES[i-3];
    if (val === 3) strengths.push(name);
    if (val === 1) weaknesses.push(name);
  }
  
  let text = base;
  if (strengths.length > 0) text += ` Сильные стороны: ${strengths.join(', ')}.`;
  if (weaknesses.length > 0) text += ` Зоны развития: ${weaknesses.join(', ')}.`;
  return text;
}

/* ======================= СОСТОЯНИЕ ======================= */
const state = {
  workbook: null,
  fileName: 'employees.xlsx',
  fileHandle: null, // Для File System Access API
  currentDept: null,
  employees: { 'отдел1': [], 'отдел2': [], 'отдел3': [] },
  selectedIndex: null,
};

const $ = sel => document.querySelector(sel);
const avg3 = (a,b,c)=> +(((a||0)+(b||0)+(c||0))/3).toFixed(2);

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
  logDebug('Листы в файле: ' + state.workbook.SheetNames.map(s=>`"${s}"`).join(', '));
  ['отдел1','отдел2','отдел3','справочник'].forEach(dept => {
    const found = findSheet(state.workbook, dept);
    if (found) {
      logDebug(`[${dept}] -> найден лист "${found}"`);
      if (dept !== 'справочник') {
        const rows = state.employees[dept].length;
        logDebug(`  Прочитано сотрудников: ${rows}`);
      }
    } else {
      logDebug(`[${dept}] -> ЛИСТ НЕ НАЙДЕН`);
    }
  });
});

/* ======================= ЧТЕНИЕ ФАЙЛА ======================= */
$('#fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  state.fileName = file.name;
  state.fileHandle = null; // Сбрасываем старый доступ
  $('#debugBox').textContent = '';

  try {
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
    state.workbook = wb;
    logDebug('Файл загружен: ' + file.name);
    logDebug('Листы: ' + wb.SheetNames.join(', '));

    readReferenceSheet(wb);
    autoDetectColumns(wb);

    ['отдел1','отдел2','отдел3'].forEach(dept => {
      state.employees[dept] = readDeptSheet(wb, dept);
    });

    document.querySelectorAll('#deptButtons button').forEach(b => b.disabled = false);
    $('#btnSave').disabled = false;
    $('#btnAdd').disabled = false;

    const total = state.employees['отдел1'].length + state.employees['отдел2'].length + state.employees['отдел3'].length;
    if (total === 0) {
      setStatus('Сотрудники не найдены. Откройте 🐞 Диагностику.', true);
    } else {
      setStatus(`Файл загружен. Всего сотрудников: ${total}.`);
    }
    selectDept('отдел1');
  } catch (err) {
    setStatus('Ошибка чтения файла: ' + err.message, true);
    logDebug('ОШИБКА: ' + err.stack);
  }
});

function autoDetectColumns(wb) {
  const sheetName = findSheet(wb, 'отдел1') || findSheet(wb, 'отдел2') || findSheet(wb, 'отдел3');
  if (!sheetName) return;
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let headerRow = -1;
  for (let r = 0; r < Math.min(10, aoa.length); r++) {
    const row = aoa[r] || [];
    const rowText = row.map(c => String(c).toLowerCase()).join(' ');
    if (rowText.includes('фио') && (rowText.includes('эффектив') || rowText.includes('потенциал'))) {
      headerRow = r;
      break;
    }
  }
  if (headerRow === -1) return;
  
  const headerCells = aoa[headerRow] || [];
  const subHeaderCells = aoa[headerRow + 1] || [];
  
  let fioCol = -1, posCol = -1, portraitCol = -1, decisionCol = -1;
  
  for (let c = 0; c < headerCells.length; c++) {
    const text = (String(headerCells[c] || '') + ' ' + String(subHeaderCells[c] || '')).toLowerCase();
    if (text.includes('фио')) fioCol = c;
    else if (text.includes('должност')) posCol = c;
    else if (text.includes('управленческий портрет')) portraitCol = c;
    else if (text.includes('управленческое решение')) decisionCol = c;
  }
  
  if (fioCol >= 0) COL_FIO = fioCol;
  if (posCol >= 0) COL_POS = posCol;
  if (portraitCol >= 0) COL_PORTRAIT = portraitCol;
  if (decisionCol >= 0) COL_DECISION = decisionCol;
  
  if (COL_FIO >= 0) {
    COLS_PERF = [COL_FIO + 2, COL_FIO + 3, COL_FIO + 4];
    for (let c = 0; c < headerCells.length; c++) {
      const t = String(headerCells[c] || '').toLowerCase();
      if (t.includes('ср. балл') && t.includes('эффектив')) {
        COLS_POT = [c + 1, c + 2, c + 3];
        break;
      }
    }
  }
}

function readReferenceSheet(wb) {
  const sheetName = findSheet(wb, 'справочник');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let perfParams = [], potParams = [], currentMode = '';

  for (let r = 0; r < aoa.length; r++) {
    const row = aoa[r];
    const col0 = String(row[0] || '').trim();
    
    if (col0.includes('Ось Эффективности')) { currentMode = 'perf'; continue; }
    if (col0.includes('Ось Потенциала')) { currentMode = 'pot'; continue; }

    if (currentMode === 'perf' && col0 && col0 !== 'Показатель') perfParams.push(col0);
    if (currentMode === 'pot' && col0 && col0 !== 'Показатель') potParams.push(col0);
  }

  if (perfParams.length >= 3) PERF_NAMES = perfParams.slice(0, 3);
  if (potParams.length >= 3) POT_NAMES = potParams.slice(0, 3);
  
  setTimeout(() => {
    $('#th_p1').textContent = PERF_NAMES[0];
    $('#th_p2').textContent = PERF_NAMES[1];
    $('#th_p3').textContent = PERF_NAMES[2];
    $('#th_p4').textContent = POT_NAMES[0];
    $('#th_p5').textContent = POT_NAMES[1];
    $('#th_p6').textContent = POT_NAMES[2];
  }, 50);
}

function readDeptSheet(wb, sheetName){
  const realName = findSheet(wb, sheetName);
  if (!realName) return [];
  
  const ws = wb.Sheets[realName];
  const range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
  const list = [];

  let startRow = -1;
  for (let r = 0; r <= Math.min(20, range.e.r); r++) {
    const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
    const fioCell = ws[fioAddr];
    const fio = fioCell ? String(fioCell.v).trim() : '';
    if (!fio || fio.toLowerCase() === 'фио' || fio.toLowerCase().includes('сотрудник')) continue;
    
    const perfAddr = XLSX.utils.encode_cell({ r, c: COLS_PERF[0] });
    const perfCell = ws[perfAddr];
    const perfVal = perfCell ? perfCell.v : '';
    if (perfVal !== '' && perfVal !== null && !isNaN(Number(perfVal))) {
      startRow = r;
      break;
    }
  }
  
  if (startRow === -1) return [];
  
  for (let r = startRow; r <= range.e.r; r++) {
    const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
    const fioCell = ws[fioAddr];
    const fio = fioCell ? String(fioCell.v).trim() : '';
    if (!fio) continue;

    const posAddr = XLSX.utils.encode_cell({ r, c: COL_POS });
    const posCell = ws[posAddr];
    const position = posCell ? String(posCell.v).trim() : '';

    const portraitAddr = XLSX.utils.encode_cell({ r, c: COL_PORTRAIT });
    const portraitCell = ws[portraitAddr];
    const portrait = portraitCell ? String(portraitCell.v).trim() : '';

    const decisionAddr = XLSX.utils.encode_cell({ r, c: COL_DECISION });
    const decisionCell = ws[decisionAddr];
    const decision = decisionCell ? String(decisionCell.v).trim() : '';

    const p = [];
    COLS_PERF.forEach(c => {
      const addr = XLSX.utils.encode_cell({ r, c });
      p.push(ws[addr] ? toNum(ws[addr].v) : '');
    });
    COLS_POT.forEach(c => {
      const addr = XLSX.utils.encode_cell({ r, c });
      p.push(ws[addr] ? toNum(ws[addr].v) : '');
    });

    const paramCells = [
      ...COLS_PERF.map(c => XLSX.utils.encode_cell({ r, c })),
      ...COLS_POT.map(c => XLSX.utils.encode_cell({ r, c }))
    ];

    list.push({
      fio, position, portrait, decision, p,
      fioCell: fioAddr, posCell: posAddr,
      portraitCell: portraitAddr, decisionCell: decisionAddr,
      paramCells, isNew: false, isDeleted: false, row: r
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
  renderTable(); renderGrid(); renderEditForm();
}

/* ======================= ТАБЛИЦА ======================= */
function renderTable(){
  const tbody = $('#empTable tbody');
  tbody.innerHTML = '';
  const dept = state.currentDept;
  if (!dept) return;
  
  // Отфильтровываем удаленных для отображения
  const list = state.employees[dept].filter(e => !e.isDeleted);

  list.forEach((emp, idx) => {
    const p = emp.p;
    const m1 = avg3(p[0],p[1],p[2]);
    const m2 = avg3(p[3],p[4],p[5]);
    const info = squareInfo(m1, m2);
    
    const portraitText = generatePortrait(emp);
    emp.portrait = portraitText;

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:11px;">${escapeHtml(portraitText)}</td>
      <td style="max-width:150px;text-align:left;font-size:11px;">${escapeHtml(emp.decision)}</td>
      <td><span class="del" data-idx="${idx}">удалить</span></td>
    `;
    tr.querySelector('.name').addEventListener('click', () => {
      state.selectedIndex = idx;
      renderTable(); renderGrid(); renderEditForm();
    });
    tr.querySelector('.del').addEventListener('click', (e) => {
      e.stopPropagation();
      if (!confirm(`Удалить сотрудника «${emp.fio}»?`)) return;
      
      // Находим этого сотрудника в оригинальном массиве и ставим флаг
      const originalIdx = state.employees[dept].indexOf(emp);
      if (originalIdx > -1) {
        state.employees[dept][originalIdx].isDeleted = true;
      }
      
      // Сбрасываем выделение
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
  if (!dept) return;
  
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

      const members = list.filter(emp => {
        const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
        const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m=>`<li>${escapeHtml(m.fio)}</li>`).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');
      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
  `;
  wrap.appendChild(legend);
}

/* ======================= ФОРМА РЕДАКТИРОВАНИЯ ======================= */
function renderEditForm(){
  const box = $('#editForm');
  const dept = state.currentDept;
  if (!dept) { box.innerHTML = '<span class="hint">Выберите отдел.</span>'; return; }
  
  const list = state.employees[dept].filter(e => !e.isDeleted);
  
  if (state.selectedIndex === null || !list[state.selectedIndex]){
    box.innerHTML = '<span class="hint">Выберите сотрудника в таблице.</span>';
    return;
  }
  const emp = list[state.selectedIndex];
  
  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1,2].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[3,4,5].map(i=>`<label title="${POT_NAMES[i-3]}">${POT_NAMES[i-3]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="form-group">
      <label>Управленческий портрет (генерируется автоматически):</label>
      <textarea id="editPortrait" class="portrait" readonly>${escapeHtml(generatePortrait(emp))}</textarea>
    </div>

    <div class="form-group">
      <label>Управленческое решение:</label>
      <input type="text" id="editDecision" class="decision" value="${escapeHtml(emp.decision || '')}">
    </div>

    <div class="means" id="meansBox"></div>
  `;
  updateMeans();

  box.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('input', () => {
      const v = toNum(inp.value);
      emp.p[+inp.dataset.param] = v;
      if (v !== '') inp.value = v;
      
      $('#editPortrait').value = generatePortrait(emp);
      
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
  $('#editDecision').addEventListener('input', e => {
    emp.decision = e.target.value;
    renderTable();
  });

  function updateMeans(){
    const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
    const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
    const info = (m1 && m2) ? squareInfo(m1, m2) : null;
    $('#meansBox').innerHTML = `Средняя по разделу 1: <b>${m1||'—'}</b> &nbsp;|&nbsp;
      Средняя по разделу 2: <b>${m2||'—'}</b> &nbsp;|&nbsp;
      Квадрат: ${info ? `<span class="badge ${info.color}">${info.title}</span>` : '—'}`;
  }
}

/* ======================= ДОБАВЛЕНИЕ СОТРУДНИКА ======================= */
$('#btnAdd').addEventListener('click', () => {
  if (!state.currentDept) return;
  const fio = prompt('ФИО нового сотрудника:');
  if (!fio) return;
  
  const newEmp = {
    fio: fio.trim(),
    position: '',
    portrait: '',
    decision: '',
    p: ['','','','','',''],
    isNew: true,
    isDeleted: false,
    fioCell: null, posCell: null, portraitCell: null, decisionCell: null,
    paramCells: [null,null,null,null,null,null],
  };
  
  state.employees[state.currentDept].push(newEmp);
  // Выделяем нового (он теперь последний в отфильтрованном списке)
  const activeList = state.employees[state.currentDept].filter(e => !e.isDeleted);
  state.selectedIndex = activeList.length - 1;
  
  renderTable(); renderGrid(); renderEditForm();
});

/* ======================= СОХРАНЕНИЕ ======================= */
$('#btnSave').addEventListener('click', async () => {
  if (!state.workbook) return;
  let updated = 0, added = 0, deleted = 0;

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    const realName = findSheet(state.workbook, dept);
    if (!realName) return;
    
    const ws = state.workbook.Sheets[realName];
    const list = state.employees[dept];

    list.forEach(emp => {
      // Обработка удаленных
      if (emp.isDeleted) {
         clearCell(ws, emp.fioCell);
         clearCell(ws, emp.posCell);
         clearCell(ws, emp.portraitCell);
         clearCell(ws, emp.decisionCell);
         emp.paramCells.forEach(addr => clearCell(ws, addr));
         clearCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_AVG_PERF }));
         clearCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_AVG_POT }));
         clearCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_SQUARE }));
         deleted++;
         return;
      }
      
      // Обработка новых
      if (emp.isNew) return; // новых добавим отдельно

      // Обработка существующих
      emp.portrait = generatePortrait(emp);
      const m1 = avg3(emp.p[0], emp.p[1], emp.p[2]);
      const m2 = avg3(emp.p[3], emp.p[4], emp.p[5]);
      const info = squareInfo(m1, m2);

      writeCell(ws, emp.fioCell, emp.fio);
      writeCell(ws, emp.posCell, emp.position);
      writeCell(ws, emp.portraitCell, emp.portrait);
      writeCell(ws, emp.decisionCell, emp.decision);
      
      for (let i=0; i<6; i++){
        writeCell(ws, emp.paramCells[i], emp.p[i] === '' ? '' : Number(emp.p[i]));
      }

      writeCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_AVG_PERF }), m1 || '');
      writeCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_AVG_POT }), m2 || '');
      writeCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_SQUARE }), info.title);

      updated++;
    });

    // Добавление новых
    const newOnes = list.filter(e => e.isNew && !e.isDeleted);
    if (newOnes.length) {
      let range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
      let lastRow = 4;
      for (let r = range.e.r; r >= 4; r--) {
        const addr = XLSX.utils.encode_cell({ r, c: COL_FIO });
        const cell = ws[addr];
        if (cell && String(cell.v||'').trim() !== '') {
          lastRow = r;
          break;
        }
      }

      newOnes.forEach((emp, k) => {
        const row = lastRow + 1 + k;
        const fioAddr = XLSX.utils.encode_cell({ r: row, c: COL_FIO });
        const posAddr = XLSX.utils.encode_cell({ r: row, c: COL_POS });
        const portAddr = XLSX.utils.encode_cell({ r: row, c: COL_PORTRAIT });
        const decAddr = XLSX.utils.encode_cell({ r: row, c: COL_DECISION });
        
        emp.portrait = generatePortrait(emp);
        const m1 = avg3(emp.p[0], emp.p[1], emp.p[2]);
        const m2 = avg3(emp.p[3], emp.p[4], emp.p[5]);
        const info = squareInfo(m1, m2);
        
        writeCell(ws, fioAddr, emp.fio);
        writeCell(ws, posAddr, emp.position);
        writeCell(ws, portAddr, emp.portrait);
        writeCell(ws, decAddr, emp.decision);
        emp.fioCell = fioAddr;
        emp.posCell = posAddr;
        emp.portraitCell = portAddr;
        emp.decisionCell = decAddr;

        const addresses = [];
        COLS_PERF.forEach((c, i) => {
          const addr = XLSX.utils.encode_cell({ r: row, c });
          writeCell(ws, addr, emp.p[i] === '' ? '' : Number(emp.p[i]));
          addresses.push(addr);
        });
        COLS_POT.forEach((c, i) => {
          const addr = XLSX.utils.encode_cell({ r: row, c });
          writeCell(ws, addr, emp.p[i+3] === '' ? '' : Number(emp.p[i+3]));
          addresses.push(addr);
        });
        emp.paramCells = addresses;

        writeCell(ws, XLSX.utils.encode_cell({ r: row, c: COL_AVG_PERF }), m1 || '');
        writeCell(ws, XLSX.utils.encode_cell({ r: row, c: COL_AVG_POT }), m2 || '');
        writeCell(ws, XLSX.utils.encode_cell({ r: row, c: COL_SQUARE }), info.title);

        emp.isNew = false;
        emp.row = row;
        added++;
      });

      range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
      const maxRow = lastRow + newOnes.length;
      if (range.e.r < maxRow) {
        range.e.r = maxRow;
        ws['!ref'] = XLSX.utils.encode_range(range);
      }
    }
  });

  // Удаляем помеченных из памяти
  ['отдел1','отдел2','отдел3'].forEach(dept => {
    state.employees[dept] = state.employees[dept].filter(e => !e.isDeleted);
  });

  // Формируем бинарные данные
  const wbout = XLSX.write(state.workbook, { bookType:'xlsx', type:'array' });

  // Пытаемся перезаписать текущий файл через File System Access API (Chrome/Edge)
  if (window.showSaveFilePicker) {
    try {
      if (!state.fileHandle) {
        // Первый раз просим пользователя выбрать файл для перезаписи
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
      
      setStatus(`✅ Файл перезаписан на диске. Обновлено: ${updated}, добавлено: ${added}, удалено: ${deleted}.`);
      renderTable(); renderGrid(); renderEditForm();
      return;
    } catch (err) {
      // Пользователь отменил выбор или ошибка — падаем в обычное скачивание
      console.log('File System API error:', err);
      if (err.name === 'AbortError') {
        setStatus('Сохранение отменено пользователем.', true);
        return;
      }
    }
  }

  // Фолбэк: обычное скачивание
  const blob = new Blob([wbout], { type: 'application/octet-stream' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = state.fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  setStatus(`Скачано: ${state.fileName}. Обновлено: ${updated}, добавлено: ${added}, удалено: ${deleted}.`);
  renderTable(); renderGrid(); renderEditForm();
});

function writeCell(ws, addr, value){
  if (!addr) return;
  if (value === '' || value === null || value === undefined){
    if (ws[addr]) { ws[addr].v = ''; ws[addr].t = 's'; }
    else { ws[addr] = { t:'s', v:'' }; }
  } else {
    if (ws[addr]) { ws[addr].v = value; ws[addr].t = typeof value === 'number' ? 'n' : 's'; }
    else { ws[addr] = { t: typeof value === 'number' ? 'n' : 's', v: value }; }
  }
}

function clearCell(ws, addr) {
  if (!addr) return;
  if (ws[addr]) { ws[addr].v = ''; ws[addr].t = 's'; }
}
</script>
</body>
</html>






















<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Оценка сотрудников — 9-box grid</title>
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
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
  input[type=text].decision { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; margin-top:4px; }
  textarea.portrait { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; min-height:60px; resize:vertical; font-family:inherit; font-size:13px;}
  
  .grid-wrap { display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; max-width:460px; }
  .cell { position: relative; border:1px solid var(--border); border-radius:10px; padding:10px; min-height:110px; }
  .cell h4 { margin:0 0 2px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:14px; font-weight:700; color:#1f2937; margin:2px 0 6px; }
  .cell ul { margin:0; padding-left:16px; font-size:12px; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }
  
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }

  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:12px; font-size:13px; color:#333; width:100%; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }

  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

  .hint { color:#666; font-size:13px; }
  .status { font-size:13px; color:#166534; }
  .del { color:#b91c1c; cursor:pointer; font-size:12px; }
  .means { font-size:14px; margin:6px 0; }
  .form-group { margin-bottom: 12px; }
  .form-group label { display:block; font-weight:600; margin-bottom:4px; font-size:13px; color:#475467; }
  .debug { background:#f8f9fa; border:1px solid #ddd; padding:8px; font-size:12px; font-family:monospace; color:#333; max-height:150px; overflow:auto; margin-top:8px; display:none; white-space:pre-wrap; }
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
  <p class="hint" style="margin-top:8px;">
    * В Chrome/Edge при первом сохранении выберите ваш файл — далее он будет перезаписываться без создания копий.
  </p>
</div>

<div class="panel">
  <div class="row" id="deptButtons">
    <button data-dept="отдел1" disabled>Отдел 1</button>
    <button data-dept="отдел2" disabled>Отдел 2</button>
    <button data-dept="отдел3" disabled>Отдел 3</button>
  </div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Сотрудники отдела</h3>
  <div style="overflow-x:auto;">
    <table id="empTable">
      <thead>
        <tr>
          <th>ФИО</th><th>Должность</th><th id="th_p1">Р1</th><th id="th_p2">Р2</th><th id="th_p3">Р3</th>
          <th id="th_p4">П1</th><th id="th_p5">П2</th><th id="th_p6">П3</th>
          <th>Ср. Эфф.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th>Решение</th><th></th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Карта 9 квадратов (текущий отдел)</h3>
  <div class="grid-wrap" id="grid9"></div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Редактирование сотрудника</h3>
  <div id="editForm" class="hint">Выберите сотрудника в таблице.</div>
</div>

<script>
/* ======================= КОНСТАНТЫ ======================= */
let COL_FIO = 1;
let COL_POS = 2;
let COLS_PERF = [3,4,5];
let COLS_POT  = [7,8,9];
let COL_PORTRAIT = 12;
let COL_DECISION = 13;

const COL_AVG_PERF = 6;
const COL_AVG_POT  = 10;
const COL_SQUARE   = 11;

let SQUARE_NAMES = {
  1: '1. Якорь', 2: '2. Пассажир', 3: '3. Звезда',
  4: '4. Проблемный', 5: '5. Стабильный', 6: '6. Результативный',
  7: '7. Аутсайдер', 8: '8. Исполнитель', 9: '9. Профессионал'
};
let PERF_NAMES = ['Дедлайн ЗОД', 'Качество операц. контроля', 'Дисциплина'];
let POT_NAMES = ['Оптимизация процессов', 'Наставничество', 'Стрессоустойчивость'];

let PORTRAIT_TEMPLATES = {
  1: 'Лидер. Максимальная эффективность и высокий потенциал. Готов к повышению.',
  2: 'Исполнитель с потенциалом. Показывает результат, но нужно развивать инициативность.',
  3: 'Перспективный сотрудник. Высокий потенциал, но пока не дотягивает до нужных результатов.',
  4: 'Проблемная зона. Низкая эффективность при среднем потенциале. Требуется контроль.',
  5: 'Стабильный сотрудник. Надежно выполняет работу, но не стремится к росту.',
  6: 'Результативный. Отлично справляется с задачами, но потенциал ограничен.',
  7: 'Зона риска. Высокий потенциал, но крайне низкие результаты.',
  8: 'Аутсайдер. Низкие показатели по обоим направлениям.',
  9: 'Специалист. Высокие результаты, но низкий потенциал (достиг потолка).'
};

function squareInfoForLevels(x, y){
  const map = {
    high: { low:['yellow', 7], mid:['green', 3], high:['green', 1] },
    mid:  { low:['red',    4], mid:['yellow',5], high:['green', 6] },
    low:  { low:['red',    8], mid:['red',   2], high:['yellow',9] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

function generatePortrait(emp) {
  const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
  const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
  if (!m1 || !m2) return 'Оценки не выставлены.';
  
  const info = squareInfo(m1, m2);
  const base = PORTRAIT_TEMPLATES[info.num] || `Квадрат: ${info.title}.`;
  
  const strengths = [];
  const weaknesses = [];
  
  for (let i=0; i<6; i++) {
    const val = Number(emp.p[i]);
    const name = i < 3 ? PERF_NAMES[i] : POT_NAMES[i-3];
    if (val === 3) strengths.push(name);
    if (val === 1) weaknesses.push(name);
  }
  
  let text = base;
  if (strengths.length > 0) text += ` Сильные стороны: ${strengths.join(', ')}.`;
  if (weaknesses.length > 0) text += ` Зоны развития: ${weaknesses.join(', ')}.`;
  return text;
}

/* ======================= СОСТОЯНИЕ ======================= */
const state = {
  workbook: null,
  fileName: 'employees.xlsx',
  fileHandle: null, // Для File System Access API
  currentDept: null,
  employees: { 'отдел1': [], 'отдел2': [], 'отдел3': [] },
  selectedIndex: null,
};

const $ = sel => document.querySelector(sel);
const avg3 = (a,b,c)=> +(((a||0)+(b||0)+(c||0))/3).toFixed(2);

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
  logDebug('Листы в файле: ' + state.workbook.SheetNames.map(s=>`"${s}"`).join(', '));
  ['отдел1','отдел2','отдел3','справочник'].forEach(dept => {
    const found = findSheet(state.workbook, dept);
    if (found) {
      logDebug(`[${dept}] -> найден лист "${found}"`);
      if (dept !== 'справочник') {
        const rows = state.employees[dept].length;
        logDebug(`  Прочитано сотрудников: ${rows}`);
      }
    } else {
      logDebug(`[${dept}] -> ЛИСТ НЕ НАЙДЕН`);
    }
  });
});

/* ======================= ЧТЕНИЕ ФАЙЛА ======================= */
$('#fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  state.fileName = file.name;
  state.fileHandle = null; // Сбрасываем старый доступ
  $('#debugBox').textContent = '';

  try {
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
    state.workbook = wb;
    logDebug('Файл загружен: ' + file.name);
    logDebug('Листы: ' + wb.SheetNames.join(', '));

    readReferenceSheet(wb);
    autoDetectColumns(wb);

    ['отдел1','отдел2','отдел3'].forEach(dept => {
      state.employees[dept] = readDeptSheet(wb, dept);
    });

    document.querySelectorAll('#deptButtons button').forEach(b => b.disabled = false);
    $('#btnSave').disabled = false;
    $('#btnAdd').disabled = false;

    const total = state.employees['отдел1'].length + state.employees['отдел2'].length + state.employees['отдел3'].length;
    if (total === 0) {
      setStatus('Сотрудники не найдены. Откройте 🐞 Диагностику.', true);
    } else {
      setStatus(`Файл загружен. Всего сотрудников: ${total}.`);
    }
    selectDept('отдел1');
  } catch (err) {
    setStatus('Ошибка чтения файла: ' + err.message, true);
    logDebug('ОШИБКА: ' + err.stack);
  }
});

function autoDetectColumns(wb) {
  const sheetName = findSheet(wb, 'отдел1') || findSheet(wb, 'отдел2') || findSheet(wb, 'отдел3');
  if (!sheetName) return;
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let headerRow = -1;
  for (let r = 0; r < Math.min(10, aoa.length); r++) {
    const row = aoa[r] || [];
    const rowText = row.map(c => String(c).toLowerCase()).join(' ');
    if (rowText.includes('фио') && (rowText.includes('эффектив') || rowText.includes('потенциал'))) {
      headerRow = r;
      break;
    }
  }
  if (headerRow === -1) return;
  
  const headerCells = aoa[headerRow] || [];
  const subHeaderCells = aoa[headerRow + 1] || [];
  
  let fioCol = -1, posCol = -1, portraitCol = -1, decisionCol = -1;
  
  for (let c = 0; c < headerCells.length; c++) {
    const text = (String(headerCells[c] || '') + ' ' + String(subHeaderCells[c] || '')).toLowerCase();
    if (text.includes('фио')) fioCol = c;
    else if (text.includes('должност')) posCol = c;
    else if (text.includes('управленческий портрет')) portraitCol = c;
    else if (text.includes('управленческое решение')) decisionCol = c;
  }
  
  if (fioCol >= 0) COL_FIO = fioCol;
  if (posCol >= 0) COL_POS = posCol;
  if (portraitCol >= 0) COL_PORTRAIT = portraitCol;
  if (decisionCol >= 0) COL_DECISION = decisionCol;
  
  if (COL_FIO >= 0) {
    COLS_PERF = [COL_FIO + 2, COL_FIO + 3, COL_FIO + 4];
    for (let c = 0; c < headerCells.length; c++) {
      const t = String(headerCells[c] || '').toLowerCase();
      if (t.includes('ср. балл') && t.includes('эффектив')) {
        COLS_POT = [c + 1, c + 2, c + 3];
        break;
      }
    }
  }
}

function readReferenceSheet(wb) {
  const sheetName = findSheet(wb, 'справочник');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let perfParams = [], potParams = [], currentMode = '';

  for (let r = 0; r < aoa.length; r++) {
    const row = aoa[r];
    const col0 = String(row[0] || '').trim();
    
    if (col0.includes('Ось Эффективности')) { currentMode = 'perf'; continue; }
    if (col0.includes('Ось Потенциала')) { currentMode = 'pot'; continue; }

    if (currentMode === 'perf' && col0 && col0 !== 'Показатель') perfParams.push(col0);
    if (currentMode === 'pot' && col0 && col0 !== 'Показатель') potParams.push(col0);
  }

  if (perfParams.length >= 3) PERF_NAMES = perfParams.slice(0, 3);
  if (potParams.length >= 3) POT_NAMES = potParams.slice(0, 3);
  
  setTimeout(() => {
    $('#th_p1').textContent = PERF_NAMES[0];
    $('#th_p2').textContent = PERF_NAMES[1];
    $('#th_p3').textContent = PERF_NAMES[2];
    $('#th_p4').textContent = POT_NAMES[0];
    $('#th_p5').textContent = POT_NAMES[1];
    $('#th_p6').textContent = POT_NAMES[2];
  }, 50);
}

function readDeptSheet(wb, sheetName){
  const realName = findSheet(wb, sheetName);
  if (!realName) return [];
  
  const ws = wb.Sheets[realName];
  const range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
  const list = [];

  let startRow = -1;
  for (let r = 0; r <= Math.min(20, range.e.r); r++) {
    const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
    const fioCell = ws[fioAddr];
    const fio = fioCell ? String(fioCell.v).trim() : '';
    if (!fio || fio.toLowerCase() === 'фио' || fio.toLowerCase().includes('сотрудник')) continue;
    
    const perfAddr = XLSX.utils.encode_cell({ r, c: COLS_PERF[0] });
    const perfCell = ws[perfAddr];
    const perfVal = perfCell ? perfCell.v : '';
    if (perfVal !== '' && perfVal !== null && !isNaN(Number(perfVal))) {
      startRow = r;
      break;
    }
  }
  
  if (startRow === -1) return [];
  
  for (let r = startRow; r <= range.e.r; r++) {
    const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
    const fioCell = ws[fioAddr];
    const fio = fioCell ? String(fioCell.v).trim() : '';
    if (!fio) continue;

    const posAddr = XLSX.utils.encode_cell({ r, c: COL_POS });
    const posCell = ws[posAddr];
    const position = posCell ? String(posCell.v).trim() : '';

    const portraitAddr = XLSX.utils.encode_cell({ r, c: COL_PORTRAIT });
    const portraitCell = ws[portraitAddr];
    const portrait = portraitCell ? String(portraitCell.v).trim() : '';

    const decisionAddr = XLSX.utils.encode_cell({ r, c: COL_DECISION });
    const decisionCell = ws[decisionAddr];
    const decision = decisionCell ? String(decisionCell.v).trim() : '';

    const p = [];
    COLS_PERF.forEach(c => {
      const addr = XLSX.utils.encode_cell({ r, c });
      p.push(ws[addr] ? toNum(ws[addr].v) : '');
    });
    COLS_POT.forEach(c => {
      const addr = XLSX.utils.encode_cell({ r, c });
      p.push(ws[addr] ? toNum(ws[addr].v) : '');
    });

    const paramCells = [
      ...COLS_PERF.map(c => XLSX.utils.encode_cell({ r, c })),
      ...COLS_POT.map(c => XLSX.utils.encode_cell({ r, c }))
    ];

    list.push({
      fio, position, portrait, decision, p,
      fioCell: fioAddr, posCell: posAddr,
      portraitCell: portraitAddr, decisionCell: decisionAddr,
      paramCells, isNew: false, isDeleted: false, row: r
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
  renderTable(); renderGrid(); renderEditForm();
}

/* ======================= ТАБЛИЦА ======================= */
function renderTable(){
  const tbody = $('#empTable tbody');
  tbody.innerHTML = '';
  const dept = state.currentDept;
  if (!dept) return;
  
  // Отфильтровываем удаленных для отображения
  const list = state.employees[dept].filter(e => !e.isDeleted);

  list.forEach((emp, idx) => {
    const p = emp.p;
    const m1 = avg3(p[0],p[1],p[2]);
    const m2 = avg3(p[3],p[4],p[5]);
    const info = squareInfo(m1, m2);
    
    const portraitText = generatePortrait(emp);
    emp.portrait = portraitText;

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:11px;">${escapeHtml(portraitText)}</td>
      <td style="max-width:150px;text-align:left;font-size:11px;">${escapeHtml(emp.decision)}</td>
      <td><span class="del" data-idx="${idx}">удалить</span></td>
    `;
    tr.querySelector('.name').addEventListener('click', () => {
      state.selectedIndex = idx;
      renderTable(); renderGrid(); renderEditForm();
    });
    tr.querySelector('.del').addEventListener('click', (e) => {
      e.stopPropagation();
      if (!confirm(`Удалить сотрудника «${emp.fio}»?`)) return;
      
      // Находим этого сотрудника в оригинальном массиве и ставим флаг
      const originalIdx = state.employees[dept].indexOf(emp);
      if (originalIdx > -1) {
        state.employees[dept][originalIdx].isDeleted = true;
      }
      
      // Сбрасываем выделение
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
  if (!dept) return;
  
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

      const members = list.filter(emp => {
        const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
        const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m=>`<li>${escapeHtml(m.fio)}</li>`).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');
      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
  `;
  wrap.appendChild(legend);
}

/* ======================= ФОРМА РЕДАКТИРОВАНИЯ ======================= */
function renderEditForm(){
  const box = $('#editForm');
  const dept = state.currentDept;
  if (!dept) { box.innerHTML = '<span class="hint">Выберите отдел.</span>'; return; }
  
  const list = state.employees[dept].filter(e => !e.isDeleted);
  
  if (state.selectedIndex === null || !list[state.selectedIndex]){
    box.innerHTML = '<span class="hint">Выберите сотрудника в таблице.</span>';
    return;
  }
  const emp = list[state.selectedIndex];
  
  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1,2].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[3,4,5].map(i=>`<label title="${POT_NAMES[i-3]}">${POT_NAMES[i-3]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}






















<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Оценка сотрудников — 9-box grid</title>
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
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
  input[type=text].decision { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; margin-top:4px; }
  textarea.portrait { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; min-height:60px; resize:vertical; font-family:inherit; font-size:13px;}
  
  .grid-wrap { display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; max-width:460px; }
  .cell { position: relative; border:1px solid var(--border); border-radius:10px; padding:10px; min-height:110px; }
  .cell h4 { margin:0 0 2px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:14px; font-weight:700; color:#1f2937; margin:2px 0 6px; }
  .cell ul { margin:0; padding-left:16px; font-size:12px; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }
  
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }

  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:12px; font-size:13px; color:#333; width:100%; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }

  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

  .hint { color:#666; font-size:13px; }
  .status { font-size:13px; color:#166534; }
  .del { color:#b91c1c; cursor:pointer; font-size:12px; }
  .means { font-size:14px; margin:6px 0; }
  .form-group { margin-bottom: 12px; }
  .form-group label { display:block; font-weight:600; margin-bottom:4px; font-size:13px; color:#475467; }
  .debug { background:#f8f9fa; border:1px solid #ddd; padding:8px; font-size:12px; font-family:monospace; color:#333; max-height:150px; overflow:auto; margin-top:8px; display:none; white-space:pre-wrap; }
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
    <button data-dept="отдел1" disabled>Отдел 1</button>
    <button data-dept="отдел2" disabled>Отдел 2</button>
    <button data-dept="отдел3" disabled>Отдел 3</button>
  </div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Сотрудники отдела</h3>
  <div style="overflow-x:auto;">
    <table id="empTable">
      <thead>
        <tr>
          <th>ФИО</th><th>Должность</th><th id="th_p1">Р1</th><th id="th_p2">Р2</th><th id="th_p3">Р3</th>
          <th id="th_p4">П1</th><th id="th_p5">П2</th><th id="th_p6">П3</th>
          <th>Ср. Эфф.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th>Решение</th><th></th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Карта 9 квадратов (текущий отдел)</h3>
  <div class="grid-wrap" id="grid9"></div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Редактирование сотрудника</h3>
  <div id="editForm" class="hint">Выберите сотрудника в таблице.</div>
</div>

<script>
/* ======================= КОНСТАНТЫ ======================= */
let COL_FIO = 1;       // B
let COL_POS = 2;       // C
let COLS_PERF = [3,4,5]; // D, E, F
let COLS_POT  = [7,8,9]; // H, I, J
let COL_PORTRAIT = 12;   // M
let COL_DECISION = 13;   // N

// Жестко заданные индексы для записи средних и квадрата
const COL_AVG_PERF = 6;   // G
const COL_AVG_POT  = 10;  // K
const COL_SQUARE   = 11;  // L

let SQUARE_NAMES = {
  1: '1. Якорь', 2: '2. Пассажир', 3: '3. Звезда',
  4: '4. Проблемный', 5: '5. Стабильный', 6: '6. Результативный',
  7: '7. Аутсайдер', 8: '8. Исполнитель', 9: '9. Профессионал'
};
let PERF_NAMES = ['Дедлайн ЗОД', 'Качество операц. контроля', 'Дисциплина'];
let POT_NAMES = ['Оптимизация процессов', 'Наставничество', 'Стрессоустойчивость'];

let PORTRAIT_TEMPLATES = {
  1: 'Лидер. Максимальная эффективность и высокий потенциал. Готов к повышению.',
  2: 'Исполнитель с потенциалом. Показывает результат, но нужно развивать инициативность.',
  3: 'Перспективный сотрудник. Высокий потенциал, но пока не дотягивает до нужных результатов.',
  4: 'Проблемная зона. Низкая эффективность при среднем потенциале. Требуется контроль.',
  5: 'Стабильный сотрудник. Надежно выполняет работу, но не стремится к росту.',
  6: 'Результативный. Отлично справляется с задачами, но потенциал ограничен.',
  7: 'Зона риска. Высокий потенциал, но крайне низкие результаты.',
  8: 'Аутсайдер. Низкие показатели по обоим направлениям.',
  9: 'Специалист. Высокие результаты, но низкий потенциал (достиг потолка).'
};

function squareInfoForLevels(x, y){
  const map = {
    high: { low:['yellow', 7], mid:['green', 3], high:['green', 1] },
    mid:  { low:['red',    4], mid:['yellow',5], high:['green', 6] },
    low:  { low:['red',    8], mid:['red',   2], high:['yellow',9] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

function generatePortrait(emp) {
  const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
  const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
  if (!m1 || !m2) return 'Оценки не выставлены.';
  
  const info = squareInfo(m1, m2);
  const base = PORTRAIT_TEMPLATES[info.num] || `Квадрат: ${info.title}.`;
  
  const strengths = [];
  const weaknesses = [];
  
  for (let i=0; i<6; i++) {
    const val = Number(emp.p[i]);
    const name = i < 3 ? PERF_NAMES[i] : POT_NAMES[i-3];
    if (val === 3) strengths.push(name);
    if (val === 1) weaknesses.push(name);
  }
  
  let text = base;
  if (strengths.length > 0) text += ` Сильные стороны: ${strengths.join(', ')}.`;
  if (weaknesses.length > 0) text += ` Зоны развития: ${weaknesses.join(', ')}.`;
  return text;
}

/* ======================= СОСТОЯНИЕ ======================= */
const state = {
  workbook: null,
  fileName: 'employees.xlsx',
  currentDept: null,
  employees: { 'отдел1': [], 'отдел2': [], 'отдел3': [] },
  selectedIndex: null,
};

const $ = sel => document.querySelector(sel);
const avg3 = (a,b,c)=> +(((a||0)+(b||0)+(c||0))/3).toFixed(2);

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

// Универсальный поиск листа
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
  logDebug('Листы в файле: ' + state.workbook.SheetNames.map(s=>`"${s}"`).join(', '));
  ['отдел1','отдел2','отдел3','справочник'].forEach(dept => {
    const found = findSheet(state.workbook, dept);
    if (found) {
      logDebug(`[${dept}] -> найден лист "${found}"`);
      if (dept !== 'справочник') {
        const rows = state.employees[dept].length;
        logDebug(`  Прочитано сотрудников: ${rows}`);
        if (rows > 0) logDebug(`  Первый: ${state.employees[dept][0].fio}, оценки: ${state.employees[dept][0].p.join(',')}`);
      }
    } else {
      logDebug(`[${dept}] -> ЛИСТ НЕ НАЙДЕН`);
    }
  });
});

/* ======================= ЧТЕНИЕ ФАЙЛА ======================= */
$('#fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  state.fileName = file.name;
  $('#debugBox').textContent = '';

  try {
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
    state.workbook = wb;
    logDebug('Файл загружен: ' + file.name);
    logDebug('Листы: ' + wb.SheetNames.join(', '));

    readReferenceSheet(wb);
    autoDetectColumns(wb);

    ['отдел1','отдел2','отдел3'].forEach(dept => {
      state.employees[dept] = readDeptSheet(wb, dept);
    });

    document.querySelectorAll('#deptButtons button').forEach(b => b.disabled = false);
    $('#btnSave').disabled = false;
    $('#btnAdd').disabled = false;

    const total = state.employees['отдел1'].length + state.employees['отдел2'].length + state.employees['отдел3'].length;
    if (total === 0) {
      setStatus('Сотрудники не найдены. Откройте 🐞 Диагностику.', true);
    } else {
      setStatus(`Файл загружен. Всего сотрудников: ${total}.`);
    }
    selectDept('отдел1');
  } catch (err) {
    setStatus('Ошибка чтения файла: ' + err.message, true);
    logDebug('ОШИБКА: ' + err.stack);
  }
});

function autoDetectColumns(wb) {
  const sheetName = findSheet(wb, 'отдел1') || findSheet(wb, 'отдел2') || findSheet(wb, 'отдел3');
  if (!sheetName) return;
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let headerRow = -1;
  for (let r = 0; r < Math.min(10, aoa.length); r++) {
    const row = aoa[r] || [];
    const rowText = row.map(c => String(c).toLowerCase()).join(' ');
    if (rowText.includes('фио') && (rowText.includes('эффектив') || rowText.includes('потенциал'))) {
      headerRow = r;
      break;
    }
  }
  if (headerRow === -1) return;
  
  const headerCells = aoa[headerRow] || [];
  const subHeaderCells = aoa[headerRow + 1] || [];
  
  let fioCol = -1, posCol = -1, portraitCol = -1, decisionCol = -1;
  
  for (let c = 0; c < headerCells.length; c++) {
    const text = (String(headerCells[c] || '') + ' ' + String(subHeaderCells[c] || '')).toLowerCase();
    if (text.includes('фио')) fioCol = c;
    else if (text.includes('должност')) posCol = c;
    else if (text.includes('управленческий портрет')) portraitCol = c;
    else if (text.includes('управленческое решение')) decisionCol = c;
  }
  
  if (fioCol >= 0) COL_FIO = fioCol;
  if (posCol >= 0) COL_POS = posCol;
  if (portraitCol >= 0) COL_PORTRAIT = portraitCol;
  if (decisionCol >= 0) COL_DECISION = decisionCol;
  
  if (COL_FIO >= 0) {
    COLS_PERF = [COL_FIO + 2, COL_FIO + 3, COL_FIO + 4];
    for (let c = 0; c < headerCells.length; c++) {
      const t = String(headerCells[c] || '').toLowerCase();
      if (t.includes('ср. балл') && t.includes('эффектив')) {
        COLS_POT = [c + 1, c + 2, c + 3];
        break;
      }
    }
  }
  
  logDebug(`Колонки: ФИО=${COL_FIO}, Должность=${COL_POS}, Перф=${COLS_PERF}, Пот=${COLS_POT}, Портрет=${COL_PORTRAIT}, Решение=${COL_DECISION}`);
}

function readReferenceSheet(wb) {
  const sheetName = findSheet(wb, 'справочник');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let perfParams = [], potParams = [], currentMode = '';

  for (let r = 0; r < aoa.length; r++) {
    const row = aoa[r];
    const col0 = String(row[0] || '').trim();
    
    if (col0.includes('Ось Эффективности')) { currentMode = 'perf'; continue; }
    if (col0.includes('Ось Потенциала')) { currentMode = 'pot'; continue; }

    if (currentMode === 'perf' && col0 && col0 !== 'Показатель') perfParams.push(col0);
    if (currentMode === 'pot' && col0 && col0 !== 'Показатель') potParams.push(col0);
  }

  if (perfParams.length >= 3) PERF_NAMES = perfParams.slice(0, 3);
  if (potParams.length >= 3) POT_NAMES = potParams.slice(0, 3);
  
  setTimeout(() => {
    $('#th_p1').textContent = PERF_NAMES[0];
    $('#th_p2').textContent = PERF_NAMES[1];
    $('#th_p3').textContent = PERF_NAMES[2];
    $('#th_p4').textContent = POT_NAMES[0];
    $('#th_p5').textContent = POT_NAMES[1];
    $('#th_p6').textContent = POT_NAMES[2];
  }, 50);
}

function readDeptSheet(wb, sheetName){
  const realName = findSheet(wb, sheetName);
  if (!realName) return [];
  
  const ws = wb.Sheets[realName];
  const range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
  const list = [];

  let startRow = -1;
  for (let r = 0; r <= Math.min(20, range.e.r); r++) {
    const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
    const fioCell = ws[fioAddr];
    const fio = fioCell ? String(fioCell.v).trim() : '';
    if (!fio || fio.toLowerCase() === 'фио' || fio.toLowerCase().includes('сотрудник')) continue;
    
    const perfAddr = XLSX.utils.encode_cell({ r, c: COLS_PERF[0] });
    const perfCell = ws[perfAddr];
    const perfVal = perfCell ? perfCell.v : '';
    if (perfVal !== '' && perfVal !== null && !isNaN(Number(perfVal))) {
      startRow = r;
      break;
    }
  }
  
  if (startRow === -1) return [];
  
  for (let r = startRow; r <= range.e.r; r++) {
    const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
    const fioCell = ws[fioAddr];
    const fio = fioCell ? String(fioCell.v).trim() : '';
    if (!fio) continue;

    const posAddr = XLSX.utils.encode_cell({ r, c: COL_POS });
    const posCell = ws[posAddr];
    const position = posCell ? String(posCell.v).trim() : '';

    const portraitAddr = XLSX.utils.encode_cell({ r, c: COL_PORTRAIT });
    const portraitCell = ws[portraitAddr];
    const portrait = portraitCell ? String(portraitCell.v).trim() : '';

    const decisionAddr = XLSX.utils.encode_cell({ r, c: COL_DECISION });
    const decisionCell = ws[decisionAddr];
    const decision = decisionCell ? String(decisionCell.v).trim() : '';

    const p = [];
    COLS_PERF.forEach(c => {
      const addr = XLSX.utils.encode_cell({ r, c });
      p.push(ws[addr] ? toNum(ws[addr].v) : '');
    });
    COLS_POT.forEach(c => {
      const addr = XLSX.utils.encode_cell({ r, c });
      p.push(ws[addr] ? toNum(ws[addr].v) : '');
    });

    const paramCells = [
      ...COLS_PERF.map(c => XLSX.utils.encode_cell({ r, c })),
      ...COLS_POT.map(c => XLSX.utils.encode_cell({ r, c }))
    ];

    list.push({
      fio, position, portrait, decision, p,
      fioCell: fioAddr, posCell: posAddr,
      portraitCell: portraitAddr, decisionCell: decisionAddr,
      paramCells, isNew: false, row: r
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
  renderTable(); renderGrid(); renderEditForm();
}

/* ======================= ТАБЛИЦА ======================= */
function renderTable(){
  const tbody = $('#empTable tbody');
  tbody.innerHTML = '';
  const dept = state.currentDept;
  if (!dept) return;
  const list = state.employees[dept];

  list.forEach((emp, idx) => {
    const p = emp.p;
    const m1 = avg3(p[0],p[1],p[2]);
    const m2 = avg3(p[3],p[4],p[5]);
    const info = squareInfo(m1, m2);
    
    const portraitText = generatePortrait(emp);
    emp.portrait = portraitText;

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:11px;">${escapeHtml(portraitText)}</td>
      <td style="max-width:150px;text-align:left;font-size:11px;">${escapeHtml(emp.decision)}</td>
      <td><span class="del" data-idx="${idx}">удалить</span></td>
    `;
    tr.querySelector('.name').addEventListener('click', () => {
      state.selectedIndex = idx;
      renderTable(); renderGrid(); renderEditForm();
    });
    tr.querySelector('.del').addEventListener('click', (e) => {
      e.stopPropagation();
      if (!confirm(`Удалить сотрудника «${emp.fio}»?`)) return;
      emp.isDeleted = true; 
      emp.fio = ''; emp.position = ''; emp.portrait = ''; emp.decision = '';
      emp.p = ['','','','','',''];
      state.employees[dept].splice(idx,1);
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
  const list = dept ? state.employees[dept] : [];

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

      const members = list.filter(emp => {
        const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
        const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m=>`<li>${escapeHtml(m.fio)}</li>`).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');
      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
  `;
  wrap.appendChild(legend);
}

/* ======================= ФОРМА РЕДАКТИРОВАНИЯ ======================= */
function renderEditForm(){
  const box = $('#editForm');
  const dept = state.currentDept;
  if (!dept || state.selectedIndex === null || !state.employees[dept][state.selectedIndex]){
    box.innerHTML = '<span class="hint">Выберите сотрудника в таблице.</span>';
    return;
  }
  const emp = state.employees[dept][state.selectedIndex];
  
  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1,2].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[3,4,5].map(i=>`<label title="${POT_NAMES[i-3]}">${POT_NAMES[i-3]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="form-group">
      <label>Управленческий портрет (генерируется автоматически):</label>
      <textarea id="editPortrait" class="portrait" readonly>${escapeHtml(generatePortrait(emp))}</textarea>
    </div>

    <div class="form-group">
      <label>Управленческое решение:</label>
      <input type="text" id="editDecision" class="decision" value="${escapeHtml(emp.decision || '')}">
    </div>

    <div class="means" id="meansBox"></div>
  `;
  updateMeans();

  box.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('input', () => {
      const v = toNum(inp.value);
      emp.p[+inp.dataset.param] = v;
      if (v !== '') inp.value = v;
      
      $('#editPortrait').value = generatePortrait(emp);
      
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
  $('#editDecision').addEventListener('input', e => {
    emp.decision = e.target.value;
    renderTable();
  });

  function updateMeans(){
    const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
    const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
    const info = (m1 && m2) ? squareInfo(m1, m2) : null;
    $('#meansBox').innerHTML = `Средняя по разделу 1: <b>${m1||'—'}</b> &nbsp;|&nbsp;
      Средняя по разделу 2: <b>${m2||'—'}</b> &nbsp;|&nbsp;
      Квадрат: ${info ? `<span class="badge ${info.color}">${info.title}</span>` : '—'}`;
  }
}

/* ======================= ДОБАВЛЕНИЕ СОТРУДНИКА ======================= */
$('#btnAdd').addEventListener('click', () => {
  if (!state.currentDept) return;
  const fio = prompt('ФИО нового сотрудника:');
  if (!fio) return;
  state.employees[state.currentDept].push({
    fio: fio.trim(),
    position: '',
    portrait: '',
    decision: '',
    p: ['','','','','',''],
    isNew: true,
    fioCell: null, posCell: null, portraitCell: null, decisionCell: null,
    paramCells: [null,null,null,null,null,null],
  });
  state.selectedIndex = state.employees[state.currentDept].length - 1;
  renderTable(); renderGrid(); renderEditForm();
});

/* ======================= СОХРАНЕНИЕ ======================= */
$('#btnSave').addEventListener('click', () => {
  if (!state.workbook) return;
  let updated = 0, added = 0, deleted = 0;

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    const realName = findSheet(state.workbook, dept);
    if (!realName) return;
    
    const ws = state.workbook.Sheets[realName];
    const list = state.employees[dept];

    // 1. Обновление существующих и удаление
    list.forEach(emp => {
      if (emp.isNew) return;
      if (emp.isDeleted) {
         clearCell(ws, emp.fioCell);
         clearCell(ws, emp.posCell);
         clearCell(ws, emp.portraitCell);
         clearCell(ws, emp.decisionCell);
         emp.paramCells.forEach(addr => clearCell(ws, addr));
         // Очищаем средние и квадрат
         clearCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_AVG_PERF }));
         clearCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_AVG_POT }));
         clearCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_SQUARE }));
         deleted++;
         return;
      }
      
      emp.portrait = generatePortrait(emp);
      const m1 = avg3(emp.p[0], emp.p[1], emp.p[2]);
      const m2 = avg3(emp.p[3], emp.p[4], emp.p[5]);
      const info = squareInfo(m1, m2);

      // Записываем основные данные
      writeCell(ws, emp.fioCell, emp.fio);
      writeCell(ws, emp.posCell, emp.position);
      writeCell(ws, emp.portraitCell, emp.portrait);
      writeCell(ws, emp.decisionCell, emp.decision);
      
      // Записываем оценки
      for (let i=0; i<6; i++){
        writeCell(ws, emp.paramCells[i], emp.p[i] === '' ? '' : Number(emp.p[i]));
      }

      // Записываем средние баллы и квадрат ЧИСЛАМИ (вместо формул)
      writeCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_AVG_PERF }), m1 || '');
      writeCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_AVG_POT }), m2 || '');
      writeCell(ws, XLSX.utils.encode_cell({ r: emp.row, c: COL_SQUARE }), info.title);

      updated++;
    });

    // 2. Добавление новых
    const newOnes = list.filter(e => e.isNew && !e.isDeleted);
    if (newOnes.length) {
      let range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
      let lastRow = 4;
      for (let r = range.e.r; r >= 4; r--) {
        const addr = XLSX.utils.encode_cell({ r, c: COL_FIO });
        const cell = ws[addr];
        if (cell && String(cell.v||'').trim() !== '') {
          lastRow = r;
          break;
        }
      }

      newOnes.forEach((emp, k) => {
        const row = lastRow + 1 + k;
        const fioAddr = XLSX.utils.encode_cell({ r: row, c: COL_FIO });
        const posAddr = XLSX.utils.encode_cell({ r: row, c: COL_POS });
        const portAddr = XLSX.utils.encode_cell({ r: row, c: COL_PORTRAIT });
        const decAddr = XLSX.utils.encode_cell({ r: row, c: COL_DECISION });
        
        emp.portrait = generatePortrait(emp);
        const m1 = avg3(emp.p[0], emp.p[1], emp.p[2]);
        const m2 = avg3(emp.p[3], emp.p[4], emp.p[5]);
        const info = squareInfo(m1, m2);
        
        writeCell(ws, fioAddr, emp.fio);
        writeCell(ws, posAddr, emp.position);
        writeCell(ws, portAddr, emp.portrait);
        writeCell(ws, decAddr, emp.decision);
        emp.fioCell = fioAddr;
        emp.posCell = posAddr;
        emp.portraitCell = portAddr;
        emp.decisionCell = decAddr;

        const addresses = [];
        COLS_PERF.forEach((c, i) => {
          const addr = XLSX.utils.encode_cell({ r: row, c });
          writeCell(ws, addr, emp.p[i] === '' ? '' : Number(emp.p[i]));
          addresses.push(addr);
        });
        COLS_POT.forEach((c, i) => {
          const addr = XLSX.utils.encode_cell({ r: row, c });
          writeCell(ws, addr, emp.p[i+3] === '' ? '' : Number(emp.p[i+3]));
          addresses.push(addr);
        });
        emp.paramCells = addresses;

        // Записываем средние и квадрат для нового сотрудника
        writeCell(ws, XLSX.utils.encode_cell({ r: row, c: COL_AVG_PERF }), m1 || '');
        writeCell(ws, XLSX.utils.encode_cell({ r: row, c: COL_AVG_POT }), m2 || '');
        writeCell(ws, XLSX.utils.encode_cell({ r: row, c: COL_SQUARE }), info.title);

        emp.isNew = false;
        added++;
      });

      range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
      const maxRow = lastRow + newOnes.length;
      if (range.e.r < maxRow) {
        range.e.r = maxRow;
        ws['!ref'] = XLSX.utils.encode_range(range);
      }
    }
  });

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    state.employees[dept] = state.employees[dept].filter(e => !e.isDeleted);
  });

  XLSX.writeFile(state.workbook, state.fileName);
  setStatus(`Сохранено: обновлено ${updated}, добавлено ${added}, удалено ${deleted}.`);
});

function writeCell(ws, addr, value){
  if (!addr) return;
  if (value === '' || value === null || value === undefined){
    if (ws[addr]) { ws[addr].v = ''; ws[addr].t = 's'; }
    else { ws[addr] = { t:'s', v:'' }; }
  } else {
    if (ws[addr]) { ws[addr].v = value; ws[addr].t = typeof value === 'number' ? 'n' : 's'; }
    else { ws[addr] = { t: typeof value === 'number' ? 'n' : 's', v: value }; }
  }
}

function clearCell(ws, addr) {
  if (!addr) return;
  if (ws[addr]) { ws[addr].v = ''; ws[addr].t = 's'; }
}
</script>
</body>
</html>




























<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Оценка сотрудников — 9-box grid</title>
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
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
  input[type=text].decision { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; margin-top:4px; }
  textarea.portrait { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; min-height:60px; resize:vertical; font-family:inherit; font-size:13px;}
  
  .grid-wrap { display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; max-width:460px; }
  .cell { position: relative; border:1px solid var(--border); border-radius:10px; padding:10px; min-height:110px; }
  .cell h4 { margin:0 0 2px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:14px; font-weight:700; color:#1f2937; margin:2px 0 6px; }
  .cell ul { margin:0; padding-left:16px; font-size:12px; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }
  
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }

  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:12px; font-size:13px; color:#333; width:100%; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }

  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

  .hint { color:#666; font-size:13px; }
  .status { font-size:13px; color:#166534; }
  .del { color:#b91c1c; cursor:pointer; font-size:12px; }
  .means { font-size:14px; margin:6px 0; }
  .form-group { margin-bottom: 12px; }
  .form-group label { display:block; font-weight:600; margin-bottom:4px; font-size:13px; color:#475467; }
  .debug { background:#f8f9fa; border:1px solid #ddd; padding:8px; font-size:12px; font-family:monospace; color:#333; max-height:150px; overflow:auto; margin-top:8px; display:none; white-space:pre-wrap; }
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
    <button data-dept="отдел1" disabled>Отдел 1</button>
    <button data-dept="отдел2" disabled>Отдел 2</button>
    <button data-dept="отдел3" disabled>Отдел 3</button>
  </div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Сотрудники отдела</h3>
  <div style="overflow-x:auto;">
    <table id="empTable">
      <thead>
        <tr>
          <th>ФИО</th><th>Должность</th><th id="th_p1">Р1</th><th id="th_p2">Р2</th><th id="th_p3">Р3</th>
          <th id="th_p4">П1</th><th id="th_p5">П2</th><th id="th_p6">П3</th>
          <th>Ср. Эфф.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th>Решение</th><th></th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Карта 9 квадратов (текущий отдел)</h3>
  <div class="grid-wrap" id="grid9"></div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Редактирование сотрудника</h3>
  <div id="editForm" class="hint">Выберите сотрудника в таблице.</div>
</div>

<script>
/* ======================= КОНСТАНТЫ ======================= */
let COL_FIO = 1;       // B
let COL_POS = 2;       // C
let COLS_PERF = [3,4,5]; // D, E, F
let COLS_POT  = [7,8,9]; // H, I, J
let COL_PORTRAIT = 12;   // M
let COL_DECISION = 13;   // N

let SQUARE_NAMES = {
  1: '1. Якорь', 2: '2. Пассажир', 3: '3. Звезда',
  4: '4. Проблемный', 5: '5. Стабильный', 6: '6. Результативный',
  7: '7. Аутсайдер', 8: '8. Исполнитель', 9: '9. Профессионал'
};
let PERF_NAMES = ['Дедлайн ЗОД', 'Качество операц. контроля', 'Дисциплина'];
let POT_NAMES = ['Оптимизация процессов', 'Наставничество', 'Стрессоустойчивость'];

let PORTRAIT_TEMPLATES = {
  1: 'Лидер. Максимальная эффективность и высокий потенциал. Готов к повышению.',
  2: 'Исполнитель с потенциалом. Показывает результат, но нужно развивать инициативность.',
  3: 'Перспективный сотрудник. Высокий потенциал, но пока не дотягивает до нужных результатов.',
  4: 'Проблемная зона. Низкая эффективность при среднем потенциале. Требуется контроль.',
  5: 'Стабильный сотрудник. Надежно выполняет работу, но не стремится к росту.',
  6: 'Результативный. Отлично справляется с задачами, но потенциал ограничен.',
  7: 'Зона риска. Высокий потенциал, но крайне низкие результаты.',
  8: 'Аутсайдер. Низкие показатели по обоим направлениям.',
  9: 'Специалист. Высокие результаты, но низкий потенциал (достиг потолка).'
};

function squareInfoForLevels(x, y){
  const map = {
    high: { low:['yellow', 7], mid:['green', 3], high:['green', 1] },
    mid:  { low:['red',    4], mid:['yellow',5], high:['green', 6] },
    low:  { low:['red',    8], mid:['red',   2], high:['yellow',9] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

function generatePortrait(emp) {
  const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
  const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
  if (!m1 || !m2) return 'Оценки не выставлены.';
  
  const info = squareInfo(m1, m2);
  const base = PORTRAIT_TEMPLATES[info.num] || `Квадрат: ${info.title}.`;
  
  const strengths = [];
  const weaknesses = [];
  
  for (let i=0; i<6; i++) {
    const val = Number(emp.p[i]);
    const name = i < 3 ? PERF_NAMES[i] : POT_NAMES[i-3];
    if (val === 3) strengths.push(name);
    if (val === 1) weaknesses.push(name);
  }
  
  let text = base;
  if (strengths.length > 0) text += ` Сильные стороны: ${strengths.join(', ')}.`;
  if (weaknesses.length > 0) text += ` Зоны развития: ${weaknesses.join(', ')}.`;
  return text;
}

/* ======================= СОСТОЯНИЕ ======================= */
const state = {
  workbook: null,
  fileName: 'employees.xlsx',
  currentDept: null,
  employees: { 'отдел1': [], 'отдел2': [], 'отдел3': [] },
  selectedIndex: null,
};

const $ = sel => document.querySelector(sel);
const avg3 = (a,b,c)=> +(((a||0)+(b||0)+(c||0))/3).toFixed(2);

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

// УНИВЕРСАЛЬНЫЙ ПОИСК ЛИСТА
function findSheet(wb, name) {
  const target = name.toLowerCase().replace(/[\s_\-]/g,'');
  // 1. Точное совпадение без учета регистра/пробелов
  for (const sn of wb.SheetNames) {
    if (sn.toLowerCase().replace(/[\s_\-]/g,'') === target) return sn;
  }
  // 2. Вхождение подстроки (например "отдел 1 (основной)")
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
  logDebug('Листы в файле: ' + state.workbook.SheetNames.map(s=>`"${s}"`).join(', '));
  ['отдел1','отдел2','отдел3','справочник'].forEach(dept => {
    const found = findSheet(state.workbook, dept);
    if (found) {
      logDebug(`[${dept}] -> найден лист "${found}"`);
      if (dept !== 'справочник') {
        const rows = state.employees[dept].length;
        logDebug(`  Прочитано сотрудников: ${rows}`);
        if (rows > 0) logDebug(`  Первый: ${state.employees[dept][0].fio}, оценки: ${state.employees[dept][0].p.join(',')}`);
      }
    } else {
      logDebug(`[${dept}] -> ЛИСТ НЕ НАЙДЕН`);
    }
  });
});

/* ======================= ЧТЕНИЕ ФАЙЛА ======================= */
$('#fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  state.fileName = file.name;
  $('#debugBox').textContent = '';

  try {
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
    state.workbook = wb;
    logDebug('Файл загружен: ' + file.name);
    logDebug('Листы: ' + wb.SheetNames.join(', '));

    readReferenceSheet(wb);
    autoDetectColumns(wb);

    ['отдел1','отдел2','отдел3'].forEach(dept => {
      state.employees[dept] = readDeptSheet(wb, dept);
    });

    document.querySelectorAll('#deptButtons button').forEach(b => b.disabled = false);
    $('#btnSave').disabled = false;
    $('#btnAdd').disabled = false;

    const total = state.employees['отдел1'].length + state.employees['отдел2'].length + state.employees['отдел3'].length;
    if (total === 0) {
      setStatus('Сотрудники не найдены. Откройте 🐞 Диагностику.', true);
    } else {
      setStatus(`Файл загружен. Всего сотрудников: ${total}.`);
    }
    selectDept('отдел1');
  } catch (err) {
    setStatus('Ошибка чтения файла: ' + err.message, true);
    logDebug('ОШИБКА: ' + err.stack);
  }
});

function autoDetectColumns(wb) {
  const sheetName = findSheet(wb, 'отдел1') || findSheet(wb, 'отдел2') || findSheet(wb, 'отдел3');
  if (!sheetName) return;
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let headerRow = -1;
  for (let r = 0; r < Math.min(10, aoa.length); r++) {
    const row = aoa[r] || [];
    const rowText = row.map(c => String(c).toLowerCase()).join(' ');
    if (rowText.includes('фио') && (rowText.includes('эффектив') || rowText.includes('потенциал'))) {
      headerRow = r;
      break;
    }
  }
  if (headerRow === -1) return;
  
  const headerCells = aoa[headerRow] || [];
  const subHeaderCells = aoa[headerRow + 1] || [];
  
  let fioCol = -1, posCol = -1, portraitCol = -1, decisionCol = -1;
  
  for (let c = 0; c < headerCells.length; c++) {
    const text = (String(headerCells[c] || '') + ' ' + String(subHeaderCells[c] || '')).toLowerCase();
    if (text.includes('фио')) fioCol = c;
    else if (text.includes('должност')) posCol = c;
    else if (text.includes('управленческий портрет')) portraitCol = c;
    else if (text.includes('управленческое решение')) decisionCol = c;
  }
  
  if (fioCol >= 0) COL_FIO = fioCol;
  if (posCol >= 0) COL_POS = posCol;
  if (portraitCol >= 0) COL_PORTRAIT = portraitCol;
  if (decisionCol >= 0) COL_DECISION = decisionCol;
  
  if (COL_FIO >= 0) {
    COLS_PERF = [COL_FIO + 2, COL_FIO + 3, COL_FIO + 4];
    for (let c = 0; c < headerCells.length; c++) {
      const t = String(headerCells[c] || '').toLowerCase();
      if (t.includes('ср. балл') && t.includes('эффектив')) {
        COLS_POT = [c + 1, c + 2, c + 3];
        break;
      }
    }
  }
  
  logDebug(`Колонки: ФИО=${COL_FIO}, Должность=${COL_POS}, Перф=${COLS_PERF}, Пот=${COLS_POT}, Портрет=${COL_PORTRAIT}, Решение=${COL_DECISION}`);
}

function readReferenceSheet(wb) {
  const sheetName = findSheet(wb, 'справочник');
  if (!sheetName) return;
  
  const ws = wb.Sheets[sheetName];
  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let perfParams = [], potParams = [], currentMode = '';

  for (let r = 0; r < aoa.length; r++) {
    const row = aoa[r];
    const col0 = String(row[0] || '').trim();
    
    if (col0.includes('Ось Эффективности')) { currentMode = 'perf'; continue; }
    if (col0.includes('Ось Потенциала')) { currentMode = 'pot'; continue; }

    if (currentMode === 'perf' && col0 && col0 !== 'Показатель') perfParams.push(col0);
    if (currentMode === 'pot' && col0 && col0 !== 'Показатель') potParams.push(col0);
  }

  if (perfParams.length >= 3) PERF_NAMES = perfParams.slice(0, 3);
  if (potParams.length >= 3) POT_NAMES = potParams.slice(0, 3);
  
  setTimeout(() => {
    $('#th_p1').textContent = PERF_NAMES[0];
    $('#th_p2').textContent = PERF_NAMES[1];
    $('#th_p3').textContent = PERF_NAMES[2];
    $('#th_p4').textContent = POT_NAMES[0];
    $('#th_p5').textContent = POT_NAMES[1];
    $('#th_p6').textContent = POT_NAMES[2];
  }, 50);
}

function readDeptSheet(wb, sheetName){
  const realName = findSheet(wb, sheetName);
  if (!realName) return [];
  
  const ws = wb.Sheets[realName];
  const range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
  const list = [];

  let startRow = -1;
  for (let r = 0; r <= Math.min(20, range.e.r); r++) {
    const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
    const fioCell = ws[fioAddr];
    const fio = fioCell ? String(fioCell.v).trim() : '';
    if (!fio || fio.toLowerCase() === 'фио' || fio.toLowerCase().includes('сотрудник')) continue;
    
    const perfAddr = XLSX.utils.encode_cell({ r, c: COLS_PERF[0] });
    const perfCell = ws[perfAddr];
    const perfVal = perfCell ? perfCell.v : '';
    if (perfVal !== '' && perfVal !== null && !isNaN(Number(perfVal))) {
      startRow = r;
      break;
    }
  }
  
  if (startRow === -1) return [];
  
  for (let r = startRow; r <= range.e.r; r++) {
    const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
    const fioCell = ws[fioAddr];
    const fio = fioCell ? String(fioCell.v).trim() : '';
    if (!fio) continue;

    const posAddr = XLSX.utils.encode_cell({ r, c: COL_POS });
    const posCell = ws[posAddr];
    const position = posCell ? String(posCell.v).trim() : '';

    const portraitAddr = XLSX.utils.encode_cell({ r, c: COL_PORTRAIT });
    const portraitCell = ws[portraitAddr];
    const portrait = portraitCell ? String(portraitCell.v).trim() : '';

    const decisionAddr = XLSX.utils.encode_cell({ r, c: COL_DECISION });
    const decisionCell = ws[decisionAddr];
    const decision = decisionCell ? String(decisionCell.v).trim() : '';

    const p = [];
    COLS_PERF.forEach(c => {
      const addr = XLSX.utils.encode_cell({ r, c });
      p.push(ws[addr] ? toNum(ws[addr].v) : '');
    });
    COLS_POT.forEach(c => {
      const addr = XLSX.utils.encode_cell({ r, c });
      p.push(ws[addr] ? toNum(ws[addr].v) : '');
    });

    const paramCells = [
      ...COLS_PERF.map(c => XLSX.utils.encode_cell({ r, c })),
      ...COLS_POT.map(c => XLSX.utils.encode_cell({ r, c }))
    ];

    list.push({
      fio, position, portrait, decision, p,
      fioCell: fioAddr, posCell: posAddr,
      portraitCell: portraitAddr, decisionCell: decisionAddr,
      paramCells, isNew: false, row: r
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
  renderTable(); renderGrid(); renderEditForm();
}

/* ======================= ТАБЛИЦА ======================= */
function renderTable(){
  const tbody = $('#empTable tbody');
  tbody.innerHTML = '';
  const dept = state.currentDept;
  if (!dept) return;
  const list = state.employees[dept];

  list.forEach((emp, idx) => {
    const p = emp.p;
    const m1 = avg3(p[0],p[1],p[2]);
    const m2 = avg3(p[3],p[4],p[5]);
    const info = squareInfo(m1, m2);
    
    const portraitText = generatePortrait(emp);
    emp.portrait = portraitText;

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:11px;">${escapeHtml(portraitText)}</td>
      <td style="max-width:150px;text-align:left;font-size:11px;">${escapeHtml(emp.decision)}</td>
      <td><span class="del" data-idx="${idx}">удалить</span></td>
    `;
    tr.querySelector('.name').addEventListener('click', () => {
      state.selectedIndex = idx;
      renderTable(); renderGrid(); renderEditForm();
    });
    tr.querySelector('.del').addEventListener('click', (e) => {
      e.stopPropagation();
      if (!confirm(`Удалить сотрудника «${emp.fio}»?`)) return;
      emp.isDeleted = true; 
      emp.fio = ''; emp.position = ''; emp.portrait = ''; emp.decision = '';
      emp.p = ['','','','','',''];
      state.employees[dept].splice(idx,1);
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
  const list = dept ? state.employees[dept] : [];

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

      const members = list.filter(emp => {
        const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
        const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m=>`<li>${escapeHtml(m.fio)}</li>`).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');
      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
  `;
  wrap.appendChild(legend);
}

/* ======================= ФОРМА РЕДАКТИРОВАНИЯ ======================= */
function renderEditForm(){
  const box = $('#editForm');
  const dept = state.currentDept;
  if (!dept || state.selectedIndex === null || !state.employees[dept][state.selectedIndex]){
    box.innerHTML = '<span class="hint">Выберите сотрудника в таблице.</span>';
    return;
  }
  const emp = state.employees[dept][state.selectedIndex];
  
  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1,2].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[3,4,5].map(i=>`<label title="${POT_NAMES[i-3]}">${POT_NAMES[i-3]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="form-group">
      <label>Управленческий портрет (генерируется автоматически):</label>
      <textarea id="editPortrait" class="portrait" readonly>${escapeHtml(generatePortrait(emp))}</textarea>
    </div>

    <div class="form-group">
      <label>Управленческое решение:</label>
      <input type="text" id="editDecision" class="decision" value="${escapeHtml(emp.decision || '')}">
    </div>

    <div class="means" id="meansBox"></div>
  `;
  updateMeans();

  box.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('input', () => {
      const v = toNum(inp.value);
      emp.p[+inp.dataset.param] = v;
      if (v !== '') inp.value = v;
      
      $('#editPortrait').value = generatePortrait(emp);
      
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
  $('#editDecision').addEventListener('input', e => {
    emp.decision = e.target.value;
    renderTable();
  });

  function updateMeans(){
    const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
    const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
    const info = (m1 && m2) ? squareInfo(m1, m2) : null;
    $('#meansBox').innerHTML = `Средняя по разделу 1: <b>${m1||'—'}</b> &nbsp;|&nbsp;
      Средняя по разделу 2: <b>${m2||'—'}</b> &nbsp;|&nbsp;
      Квадрат: ${info ? `<span class="badge ${info.color}">${info.title}</span>` : '—'}`;
  }
}

/* ======================= ДОБАВЛЕНИЕ СОТРУДНИКА ======================= */
$('#btnAdd').addEventListener('click', () => {
  if (!state.currentDept) return;
  const fio = prompt('ФИО нового сотрудника:');
  if (!fio) return;
  state.employees[state.currentDept].push({
    fio: fio.trim(),
    position: '',
    portrait: '',
    decision: '',
    p: ['','','','','',''],
    isNew: true,
    fioCell: null, posCell: null, portraitCell: null, decisionCell: null,
    paramCells: [null,null,null,null,null,null],
  });
  state.selectedIndex = state.employees[state.currentDept].length - 1;
  renderTable(); renderGrid(); renderEditForm();
});

/* ======================= СОХРАНЕНИЕ ======================= */
$('#btnSave').addEventListener('click', () => {
  if (!state.workbook) return;
  let updated = 0, added = 0, deleted = 0;

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    const realName = findSheet(state.workbook, dept);
    if (!realName) return;
    
    const ws = state.workbook.Sheets[realName];
    const list = state.employees[dept];

    list.forEach(emp => {
      if (emp.isNew) return;
      if (emp.isDeleted) {
         clearCell(ws, emp.fioCell);
         clearCell(ws, emp.posCell);
         clearCell(ws, emp.portraitCell);
         clearCell(ws, emp.decisionCell);
         emp.paramCells.forEach(addr => clearCell(ws, addr));
         deleted++;
         return;
      }
      emp.portrait = generatePortrait(emp);
      
      writeCell(ws, emp.fioCell, emp.fio);
      writeCell(ws, emp.posCell, emp.position);
      writeCell(ws, emp.portraitCell, emp.portrait);
      writeCell(ws, emp.decisionCell, emp.decision);
      for (let i=0; i<6; i++){
        writeCell(ws, emp.paramCells[i], emp.p[i] === '' ? '' : Number(emp.p[i]));
      }
      updated++;
    });

    const newOnes = list.filter(e => e.isNew && !e.isDeleted);
    if (newOnes.length) {
      let range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
      let lastRow = 4;
      for (let r = range.e.r; r >= 4; r--) {
        const addr = XLSX.utils.encode_cell({ r, c: COL_FIO });
        const cell = ws[addr];
        if (cell && String(cell.v||'').trim() !== '') {
          lastRow = r;
          break;
        }
      }

      newOnes.forEach((emp, k) => {
        const row = lastRow + 1 + k;
        const fioAddr = XLSX.utils.encode_cell({ r: row, c: COL_FIO });
        const posAddr = XLSX.utils.encode_cell({ r: row, c: COL_POS });
        const portAddr = XLSX.utils.encode_cell({ r: row, c: COL_PORTRAIT });
        const decAddr = XLSX.utils.encode_cell({ r: row, c: COL_DECISION });
        
        emp.portrait = generatePortrait(emp);
        
        writeCell(ws, fioAddr, emp.fio);
        writeCell(ws, posAddr, emp.position);
        writeCell(ws, portAddr, emp.portrait);
        writeCell(ws, decAddr, emp.decision);
        emp.fioCell = fioAddr;
        emp.posCell = posAddr;
        emp.portraitCell = portAddr;
        emp.decisionCell = decAddr;

        const addresses = [];
        COLS_PERF.forEach((c, i) => {
          const addr = XLSX.utils.encode_cell({ r: row, c });
          writeCell(ws, addr, emp.p[i] === '' ? '' : Number(emp.p[i]));
          addresses.push(addr);
        });
        COLS_POT.forEach((c, i) => {
          const addr = XLSX.utils.encode_cell({ r: row, c });
          writeCell(ws, addr, emp.p[i+3] === '' ? '' : Number(emp.p[i+3]));
          addresses.push(addr);
        });
        emp.paramCells = addresses;
        emp.isNew = false;
        added++;
      });

      range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
      const maxRow = lastRow + newOnes.length;
      if (range.e.r < maxRow) {
        range.e.r = maxRow;
        ws['!ref'] = XLSX.utils.encode_range(range);
      }
    }
  });

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    state.employees[dept] = state.employees[dept].filter(e => !e.isDeleted);
  });

  XLSX.writeFile(state.workbook, state.fileName);
  setStatus(`Сохранено: обновлено ${updated}, добавлено ${added}, удалено ${deleted}.`);
});

function writeCell(ws, addr, value){
  if (!addr) return;
  if (value === '' || value === null || value === undefined){
    if (ws[addr]) { ws[addr].v = ''; ws[addr].t = 's'; }
    else { ws[addr] = { t:'s', v:'' }; }
  } else {
    if (ws[addr]) { ws[addr].v = value; ws[addr].t = typeof value === 'number' ? 'n' : 's'; }
    else { ws[addr] = { t: typeof value === 'number' ? 'n' : 's', v: value }; }
  }
}

function clearCell(ws, addr) {
  if (!addr) return;
  if (ws[addr]) { ws[addr].v = ''; ws[addr].t = 's'; }
}
</script>
</body>
</html>



























<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Оценка сотрудников — 9-box grid</title>
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
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
  input[type=text].decision { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; margin-top:4px; }
  textarea.portrait { width:100%; padding:6px; border:1px solid var(--border); border-radius:6px; min-height:60px; resize:vertical; font-family:inherit; font-size:13px;}
  
  /* 9-box сетка */
  .grid-wrap { display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; max-width:460px; }
  .cell { position: relative; border:1px solid var(--border); border-radius:10px; padding:10px; min-height:110px; }
  .cell h4 { margin:0 0 2px; font-size:12px; color:#475467; font-weight:600; text-transform:uppercase; letter-spacing:.3px; }
  .cell .sq-title { font-size:14px; font-weight:700; color:#1f2937; margin:2px 0 6px; }
  .cell ul { margin:0; padding-left:16px; font-size:12px; }
  .cell.hl { outline:3px solid var(--accent); outline-offset:-3px; }
  
  .cell.green { background:#d9f2d9; border-color:#86c986; }
  .cell.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .cell.red   { background:#fde2e1; border-color:#e58b88; }

  .legend { display:flex; gap:16px; flex-wrap:wrap; margin-top:12px; font-size:13px; color:#333; width:100%; }
  .legend .item { display:flex; align-items:center; gap:6px; }
  .legend .swatch { width:16px; height:16px; border-radius:4px; border:1px solid #bbb; }
  .legend .swatch.green{ background:#d9f2d9; border-color:#86c986; }
  .legend .swatch.yellow{ background:#fff4cc; border-color:#e6c94a; }
  .legend .swatch.red{ background:#fde2e1; border-color:#e58b88; }

  .badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
  .badge.green { background:#d9f2d9; color:#166534; }
  .badge.yellow{ background:#fff4cc; color:#92400e; }
  .badge.red   { background:#fde2e1; color:#991b1b; }
  .badge.gray  { background:#f3f4f6; color:#4b5563; }

  .hint { color:#666; font-size:13px; }
  .status { font-size:13px; color:#166534; }
  .del { color:#b91c1c; cursor:pointer; font-size:12px; }
  .means { font-size:14px; margin:6px 0; }
  .form-group { margin-bottom: 12px; }
  .form-group label { display:block; font-weight:600; margin-bottom:4px; font-size:13px; color:#475467; }
</style>
</head>
<body>

<h1>Оценка сотрудников — 9-box grid</h1>

<div class="panel">
  <div class="row">
    <input type="file" id="fileInput" accept=".xlsx,.xls">
    <button id="btnSave" class="primary" disabled>💾 Сохранить</button>
    <button id="btnAdd" disabled>➕ Добавить сотрудника</button>
    <span id="status" class="status"></span>
  </div>
  <p class="hint">
    Колонки: B (ФИО), C (Должность), D-F (Эффективность), H-J (Потенциал), M (Портрет), N (Решение).
    Формулы в G, K, L не затрагиваются.
  </p>
</div>

<div class="panel">
  <div class="row" id="deptButtons">
    <button data-dept="отдел1" disabled>Отдел 1</button>
    <button data-dept="отдел2" disabled>Отдел 2</button>
    <button data-dept="отдел3" disabled>Отдел 3</button>
  </div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Сотрудники отдела</h3>
  <div style="overflow-x:auto;">
    <table id="empTable">
      <thead>
        <tr>
          <th>ФИО</th><th>Должность</th><th id="th_p1">Р1</th><th id="th_p2">Р2</th><th id="th_p3">Р3</th>
          <th id="th_p4">П1</th><th id="th_p5">П2</th><th id="th_p6">П3</th>
          <th>Ср. Эфф.</th><th>Ср. Пот.</th><th>Квадрат</th><th>Портрет</th><th>Решение</th><th></th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Карта 9 квадратов (текущий отдел)</h3>
  <div class="grid-wrap" id="grid9"></div>
</div>

<div class="panel">
  <h3 style="margin-top:0">Редактирование сотрудника</h3>
  <div id="editForm" class="hint">Выберите сотрудника в таблице.</div>
</div>

<script>
/* ======================= КОНСТАНТЫ ======================= */
const COL_FIO = 1;       // B
const COL_POS = 2;       // C
const COLS_PERF = [3,4,5]; // D, E, F
const COLS_POT  = [7,8,9]; // H, I, J
const COL_PORTRAIT = 12;   // M
const COL_DECISION = 13;   // N

// Значения по умолчанию
let SQUARE_NAMES = {
  1: '1. Якорь', 2: '2. Пассажир', 3: '3. Звезда',
  4: '4. Проблемный', 5: '5. Стабильный', 6: '6. Результативный',
  7: '7. Аутсайдер', 8: '8. Исполнитель', 9: '9. Профессионал'
};
let PERF_NAMES = ['Дедлайн ЗОД', 'Качество операц. контроля', 'Дисциплина'];
let POT_NAMES = ['Оптимизация процессов', 'Наставничество', 'Стрессоустойчивость'];

// Шаблоны портретов (если справочник пуст, используется этот текст)
let PORTRAIT_TEMPLATES = {
  1: 'Лидер. Максимальная эффективность и высокий потенциал. Готов к повышению.',
  2: 'Исполнитель с потенциалом. Показывает результат, но нужно развивать инициативность.',
  3: 'Перспективный сотрудник. Высокий потенциал, но пока не дотягивает до нужных результатов.',
  4: 'Проблемная зона. Низкая эффективность при среднем потенциале. Требуется контроль.',
  5: 'Стабильный сотрудник. Надежно выполняет работу, но не стремится к росту.',
  6: 'Результативный. Отлично справляется с задачами, но потенциал ограничен.',
  7: 'Зона риска. Высокий потенциал, но крайне низкие результаты.',
  8: 'Аутсайдер. Низкие показатели по обоим направлениям.',
  9: 'Специалист. Высокие результаты, но низкий потенциал (достиг потолка).'
};

function squareInfoForLevels(x, y){
  const map = {
    high: { low:['yellow', 7], mid:['green', 3], high:['green', 1] },
    mid:  { low:['red',    4], mid:['yellow',5], high:['green', 6] },
    low:  { low:['red',    8], mid:['red',   2], high:['yellow',9] }
  };
  const [color, num] = map[y][x];
  return { color, num, title: SQUARE_NAMES[num] || `Квадрат ${num}` };
}

function squareInfo(m1, m2){
  if (!m1 || !m2) return { title: '—', color: 'gray', num: 0 };
  const lvl = v => v < 1.67 ? 'low' : (v < 2.34 ? 'mid' : 'high');
  return squareInfoForLevels(lvl(m1), lvl(m2));
}

// Генерация управленческого портрета
function generatePortrait(emp) {
  const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
  const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
  if (!m1 || !m2) return 'Оценки не выставлены.';
  
  const info = squareInfo(m1, m2);
  const base = PORTRAIT_TEMPLATES[info.num] || `Квадрат: ${info.title}.`;
  
  const strengths = [];
  const weaknesses = [];
  
  for (let i=0; i<6; i++) {
    const val = Number(emp.p[i]);
    const name = i < 3 ? PERF_NAMES[i] : POT_NAMES[i-3];
    if (val === 3) strengths.push(name);
    if (val === 1) weaknesses.push(name);
  }
  
  let text = base;
  if (strengths.length > 0) text += ` Сильные стороны: ${strengths.join(', ')}.`;
  if (weaknesses.length > 0) text += ` Зоны развития: ${weaknesses.join(', ')}.`;
  return text;
}

/* ======================= СОСТОЯНИЕ ======================= */
const state = {
  workbook: null,
  fileName: 'employees.xlsx',
  currentDept: null,
  employees: { 'отдел1': [], 'отдел2': [], 'отдел3': [] },
  selectedIndex: null,
};

const $ = sel => document.querySelector(sel);
const avg3 = (a,b,c)=> +(((a||0)+(b||0)+(c||0))/3).toFixed(2);

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
  setTimeout(()=>{ if (el.textContent === msg) el.textContent=''; }, 5000);
}

/* ======================= ЧТЕНИЕ ФАЙЛА ======================= */
$('#fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  state.fileName = file.name;

  const data = await file.arrayBuffer();
  const wb = XLSX.read(data, { type:'array', cellStyles:true, cellDates:true });
  state.workbook = wb;

  readReferenceSheet(wb);

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    state.employees[dept] = readDeptSheet(wb, dept);
  });

  document.querySelectorAll('#deptButtons button').forEach(b => b.disabled = false);
  $('#btnSave').disabled = false;
  $('#btnAdd').disabled = false;

  setStatus('Файл загружен.');
  selectDept('отдел1');
});

function readReferenceSheet(wb) {
  const ws = wb.Sheets['Справочник'] || wb.Sheets['справочник'];
  if (!ws) return;

  const aoa = XLSX.utils.sheet_to_json(ws, { header:1, defval:'' });
  
  let perfParams = [];
  let potParams = [];
  let currentMode = '';
  let foundPortraits = {};

  for (let r = 0; r < aoa.length; r++) {
    const row = aoa[r];
    const col0 = String(row[0] || '').trim();
    
    // Ищем заголовки разделов
    if (col0.includes('Ось Эффективности')) { currentMode = 'perf'; continue; }
    if (col0.includes('Ось Потенциала')) { currentMode = 'pot'; continue; }
    if (col0.includes('Портрет') || col0.includes('Квадрат')) { currentMode = 'portrait'; continue; }

    if (currentMode === 'perf' && col0 && col0 !== 'Показатель') perfParams.push(col0);
    if (currentMode === 'pot' && col0 && col0 !== 'Показатель') potParams.push(col0);
    
    // Пытаемся найти тексты портретов в справочнике (если они там есть)
    if (currentMode === 'portrait' && col0) {
       // Логика поиска текстов портретов (если они есть в виде таблицы)
    }
  }

  if (perfParams.length >= 3) PERF_NAMES = perfParams.slice(0, 3);
  if (potParams.length >= 3) POT_NAMES = potParams.slice(0, 3);
  
  // Обновляем заголовки
  setTimeout(() => {
    $('#th_p1').textContent = PERF_NAMES[0];
    $('#th_p2').textContent = PERF_NAMES[1];
    $('#th_p3').textContent = PERF_NAMES[2];
    $('#th_p4').textContent = POT_NAMES[0];
    $('#th_p5').textContent = POT_NAMES[1];
    $('#th_p6').textContent = POT_NAMES[2];
  }, 50);
}

function readDeptSheet(wb, sheetName){
  const ws = wb.Sheets[sheetName];
  if (!ws) return [];
  const range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
  const list = [];

  for (let r = 4; r <= range.e.r; r++) {
    const fioAddr = XLSX.utils.encode_cell({ r, c: COL_FIO });
    const fioCell = ws[fioAddr];
    const fio = fioCell ? String(fioCell.v).trim() : '';
    if (!fio) continue;

    const posAddr = XLSX.utils.encode_cell({ r, c: COL_POS });
    const posCell = ws[posAddr];
    const position = posCell ? String(posCell.v).trim() : '';

    const portraitAddr = XLSX.utils.encode_cell({ r, c: COL_PORTRAIT });
    const portraitCell = ws[portraitAddr];
    const portrait = portraitCell ? String(portraitCell.v).trim() : '';

    const decisionAddr = XLSX.utils.encode_cell({ r, c: COL_DECISION });
    const decisionCell = ws[decisionAddr];
    const decision = decisionCell ? String(decisionCell.v).trim() : '';

    const p = [];
    COLS_PERF.forEach(c => {
      const addr = XLSX.utils.encode_cell({ r, c });
      p.push(ws[addr] ? toNum(ws[addr].v) : '');
    });
    COLS_POT.forEach(c => {
      const addr = XLSX.utils.encode_cell({ r, c });
      p.push(ws[addr] ? toNum(ws[addr].v) : '');
    });

    const paramCells = [
      ...COLS_PERF.map(c => XLSX.utils.encode_cell({ r, c })),
      ...COLS_POT.map(c => XLSX.utils.encode_cell({ r, c }))
    ];

    list.push({
      fio,
      position,
      portrait,
      decision,
      p,
      fioCell: fioAddr,
      posCell: posAddr,
      portraitCell: portraitAddr,
      decisionCell: decisionAddr,
      paramCells: paramCells,
      isNew: false,
      row: r
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
  renderTable(); renderGrid(); renderEditForm();
}

/* ======================= ТАБЛИЦА ======================= */
function renderTable(){
  const tbody = $('#empTable tbody');
  tbody.innerHTML = '';
  const dept = state.currentDept;
  if (!dept) return;
  const list = state.employees[dept];

  list.forEach((emp, idx) => {
    const p = emp.p;
    const m1 = avg3(p[0],p[1],p[2]);
    const m2 = avg3(p[3],p[4],p[5]);
    const info = squareInfo(m1, m2);
    
    // Автогенерация портрета
    const portraitText = generatePortrait(emp);
    emp.portrait = portraitText; // сохраняем в память для записи в Excel

    const tr = document.createElement('tr');
    if (idx === state.selectedIndex) tr.classList.add('selected');
    tr.innerHTML = `
      <td class="name">${escapeHtml(emp.fio)}</td>
      <td>${escapeHtml(emp.position)}</td>
      ${p.map(v=>`<td>${v===''?'':v}</td>`).join('')}
      <td>${m1||''}</td>
      <td>${m2||''}</td>
      <td><span class="badge ${info.color}">${info.title}</span></td>
      <td style="max-width:200px;text-align:left;font-size:11px;">${escapeHtml(portraitText)}</td>
      <td style="max-width:150px;text-align:left;font-size:11px;">${escapeHtml(emp.decision)}</td>
      <td><span class="del" data-idx="${idx}">удалить</span></td>
    `;
    tr.querySelector('.name').addEventListener('click', () => {
      state.selectedIndex = idx;
      renderTable(); renderGrid(); renderEditForm();
    });
    tr.querySelector('.del').addEventListener('click', (e) => {
      e.stopPropagation();
      if (!confirm(`Удалить сотрудника «${emp.fio}»? Данные будут очищены при сохранении.`)) return;
      emp.isDeleted = true; 
      emp.fio = '';
      emp.position = '';
      emp.portrait = '';
      emp.decision = '';
      emp.p = ['','','','','',''];
      state.employees[dept].splice(idx,1);
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
  const list = dept ? state.employees[dept] : [];

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

      const members = list.filter(emp => {
        const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
        const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
        if (!m1 || !m2) return false;
        return lvl(m1) === x && lvl(m2) === y;
      });

      cell.innerHTML = `
        <h4>Результат: ${colLabel[x]} / Потенциал: ${rowLabel[y]}</h4>
        <div class="sq-title">${info.title}</div>
        <ul>${members.map(m=>`<li>${escapeHtml(m.fio)}</li>`).join('')}</ul>
      `;
      if (list[state.selectedIndex] && members.includes(list[state.selectedIndex]))
        cell.classList.add('hl');
      wrap.appendChild(cell);
    }
  }

  const legend = document.createElement('div');
  legend.className = 'legend';
  legend.innerHTML = `
    <div class="item"><span class="swatch green"></span> Сильная зона — кадровый резерв</div>
    <div class="item"><span class="swatch yellow"></span> Зона внимания / развития</div>
    <div class="item"><span class="swatch red"></span> Зона риска — требует вмешательства</div>
  `;
  wrap.appendChild(legend);
}

/* ======================= ФОРМА РЕДАКТИРОВАНИЯ ======================= */
function renderEditForm(){
  const box = $('#editForm');
  const dept = state.currentDept;
  if (!dept || state.selectedIndex === null || !state.employees[dept][state.selectedIndex]){
    box.innerHTML = '<span class="hint">Выберите сотрудника в таблице.</span>';
    return;
  }
  const emp = state.employees[dept][state.selectedIndex];
  
  box.innerHTML = `
    <div class="row" style="margin-bottom:10px">
      <label>ФИО: <input id="editFio" class="fio" value="${escapeHtml(emp.fio)}"></label>
      <label>Должность: <input id="editPos" class="pos" value="${escapeHtml(emp.position || '')}"></label>
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Эффективность (Раздел 1)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[0,1,2].map(i=>`<label title="${PERF_NAMES[i]}">${PERF_NAMES[i]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>
    
    <div class="row" style="margin-bottom:6px"><b>Ось Потенциала (Раздел 2)</b></div>
    <div class="row" style="margin-bottom:10px">
      ${[3,4,5].map(i=>`<label title="${POT_NAMES[i-3]}">${POT_NAMES[i-3]}: <input type="number" min="1" max="3" step="1" data-param="${i}" value="${emp.p[i]===''?'':emp.p[i]}"></label>`).join('')}
    </div>

    <div class="form-group">
      <label>Управленческий портрет (генерируется автоматически):</label>
      <textarea id="editPortrait" class="portrait" readonly>${escapeHtml(generatePortrait(emp))}</textarea>
    </div>

    <div class="form-group">
      <label>Управленческое решение:</label>
      <input type="text" id="editDecision" class="decision" value="${escapeHtml(emp.decision || '')}">
    </div>

    <div class="means" id="meansBox"></div>
  `;
  updateMeans();

  box.querySelectorAll('input[type=number]').forEach(inp => {
    inp.addEventListener('input', () => {
      const v = toNum(inp.value);
      emp.p[+inp.dataset.param] = v;
      if (v !== '') inp.value = v;
      
      // Обновляем портрет при изменении оценок
      $('#editPortrait').value = generatePortrait(emp);
      
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
  $('#editDecision').addEventListener('input', e => {
    emp.decision = e.target.value;
    renderTable();
  });

  function updateMeans(){
    const m1 = avg3(emp.p[0],emp.p[1],emp.p[2]);
    const m2 = avg3(emp.p[3],emp.p[4],emp.p[5]);
    const info = (m1 && m2) ? squareInfo(m1, m2) : null;
    $('#meansBox').innerHTML = `Средняя по разделу 1: <b>${m1||'—'}</b> &nbsp;|&nbsp;
      Средняя по разделу 2: <b>${m2||'—'}</b> &nbsp;|&nbsp;
      Квадрат: ${info ? `<span class="badge ${info.color}">${info.title}</span>` : '—'}`;
  }
}

/* ======================= ДОБАВЛЕНИЕ СОТРУДНИКА ======================= */
$('#btnAdd').addEventListener('click', () => {
  if (!state.currentDept) return;
  const fio = prompt('ФИО нового сотрудника:');
  if (!fio) return;
  state.employees[state.currentDept].push({
    fio: fio.trim(),
    position: '',
    portrait: '',
    decision: '',
    p: ['','','','','',''],
    isNew: true,
    fioCell: null,
    posCell: null,
    portraitCell: null,
    decisionCell: null,
    paramCells: [null,null,null,null,null,null],
  });
  state.selectedIndex = state.employees[state.currentDept].length - 1;
  renderTable(); renderGrid(); renderEditForm();
});

/* ======================= СОХРАНЕНИЕ ======================= */
$('#btnSave').addEventListener('click', () => {
  if (!state.workbook) return;
  let updated = 0, added = 0, deleted = 0;

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    const ws = state.workbook.Sheets[dept];
    if (!ws) return;
    const list = state.employees[dept];

    list.forEach(emp => {
      if (emp.isNew) return;
      if (emp.isDeleted) {
         clearCell(ws, emp.fioCell);
         clearCell(ws, emp.posCell);
         clearCell(ws, emp.portraitCell);
         clearCell(ws, emp.decisionCell);
         emp.paramCells.forEach(addr => clearCell(ws, addr));
         deleted++;
         return;
      }
      // Перед сохранением актуализируем портрет
      emp.portrait = generatePortrait(emp);
      
      writeCell(ws, emp.fioCell, emp.fio);
      writeCell(ws, emp.posCell, emp.position);
      writeCell(ws, emp.portraitCell, emp.portrait);
      writeCell(ws, emp.decisionCell, emp.decision);
      for (let i=0; i<6; i++){
        writeCell(ws, emp.paramCells[i], emp.p[i] === '' ? '' : Number(emp.p[i]));
      }
      updated++;
    });

    const newOnes = list.filter(e => e.isNew && !e.isDeleted);
    if (newOnes.length) {
      const range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
      let lastRow = 4;
      for (let r = range.e.r; r >= 4; r--) {
        const addr = XLSX.utils.encode_cell({ r, c: COL_FIO });
        const cell = ws[addr];
        if (cell && String(cell.v||'').trim() !== '') {
          lastRow = r;
          break;
        }
      }

      newOnes.forEach((emp, k) => {
        const row = lastRow + 1 + k;
        const fioAddr = XLSX.utils.encode_cell({ r: row, c: COL_FIO });
        const posAddr = XLSX.utils.encode_cell({ r: row, c: COL_POS });
        const portAddr = XLSX.utils.encode_cell({ r: row, c: COL_PORTRAIT });
        const decAddr = XLSX.utils.encode_cell({ r: row, c: COL_DECISION });
        
        emp.portrait = generatePortrait(emp);
        
        writeCell(ws, fioAddr, emp.fio);
        writeCell(ws, posAddr, emp.position);
        writeCell(ws, portAddr, emp.portrait);
        writeCell(ws, decAddr, emp.decision);
        emp.fioCell = fioAddr;
        emp.posCell = posAddr;
        emp.portraitCell = portAddr;
        emp.decisionCell = decAddr;

        const addresses = [];
        COLS_PERF.forEach((c, i) => {
          const addr = XLSX.utils.encode_cell({ r: row, c });
          writeCell(ws, addr, emp.p[i] === '' ? '' : Number(emp.p[i]));
          addresses.push(addr);
        });
        COLS_POT.forEach((c, i) => {
          const addr = XLSX.utils.encode_cell({ r: row, c });
          writeCell(ws, addr, emp.p[i+3] === '' ? '' : Number(emp.p[i+3]));
          addresses.push(addr);
        });
        emp.paramCells = addresses;
        emp.isNew = false;
        added++;
      });

      const newRange = XLSX.utils.decode_range(ws['!ref']);
      const maxRow = lastRow + newOnes.length;
      if (newRange.e.r < maxRow) {
        newRange.e.r = maxRow;
        ws['!ref'] = XLSX.utils.encode_range(newRange);
      }
    }
  });

  ['отдел1','отдел2','отдел3'].forEach(dept => {
    state.employees[dept] = state.employees[dept].filter(e => !e.isDeleted);
  });

  XLSX.writeFile(state.workbook, state.fileName);
  setStatus(`Сохранено: обновлено ${updated}, добавлено ${added}, удалено ${deleted}.`);
});

function writeCell(ws, addr, value){
  if (!addr) return;
  if (value === '' || value === null || value === undefined){
    if (ws[addr]) {
      ws[addr].v = '';
      ws[addr].t = 's';
    } else {
      ws[addr] = { t:'s', v:'' };
    }
  } else {
    if (ws[addr]) {
      ws[addr].v = value;
      ws[addr].t = typeof value === 'number' ? 'n' : 's';
    } else {
      ws[addr] = { t: typeof value === 'number' ? 'n' : 's', v: value };
    }
  }
}

function clearCell(ws, addr) {
  if (!addr) return;
  if (ws[addr]) {
    ws[addr].v = '';
    ws[addr].t = 's';
  }
}
</script>
</body>
</html>

























<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Разбить по столбцу А</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h2 { margin-top: 0; color: #333; }
        p { color: #666; font-size: 14px; }
        button { background: #2b7b8c; color: white; border: none; padding: 10px 24px; font-size: 16px; border-radius: 4px; cursor: pointer; width: 100%; }
        button:hover { background: #1f5f6e; }
        #status { margin-top: 15px; padding: 10px; background: #f0f0f0; border-radius: 4px; font-size: 13px; display: none; }
    </style>
</head>
<body>
<div class="container">
    <h2>📊 Разбить по столбцу А</h2>
    <p>Создаёт отдельные листы для каждого уникального значения в столбце A.</p>
    <button id="runBtn">▶ Выполнить</button>
    <div id="status">Готово! Создано листов: <span id="count"></span></div>
</div>

<script>
    // ----- Код макроса (рабочий, проверенный) -----
    var macroCode = `
(function() {
    var srcSheet = Api.GetActiveSheet();
    var lastRow = 0;
    var maxRows = 5000;

    // Определяем последнюю строку с данными
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

    // Определяем последний столбец
    var maxCols = 1;
    for (var c = 1; c <= 50; c++) {
        var colLetter = String.fromCharCode(64 + c);
        var val = srcSheet.GetRange(colLetter + "1").GetValue();
        if (val !== undefined && val !== null && val !== "") {
            maxCols = c;
        }
    }

    // Собираем уникальные значения (пропускаем первую строку-заголовок)
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
        return;
    }

    // Для каждого уникального значения создаём лист и копируем строки
    for (var u = 0; u < uniqueValues.length; u++) {
        var currentValue = uniqueValues[u];
        var sheetName = currentValue;
        if (sheetName.length > 31) sheetName = sheetName.substring(0, 31);
        sheetName = sheetName.replace(/[\\\\\\/\\?\\*\\[\\]]/g, '_');

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

        if (!destSheet) continue;

        // Копируем заголовок
        for (var c = 1; c <= maxCols; c++) {
            var colLetter = String.fromCharCode(64 + c);
            var headerVal = srcSheet.GetRange(colLetter + headerRow).GetValue();
            destSheet.GetRange(colLetter + "1").SetValue(headerVal);
        }

        // Копируем строки с нужным значением
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

    // Итог
    srcSheet.GetRange("Z1").SetValue("Готово! Создано листов: " + uniqueValues.length);
    // Передаём количество обратно в плагин через закрытие
    window.Asc.plugin.executeCommand("close", JSON.stringify({ count: uniqueValues.length }));
})();
    `;

    // ----- Обработчик кнопки -----
    document.getElementById('runBtn').addEventListener('click', function() {
        var btn = this;
        btn.disabled = true;
        btn.textContent = 'Выполняется...';

        // Выполняем код как макрос
        window.Asc.plugin.executeCommand("macro", macroCode);

        // Ждём результат через onClose
        window.Asc.plugin.onClose = function(result) {
            if (result) {
                try {
                    var data = JSON.parse(result);
                    document.getElementById('count').textContent = data.count;
                    document.getElementById('status').style.display = 'block';
                } catch(e) {
                    document.getElementById('count').textContent = 'неизвестно';
                    document.getElementById('status').style.display = 'block';
                }
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
    <style>
        body { font-family: Arial; padding: 20px; background: #f5f5f5; }
        .container { max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        button { background: #2b7b8c; color: white; border: none; padding: 10px 24px; font-size: 16px; border-radius: 4px; cursor: pointer; width: 100%; }
        button:hover { background: #1f5f6e; }
        #log { margin-top: 15px; padding: 10px; background: #f0f0f0; border-radius: 4px; font-size: 13px; max-height: 300px; overflow-y: auto; white-space: pre-wrap; word-break: break-all; font-family: monospace; }
    </style>
</head>
<body>
<div class="container">
    <h2>📊 Разбить по столбцу А</h2>
    <button id="runBtn">▶ Выполнить</button>
    <div id="log">Лог будет здесь...</div>
</div>

<script>
    function logMessage(msg) {
        var logDiv = document.getElementById('log');
        logDiv.textContent += msg + '\n';
        logDiv.scrollTop = logDiv.scrollHeight;
    }

    document.getElementById('runBtn').addEventListener('click', function() {
        var btn = this;
        btn.disabled = true;
        btn.textContent = 'Выполняется...';
        logMessage('=== СТАРТ ===');

        // Используем executeMethod для доступа к API
        window.Asc.plugin.executeMethod("callCommand", [function() {
            try {
                // Внутри этого колбэка Api должен быть доступен
                if (typeof Api === 'undefined') {
                    // Если всё равно undefined, попробуем получить через this
                    var api = this.Api || window.Api;
                    if (!api) {
                        logMessage('❌ Api не определён');
                        window.Asc.plugin.executeCommand("close", "error");
                        return;
                    }
                }
                logMessage('✅ Api доступен');

                var srcSheet = Api.GetActiveSheet();
                if (!srcSheet) {
                    logMessage('❌ Активный лист не получен');
                    window.Asc.plugin.executeCommand("close", "error");
                    return;
                }
                logMessage('✅ Активный лист получен');

                // Проверка записи
                srcSheet.GetRange("Z1").SetValue("Плагин работает!");
                logMessage('✅ Запись в Z1 выполнена');

                // ---- Ваш основной код здесь ----
                // (код разбиения по столбцу А, который мы уже писали)
                // Я сокращу для примера, но вы можете вставить полную версию

                // Закрываем плагин с успехом
                window.Asc.plugin.executeCommand("close", "success");
            } catch (e) {
                logMessage('❌ Ошибка: ' + e.message);
                window.Asc.plugin.executeCommand("close", "error");
            }
        }]);

        window.Asc.plugin.onClose = function(result) {
            logMessage('🔚 Результат: ' + result);
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
    <style>
        body { font-family: Arial; padding: 20px; background: #f5f5f5; }
        .container { max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        button { background: #2b7b8c; color: white; border: none; padding: 10px 24px; font-size: 16px; border-radius: 4px; cursor: pointer; width: 100%; }
        button:hover { background: #1f5f6e; }
        #log { margin-top: 15px; padding: 10px; background: #f0f0f0; border-radius: 4px; font-size: 13px; max-height: 300px; overflow-y: auto; white-space: pre-wrap; word-break: break-all; font-family: monospace; }
    </style>
</head>
<body>
<div class="container">
    <h2>📊 Разбить по столбцу А</h2>
    <button id="runBtn">▶ Выполнить</button>
    <div id="log">Лог будет здесь...</div>
</div>

<script>
    function logMessage(msg) {
        var logDiv = document.getElementById('log');
        logDiv.textContent += msg + '\n';
        logDiv.scrollTop = logDiv.scrollHeight;
    }

    document.getElementById('runBtn').addEventListener('click', function() {
        var btn = this;
        btn.disabled = true;
        btn.textContent = 'Выполняется...';
        logMessage('=== СТАРТ ===');

        // Проверяем доступность Api
        if (typeof Api === 'undefined') {
            logMessage('❌ ОШИБКА: Api не определён!');
            btn.disabled = false;
            btn.textContent = '▶ Выполнить';
            return;
        }
        logMessage('✅ Api доступен');

        window.Asc.plugin.callCommand(function() {
            try {
                logMessage('▶ callCommand выполняется');

                var srcSheet = Api.GetActiveSheet();
                if (!srcSheet) {
                    logMessage('❌ Не удалось получить активный лист');
                    window.Asc.plugin.executeCommand("close", "error");
                    return;
                }
                logMessage('✅ Активный лист получен');

                // Проверочная запись
                srcSheet.GetRange("Z1").SetValue("Плагин начал работу");
                logMessage('✅ Записано в Z1: "Плагин начал работу"');

                // ---- Определяем последнюю строку ----
                var lastRow = 0;
                var maxRows = 5000;
                logMessage('🔍 Поиск последней строки...');

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

                logMessage('📌 Последняя строка: ' + lastRow);
                srcSheet.GetRange("Z2").SetValue("LastRow: " + lastRow);

                if (lastRow === 0) {
                    srcSheet.GetRange("Z1").SetValue("Нет данных в столбце A");
                    logMessage('❌ Нет данных, завершение');
                    window.Asc.plugin.executeCommand("close", "no data");
                    return;
                }

                // ---- Определяем максимальный столбец ----
                var maxCols = 1;
                for (var c = 1; c <= 50; c++) {
                    var colLetter = String.fromCharCode(64 + c);
                    var val = srcSheet.GetRange(colLetter + "1").GetValue();
                    if (val !== undefined && val !== null && val !== "") {
                        maxCols = c;
                    }
                }
                logMessage('📌 Макс колонок: ' + maxCols);
                srcSheet.GetRange("Z3").SetValue("MaxCols: " + maxCols);

                // ---- Собираем уникальные значения ----
                var uniqueValues = [];
                var headerRow = 1;
                logMessage('🔍 Сбор уникальных значений...');

                for (var r = 2; r <= lastRow; r++) {
                    var val = srcSheet.GetRange("A" + r).GetValue();
                    if (val && val.toString().trim() !== "") {
                        var key = val.toString().trim();
                        if (uniqueValues.indexOf(key) === -1) {
                            uniqueValues.push(key);
                        }
                    }
                }

                logMessage('📌 Найдено уникальных: ' + uniqueValues.length);
                srcSheet.GetRange("Z4").SetValue("Unique: " + uniqueValues.length);

                if (uniqueValues.length === 0) {
                    srcSheet.GetRange("Z1").SetValue("Нет уникальных значений");
                    logMessage('❌ Нет уникальных, завершение');
                    window.Asc.plugin.executeCommand("close", "no unique");
                    return;
                }

                // ---- Создаём листы и копируем ----
                logMessage('🚀 Начинаем создание листов...');
                for (var u = 0; u < uniqueValues.length; u++) {
                    var currentValue = uniqueValues[u];
                    var sheetName = currentValue;
                    if (sheetName.length > 31) sheetName = sheetName.substring(0, 31);
                    sheetName = sheetName.replace(/[\\\/\?\*\[\]]/g, '_');
                    logMessage('▶ Обработка: "' + sheetName + '"');

                    var destSheet = Api.GetSheet(sheetName);
                    if (!destSheet) {
                        Api.AddSheet(sheetName);
                        destSheet = Api.GetSheet(sheetName);
                        logMessage('✅ Создан новый лист: ' + sheetName);
                    } else {
                        logMessage('⚠️ Лист уже существует, очищаем: ' + sheetName);
                        // Очистка (упрощённая)
                        for (var clearR = 1; clearR <= 5000; clearR++) {
                            for (var clearC = 1; clearC <= maxCols; clearC++) {
                                var clearLetter = String.fromCharCode(64 + clearC);
                                destSheet.GetRange(clearLetter + clearR).SetValue("");
                            }
                        }
                    }

                    if (!destSheet) {
                        logMessage('❌ Ошибка создания листа: ' + sheetName);
                        continue;
                    }

                    // Копируем заголовок
                    for (var c = 1; c <= maxCols; c++) {
                        var colLetter = String.fromCharCode(64 + c);
                        var headerVal = srcSheet.GetRange(colLetter + headerRow).GetValue();
                        destSheet.GetRange(colLetter + "1").SetValue(headerVal);
                    }

                    // Копируем строки
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
                    logMessage('✅ Скопировано строк для "' + sheetName + '": ' + (destRow - 2));
                }

                // ---- Итог ----
                srcSheet.GetRange("Z1").SetValue("Готово! Создано листов: " + uniqueValues.length);
                logMessage('✅ ЗАВЕРШЕНО УСПЕШНО! Создано листов: ' + uniqueValues.length);
                window.Asc.plugin.executeCommand("close", "success");

            } catch (e) {
                logMessage('❌ ИСКЛЮЧЕНИЕ: ' + e.message);
                logMessage('Stack: ' + e.stack);
                var srcSheet = Api.GetActiveSheet();
                if (srcSheet) srcSheet.GetRange("Z1").SetValue("Ошибка: " + e.message);
                window.Asc.plugin.executeCommand("close", "error");
            }
        }, false);

        // Обработчик закрытия
        window.Asc.plugin.onClose = function(result) {
            logMessage('🔚 Плагин завершил работу, результат: ' + result);
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
