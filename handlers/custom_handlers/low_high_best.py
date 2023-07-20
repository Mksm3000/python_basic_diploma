from telebot.types import Message, CallbackQuery

from loader import bot
from states.states import UserInfoState
from utils.misc.find_destination_id import destination_id
import keyboards.inline.cities_buttons


@bot.message_handler(commands=["low_price", "high_price", "best_deal"])
def bot_commands(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.enter_city, message.chat.id)
    bot.send_message(message.from_user.id, 'Введите название города: ')
    bot.register_next_step_handler()


@bot.message_handler(state=UserInfoState.enter_city)
def find_city(message: Message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['enter_city'] = message.text
    bot.send_message(message.from_user.id, f'Выполняем поиск в городе "{data["enter_city"]}"')
    similar = destination_id(data['enter_city'])
    keyboards.inline.cities_buttons.buttons_generator(message, similar)


@bot.callback_query_handler(func=lambda call: True, state=UserInfoState.enter_city)
def check_id_city(call):
    pass
