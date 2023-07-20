import requests
import json
import re
from config_data import config

city_url = "https://hotels4.p.rapidapi.com/locations/v3/search"
headers = {
    "X-RapidAPI-Key": config.RAPID_API_KEY,
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}


def destination_id(city: str):
    querystring = {"q": city, "locale": "en_US", "langid": "1033", "siteid": "300000001"}
    response = requests.get(city_url, headers=headers, params=querystring)
    data = json.loads(response.text)
    similar = {}
    for element in data['sr']:
        element_fullname = element['regionNames']['fullName']
        element_id = element['essId']['sourceId']
        # справочная печать в терминал
        # print(f"Fullname: {element_fullname}, ID: {element_id}")
        similar[element_fullname] = element_id

    return similar

