
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
