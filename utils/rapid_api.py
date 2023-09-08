import requests
import json
from typing import Optional, List, Tuple, Dict, Any
from pprint import pprint
from config_data.config import RAPID_API_KEY


def api_query(method: str, url: str, params: Dict) -> Optional[requests.Response]:
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    if method == 'get':
        response = requests.get(url=url, params=params, headers=headers, allow_redirects=True, timeout=15)
    elif method == 'post':
        response = requests.post(url=url, json=params, headers=headers, allow_redirects=True, timeout=15)

    return response


def get_city(city: str) -> Dict:
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {"q": city, "locale": "en_US", "langid": "1033", "siteid": "300000001"}

    response = api_query(method='get', url=url, params=querystring)
    resp_dict = json.loads(response.text)

    city_dict = {}

    for element in resp_dict['sr']:
        if element.get('gaiaId'):
            city_id = element['gaiaId']
            city_name = element['regionNames']['fullName']
            city_dict[city_name] = city_id

    return city_dict


def price_sort(hotel: Dict):
    return hotel["price"].split("$")[1]


def get_hotels(data: Dict[str, Any]) -> List:
    # print(data)
    url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": data['city_id']},
        "checkInDate": {
            "day": int(data['date_in'].strftime('%d')),
            "month": int(data['date_in'].strftime('%m')),
            "year": int(data['date_in'].strftime('%Y'))
        },
        "checkOutDate": {
            "day": int(data['date_out'].strftime('%d')),
            "month": int(data['date_out'].strftime('%m')),
            "year": int(data['date_out'].strftime('%Y'))
        },
        "rooms": [
            {
                "adults": 2,
                "children": []
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": int(data['amount_hotels'].split('hotels_count_')[1]),
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {
            "max": int(data.get("price_max", 200)),
            "min": int(data.get("price_min", 10))
        }}
    }

    response = api_query(method='post', url=url, params=payload)
    response_dict = json.loads(response.text)
    # print(response_dict)
    hotels_list = list()

    for element in response_dict['data']['propertySearch']['properties']:
        if element.get("id") and element.get("name"):
            hotel_temp = {"name": element.get("name"),
                          "id": element.get("id"),
                          "price": element["price"]["displayMessages"][0]["lineItems"][0]["price"].get("formatted"),
                          "price_total": element["price"]["displayMessages"][1]["lineItems"][0].get("value").split(' ')[0],
                          "score": element["reviews"].get("score"),
                          "total": element["reviews"].get("total"),
                          "image": get_hotel_photos(element["id"], data["amount_photos"])}
            hotels_list.append(hotel_temp)

    hotels_list.sort(key=price_sort)
    # pprint(hotels_list)
    return hotels_list


def get_hotel_photos(hotel_id: str, amount_photo: str) -> List:
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
    response_dict = json.loads(response.text)
    # print(response_dict)
    image_list = list()

    for element in response_dict["data"]["propertyInfo"]["propertyGallery"]["images"]:
        if element["image"].get("url") and (len(image_list) < int(image_num)):
            image_link = element["image"]["url"].split('?impolicy')[0]
            image_list.append(image_link)

    # pprint(image_list)
    return image_list
