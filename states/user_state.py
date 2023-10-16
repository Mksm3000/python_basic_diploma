from aiogram.dispatcher.filters.state import StatesGroup, State


class UsersStates(StatesGroup):
    """
    Класс реализует состояние пользователя внутри сценария.
    Атрибуты заполняются во время опроса пользователя.
    Очищаются при каждой новой команде.

    Attributes:
        city_name (str): город, в котором ищем отели.
        city_id (str): id города, в котором ищем отели.
        date_in: (datetime.date): дата заезда в отель.
        date_out: (datetime.date): дата выезда из отеля.
        price_min (int): минимальная цена за ночь.
        price_max (int): максимальная цена за ночь.
        amount_hotels: (str): кол-во отелей (от 1 до 10)
        amount_photos: (str): кол-во фото при показе инфо отеля (от 1 до 5)
        max_km_distance (float): максимальная дистанция до центра города.
        result (str): результат поиска отелей.
        page (str): текущая страница пагинации.
        history (str): просмотр выбранного результата поиска
    """

    city_name = State()
    city_id = State()

    date_in = State()
    date_out = State()

    price_min = State()
    price_max = State()

    amount_hotels = State()
    amount_photos = State()

    max_km_distance = State()

    result = State()

    page = State()

    history = State()
