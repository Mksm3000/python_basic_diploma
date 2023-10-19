from aiogram import types

from config_data.config import DEFAULT_COMMANDS
from loader import dp


@dp.message_handler(commands=['start', 'help'])
async def start_help(message: types.Message) -> None:
    """
    Выбираем команду 'start' или 'help'.
    Выводим список команд.
    """
    if message.text == '/start':
        await message.answer(text=f'Привет, {message.from_user.first_name}!\nБот запущен! Выберите нужную команду:')
    await message.answer(text=DEFAULT_COMMANDS, parse_mode='HTML')
    await message.delete()
