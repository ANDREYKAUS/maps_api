import math
from io import BytesIO
import requests
from PIL import Image

GEOCODE_API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"
GEOCODE_SERVER = "https://geocode-maps.yandex.ru/1.x/"
STATIC_MAP_SERVER = "https://static-maps.yandex.ru/1.x/"
SEARCH_SERVER = "https://search-maps.yandex.ru/v1/"
SEARCH_API_KEY = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
COORD_TO_GEO_X = 0.0000426
COORD_TO_GEO_Y = 0.0000428


def get_coordinates_from_object(toponym):
    toponym_coordinates = toponym['Point']['pos']
    toponym_longitude, toponym_lattitude = toponym_coordinates.split()

    return (float(toponym_longitude), float(toponym_lattitude))


def get_object_by_address(address: str):
    request_params = {
        'apikey': GEOCODE_API_KEY,
        'geocode': address,
        'format': "json"
    }
    response = requests.get(GEOCODE_SERVER, params=request_params)

    if not response:
        raise RuntimeError(f"Ошибка выполнения запроса:\n"
                           f"{response.url}\n"
                           f"Статус: {response.status_code} {response.reason}\n"
                           f"{response.content}")

    data = response.json()
    features = data['response']['GeoObjectCollection']['featureMember']
    return features[0]['GeoObject'] if features else None


def get_coordinates_by_address(address: str):
    toponym = get_object_by_address(address)
    if toponym is None:
        return (None, None)

    toponym_coordinates = toponym['Point']['pos']
    toponym_longitude, toponym_lattitude = toponym_coordinates.split()

    return (float(toponym_longitude), float(toponym_lattitude))


def get_static_map_image(ll, mode, points=None, 
        zoom=None, placemark="ya_en"):
    request_params = {
        'll': ll,
        'l': mode,
        'size': "650,450"
    }
    
    if points:
        request_params['pt'] = "~".join([",".join(point) for point in points])

    if zoom:
        request_params['z'] = zoom

    response = requests.get(STATIC_MAP_SERVER, params=request_params)

    if not response:
        raise RuntimeError(f"Ошибка при получении статического изображения:\n"
                             f"{response.url}\n"
                             f"{response.status_code} {response.reason}\n"
                             f"{response.content}")

    return bytes(response.content)


def screen_to_geo(map_long, map_lat, mouse_long, mouse_lat, zoom):
    dy = 225 - mouse_lat
    dx = mouse_long - 300
    lx = map_long + dx * COORD_TO_GEO_X * math.pow(2, 15 - zoom)
    ly = map_lat + dy * COORD_TO_GEO_Y * \
            math.cos(math.radians(map_lat)) * math.pow(2, 15 - zoom)
    return lx, ly


def find_closest_organization(address, ll):
    request_params = {
        "apikey": SEARCH_API_KEY,
        "type": "biz",
        "lang": "ru_RU",
        "text": address,
        "results": 1,
        "ll": ll,
        "spn": "0.05,0.05",
        "rspn": 1
    }

    response = requests.get(SEARCH_SERVER, params=request_params)
    if not response:
        raise RuntimeError(f"Ошибка при получении статического изображения:\n"
                             f"{response.url}\n"
                             f"{response.status_code} {response.reason}\n"
                             f"{response.content}")
    data = response.json()
    return data['features'][0] if data['features'] else None
