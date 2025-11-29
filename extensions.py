import requests
import json

class APIException(Exception):
    pass

class CryptoConverter:
    @staticmethod
    def get_price(base: str, quote: str, amount: str):
        # Приводим к нижнему регистру для удобства
        base = base.lower()
        quote = quote.lower()
        amount = amount.replace(',', '.')  # Заменяем запятую на точку
        
        # Доступные валюты
        available_currencies = {
            'евро': 'EUR',
            'доллар': 'USD', 
            'рубль': 'RUB',
            'биткоин': 'BTC',
            'эфириум': 'ETH'
        }
        
        # Проверка валют
        if base not in available_currencies:
            raise APIException(f'Валюта "{base}" не найдена. Доступные валюты: {", ".join(available_currencies.keys())}')
        
        if quote not in available_currencies:
            raise APIException(f'Валюта "{quote}" не найдена. Доступные валюты: {", ".join(available_currencies.keys())}')
        
        # Проверка одинаковых валют
        if base == quote:
            raise APIException(f'Невозможно перевести одинаковые валюты "{base}"')
        
        # Проверка количества
        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удалось обработать количество "{amount}". Введите число.')
        
        if amount <= 0:
            raise APIException('Количество валюты должно быть больше 0')
        
        # Получаем курсы валют через CryptoCompare API
        base_ticker = available_currencies[base]
        quote_ticker = available_currencies[quote]
        
        url = f'https://min-api.cryptocompare.com/data/price?fsym={base_ticker}&tsyms={quote_ticker}'
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                raise APIException('Ошибка при получении данных от сервера')
            
            data = json.loads(response.content)
            
            if quote_ticker not in data:
                raise APIException(f'Не удалось получить курс для валют {base} -> {quote}')
            
            rate = data[quote_ticker]
            total = rate * amount
            
            return round(total, 2)
            
        except requests.exceptions.ConnectionError:
            raise APIException('Ошибка соединения. Проверьте интернет-соединение.')
        except requests.exceptions.Timeout:
            raise APIException('Таймаут соединения. Попробуйте позже.')
        except Exception as e:
            raise APIException(f'Произошла ошибка: {str(e)}')