import datetime
from telebot.types import Message, Dict
from loader import bot
from states.states import UserInfoState
from utils.misc.find_destination_id import destination_id


@bot.message_handler(commands=["low_price", "high_price", "best_deal"])
def bot_commands(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoState.enter_city, message.chat.id)
    bot.send_message(message.from_user.id, 'Введите название города: ')


@bot.message_handler(state=UserInfoState.enter_city)
def find_city(message: Message) -> Dict:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['enter_city'] = message.text
    bot.send_message(message.from_user.id, f'Выполняем поиск в городе "{data["enter_city"]}"')
    similar = destination_id(data['enter_city'])
    return similar


