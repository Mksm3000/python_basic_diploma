from telebot import types
from loader import bot


def buttons_generator(message, cities):
    cities_markup = types.InlineKeyboardMarkup()
    for key, value in cities.items():
        cities_markup.add(types.InlineKeyboardButton(text=key, callback_data=str(value)))
    bot.send_message(message.from_user.id, "Выберите ниже один из вариантов", reply_markup=cities_markup)
