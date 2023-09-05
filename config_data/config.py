import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

DEFAULT_COMMANDS = """
<b>/start</b> - Запустить бота
<b>/help</b> - Вывести справку
<b>/low_price</b> - Вывод самых дешёвых отелей в городе
<b>/high_price</b> - Вывод самых дорогих отелей в городе
<b>/best_deal</b> - Вывод отелей, наиболее подходящих по цене и расположению от центра
<b>/history</b> - Вывод истории поиска отелей
"""
