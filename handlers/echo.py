from aiogram import types
from loader import dp


@dp.message_handler()
async def echo(message: types.Message) -> None:
    await message.answer(text='Неизвестная команда. Попробуйте еще раз, пожалуйста.')
