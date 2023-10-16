from json import loads

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config_data.config import DEFAULT_COMMANDS
from data.database import show_tables, show_hotels_found
from keyboards.inline import hisory_kb
from loader import dp
from states.user_state import UsersStates


@dp.message_handler(commands=['history'])
async def history_list(message: types.Message, state: FSMContext) -> None:
    """
    Выбираем команду 'history'.
    Выбираем нужную строку с результатом поиска. Устанавливаем состояние 'history'.
    """
    async with state.proxy() as data:
        if not data.get('user_uniq_id'):
            data['user_uniq_id'] = message.from_user.id

        user_uniq_id = data['user_uniq_id']
        result = await show_tables(user_uniq_id)

    if len(result) == 0:
        await message.answer(text=f'<b>История запросов пуста!</b>\nВыберите нужную команду:{DEFAULT_COMMANDS}',
                             parse_mode='HTML')
        await state.finish()
    else:
        await message.answer(text='Выберите нужный запрос из списка:',
                             reply_markup=hisory_kb(result))
        await state.set_state(state=UsersStates.history)


@dp.callback_query_handler(lambda callback: callback.data.startswith("row_"), state=UsersStates.history)
async def callback_history_row(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Nista
    """
    row_num = callback.data.split("row_")[1]
    temp_tuple = await show_hotels_found(row_num)

    if len(temp_tuple) != 0:
        command, data = temp_tuple
        result = loads(data)
        text = (f"📍<b>Город:</b> {result[0]['destination']}\n"
                f"📆<b>Заезд\выезд:</b> {result[0]['checkIn']} \ {result[0]['checkOut']}\n"
                f"🔎<b>Условия поиска:</b> {result[0]['sort_by']}\n"
                f"\n")

        for element in result:
            text_temp = (f"<b>Название отеля:</b> {element['name']}\n"
                         f"<b>Цена за 1 ночь:</b> {element['price']}\n"
                         f"<b>Цена общая:</b> {element['price_total']}\n"
                         f"<b>Рейтинг отеля:</b> {element['score']}/10\n"
                         f"<b>Кол-во отзывов:</b> {element['total']}\n"
                         f"<b>Ссылка:</b> https://www.hotels.com/h{element['hotel_id']}.Hotel-Information\n")
            if command == '/best_deal':
                text_temp += f"<b>Расстояние от центра, км:</b> {element['distance']}\n"

            text += text_temp + '\n'

        keyboard = InlineKeyboardMarkup()
        button = InlineKeyboardButton(text=f'✅главное меню✅', callback_data='cancel_show')
        keyboard.add(button)

        await callback.message.answer(text=text,
                                      parse_mode='HTML',
                                      reply_markup=keyboard)
        await state.set_state(state=UsersStates.history)

    else:
        await callback.message.answer(text=f"‼️Извините, при обработке данных произошла ошибка!‼️\n"
                                           f"Мы уже работаем над её устранением.\n"
                                           f"Пожалуйста, выберите ниже нужную вам команду. {DEFAULT_COMMANDS}")
        await state.finish()
