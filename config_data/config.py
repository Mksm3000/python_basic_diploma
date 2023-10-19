import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

DEFAULT_COMMANDS = """
<b>/start</b> - запуск бота
<b>/help</b> - справка
<b>/low_price</b> - поиск по цене (мин. $ → макс. $$$)
<b>/high_price</b> - поиск по цене (макс. $$$ → мин. $)
<b>/best_deal</b> - поиск с учётом мин. $ и мин. км от центра
<b>/history</b> - история поиска
"""
