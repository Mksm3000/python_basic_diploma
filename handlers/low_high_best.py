from datetime import date, timedelta

from aiogram import types
from aiogram.dispatcher import FSMContext
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from config_data.config import DEFAULT_COMMANDS
from keyboards.inline import cities_kb, hotels_count_kb, photos_count_kb
from loader import dp, bot
from states.user_state import UsersStates
from utils.rapid_api import get_city, get_hotels
from pprint import pprint


@dp.message_handler(commands=['low_price', 'high_price', 'best_deal'])
async def low_high_best(message: types.Message, state: FSMContext) -> None:
    """
    Выбираем команду 'low_price', 'high_price' или 'best_deal'.
    Устанавливаем состояние 'city_name'.
    """
    async with state.proxy() as data:
        data['command'] = message.text

    await message.answer(text='Введите название города')
    await state.set_state(state=UsersStates.city_name)


@dp.message_handler(content_types=['text'], state=UsersStates.city_name)
async def cities_search(message: types.Message, state: FSMContext) -> None:
    """
    Получаем имя города.
    Создаём inline-клавиатуру со списком городов с подходящими именами.
    Устанавливаем состояние 'city_id'.
    """
    async with state.proxy() as data:
        data['city_name'] = message.text

    cities_dict = get_city(message.text)
    if cities_dict:
        await message.answer(text='Выберите город из списка', reply_markup=cities_kb(cities_dict=cities_dict))
        await message.delete()
        await state.set_state(state=UsersStates.city_id)
    else:
        await message.delete()
        await message.answer(text="‼️Указанный вами город не найден!‼️\nПожалуйста, ведите другое название.")


@dp.callback_query_handler(lambda callback: callback, state=UsersStates.city_id)
async def callback_city_id(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Выбираем нужное имя города и получаем его id.
    Указываем дату заезда. Устанавливаем состояние 'date_in'.
    """

    await callback.message.delete()

    if callback.data == 'main_menu':
        await callback.message.answer(text=f'{DEFAULT_COMMANDS}',
                                      parse_mode='HTML')
        await state.finish()
    else:
        async with state.proxy() as data:
            data['city_id'] = callback.data

            for element in callback.message.reply_markup.inline_keyboard:
                if element[0]["callback_data"] == callback.data:
                    data['city_name'] = element[0]["text"]

        await callback.message.answer(text=f"{data['city_name']}")

        await state.set_state(state=UsersStates.date_in)
        calendar_1, step = DetailedTelegramCalendar(calendar_id=1,
                                                    locale='en',
                                                    min_date=date.today()
                                                    ).build()
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=f"Выберите дату приезда",
                               reply_markup=calendar_1)


@dp.callback_query_handler(lambda callback: callback, state=UsersStates.date_in)
async def callback_date_in(callback: types.CallbackQuery, state: FSMContext):
    """
    Получаем дата заезда.
    Указываем дату выезда. Устанавливаем состояние 'date_out'.
    """
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
        await state.set_state(state=UsersStates.date_out)


@dp.callback_query_handler(lambda callback: callback, state=UsersStates.date_out)
async def callback_date_out(callback: types.CallbackQuery, state: FSMContext):
    """
    Получаем дата выезда.
    Указываем кол-во отелей. Устанавливаем состояние 'amount_hotels'.
    """
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
    """
    Получаем кол-во отелей.
    Если выбрана команда "best_deal", то указываем максимальное растстояние от центра, км.
    Устанавливаем состояние 'max_km_distance'.
    В остальных случаях указываем кол-во фото для отеля. Устанавливаем состояние 'amount_photos'.
    """
    await bot.delete_message(chat_id=callback.from_user.id,
                             message_id=callback.message.message_id)
    await callback.message.answer(text=f"Кол-во отелей: {callback.data.split('hotels_count_')[1]}")
    async with state.proxy() as data:
        data['amount_hotels'] = callback.data
        if data['command'] == '/best_deal':
            await callback.message.answer(text='Укажите макс.расстояние от центра города до отеля, км (например, 1.5)')
            await state.set_state(state=UsersStates.max_km_distance)
        else:
            await callback.message.answer(text='Сколько фотографий отеля нужно?',
                                          reply_markup=photos_count_kb())
            await state.set_state(state=UsersStates.amount_photos)


@dp.message_handler(content_types=['text'], state=UsersStates.max_km_distance)
async def get_max_distance(message: types.Message, state: FSMContext) -> None:
    """
    Получаем максимальное растстояние от центра, км.
    Указываем минимальную цену за ночь. Устанавливаем состояние 'price_min'.
    """
    await message.delete()
    await message.answer(text=f"Макс.расстояние от центра: {message.text} км")

    async with state.proxy() as data:
        if message.text.isdigit() and float(message.text) > 0:
            data['max_km_distance'] = message.text
            await message.answer(text='Укажите мин.цену в $ за 1 ночь (например, 10)')
            await state.set_state(state=UsersStates.price_min)

        else:
            await bot.delete_message(message.from_user.id, message.message_id)
            await message.answer(f'⚠️Расстояние - это целое положительное число.\n'
                                 f'Укажите еще раз расстояние до центра города, км (например, 1.5)')
            await state.set_state(state=UsersStates.max_km_distance)


@dp.message_handler(content_types=['text'], state=UsersStates.price_min)
async def get_min_price(message: types.Message, state: FSMContext) -> None:
    """
    Получаем минимальную цену за 1 ночь.
    Устанавливаем состояние 'price_max'.
    """
    await message.delete()
    await message.answer(text=f"Мин.цена за 1 ночь:${message.text}")
    async with state.proxy() as data:
        if message.text.isdigit() and int(message.text) > 0:
            data['price_min'] = message.text
            await message.answer(text='Укажите макс.цену в $ за 1 ночь (например, 500)')
            await state.set_state(state=UsersStates.price_max)

        else:
            await bot.delete_message(message.from_user.id, message.message_id)
            await message.answer(f'⚠️Цена - это целое положительное число.\n'
                                 f'Укажите еще раз мин.цену в $ за 1 ночь (например, 10)')
            await state.set_state(state=UsersStates.price_min)


@dp.message_handler(content_types=['text'], state=UsersStates.price_max)
async def get_max_price(message: types.Message, state: FSMContext) -> None:
    """
    Получаем максимальную цену за 1 ночь.
    Указываем кол-во фото для отеля. Устанавливаем состояние 'amount_photos'.
    """
    await bot.delete_message(message.from_user.id, message.message_id)
    await message.answer(text=f"Макс.цена за 1 ночь:${message.text}")
    async with state.proxy() as data:
        if message.text.isdigit() and int(message.text) > 0:
            data['price_max'] = message.text
            await message.answer(text='Сколько фотографий отеля нужно?',
                                 reply_markup=photos_count_kb())
            await state.set_state(state=UsersStates.amount_photos)

        else:
            await bot.delete_message(message.from_user.id, message.message_id)
            await message.answer(f'⚠️Цена - это целое положительное число.\n'
                                 f'Укажите еще раз макс.цену в $ за 1 ночь (например, 280)')
            await state.set_state(state=UsersStates.price_max)


@dp.callback_query_handler(state=UsersStates.amount_photos)
async def check_amount_photos(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Получаем кол-во фото для отеля.
    Выполняется поиск отелей с учётом всех заданных условий.
    Устанавливаем состояние 'result'.
    """
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    await callback.message.answer(text=f"Кол-во фото для отеля: {callback.data.split('photos_count_')[1]}")
    async with state.proxy() as data:
        data['amount_photos'] = callback.data

    await state.set_state(state=UsersStates.result)
    await get_result(message=callback.message, state=state)


@dp.message_handler(state=UsersStates.result)
async def get_result(message: types.Message, state: FSMContext) -> None:
    """
    Получаем результат поиска отелей.
    Устанавливаем состояние 'page'.
    """
    async with state.proxy() as data:
        pprint(data.as_dict())
        result = get_hotels(data)

        if len(result) != 0:
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
        else:
            await message.answer(text=f"‼️Извините, при обработке данных произошла ошибка!‼️\n"
                                      f"Мы уже работаем над её устранением.\n"
                                      f"Пожалуйста, выберите ниже нужную вам команду. {DEFAULT_COMMANDS}",
                                 parse_mode='HTML')
            await state.finish()


@dp.message_handler(state=UsersStates.page)
async def show_page(chat_id: str, page_block: dict, page_num: int, pages_total: int, state: FSMContext):
    """
    Получаем номер страницы.
    Выводим на экран 2 сообщения об отеле:
    - в первом — фото;
    - во втором — описание и inline-клавиатура, соответствующая номеру страницы.
    Устанавливаем состояние 'page'.
    """
    page_keyboard = types.InlineKeyboardMarkup(row_width=3)

    if page_num > 0:
        page_keyboard.insert(types.InlineKeyboardButton(text="⬅️", callback_data='page_back'))

    url_data = (f"https://www.hotels.com/Hotel-Search?adults=2"
                f"&d1={page_block['checkIn']}"
                f"&d2={page_block['checkOut']}"
                f"&destination={page_block['destination']}"
                f"&endDate={page_block['checkOut']}"
                f"&flexibility=0_DAY"
                f"&latLong={page_block['dest_coord']['latitude']}%2C{page_block['dest_coord']['longitude']}"
                f"&price={page_block['price_min']}"
                f"&price={page_block['price_max']}"
                f"&regionId={page_block['dest_id']}"
                f"&rooms=1"
                f"&semdtl="
                f"&sort={page_block['sort_by']}"
                f"&startDate={page_block['checkIn']}"
                f"&theme="
                f"&useRewards=false"
                f"&userIntent=")

    page_keyboard.insert(types.InlineKeyboardButton(text=f'отель №{page_num + 1} из {pages_total}',
                                                    url=url_data))

    if page_num < pages_total - 1:
        page_keyboard.insert(types.InlineKeyboardButton(text="➡️", callback_data='page_next'))

    page_keyboard.add(types.InlineKeyboardButton(text=f'⛔️завершить просмотр⛔️', callback_data='cancel_show'))

    await state.set_state(state=UsersStates.page)

    await bot.send_media_group(chat_id=chat_id,
                               media=[types.InputMediaPhoto(i_image) for i_image in page_block['image']])

    if page_block.get('distance'):
        await bot.send_message(chat_id=chat_id,
                               text=f"<b>Название отеля:</b> {page_block['name']}\n"
                                    f"<b>Цена за 1 ночь:</b> {page_block['price']}\n"
                                    f"<b>Цена общая:</b> {page_block['price_total']}\n"
                                    f"<b>Расстояние от центра, км:</b> {page_block['distance']}\n"
                                    f"<b>Рейтинг отеля:</b> {page_block['score']}/10\n"
                                    f"<b>Кол-во отзывов:</b> {page_block['total']}",
                               parse_mode='HTML',
                               reply_markup=page_keyboard)
    else:
        await bot.send_message(chat_id=chat_id,
                               text=f"<b>Название отеля:</b> {page_block['name']}\n"
                                    f"<b>Цена за 1 ночь:</b> {page_block['price']}\n"
                                    f"<b>Цена общая:</b> {page_block['price_total']}\n"
                                    f"<b>Рейтинг отеля:</b> {page_block['score']}/10\n"
                                    f"<b>Кол-во отзывов:</b> {page_block['total']}",
                               parse_mode='HTML',
                               reply_markup=page_keyboard)


@dp.callback_query_handler(lambda callback: callback.data.startswith("page_"), state=UsersStates.page)
async def page_change(callback: types.CallbackQuery, state: FSMContext):
    """
    Получаем номер страницы.
    Выполняем пагинацию.
    Выводим на экран 2 сообщения:
    - комментарий-"заплатка" к фото (их нельзя удалить);
    - во втором — описание отеля и inline-клавиатура, соответствующая новому номеру страницы.
    Устанавливаем состояние 'page'.
    """
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

        patch = callback.message.text.split("\n")
        await callback.message.edit_text(text=f"⬆️ {patch[0].split('Название отеля: ')[1]} ({patch[1]}) ⬆️")
        await callback.answer()


@dp.callback_query_handler(lambda callback: callback.data.startswith("cancel_show"), state='*')
async def page_change(callback: types.CallbackQuery, state: FSMContext):
    """
    Завершаем просмотр отеля.
    Выполняем выход в главное меню.
    Устанавливаем состояние 'finish'.
    """
    await callback.message.answer(text=f'Просмотр завершен. Выберите дальнейшее действие\n{DEFAULT_COMMANDS}',
                                  parse_mode='HTML')
    await state.finish()
