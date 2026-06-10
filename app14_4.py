
import requests
import json
import re
from bs4 import BeautifulSoup

url = "https://www.rshb.ru/branches/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}

try:
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')

    storage_uuid = None
    # Ищем во всех тегах script
    for script in soup.find_all('script'):
        if script.string and 'branchesDataStorageUuid' in script.string:
            # Пытаемся извлечь UUID через регулярное выражение
            match = re.search(r'branchesDataStorageUuid["\']?\s*:\s*["\']([^"\']+)["\']', script.string)
            if match:
                storage_uuid = match.group(1)
                print(f"✅ UUID найден в скрипте: {storage_uuid}")
                break
            # Альтернативно: если это window.__NEXT_DATA__ = {...}
            match = re.search(r'__NEXT_DATA__\s*=\s*({.*?});', script.string, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                try:
                    storage_uuid = data['props']['pageProps']['branchesDataStorageUuid']
                    print(f"✅ UUID найден через __NEXT_DATA__: {storage_uuid}")
                    break
                except KeyError:
                    pass

    if not storage_uuid:
        print("❌ UUID не найден ни в одном скрипте.")
        print("➡️  Похоже, данные загружаются отдельным API-запросом после рендеринга страницы.")
        print("    Используй DevTools браузера (вкладка Network), чтобы перехватить этот запрос.")
    else:
        data_url = f"https://www.rshb.ru/api/v1/storage/{storage_uuid}/file"
        print("⏳ Загрузка данных отделений...")
        data_r = requests.get(data_url, headers=headers, timeout=15)
        data_r.raise_for_status()
        offices = data_r.json()
        print(f"✅ Загружено {len(offices)} офисов")

        with open("rshb_offices.json", "w", encoding="utf-8") as f:
            json.dump(offices, f, ensure_ascii=False, indent=2)
        print("📁 Данные сохранены в 'rshb_offices.json'")

except Exception as e:
    print(f"⚠️ Ошибка: {e}")





import requests
import json

# --- НАСТРОЙКИ ---
# URL сайта (убедитесь, что он правильный)
map_url = "https://www.rshb.ru/branches/"

# Заголовки, имитирующие запрос от браузера
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}

try:
    # 1. Загружаем главную страницу с правильными заголовками
    print("⏳ Загрузка главной страницы...")
    r = requests.get(map_url, headers=headers, timeout=15)
    r.raise_for_status()

    # 2. Ищем во всем HTML уникальный идентификатор файла данных
    start_marker = 'id="__NEXT_DATA__"'
    if start_marker in r.text:
        data_block = r.text.split(start_marker)[1].split("></script>")[0].strip()
        json_data = json.loads(data_block)

        storage_uuid = None
        # 3. Ищем нужный путь в структуре JSON
        try:
            storage_uuid = json_data["props"]["pageProps"]["branchesDataStorageUuid"]
        except KeyError:
            pass

        if storage_uuid:
            print(f"✅ Найден UUID хранилища: {storage_uuid}")

            # 4. Загружаем JSON-файл с полными данными
            data_url = f"https://www.rshb.ru/api/v1/storage/{storage_uuid}/file"
            print("⏳ Загрузка данных отделений...")
            data_response = requests.get(data_url, headers=headers, timeout=15)
            data_response.raise_for_status()

            offices_data = data_response.json()
            print(f"✅ Загружено {len(offices_data)} офисов")

            # 5. Сохраняем в файл
            with open("rshb_offices.json", "w", encoding="utf-8") as f:
                json.dump(offices_data, f, ensure_ascii=False, indent=2)
            print("📁 Данные сохранены в файл 'rshb_offices.json'")

            # 6. Показываем пример
            if offices_data:
                print("\n📌 Пример данных (первый офис):")
                print(json.dumps(offices_data[0], ensure_ascii=False, indent=2))
        else:
            print("❌ Не удалось найти UUID хранилища")
    else:
        print("❌ Не удалось найти блок данных '__NEXT_DATA__' на странице.")

except Exception as e:
    print(f"⚠️ Произошла ошибка: {e}")




import requests
import json

# 1. Получаем главную страницу с картой, чтобы извлечь ID хранилища данных
map_url = "https://www.rshb.ru/branches/"
try:
    r = requests.get(map_url)
    r.raise_for_status()
    # Ищем во всем HTML уникальный идентификатор файла данных
    start_marker = 'id="__NEXT_DATA__"'
    if start_marker in r.text:
        data_block = r.text.split(start_marker)[1].split("></script>")[0].strip()
        json_data = json.loads(data_block)
        storage_uuid = None
        # Ищем нужный путь в структуре JSON
        try:
            storage_uuid = json_data["props"]["pageProps"]["branchesDataStorageUuid"]
        except KeyError:
            pass
        if storage_uuid:
            print(f"✅ Найден UUID хранилища: {storage_uuid}")
            # 2. Загружаем JSON-файл с полными данными по этому UUID
            data_url = f"https://www.rshb.ru/api/v1/storage/{storage_uuid}/file"
            data_response = requests.get(data_url)
            data_response.raise_for_status()
            offices_data = data_response.json()
            print(f"✅ Загружено {len(offices_data)} офисов")
            with open("rshb_offices.json", "w", encoding="utf-8") as f:
                json.dump(offices_data, f, ensure_ascii=False, indent=2)
            print("📁 Данные сохранены в файл 'rshb_offices.json'")
            # Краткий пример вывода первого офиса
            if offices_data:
                print("\n📌 Пример данных (первый офис):")
                print(json.dumps(offices_data[0], ensure_ascii=False, indent=2))
        else:
            print("❌ Не удалось найти UUID хранилища")
    else:
        print("❌ Не удалось найти блок данных '__NEXT_DATA__' на странице.")
except Exception as e:
    print(f"⚠️ Произошла ошибка: {e}")
