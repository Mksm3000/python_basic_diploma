from telebot import types
from loader import bot


def buttons_generator(message, cities):
    cities_markup = types.InlineKeyboardMarkup(row_width=1)

    for city_name, city_id in cities.items():
        button = types.InlineKeyboardButton(text=city_name, callback_data=city_id)
        cities_markup.add(button)

    bot.send_message(message.from_user.id, "Выберите ниже один из вариантов", reply_markup=cities_markup)
