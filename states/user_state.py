from aiogram.dispatcher.filters.state import StatesGroup, State
import datetime


class UsersStates(StatesGroup):
    """
    Класс реализует состояние пользователя внутри сценария.
    Атрибуты заполняются во время опроса пользователя. Очищаются при каждой новой команде.

    Attributes:
        city_name (str): город, в котором ищем отели.
        city_id (str): id города, в котором ищем отели.
        # cities (Dict): подходящие по названию города, из которых пользователь выбирает нужный ему.
        amount_hotels (int): количество отелей.
        start_date (datetime.date): дата заезда в отель.
        amount_nights (int): количество ночей.
        amount_adults (int): количество взрослых.
        min_price (int): минимальная цена за ночь.
        max_price (int): максимальная цена за ночь.
        max_distance (float): максимальная дистанция до центра города.
        current_page (int): текущая страница пагинации.
        result (list): результат поиска отелей.
    """

    city_name: str = State()
    city_id: str = State()

    date_in: datetime.date = State()
    date_out: datetime.date = State()

    price_min: int = State()
    price_max: int = State()

    amount_hotels: str = State()
    amount_photos: str = State()

    max_distance: float = State()

    result = State()
