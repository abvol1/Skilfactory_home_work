
# ============================================
# ПРОСТОЙ ЭКСПОРТ РЕЗУЛЬТАТА СРАВНЕНИЯ (CSV)
# ============================================
@app.route('/download_comparison/<filename>')
def download_comparison(filename):
    """Скачивает результат сравнения (обходной путь)"""
    try:
        # Пытаемся найти файл
        file_path = os.path.join(TEMP_DIR, filename)
        
        if not os.path.exists(file_path):
            # Если файл .xlsx не найден, пробуем .csv
            csv_path = file_path.replace('.xlsx', '.csv')
            if os.path.exists(csv_path):
                file_path = csv_path
            else:
                return f"❌ Файл не найден: {file_path}", 404
        
        # Определяем MIME тип
        if file_path.endswith('.csv'):
            mimetype = 'text/csv'
            download_name = f'comparison_result_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
        else:
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            download_name = filename
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name,
            mimetype=mimetype
        )
        
    except Exception as e:
        return f"❌ Ошибка: {str(e)}", 500






ДА, ЛЕГКО! Сделаем две вкладки:

· 📋 Вкладка 1: База данных — все операции с записями
· 📁 Вкладка 2: Файлы — Excel сравнение, DOCX генерация, бэкапы

---

🎯 ПОЛНЫЙ КОД С ДВУМЯ ВКЛАДКАМИ

```python
# ============================================
# ИМПОРТ НЕОБХОДИМЫХ БИБЛИОТЕК
# ============================================
from flask import Flask, request, render_template_string, redirect, make_response, send_file, session
import sqlite3
from datetime import datetime
import csv
import io
import os
import shutil
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from docxtpl import DocxTemplate
import json

# ============================================
# СОЗДАНИЕ ПРИЛОЖЕНИЯ FLASK
# ============================================
app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'  # Для сессий

# ============================================
# НАСТРОЙКА ПУТЕЙ
# ============================================
DATABASE = 'data.db'
BACKUP_DIR = 'backups'
TEMP_DIR = '/tmp/excel_comparison'  # Linux
# TEMP_DIR = 'C:/temp/excel_comparison'  # Windows
TEMPLATES_DIR = 'templates_docx'

# Создаём необходимые папки
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# ============================================
# ФУНКЦИЯ ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ
# ============================================
def get_db():
    conn = sqlite3.connect(
        DATABASE,
        timeout=10.0,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# ФУНКЦИЯ ИНИЦИАЛИЗАЦИИ БАЗЫ ДАННЫХ
# ============================================
def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field1 TEXT NOT NULL,
                field2 TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# ============================================
# ФУНКЦИЯ АВТОМАТИЧЕСКОГО РЕЗЕРВНОГО КОПИРОВАНИЯ
# ============================================
def auto_backup():
    if not os.path.exists(DATABASE):
        print("⚠️ База данных не найдена, бэкап не создан")
        return
    
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'data_{timestamp}.db')
    shutil.copy2(DATABASE, backup_file)
    print(f"✅ Создан бэкап: {backup_file}")
    
    backup_files = [f for f in os.listdir(BACKUP_DIR) if f.startswith('data_') and f.endswith('.db')]
    backup_files.sort()
    
    if len(backup_files) > 10:
        files_to_delete = backup_files[:-10]
        for old_file in files_to_delete:
            os.remove(os.path.join(BACKUP_DIR, old_file))
            print(f"🗑️ Удалён старый бэкап: {old_file}")

# ============================================
# ФУНКЦИЯ ГЕНЕРАЦИИ DOCX ИЗ ШАБЛОНА
# ============================================
def generate_doc_from_template(template_filename, data):
    template_path = os.path.join(TEMPLATES_DIR, template_filename)
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Шаблон не найден: {template_path}")
    
    doc = DocxTemplate(template_path)
    doc.render(data)
    
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    return file_stream

# ============================================
# ФУНКЦИЯ СРАВНЕНИЯ EXCEL ФАЙЛОВ
# ============================================
def compare_excel_files(file1_path, file2_path, compare_columns, output_path):
    wb1 = load_workbook(file1_path)
    wb2 = load_workbook(file2_path)
    
    ws1 = wb1.active
    ws2 = wb2.active
    
    yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
    
    diff_count = 0
    total_rows = 0
    
    max_rows = max(ws1.max_row, ws2.max_row)
    
    for row_num in range(1, max_rows + 1):
        row_diff = False
        total_rows += 1
        
        for col_num in compare_columns:
            val1 = ws1.cell(row=row_num, column=col_num).value if row_num <= ws1.max_row else None
            val2 = ws2.cell(row=row_num, column=col_num).value if row_num <= ws2.max_row else None
            
            if val1 != val2:
                row_diff = True
                break
        
        if row_diff:
            diff_count += 1
            
            for col_num in range(1, ws1.max_column + 1):
                if row_num <= ws1.max_row:
                    ws1.cell(row=row_num, column=col_num).fill = yellow_fill
            
            for col_num in range(1, ws2.max_column + 1):
                if row_num <= ws2.max_row:
                    ws2.cell(row=row_num, column=col_num).fill = yellow_fill
    
    wb1.save(output_path)
    
    output_path2 = output_path.replace('.xlsx', '_file2.xlsx')
    wb2.save(output_path2)
    
    return diff_count, total_rows

# ============================================
# HTML ШАБЛОН С ДВУМЯ ВКЛАДКАМИ
# ============================================
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask Универсальное Приложение</title>
    <style>
        /* ===== ГЛОБАЛЬНЫЕ СТИЛИ ===== */
        * { box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #f0f2f5; 
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white; 
            padding: 25px; 
            border-radius: 12px; 
            box-shadow: 0 2px 15px rgba(0,0,0,0.1); 
        }
        
        /* ===== ШАПКА ===== */
        .header { 
            background: linear-gradient(135deg, #4CAF50, #45a049); 
            color: white; 
            padding: 20px; 
            border-radius: 8px; 
            margin-bottom: 25px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            flex-wrap: wrap;
        }
        .header h2 { margin: 0; }
        .badge { 
            background: #FF9800; 
            padding: 6px 15px; 
            border-radius: 20px; 
            font-size: 13px; 
            font-weight: bold;
        }
        
        /* ===== ВКЛАДКИ ===== */
        .tabs {
            display: flex;
            border-bottom: 3px solid #4CAF50;
            margin-bottom: 25px;
            gap: 0;
            flex-wrap: wrap;
        }
        .tab-button {
            padding: 12px 30px;
            background: #f5f5f5;
            border: none;
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            color: #666;
            transition: all 0.3s;
            margin-right: 2px;
        }
        .tab-button:hover {
            background: #e8f5e9;
            color: #2E7D32;
        }
        .tab-button.active {
            background: #4CAF50;
            color: white;
            border-bottom: 3px solid #4CAF50;
        }
        .tab-content {
            display: none;
            padding: 20px 0;
            animation: fadeIn 0.5s;
        }
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* ===== СТАТИСТИКА ===== */
        .stats { 
            background: #e3f2fd; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 15px 0; 
            border-left: 4px solid #2196F3; 
            display: flex; 
            flex-wrap: wrap; 
            gap: 20px;
        }
        .stats span { margin-right: 20px; }
        
        /* ===== ФОРМЫ ===== */
        .form-group { margin: 12px 0; }
        .form-group label { font-weight: 600; display: block; margin-bottom: 4px; }
        input[type="text"], 
        input[type="password"],
        input[type="file"],
        select { 
            padding: 8px 12px; 
            margin: 4px 0; 
            border: 1px solid #ddd; 
            border-radius: 6px; 
            width: 100%; 
            max-width: 350px; 
            font-size: 14px;
        }
        input[type="file"] { padding: 6px; }
        
        /* ===== КНОПКИ ===== */
        button, .btn { 
            padding: 8px 20px; 
            margin: 4px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-weight: 600; 
            font-size: 14px;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 2px 8px rgba(0,0,0,0.2); }
        
        .btn-add { background: #4CAF50; color: white; }
        .btn-add:hover { background: #43A047; }
        .btn-edit { background: #2196F3; color: white; }
        .btn-edit:hover { background: #1E88E5; }
        .btn-delete { background: #f44336; color: white; }
        .btn-delete:hover { background: #E53935; }
        .btn-export { background: #FF9800; color: white; }
        .btn-export:hover { background: #FB8C00; }
        .btn-delete-all { background: #9E9E9E; color: white; }
        .btn-delete-all:hover { background: #757575; }
        .btn-cancel { background: #607D8B; color: white; }
        .btn-cancel:hover { background: #546E7A; }
        .btn-compare { background: #9C27B0; color: white; }
        .btn-compare:hover { background: #8E24AA; }
        .btn-doc { background: #E91E63; color: white; }
        .btn-doc:hover { background: #D81B60; }
        .btn-backup { background: #00BCD4; color: white; }
        .btn-backup:hover { background: #00ACC1; }
        
        /* ===== ТАБЛИЦА ===== */
        .table-wrapper { overflow-x: auto; margin-top: 15px; }
        table { 
            border-collapse: collapse; 
            width: 100%; 
            font-size: 14px;
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 10px 12px; 
            text-align: left; 
        }
        th { 
            background: #4CAF50; 
            color: white; 
            font-weight: 600;
        }
        tr:nth-child(even) { background: #f9f9f9; }
        tr:hover { background: #f1f1f1; }
        
        /* ===== ПАНЕЛЬ ИНСТРУМЕНТОВ ===== */
        .toolbar { 
            margin: 15px 0; 
            padding: 15px; 
            background: #f5f5f5; 
            border-radius: 8px; 
            display: flex; 
            flex-wrap: wrap; 
            align-items: center; 
            gap: 10px;
        }
        .toolbar form { display: inline-flex; align-items: center; gap: 5px; flex-wrap: wrap; }
        
        /* ===== ФОРМА РЕДАКТИРОВАНИЯ ===== */
        .edit-form { 
            background: #fff3e0; 
            padding: 20px; 
            border: 1px solid #FFB74D; 
            border-radius: 8px; 
            margin-top: 20px; 
        }
        
        /* ===== БЛОКИ ФАЙЛОВОЙ ВКЛАДКИ ===== */
        .file-section { 
            background: #f5f5f5; 
            padding: 25px; 
            border-radius: 10px; 
            margin-top: 20px; 
        }
        .file-section h3 { margin-top: 0; }
        
        .compare-section { 
            background: #f3e5f5; 
            padding: 25px; 
            border-radius: 10px; 
            border: 2px solid #9C27B0; 
            margin-top: 20px; 
        }
        .compare-result { 
            background: #e8f5e9; 
            padding: 15px; 
            border-radius: 6px; 
            margin: 15px 0; 
            border-left: 4px solid #4CAF50; 
        }
        
        .docx-section { 
            background: #fce4ec; 
            padding: 25px; 
            border-radius: 10px; 
            border: 2px solid #E91E63; 
            margin-top: 20px; 
        }
        
        .backup-section { 
            background: #e0f7fa; 
            padding: 25px; 
            border-radius: 10px; 
            border: 2px solid #00BCD4; 
            margin-top: 20px; 
        }
        
        /* ===== СООБЩЕНИЯ ===== */
        .msg { 
            color: #4CAF50; 
            font-weight: bold; 
            padding: 12px; 
            background: #e8f5e9; 
            border-radius: 6px; 
            border-left: 4px solid #4CAF50; 
        }
        .msg-error { 
            color: #f44336; 
            font-weight: bold; 
            padding: 12px; 
            background: #ffebee; 
            border-radius: 6px; 
            border-left: 4px solid #f44336; 
        }
        
        /* ===== СПИСОК БЭКАПОВ ===== */
        .backup-list {
            max-height: 300px;
            overflow-y: auto;
            background: white;
            border-radius: 6px;
            padding: 10px;
        }
        .backup-item {
            padding: 8px 12px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .backup-item:last-child { border-bottom: none; }
        .backup-item:hover { background: #f5f5f5; }
        
        /* ===== АДАПТИВНОСТЬ ===== */
        @media (max-width: 768px) {
            body { padding: 10px; }
            .container { padding: 15px; }
            .header { flex-direction: column; align-items: flex-start; gap: 10px; }
            .tabs { flex-direction: column; }
            .tab-button { border-radius: 0; text-align: left; }
            .toolbar { flex-direction: column; align-items: stretch; }
            .toolbar form { flex-direction: column; align-items: stretch; }
            input[type="text"], select { max-width: 100%; }
            table { font-size: 12px; }
            th, td { padding: 6px 8px; }
        }
        
        /* ===== ССЫЛКИ В ТАБЛИЦЕ ===== */
        .action-links a { text-decoration: none; }
    </style>
    
    <script>
        // ===== ПЕРЕКЛЮЧЕНИЕ ВКЛАДОК =====
        function openTab(tabName) {
            // Скрываем все вкладки
            var contents = document.getElementsByClassName("tab-content");
            for (var i = 0; i < contents.length; i++) {
                contents[i].classList.remove("active");
            }
            
            // Убираем активный класс у всех кнопок
            var buttons = document.getElementsByClassName("tab-button");
            for (var i = 0; i < buttons.length; i++) {
                buttons[i].classList.remove("active");
            }
            
            // Показываем нужную вкладку
            document.getElementById(tabName).classList.add("active");
            
            // Активируем кнопку
            event.currentTarget.classList.add("active");
            
            // Сохраняем выбранную вкладку в localStorage
            localStorage.setItem('activeTab', tabName);
        }
        
        // При загрузке страницы открываем последнюю активную вкладку
        window.onload = function() {
            var activeTab = localStorage.getItem('activeTab');
            if (activeTab) {
                var buttons = document.getElementsByClassName("tab-button");
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].getAttribute('onclick').includes(activeTab)) {
                        buttons[i].click();
                        break;
                    }
                }
            }
        }
    </script>
</head>
<body>
    <div class="container">
        
        <!-- ========================================== -->
        <!-- ШАПКА                                        -->
        <!-- ========================================== -->
        <div class="header">
            <h2>📋 Универсальное приложение</h2>
            <div>
                <span class="badge">✅ Автобэкап</span>
                <span class="badge" style="background: #9C27B0;">📊 Excel сравнение</span>
                <span class="badge" style="background: #E91E63;">📄 DOCX</span>
            </div>
        </div>
        
        <!-- ========================================== -->
        <!-- ВКЛАДКИ                                      -->
        <!-- ========================================== -->
        <div class="tabs">
            <button class="tab-button active" onclick="openTab('tab_db')">
                📋 База данных
            </button>
            <button class="tab-button" onclick="openTab('tab_files')">
                📁 Файлы и инструменты
            </button>
        </div>
        
        <!-- ========================================== -->
        <!-- ВКЛАДКА 1: БАЗА ДАННЫХ                      -->
        <!-- ========================================== -->
        <div id="tab_db" class="tab-content active">
            
            <!-- СТАТИСТИКА -->
            <div class="stats">
                <span>📊 <strong>Всего записей:</strong> {{ total_records }}</span>
                <span>🕐 <strong>Обновлено:</strong> {{ last_update }}</span>
                <span>💾 <strong>Бэкапы:</strong> последние 10 копий</span>
            </div>
            
            <!-- ФОРМА ДОБАВЛЕНИЯ -->
            <form method="post" action="/">
                <h3>➕ Добавить запись</h3>
                <div class="form-group">
                    <label>Поле 1:</label>
                    <input type="text" name="field1" required placeholder="Введите значение...">
                </div>
                <div class="form-group">
                    <label>Поле 2:</label>
                    <input type="text" name="field2" required placeholder="Введите значение...">
                </div>
                <button type="submit" class="btn-add">💾 Сохранить</button>
            </form>
            
            {% if msg %}
                <p class="msg">{{ msg }}</p>
            {% endif %}
            
            <!-- ПАНЕЛЬ ИНСТРУМЕНТОВ -->
            <div class="toolbar">
                <form method="get" action="/">
                    <input type="text" name="search" placeholder="🔍 Поиск..." value="{{ search_query or '' }}">
                    <button type="submit" class="btn" style="background: #4CAF50; color: white;">Найти</button>
                    {% if search_query %}
                        <a href="/" style="color: #f44336; font-weight: bold;">✕ Сбросить</a>
                    {% endif %}
                </form>
                
                <form method="get" action="/">
                    <select name="sort_by">
                        <option value="">📊 Сортировать...</option>
                        <option value="field1" {% if sort_by == 'field1' %}selected{% endif %}>Поле 1</option>
                        <option value="field2" {% if sort_by == 'field2' %}selected{% endif %}>Поле 2</option>
                        <option value="created_at" {% if sort_by == 'created_at' %}selected{% endif %}>Дата</option>
                    </select>
                    <select name="sort_order">
                        <option value="asc" {% if sort_order == 'asc' %}selected{% endif %}>⬆ Возрастанию</option>
                        <option value="desc" {% if sort_order == 'desc' %}selected{% endif %}>⬇ Убыванию</option>
                    </select>
                    <button type="submit" class="btn" style="background: #2196F3; color: white;">Сортировать</button>
                    {% if sort_by %}
                        <a href="/" style="color: #f44336; font-weight: bold;">✕ Сбросить</a>
                    {% endif %}
                </form>
                
                <form method="post" action="/export">
                    <button type="submit" class="btn-export">📊 Экспорт CSV</button>
                </form>
                
                <form method="post" action="/delete_all" onsubmit="return confirm('⚠️ Удалить ВСЕ записи? Это действие необратимо!')">
                    <button type="submit" class="btn-delete-all">🗑️ Удалить всё</button>
                </form>
            </div>
            
            <!-- ТАБЛИЦА ЗАПИСЕЙ -->
            <div class="table-wrapper">
                {% if records %}
                    <table>
                        <thead>
                            <tr>
                                <th style="width: 60px;">ID</th>
                                <th>Поле 1</th>
                                <th>Поле 2</th>
                                <th style="width: 180px;">Дата</th>
                                <th style="width: 220px;">Действия</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for row in records %}
                            <tr>
                                <td>{{ row.id }}</td>
                                <td>{{ row.field1 }}</td>
                                <td>{{ row.field2 }}</td>
                                <td>{{ row.created_at }}</td>
                                <td class="action-links">
                                    <a href="/edit/{{ row.id }}"><button class="btn-edit">✏️</button></a>
                                    <a href="/delete/{{ row.id }}" onclick="return confirm('Удалить запись #{{ row.id }}?')"><button class="btn-delete">🗑️</button></a>
                                    <a href="/generate_doc/{{ row.id }}"><button class="btn-doc">📄 DOCX</button></a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                {% else %}
                    <p style="text-align: center; padding: 40px; color: #999; font-size: 18px;">
                        📭 Нет записей. Добавьте первую!
                    </p>
                {% endif %}
            </div>
            
            <!-- ФОРМА РЕДАКТИРОВАНИЯ -->
            {% if edit_mode %}
            <div class="edit-form">
                <h3>✏️ Редактировать запись #{{ edit_id }}</h3>
                <form method="post" action="/edit/{{ edit_id }}">
                    <div class="form-group">
                        <label>Поле 1:</label>
                        <input type="text" name="field1" value="{{ edit_row.field1 }}" required>
                    </div>
                    <div class="form-group">
                        <label>Поле 2:</label>
                        <input type="text" name="field2" value="{{ edit_row.field2 }}" required>
                    </div>
                    <button type="submit" class="btn-add">💾 Обновить</button>
                    <a href="/"><button type="button" class="btn-cancel">❌ Отмена</button></a>
                </form>
            </div>
            {% endif %}
            
        </div>
        <!-- КОНЕЦ ВКЛАДКИ 1 -->
        
        <!-- ========================================== -->
        <!-- ВКЛАДКА 2: ФАЙЛЫ И ИНСТРУМЕНТЫ              -->
        <!-- ========================================== -->
        <div id="tab_files" class="tab-content">
            
            <!-- ========================================== -->
            <!-- СЕКЦИЯ: ГЕНЕРАЦИЯ DOCX                      -->
            <!-- ========================================== -->
            <div class="file-section docx-section">
                <h3>📄 Генерация DOCX из шаблона</h3>
                <p style="color: #666;">Выберите запись на вкладке "База данных" и нажмите кнопку 📄 DOCX в таблице.</p>
                
                <div style="background: white; padding: 15px; border-radius: 6px; margin-top: 10px;">
                    <h4>📁 Доступные шаблоны:</h4>
                    <ul>
                        <li><strong>template.docx</strong> — используйте метки: <code>{{ field1 }}</code>, <code>{{ field2 }}</code>, <code>{{ id }}</code>, <code>{{ created_at }}</code></li>
                    </ul>
                    <p style="color: #999; font-size: 13px;">
                        💡 Поместите файл <code>template.docx</code> в папку <code>templates_docx/</code>
                    </p>
                </div>
                
                <div style="margin-top: 10px;">
                    <form method="post" action="/generate_doc_all" style="display: inline-block;">
                        <button type="submit" class="btn-doc" onclick="return confirm('Сгенерировать DOCX для ВСЕХ записей?')">
                            📄 Сгенерировать для всех
                        </button>
                    </form>
                </div>
            </div>
            
            <!-- ========================================== -->
            <!-- СЕКЦИЯ: СРАВНЕНИЕ EXCEL                    -->
            <!-- ========================================== -->
            <div class="file-section compare-section">
                <h3>📊 Сравнение Excel файлов</h3>
                <p style="color: #666;">Загрузите два Excel файла (.xlsx) для сравнения. Строки с расхождениями будут выделены <span style="background: #FFFF00; padding: 2px 8px; border-radius: 3px;">ЖЁЛТЫМ</span> цветом.</p>
                
                {% if compare_result %}
                    <div class="compare-result">
                        <strong>✅ Результат сравнения:</strong><br>
                        📊 Всего строк: <strong>{{ compare_result.total }}</strong><br>
                        ⚠️ Найдено расхождений: <strong style="color: #f44336;">{{ compare_result.diffs }}</strong><br>
                        📁 Скачать результат: 
                        <a href="/download_comparison/{{ compare_result.filename }}"><button class="btn-export">📥 Скачать</button></a>
                    </div>
                {% endif %}
                
                <form method="post" action="/compare_excel" enctype="multipart/form-data" style="margin-top: 15px;">
                    <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                        <div style="flex: 1; min-width: 200px;">
                            <label><strong>📄 Файл 1 (эталон):</strong></label><br>
                            <input type="file" name="file1" accept=".xlsx" required>
                        </div>
                        <div style="flex: 1; min-width: 200px;">
                            <label><strong>📄 Файл 2 (сравниваемый):</strong></label><br>
                            <input type="file" name="file2" accept=".xlsx" required>
                        </div>
                    </div>
                    
                    <div style="margin: 15px 0;">
                        <label><strong>🔢 Столбцы для сравнения (номера через запятую):</strong></label><br>
                        <input type="text" name="columns" placeholder="Например: 1,2,3" required style="max-width: 300px;">
                        <small style="color: #666; display: block; margin-top: 4px;">Введите номера столбцов (начиная с 1), по которым нужно сравнивать данные</small>
                    </div>
                    
                    <button type="submit" class="btn-compare">🔍 Сравнить файлы</button>
                </form>
            </div>
            
            <!-- ========================================== -->
            <!-- СЕКЦИЯ: УПРАВЛЕНИЕ БЭКАПАМИ                 -->
            <!-- ========================================== -->
            <div class="file-section backup-section">
                <h3>💾 Управление бэкапами</h3>
                <p style="color: #666; font-size: 14px;">
                    Автоматическое резервное копирование при каждом изменении данных.<br>
                    Хранится <strong>10 последних</strong> копий в папке <code>{{ backup_dir }}</code>.
                </p>
                
                <div style="display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0;">
                    <form method="post" action="/restore_backup" style="display: inline-block;">
                        <button type="submit" class="btn-backup" onclick="return confirm('Восстановить из последнего бэкапа? Текущие данные будут заменены!')">
                            🔄 Восстановить из бэкапа
                        </button>
                    </form>
                    <a href="/list_backups"><button class="btn" style="background: #795548; color: white;">📋 Список бэкапов</button></a>
                    <form method="post" action="/create_backup_now" style="display: inline-block;">
                        <button type="submit" class="btn" style="background: #4CAF50; color: white;">💾 Создать бэкап сейчас</button>
                    </form>
                </div>
                
                <!-- Список последних бэкапов -->
                {% if backup_list %}
                    <div class="backup-list">
                        <h4>📂 Последние бэкапы:</h4>
                        {% for backup in backup_list %}
                            <div class="backup-item">
                                <span>📄 {{ backup.name }}</span>
                                <span style="color: #666; font-size: 13px;">
                                    {{ backup.size }} KB • {{ backup.date }}
                                </span>
                            </div>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
            
        </div>
        <!-- КОНЕЦ ВКЛАДКИ 2 -->
        
    </div>
    <!-- КОНЕЦ container -->
</body>
</html>
'''

# ============================================
# ГЛАВНАЯ СТРАНИЦА (ПРОСМОТР + ДОБАВЛЕНИЕ)
# ============================================
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        field1 = request.form.get('field1', '').strip()
        field2 = request.form.get('field2', '').strip()
        
        if not field1 or not field2:
            return render_template_string(
                HTML, 
                msg='❌ Поля не могут быть пустыми!', 
                records=[], 
                total_records=0, 
                last_update='',
                edit_mode=False,
                backup_dir=BACKUP_DIR,
                backup_list=get_backup_list()
            )
        
        try:
            with get_db() as conn:
                conn.execute(
                    'INSERT INTO records (field1, field2) VALUES (?, ?)',
                    (field1, field2)
                )
                conn.commit()
            
            auto_backup()
            return redirect('/')
            
        except sqlite3.Error as e:
            return render_template_string(
                HTML,
                msg=f'❌ Ошибка базы данных: {e}',
                records=[],
                total_records=0,
                last_update='',
                edit_mode=False,
                backup_dir=BACKUP_DIR,
                backup_list=get_backup_list()
            )
    
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', '')
    sort_order = request.args.get('sort_order', 'asc')
    
    query = 'SELECT * FROM records'
    params = []
    
    if search_query:
        query += ' WHERE field1 LIKE ? OR field2 LIKE ?'
        params = [f'%{search_query}%', f'%{search_query}%']
    
    if sort_by in ['field1', 'field2', 'created_at']:
        query += f' ORDER BY {sort_by} COLLATE NOCASE'
        query += ' DESC' if sort_order == 'desc' else ' ASC'
    else:
        query += ' ORDER BY id DESC'
    
    try:
        with get_db() as conn:
            records = conn.execute(query, params).fetchall()
            total = conn.execute('SELECT COUNT(*) as count FROM records').fetchone()['count']
            last = conn.execute('SELECT MAX(created_at) as last FROM records').fetchone()['last']
        
        last_update = last or 'Нет записей'
        
        return render_template_string(
            HTML,
            msg=None,
            records=records,
            total_records=total,
            last_update=last_update,
            edit_mode=False,
            search_query=search_query,
            sort_by=sort_by,
            sort_order=sort_order,
            backup_dir=BACKUP_DIR,
            backup_list=get_backup_list()
        )
        
    except sqlite3.Error as e:
        return f"❌ Ошибка при чтении базы данных: {e}", 500

# ============================================
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ СПИСКА БЭКАПОВ
# ============================================
def get_backup_list(limit=10):
    """Возвращает список последних бэкапов для отображения"""
    if not os.path.exists(BACKUP_DIR):
        return []
    
    backups = []
    files = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')], reverse=True)
    
    for f in files[:limit]:
        path = os.path.join(BACKUP_DIR, f)
        size = round(os.path.getsize(path) / 1024, 1)
        mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M')
        backups.append({'name': f, 'size': size, 'date': mtime})
    
    return backups

# ============================================
# УДАЛЕНИЕ ЗАПИСИ
# ============================================
@app.route('/delete/<int:record_id>')
def delete(record_id):
    try:
        with get_db() as conn:
            conn.execute('DELETE FROM records WHERE id = ?', (record_id,))
            conn.commit()
        
        auto_backup()
        return redirect('/')
        
    except sqlite3.Error as e:
        return f"❌ Ошибка при удалении: {e}", 500

# ============================================
# РЕДАКТИРОВАНИЕ ЗАПИСИ
# ============================================
@app.route('/edit/<int:record_id>', methods=['GET', 'POST'])
def edit(record_id):
    if request.method == 'POST':
        field1 = request.form.get('field1', '').strip()
        field2 = request.form.get('field2', '').strip()
        
        if not field1 or not field2:
            return "❌ Поля не могут быть пустыми!", 400
        
        try:
            with get_db() as conn:
                conn.execute(
                    'UPDATE records SET field1 = ?, field2 = ? WHERE id = ?',
                    (field1, field2, record_id)
                )
                conn.commit()
            
            auto_backup()
            return redirect('/')
            
        except sqlite3.Error as e:
            return f"❌ Ошибка при обновлении: {e}", 500
    
    try:
        with get_db() as conn:
            record = conn.execute(
                'SELECT * FROM records WHERE id = ?', 
                (record_id,)
            ).fetchone()
            
            if not record:
                return redirect('/')
            
            records = conn.execute('SELECT * FROM records ORDER BY id DESC').fetchall()
            total = conn.execute('SELECT COUNT(*) as count FROM records').fetchone()['count']
            last = conn.execute('SELECT MAX(created_at) as last FROM records').fetchone()['last']
        
        return render_template_string(
            HTML,
            msg=None,
            records=records,
            total_records=total,
            last_update=last or 'Нет записей',
            edit_mode=True,
            edit_id=record_id,
            edit_row=record,
            search_query=None,
            sort_by=None,
            sort_order=None,
            backup_dir=BACKUP_DIR,
            backup_list=get_backup_list()
        )
        
    except sqlite3.Error as e:
        return f"❌ Ошибка при чтении записи: {e}", 500

# ============================================
# УДАЛЕНИЕ ВСЕХ ЗАПИСЕЙ
# ============================================
@app.route('/delete_all', methods=['POST'])
def delete_all():
    try:
        with get_db() as conn:
            conn.execute('DELETE FROM records')
            conn.commit()
        
        auto_backup()
        return redirect('/')
        
    except sqlite3.Error as e:
        return f"❌ Ошибка при удалении: {e}", 500

# ============================================
# ЭКСПОРТ В CSV
# ============================================
@app.route('/export', methods=['POST'])
def export():
    try:
        with get_db() as conn:
            rows = conn.execute(
                'SELECT id, field1, field2, created_at FROM records ORDER BY id'
            ).fetchall()
        
        if not rows:
            return "❌ Нет данных для экспорта", 400
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Поле 1', 'Поле 2', 'Дата создания'])
        
        for row in rows:
            writer.writerow([row['id'], row['field1'], row['field2'], row['created_at']])
        
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = (
            f'attachment; filename=export_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
        )
        response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
        
        return response
        
    except sqlite3.Error as e:
        return f"❌ Ошибка при экспорте: {e}", 500

# ============================================
# ГЕНЕРАЦИЯ DOCX ИЗ ШАБЛОНА
# ============================================
@app.route('/generate_doc/<int:record_id>')
def generate_doc(record_id):
    try:
        with get_db() as conn:
            record = conn.execute(
                'SELECT * FROM records WHERE id = ?', 
                (record_id,)
            ).fetchone()
        
        if not record:
            return "❌ Запись не найдена", 404
        
        data = {
            'id': record['id'],
            'field1': record['field1'],
            'field2': record['field2'],
            'created_at': record['created_at']
        }
        
        doc_stream = generate_doc_from_template('template.docx', data)
        
        return send_file(
            doc_stream,
            as_attachment=True,
            download_name=f'record_{record_id}_{datetime.now().strftime("%Y%m%d")}.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except FileNotFoundError as e:
        return f"❌ {str(e)}", 404
    except Exception as e:
        return f"❌ Ошибка генерации DOCX: {str(e)}", 500

# ============================================
# ГЕНЕРАЦИЯ DOCX ДЛЯ ВСЕХ ЗАПИСЕЙ
# ============================================
@app.route('/generate_doc_all', methods=['POST'])
def generate_doc_all():
    try:
        with get_db() as conn:
            records = conn.execute('SELECT * FROM records ORDER BY id').fetchall()
        
        if not records:
            return "❌ Нет записей для генерации", 400
        
        # Создаём архив с DOCX файлами
        import zipfile
        zip_stream = io.BytesIO()
        
        with zipfile.ZipFile(zip_stream, 'w', zipfile.ZIP_DEFLATED) as zf:
            for record in records:
                data = {
                    'id': record['id'],
                    'field1': record['field1'],
                    'field2': record['field2'],
                    'created_at': record['created_at']
                }
                
                doc_stream = generate_doc_from_template('template.docx', data)
                zf.writestr(f'record_{record["id"]}.docx', doc_stream.getvalue())
        
        zip_stream.seek(0)
        
        return send_file(
            zip_stream,
            as_attachment=True,
            download_name=f'all_records_{datetime.now().strftime("%Y%m%d")}.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        return f"❌ Ошибка: {str(e)}", 500

# ============================================
# СРАВНЕНИЕ EXCEL ФАЙЛОВ
# ============================================
@app.route('/compare_excel', methods=['POST'])
def compare_excel():
    if 'file1' not in request.files or 'file2' not in request.files:
        return "❌ Выберите оба файла!", 400
    
    file1 = request.files['file1']
    file2 = request.files['file2']
    
    if file1.filename == '' or file2.filename == '':
        return "❌ Выберите оба файла!", 400
    
    if not file1.filename.endswith('.xlsx') or not file2.filename.endswith('.xlsx'):
        return "❌ Поддерживаются только файлы .xlsx!", 400
    
    columns_str = request.form.get('columns', '')
    try:
        compare_columns = [int(x.strip()) for x in columns_str.split(',') if x.strip()]
    except ValueError:
        return "❌ Введите корректные номера столбцов (через запятую)", 400
    
    if not compare_columns:
        return "❌ Укажите хотя бы один столбец для сравнения!", 400
    
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file1_path = os.path.join(TEMP_DIR, f'file1_{timestamp}.xlsx')
    file2_path = os.path.join(TEMP_DIR, f'file2_{timestamp}.xlsx')
    output_path = os.path.join(TEMP_DIR, f'result_{timestamp}.xlsx')
    
    file1.save(file1_path)
    file2.save(file2_path)
    
    try:
        diff_count, total_rows = compare_excel_files(
            file1_path,
            file2_path,
            compare_columns,
            output_path
        )
        
        compare_result = {
            'total': total_rows,
            'diffs': diff_count,
            'filename': f'result_{timestamp}.xlsx'
        }
        
        with get_db() as conn:
            records = conn.execute('SELECT * FROM records ORDER BY id DESC').fetchall()
            total = conn.execute('SELECT COUNT(*) as count FROM records').fetchone()['count']
            last = conn.execute('SELECT MAX(created_at) as last FROM records').fetchone()['last']
        
        return render_template_string(
            HTML,
            msg=None,
            records=records,
            total_records=total,
            last_update=last or 'Нет записей',
            edit_mode=False,
            search_query=None,
            sort_by=None,
            sort_order=None,
            compare_result=compare_result,
            backup_dir=BACKUP_DIR,
            backup_list=get_backup_list()
        )
        
    except Exception as e:
        return f"❌ Ошибка при сравнении: {str(e)}", 500

# ============================================
# СКАЧИВАНИЕ РЕЗУЛЬТАТА СРАВНЕНИЯ
# ============================================
@app.route('/download_comparison/<filename>')
def download_comparison(filename):
    file_path = os.path.join(TEMP_DIR, filename)
    
    if not os.path.exists(file_path):
        return "❌ Файл не найден!", 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=f'comparison_result_{filename}',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# ============================================
# СПИСОК БЭКАПОВ
# ============================================
@app.route('/list_backups')
def list_backups():
    if not os.path.exists(BACKUP_DIR):
        return "📁 Папка с бэкапами не найдена", 404
    
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')], reverse=True)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Список бэкапов</title>
        <style>
            body { font-family: 'Segoe UI', Arial; padding: 20px; max-width: 900px; margin: 0 auto; }
            h2 { color: #4CAF50; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background: #4CAF50; color: white; }
            tr:nth-child(even) { background: #f9f9f9; }
            tr:hover { background: #f1f1f1; }
            .back { margin-top: 20px; display: inline-block; }
            .btn { padding: 10px 25px; background: #4CAF50; color: white; border: none; border-radius: 6px; cursor: pointer; }
            .btn:hover { background: #43A047; }
            .stats { background: #e3f2fd; padding: 15px; border-radius: 6px; margin: 15px 0; }
        </style>
    </head>
    <body>
        <h2>💾 Список резервных копий</h2>
        <div class="stats">
            📊 Всего: <strong>{{ count }}</strong> файлов
        </div>
        <table>
            <tr>
                <th>#</th>
                <th>Имя файла</th>
                <th>Размер</th>
                <th>Дата создания</th>
            </tr>
    """
    
    for i, backup in enumerate(backups[:50], 1):
        file_path = os.path.join(BACKUP_DIR, backup)
        size = os.path.getsize(file_path) / 1024
        mtime = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        html += f"""
            <tr>
                <td>{i}</td>
                <td>{backup}</td>
                <td>{size:.1f} KB</td>
                <td>{mtime}</td>
            </tr>
        """
    
    html += """
        </table>
        <div style="margin-top: 20px;">
            <a href="/"><button class="btn">🏠 Вернуться</button></a>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html, count=len(backups))

# ============================================
# ВОССТАНОВЛЕНИЕ ИЗ БЭКАПА
# ============================================
@app.route('/restore_backup', methods=['POST'])
def restore_backup():
    if not os.path.exists(BACKUP_DIR):
        return "❌ Папка с бэкапами не найдена", 404
    
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')])
    
    if not backups:
        return "❌ Нет доступных бэкапов", 404
    
    latest_backup = backups[-1]
    backup_path = os.path.join(BACKUP_DIR, latest_backup)
    
    try:
        shutil.copy2(backup_path, DATABASE)
        return redirect('/')
        
    except Exception as e:
        return f"❌ Ошибка восстановления: {str(e)}", 500

# ============================================
# СОЗДАНИЕ БЭКАПА ВРУЧНУЮ
# ============================================
@app.route('/create_backup_now', methods=['POST'])
def create_backup_now():
    try:
        auto_backup()
        return redirect('/')
    except Exception as e:
        return f"❌ Ошибка создания бэкапа: {str(e)}", 500

# ============================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ============================================
if __name__ == '__main__':
    # Создаём необходимые папки
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Проверяем наличие шаблона DOCX
    template_path = os.path.join(TEMPLATES_DIR, 'template.docx')
    if not os.path.exists(template_path):
        print(f"⚠️ ВНИМАНИЕ: Шаблон DOCX не найден в {template_path}")
        print("   Создайте файл template.docx с метками {{ field1 }}, {{ field2 }}")
    
    # Инициализация базы данных
    init_db()
    print("✅ База данных инициализирована")
    
    # Создаём первый бэкап
    auto_backup()
    print("✅ Первый бэкап создан")
    
    print("\n" + "="*70)
    print("🚀 СЕРВЕР ЗАПУЩЕН!")
    print("="*70)
    print("\n📌 ДОСТУПНЫЕ ВКЛАДКИ:")
    print("   📋 Вкладка 1: База данных (CRUD, поиск, сортировка)")
    print("   📁 Вкладка 2: Файлы (Excel сравнение, DOCX, бэкапы)")
    print("\n📌 ДЛЯ ДОСТУПА:")
    print("   http://localhost:5000")
    print("   http://[ВАШ_IP]:5000")
    print("\n" + "="*70)
    print("💡 Нажмите Ctrl+C для остановки")
    print("="*70 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
```

---

📋 ЧТО ИЗМЕНИЛОСЬ

1. Две вкладки

· 📋 Вкладка 1: База данных — все операции с записями
· 📁 Вкладка 2: Файлы — Excel сравнение, DOCX, бэкапы

2. Визуальное разделение

· Чёткие секции с цветами
· Каждая секция подписана
· Удобная навигация

3. Новые функции

· ✅ Генерация DOCX для всех записей сразу (ZIP архив)
· ✅ Создание бэкапа вручную
· ✅ Список последних бэкапов на вкладке
· ✅ Автоматическое сохранение активной вкладки (localStorage)

---

✅ УСТАНОВКА И ЗАПУСК

```bash
# 1. Установка зависимостей
pip install flask openpyxl docxtpl

# 2. Создайте папки
mkdir templates_docx backups

# 3. Поместите шаблон template.docx в папку templates_docx/

# 4. Запуск
python3 app.py
```

---

🎯 ВСЁ ГОТОВО!

Теперь у вас две удобные вкладки:

· 📋 База данных — все операции с записями
· 📁 Файлы — все инструменты для работы с файлами

Всё в одном приложении, чисто, понятно и безопасно! 🚀
