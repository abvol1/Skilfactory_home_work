import telebot
from config import TOKEN
from extensions import CryptoConverter, APIException

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Доступные валюты для отображения
available_currencies = {
    'евро': 'EUR',
    'доллар': 'USD', 
    'рубль': 'RUB',
    'биткоин': 'BTC',
    'эфириум': 'ETH'
}

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    text = (
        '💱 *Конвертер валют*\n\n'
        'Чтобы узнать цену валюты, отправьте сообщение в формате:\n'
        '`<валюта1> <валюта2> <количество>`\n\n'
        '*Пример:*\n'
        '`евро рубль 100` - узнает стоимость 100 евро в рублях\n'
        '`доллар евро 50` - узнает стоимость 50 долларов в евро\n\n'
        'Доступные команды:\n'
        '/start, /help - показать это сообщение\n'
        '/values - показать доступные валюты\n\n'
        '*Доступные валюты:* евро, доллар, рубль, биткоин, эфириум'
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['values'])
def handle_values(message):
    text = '💰 *Доступные валюты:*\n\n'
    for currency, ticker in available_currencies.items():
        text += f'• {currency.capitalize()} ({ticker})\n'
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(content_types=['text'])
def handle_convert(message):
    try:
        # Разбиваем сообщение на части
        values = message.text.split()
        
        # Проверяем количество параметров
        if len(values) != 3:
            raise APIException(
                'Неверное количество параметров.\n\n'
                'Правильный формат:\n'
                '`<валюта1> <валюта2> <количество>`\n\n'
                '*Пример:*\n'
                '`евро рубль 100`'
            )
        
        base, quote, amount = values
        
        # Конвертируем валюту
        result = CryptoConverter.get_price(base, quote, amount)
        
        # Формируем ответ
        response_text = (
            f'💱 *Результат конвертации:*\n\n'
            f'• {amount} {base.capitalize()} = *{result} {quote.capitalize()}*\n\n'
            f'*Курс:* 1 {base} = {result/float(amount):.2f} {quote}'
        )
        
        bot.send_message(message.chat.id, response_text, parse_mode='Markdown')
        
    except APIException as e:
        bot.send_message(message.chat.id, f'❌ *Ошибка:*\n{str(e)}', parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, f'⚠️ *Неизвестная ошибка:*\n{str(e)}', parse_mode='Markdown')

if __name__ == '__main__':
    print('Бот запущен...')
    bot.polling(none_stop=True)