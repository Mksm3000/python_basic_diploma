from datetime import date, timedelta
from pprint import pprint
from urllib.parse import urlparse, parse_qs
import pdb

from aiogram import types
from aiogram.dispatcher import FSMContext
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from keyboards.inline import cities_kb, hotels_count_kb, photos_count_kb
from loader import dp, bot
from states.user_state import UsersStates
from utils.rapid_api import get_city, get_hotels
import requests


@dp.message_handler(commands=['low_price'])
async def cmd_low_price(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['command'] = message.text

    await message.answer(text='Введите название города')
    await state.set_state(state=UsersStates.city_name)


@dp.message_handler(content_types=['text'], state=UsersStates.city_name)
async def cities_search(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['city_name'] = message.text

    cities_dict = get_city(message.text)
    await message.answer(text='Выберите город из списка', reply_markup=cities_kb(cities_dict=cities_dict))
    await UsersStates.next()


@dp.callback_query_handler(lambda callback: callback, state=UsersStates.city_id)
async def callback_city_id(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data:
        async with state.proxy() as data:
            data['city_id'] = callback.data

            for element in callback.message.reply_markup.inline_keyboard:
                if element[0]["callback_data"] == callback.data:
                    data['city_name'] = element[0]["text"]

        await UsersStates.next()
        calendar_1, step = DetailedTelegramCalendar(calendar_id=1,
                                                    locale='en',
                                                    min_date=date.today()
                                                    ).build()
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=f"Выберите дату приезда",
                               reply_markup=calendar_1)


@dp.callback_query_handler(lambda callback: callback, state=UsersStates.date_in)
async def callback_date_in(callback: types.CallbackQuery, state: FSMContext):
    if callback.data:
        async with state.proxy() as data:
            data['date_in'] = callback.data

    result, key, step = DetailedTelegramCalendar(calendar_id=1,
                                                 locale='en',
                                                 min_date=date.today()
                                                 ).process(callback.data)

    if not result and key:
        await bot.edit_message_text(text=f"Select {LSTEP[step]}",
                                    chat_id=callback.message.chat.id,
                                    message_id=callback.message.message_id,
                                    reply_markup=key)
    elif result:
        await bot.edit_message_text(text=f"Дата заезда:\t{result}",
                                    chat_id=callback.message.chat.id,
                                    message_id=callback.message.message_id)

        await state.update_data(date_in=result)
        calendar_2, step = DetailedTelegramCalendar(calendar_id=2,
                                                    locale='en',
                                                    min_date=(result + timedelta(1))
                                                    ).build()

        await bot.send_message(chat_id=callback.message.chat.id,
                               text=f"Выберите дату выезда",
                               reply_markup=calendar_2)
        await UsersStates.next()


@dp.callback_query_handler(lambda callback: callback, state=UsersStates.date_out)
async def callback_date_out(callback: types.CallbackQuery, state: FSMContext):
    if callback.data:
        async with state.proxy() as data:
            data['date_out'] = callback.data

    result, key, step = DetailedTelegramCalendar(calendar_id=2,
                                                 locale='en',
                                                 min_date=data.get('date_in') + timedelta(1)
                                                 ).process(callback.data)

    if not result and key:
        await bot.edit_message_text(text=f"Select {LSTEP[step]}",
                                    chat_id=callback.message.chat.id,
                                    message_id=callback.message.message_id,
                                    reply_markup=key)
    elif result:
        await bot.edit_message_text(text=f"Дата выезда:\t{result}",
                                    chat_id=callback.message.chat.id,
                                    message_id=callback.message.message_id)

        await state.update_data(date_out=result)
        await callback.message.answer(text='Сколько отелей будем искать?',
                                      reply_markup=hotels_count_kb())
        await state.set_state(state=UsersStates.amount_hotels)


@dp.callback_query_handler(state=UsersStates.amount_hotels)
async def check_amount_hotels(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data:
        await bot.delete_message(chat_id=callback.from_user.id,
                                 message_id=callback.message.message_id)
        await callback.message.answer(text=f"Кол-во отелей: {callback.data.split('hotels_count_')[1]}")
        async with state.proxy() as data:
            data['amount_hotels'] = callback.data

        await callback.message.answer(text='Сколько фотографий отеля нужно?',
                                      reply_markup=photos_count_kb())
        await state.set_state(state=UsersStates.amount_photos)


@dp.callback_query_handler(state=UsersStates.amount_photos)
async def check_amount_photos(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await callback.message.answer(text=f"Кол-во фото для отеля: {callback.data.split('photos_count_')[1]}")
        async with state.proxy() as data:
            data['amount_photos'] = callback.data

        await state.set_state(state=UsersStates.result)
        await get_result(message=callback.message, state=state)


@dp.message_handler(state=UsersStates.result)
async def get_result(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        result = get_hotels(data)
        data['result'] = result
        pprint(result)

        pages_list = [result[i] for i in range(len(result))]
        current_page_num = 0
        data['page'] = current_page_num
        current_page = pages_list[current_page_num]

        await state.set_state(state=UsersStates.page)
        await show_page(chat_id=message.chat.id,
                        page_block=current_page,
                        page_num=current_page_num,
                        pages_total=len(pages_list),
                        state=state)


@dp.message_handler(state=UsersStates.page)
async def show_page(chat_id: str, page_block: dict, page_num: int, pages_total: int, state: FSMContext):
    page_keyboard = types.InlineKeyboardMarkup(row_width=3)
    if page_num > 0:
        page_keyboard.insert(types.InlineKeyboardButton(text="⬅️", callback_data='page_back'))

    page_keyboard.insert(types.InlineKeyboardButton(text=f'отель №{page_num + 1}', callback_data='***'))

    if page_num < pages_total - 1:
        page_keyboard.insert(types.InlineKeyboardButton(text="➡️", callback_data='page_next'))

    await state.set_state(state=UsersStates.page)

    # media=[types.InputMediaPhoto(i_image) for i_image in page['image']]
    # await bot.send_media_group()
    # await bot.send_photo(chat_id=chat_id,
    #                      photo=media,
    #                      caption=f"<b>Название отеля:</b> {page['name']}\n"
    #                              f"<b>Цена за 1 ночь:</b> {page['price']}\n"
    #                              f"<b>Цена общая:</b> {page['price_total']}\n"
    #                              f"<b>Рейтинг отеля:</b> {page['score']}/10\n"
    #                              f"<b>Кол-во отзывов:</b> {page['total']}",
    #                      parse_mode='HTML',
    #                      reply_markup=page_keyboard)

    await bot.send_media_group(chat_id=chat_id, media=[types.InputMediaPhoto(i_image) for i_image in page_block['image']])
    await bot.send_message(chat_id=chat_id,
                           text=f"<b>Название отеля:</b> {page_block['name']}\n"
                                f"<b>Цена за 1 ночь:</b> {page_block['price']}\n"
                                f"<b>Цена общая:</b> {page_block['price_total']}\n"
                                f"<b>Рейтинг отеля:</b> {page_block['score']}/10\n"
                                f"<b>Кол-во отзывов:</b> {page_block['total']}",
                           parse_mode='HTML',
                           reply_markup=page_keyboard)


@dp.callback_query_handler(lambda callback: callback.data.startswith("page_"), state=UsersStates.page)
async def page_change(callback: types.CallbackQuery, state=FSMContext):
    async with state.proxy() as data:
        current_page_num = data['page']
        result = data['result']
        pages_list = [result[i] for i in range(len(result))]

        if callback.data == "page_next":
            current_page_num += 1
        elif callback.data == "page_back":
            current_page_num -= 1

        data['page'] = current_page_num
        current_page = pages_list[current_page_num]

        await state.set_state(state=UsersStates.page)
        await show_page(chat_id=callback.message.chat.id,
                        page_block=current_page,
                        page_num=current_page_num,
                        pages_total=len(pages_list),
                        state=state)
        await callback.message.delete()
        await callback.answer()
