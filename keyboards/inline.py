from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict, List
from pprint import pprint


def cities_kb(cities_dict: Dict) -> InlineKeyboardMarkup:
    """
    Клавиатура с кнопками - выбор подходящего по названию города, из которых пользователь выбирает нужный ему.
    """

    keyboard = InlineKeyboardMarkup()
    for key, value in cities_dict.items():
        keyboard.add(InlineKeyboardButton(text=key, callback_data=value))

    return keyboard


def hotels_count_kb() -> InlineKeyboardMarkup:
    """
    Клавиатура с кнопками - выбор количества отелей в ответе, пользователь выбирает нужное число.
    """
    keyboard = InlineKeyboardMarkup(row_width=5)
    for i in range(10):
        keyboard.insert(InlineKeyboardButton(f"{i+1}", callback_data=f"hotels_count_{i+1}"))

    return keyboard


def photos_count_kb() -> InlineKeyboardMarkup:
    """
    Клавиатура с кнопками - выбор количества фотографий отеля в ответе, пользователь выбирает нужное число.
    """
    keyboard = InlineKeyboardMarkup(row_width=5)
    for i in range(5):
        keyboard.insert(InlineKeyboardButton(f"{i+1}", callback_data=f"photos_count_{i+1}"))

    return keyboard


def hisory_kb(line: List) -> InlineKeyboardMarkup:
    """
    Клавиатура с кнопками — вывод имеющихся результатов, из которых пользователь выбирает нужный ему.
    """

    keyboard = InlineKeyboardMarkup()
    for item in line:
        row = item[0]
        date_time = item[1]
        command = item[2].split('/')[1]
        location = item[3]
        keyboard.add(InlineKeyboardButton(text=f"{date_time} / {command} / {location}", callback_data=f"row_{row}"))

    keyboard.add(InlineKeyboardButton(text=f'⛔️завершить просмотр⛔️', callback_data='cancel_show'))

    return keyboard
