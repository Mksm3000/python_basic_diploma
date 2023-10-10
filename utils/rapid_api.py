import json
import logging
from pprint import pprint
from typing import Optional, List, Dict, Any

import requests

from config_data.config import RAPID_API_KEY


def api_query(method: str, url: str, params: Dict) -> Optional[requests.Response]:
    """
    Для выполнения запроса указываем:
    - тип: "get" или "post";
    - url-ссылку;
    - параметры.
    """
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = None
    logging.info(f"Starting request to API (method: {method}; url: {url})")
    try:
        if method == 'get':
            response = requests.get(url=url, params=params, headers=headers, allow_redirects=True, timeout=15)
        elif method == 'post':
            response = requests.post(url=url, json=params, headers=headers, allow_redirects=True, timeout=15)

        if response.status_code == requests.codes.ok:
            logging.info("request OK")
            return response
        logging.error(f"Запрос для функции 'api_query' вернулся с кодом '{response.status_code}'")
        return None
    except Exception as ex:
        logging.error("Bad request:", ex)
        return None


def get_city(city: str) -> Dict:
    """
    Получаем словарь по типу {'city': 'id'} из городов, подходящих по имени.
    """
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {"q": city, "locale": "en_US", "langid": "1033", "siteid": "300000001"}

    response = api_query(method='get', url=url, params=querystring)

    city_dict = {}

    try:
        if response:
            resp_dict = json.loads(response.text)
            for element in resp_dict['sr']:
                if element.get('gaiaId'):
                    city_id = element['gaiaId']
                    city_name = element['regionNames']['fullName']
                    city_dict[city_name] = city_id
            if len(city_dict) != 0:
                city_dict["❎вернуться в главное меню❎"] = "main_menu"
    except Exception as ex:
        logging.error("Ошибка при создании словаря 'city_dict'", ex)
    finally:
        return city_dict


def price_sort(temp: Dict):
    """
    Сортируем отели по цене за 1 ночь.
    """
    price_ = temp["price"]["displayMessages"][0]["lineItems"][0]["price"]["formatted"].split("$")[1]
    price = price_.replace(",", "")
    return int(price)


def get_hotels(data: Dict[str, Any]) -> List:
    """
    Получаем список словарей для найденых отелей.
    """
    sort_of_data = "PRICE_LOW_TO_HIGH"

    if data['command'] == '/best_deal':
        sort_of_data = "DISTANCE"

    url = "https://hotels4.p.rapidapi.com/properties/v2/list"

    destination = data['city_id']
    day_in = int(data['date_in'].strftime('%d'))
    month_in = int(data['date_in'].strftime('%m'))
    year_in = int(data['date_in'].strftime('%Y'))
    day_out = int(data['date_out'].strftime('%d'))
    month_out = int(data['date_out'].strftime('%m'))
    year_out = int(data['date_out'].strftime('%Y'))
    price_max = int(data.get("price_max", 1000))
    price_min = int(data.get("price_min", 10))

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": destination},
        "checkInDate": {
            "day": day_in,
            "month": month_in,
            "year": year_in
        },
        "checkOutDate": {
            "day": day_out,
            "month": month_out,
            "year": year_out
        },
        "rooms": [
            {
                "adults": 2,
                "children": []
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 200,
        "sort": sort_of_data,
        "filters": {"price": {
            "max": price_max,
            "min": price_min
        }}
    }

    response = api_query(method='post', url=url, params=payload)

    sorted_hotels = list()
    hotels_finish_list = list()
    amount = int(data['amount_hotels'].split('hotels_count_')[1])

    try:
        if response:
            response_dict = json.loads(response.text)

            if data['command'] in ['/low_price', '/best_deal']:
                """ Сортировка цены по возростанию """
                sorted_hotels = sorted(response_dict['data']['propertySearch']['properties'], key=price_sort)

            elif data['command'] == '/high_price':
                """ Сортировка цены по убыванию """
                sorted_hotels = sorted(response_dict['data']['propertySearch']['properties'], key=price_sort, reverse=True)

            for element in sorted_hotels:
                if (data['command'] == '/best_deal'
                        and data.get('max_km_distance')
                        and element.get("id")
                        and element.get("name")
                        and len(hotels_finish_list) < amount):
                    user_km_distance = float(data.get('max_km_distance'))
                    mile_distance = element["destinationInfo"]["distanceFromDestination"].get("value")
                    data_km_distance = float(mile_distance * 1.60934)
                    if user_km_distance >= data_km_distance:
                        hotel_temp = {"name": element.get("name"),
                                      "hotel_id": element.get("id"),
                                      "destination": data['city_name'],
                                      "dest_id": data['city_id'],
                                      "dest_coord": element['mapMarker']['latLong'],
                                      "distance": element["destinationInfo"]["distanceFromDestination"].get("value"),
                                      "price_min": price_min,
                                      "price_max": price_max,
                                      "price": element["price"]["displayMessages"][0]["lineItems"][0]["price"].get("formatted"),
                                      "price_total": element["price"]["displayMessages"][1]["lineItems"][0].get("value").split(' ')[0],
                                      "score": element["reviews"].get("score"),
                                      "total": element["reviews"].get("total"),
                                      "image": get_hotel_photos(element["id"], data["amount_photos"]),
                                      "checkIn": data['date_in'].strftime('%Y-%m-%d'),
                                      "checkOut": data['date_out'].strftime('%Y-%m-%d'),
                                      "sort_by": sort_of_data
                                      }
                        hotels_finish_list.append(hotel_temp)

                elif (data['command'] in ['/low_price', '/high_price']
                      and element.get("id")
                      and element.get("name")
                      and len(hotels_finish_list) < amount):
                    hotel_temp = {"name": element.get("name"),
                                  "hotel_id": element.get("id"),
                                  "destination": data['city_name'],
                                  "dest_id": data['city_id'],
                                  "dest_coord": element['mapMarker']['latLong'],
                                  "price_min": price_min,
                                  "price_max": price_max,
                                  "price": element["price"]["displayMessages"][0]["lineItems"][0]["price"].get("formatted"),
                                  "price_total": element["price"]["displayMessages"][1]["lineItems"][0].get("value").split(' ')[0],
                                  "score": element["reviews"].get("score"),
                                  "total": element["reviews"].get("total"),
                                  "image": get_hotel_photos(element["id"], data["amount_photos"]),
                                  "checkIn": data['date_in'].strftime('%Y-%m-%d'),
                                  "checkOut": data['date_out'].strftime('%Y-%m-%d'),
                                  "sort_by": sort_of_data
                                  }
                    hotels_finish_list.append(hotel_temp)

    except Exception as ex:
        logging.error(msg=f"Ошибка при создании словаря 'hotels_finish_list': {ex}")

    finally:
        return hotels_finish_list


def get_hotel_photos(hotel_id: str, amount_photo: str) -> List:
    """
    Получаем список url-ссылок на изображения отеля в кол-ве, указанном пользователем.
    """
    image_num = amount_photo.split('photos_count_')[1]
    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": hotel_id
    }

    response = api_query(method='post', url=url, params=payload)

    image_list = list()

    try:
        if response:
            response_dict = json.loads(response.text)

            for element in response_dict["data"]["propertyInfo"]["propertyGallery"]["images"]:
                if element["image"].get("url") and (len(image_list) < int(image_num)):
                    image_link = element["image"]["url"].split('?impolicy')[0]
                    image_list.append(image_link)

    except Exception as ex:
        logging.error(msg=f"Ошибка при создании списка изображений 'image_list': {ex}")
    finally:
        return image_list
