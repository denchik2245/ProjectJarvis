import os
import requests

# Чтобы считывать переменные из .env:
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ.get('YANDEX_WEATHER_API_KEY')  # Читаем из .env
BASE_URL = 'https://api.weather.yandex.ru/v2/'

# Сопоставление состояний на английском → русские строки
CONDITION_TRANSLATIONS = {
    "clear": "Ясно",
    "partly-cloudy": "Малооблачно",
    "cloudy": "Облачно с прояснениями",
    "overcast": "Пасмурно",
    "drizzle": "Морось",
    "light-rain": "Небольшой дождь",
    "rain": "Дождь",
    "moderate-rain": "Умеренно сильный дождь",
    "heavy-rain": "Сильный дождь",
    "continuous-heavy-rain": "Длительный сильный дождь",
    "showers": "Ливень",
    "wet-snow": "Дождь со снегом",
    "light-snow": "Небольшой снег",
    "snow": "Снег",
    "snow-showers": "Снегопад",
    "hail": "Град",
    "thunderstorm": "Гроза",
    "thunderstorm-with-rain": "Дождь с грозой",
    "thunderstorm-with-hail": "Гроза с градом",
    # добавляйте при необходимости
}

cities = [
    {'city': 'Москва',            'lat': '55.7558', 'lon': '37.6173'},
    {'city': 'Санкт-Петербург',   'lat': '59.9343', 'lon': '30.3351'},
    {'city': 'Новосибирск',       'lat': '55.0084', 'lon': '82.0155'},
    {'city': 'Екатеринбург',      'lat': '56.8389', 'lon': '60.6057'},
    {'city': 'Нижний Новгород',   'lat': '56.2965', 'lon': '43.9361'},
    {'city': 'Казань',            'lat': '55.8304', 'lon': '49.0661'},
    {'city': 'Челябинск',         'lat': '55.1644', 'lon': '61.4368'},
    {'city': 'Омск',              'lat': '54.9885', 'lon': '73.3242'},
    {'city': 'Самара',            'lat': '53.2001', 'lon': '50.15'},
    {'city': 'Ростов-на-Дону',    'lat': '47.2225', 'lon': '39.7182'},
    {'city': 'Уфа',               'lat': '54.7388', 'lon': '55.9721'},
    {'city': 'Красноярск',        'lat': '56.0153', 'lon': '92.8932'},
    {'city': 'Воронеж',           'lat': '51.6615', 'lon': '39.1973'},
    {'city': 'Пермь',             'lat': '58.0105', 'lon': '56.2502'},
    {'city': 'Волгоград',         'lat': '48.7080', 'lon': '44.5133'},
    {'city': 'Саратов',           'lat': '51.5320', 'lon': '46.0342'},
    {'city': 'Тюмень',            'lat': '57.1522', 'lon': '65.5272'},
    {'city': 'Ижевск',            'lat': '56.8529', 'lon': '53.2112'},
    {'city': 'Барнаул',           'lat': '53.3472', 'lon': '83.7779'},
    {'city': 'Ульяновск',         'lat': '54.3213', 'lon': '48.4025'},
    {'city': 'Калуга',            'lat': '54.5146', 'lon': '36.2732'},
]

def find_city_coordinates(city_name: str) -> dict:
    """
    Ищет в списке cities словарь с координатами для указанного города.
    Возвращает dict вида {'lat': ..., 'lon': ...},
    либо бросает ValueError, если город не найден.
    """
    for c in cities:
        if c['city'].lower() == city_name.lower():
            return {'lat': c['lat'], 'lon': c['lon']}
    raise ValueError(f'Город "{city_name}" не найден в списке.')

def translate_condition(condition: str) -> str:
    """
    Переводит состояние погоды (condition) с английского на русский,
    используя словарь CONDITION_TRANSLATIONS.
    Если ключа нет, возвращаем исходную строку.
    """
    return CONDITION_TRANSLATIONS.get(condition, condition)

def get_current_weather(lat_lon: dict) -> dict:
    """
    Получить текущую погоду для координат (lat_lon = {'lat': ..., 'lon': ...}).
    Используем v2/forecast с days=1 и забираем данные текущей погоды из "fact".
    Возвращает словарь вида:
        {
          'temperature':  ...,
          'condition':    ...,
          'wind_speed':   ...,
          'humidity':     ...
        }
    """
    if not API_KEY:
        raise Exception("YANDEX_WEATHER_API_KEY не найден. Укажите его в .env.")

    headers = {
        'X-Yandex-API-Key': API_KEY
    }
    # Запрашиваем forecast на 1 день, чтобы получить и текущие данные (fact)
    url = f'{BASE_URL}forecast?lat={lat_lon["lat"]}&lon={lat_lon["lon"]}&days=1'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        fact = data.get('fact', {})
        # Переводим английское condition → русское
        condition_ru = translate_condition(fact.get('condition', ''))
        return {
            'temperature': fact.get('temp'),
            'condition': condition_ru,
            'wind_speed': fact.get('wind_speed'),
            'humidity': fact.get('humidity')
        }
    else:
        raise Exception(f'Ошибка при запросе погоды: {response.status_code} - {response.text}')

def get_weather_forecast(lat_lon: dict, days: int = 1) -> dict:
    """
    Получить прогноз погоды на указанные дни (1..7).
    Возвращает список со словарями, где каждая запись - один день:
       [
         {
           "date": "...",
           "parts": {...},
           ...
         },
         ...
       ]
    """
    if not API_KEY:
        raise Exception("YANDEX_WEATHER_API_KEY не найден. Укажите его в .env.")

    headers = {
        'X-Yandex-API-Key': API_KEY
    }
    url = f'{BASE_URL}forecast?lat={lat_lon["lat"]}&lon={lat_lon["lon"]}&days={days}'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        forecast_data = response.json()
        # Здесь вы при желании тоже можете переводить "condition" в каждом из блоков "parts",
        # если хотите выводить русский текст при формировании ответа.
        return forecast_data.get('forecasts', [])
    else:
        raise Exception(f'Ошибка при запросе прогноза: {response.status_code} - {response.text}')