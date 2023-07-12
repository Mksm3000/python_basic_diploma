from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    start = State()
    enter_city = State()
    city_id = State()
    hotel_quantity = State()
    check_in = State()
    check_out = State()
    photo = State()
    photo_quantity = State()
    price_min = State()
    price_max = State()
    distance = State()
    final = State()
    cansel = State()
