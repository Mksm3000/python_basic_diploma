from loader import bot
from states.states import UserInfoState


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.message:
        bot.set_state(call.message.from_user.id, UserInfoState.city_id, call.message.chat.id)
        with bot.retrieve_data(call.message.from_user.id, call.message.chat.id) as data:
            data['--id'] = call.data
        bot.delete_message(call.message.chat.id, call.message.message_id)

        find_hotels(call, call.data)


def find_hotels(message, destinationId):
    bot.send_message(message.from_user.id, "Будем искать отель в городе ...")