from io import BytesIO
import requests
from PIL import Image

GEOCODE_API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"
GEOCODE_SERVER = "https://geocode-maps.yandex.ru/1.x/"
STATIC_MAP_SERVER = "https://static-maps.yandex.ru/1.x/"


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
        spn=None, placemark="ya_en"):
    request_params = {
        'll': ll,
        'l': mode,
    }
    
    if points:
        request_params['pt'] = "~".join([",".join(point) for point in points])

    if spn:
        request_params['spn'] = spn

    response = requests.get(STATIC_MAP_SERVER, params=request_params)

    if not response:
        raise AssertionError(f"Ошибка при получении статического изображения:\n"
                             f"{response.url}\n"
                             f"{response.status_code} {response.reason}\n"
                             f"{response.content}")

    return bytes(response.content)
