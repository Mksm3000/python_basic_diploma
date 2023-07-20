from loader import bot
from states.states import UserInfoState
from utils.misc.find_hotels import find_hotels_dict


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.message:
        bot.set_state(call.message.from_user.id, UserInfoState.enter_city, call.message.chat.id)
        with bot.retrieve_data(call.message.from_user.id, call.message.chat.id) as data:
            data['city_id'] = call.data
        bot.delete_message(call.message.chat.id, call.message.message_id)

        find_hotels(call, call.data)


def find_hotels(message, city_id):
    bot.send_message(message.chat.id, f'Будем искать отель в городе {city_id}')
    found_hotels = find_hotels_dict(message, city_id)
    print(found_hotels)

        # bot.set_state(call.message.chat.id, UserInfoState.hotel_quantity)
        # bot.send_message(call.message.chat.id, 'Сколько отелей вывести?')
