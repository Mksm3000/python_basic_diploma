from aiogram import types

from config_data.config import DEFAULT_COMMANDS
from loader import dp


@dp.message_handler(commands=['start'])
async def bot_start(message: types.Message) -> None:
    await message.answer(text='Бот запущен! Выберите нужную команду:')
    await message.answer(text=DEFAULT_COMMANDS, parse_mode='HTML')


@dp.message_handler(commands=['help'])
async def get_help(message: types.Message) -> None:
    await message.answer(text=DEFAULT_COMMANDS, parse_mode='HTML')

