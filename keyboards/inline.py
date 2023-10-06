from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict
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


def inline_delete() -> InlineKeyboardMarkup:
    """
    Returns inline keyboard for remove answer bot
    """
    keyboard = InlineKeyboardMarkup(InlineKeyboardButton('❎ Удалить это сообщение', callback_data='delete'))
    return keyboard


def inline_delete_stop() -> InlineKeyboardMarkup:
    """
    Returns the inline keyboard to delete the bot response or stop the search
    """
    keyboard = InlineKeyboardMarkup()
    b1 = InlineKeyboardButton('❎ Удалить это сообщение', callback_data='delete')
    b2 = InlineKeyboardButton('❌ Закончить поиск', callback_data='stop')
    keyboard.add(b1).add(b2)
    return keyboard
