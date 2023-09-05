import handlers
from loader import dp
from data.database import create_database
from aiogram import executor


async def on_startup(_):
    await create_database()
    print(">>> TelegramBot is starting <<<")


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp,
                           on_startup=on_startup,
                           skip_updates=True)

