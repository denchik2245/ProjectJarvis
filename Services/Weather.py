import requests

API_KEY = 'YOUR_YANDEX_WEATHER_API_KEY'  # API-ключ. Пример: "demo_yandex_weather_api_key_ca6d09349ba0"
BASE_URL = 'https://api.weather.yandex.ru/v2/'

# Координаты Москвы
city = {'lat': 55.7558, 'lon': 37.6173}

cities = [
    {'city': 'Москва', 'lat': '55.7558', 'lon': '37.6173'},
    {'city': 'Санкт-Петербург', 'lat': '59.9343', 'lon': '30.3351'},
    {'city': 'Новосибирск', 'lat': '55.0084', 'lon': '82.0155'},
    {'city': 'Екатеринбург', 'lat': '56.8389', 'lon': '60.6057'},
    {'city': 'Нижний Новгород', 'lat': '56.2965', 'lon': '43.9361'},
    {'city': 'Казань', 'lat': '55.8304', 'lon': '49.0661'},
    {'city': 'Челябинск', 'lat': '55.1644', 'lon': '61.4368'},
    {'city': 'Омск', 'lat': '54.9885', 'lon': '73.3242'},
    {'city': 'Самара', 'lat': '53.2001', 'lon': '50.15'},
    {'city': 'Ростов-на-Дону', 'lat': '47.2225', 'lon': '39.7182'},
    {'city': 'Уфа', 'lat': '54.7388', 'lon': '55.9721'},
    {'city': 'Красноярск', 'lat': '56.0153', 'lon': '92.8932'},
    {'city': 'Воронеж', 'lat': '51.6615', 'lon': '39.1973'},
    {'city': 'Пермь', 'lat': '58.0105', 'lon': '56.2502'},
    {'city': 'Волгоград', 'lat': '48.7080', 'lon': '44.5133'},
    {'city': 'Саратов', 'lat': '51.5320', 'lon': '46.0342'},
    {'city': 'Тюмень', 'lat': '57.1522', 'lon': '65.5272'},
    {'city': 'Ижевск', 'lat': '56.8529', 'lon': '53.2112'},
    {'city': 'Барнаул', 'lat': '53.3472', 'lon': '83.7779'},
    {'city': 'Ульяновск', 'lat': '54.3213', 'lon': '48.4025'},
    {'city': 'Калуга', 'lat': '54.5146', 'lon': '36.2732'},
]

# возможно, стоит заставить нейронного агента искать координаты городов? Или просто это делать "этажом выше"
def change_coordinates(city):
    coordinate = cities['city': city] # // Выбор города из массива 
    if coordinate:
        city = {'lat': coordinate['lat'], 'lon':coordinate['lon']}
        return {coordinate}
    else:
        raise Exception(f'Error: {city} не имеется в реестре городов.')

def change_coordinates(lat, lon): # {} <-- Нуну, скобочки, ага
    city = {'lat': lat, 'lon': lon}
    return {city}
    
def get_current_weather(city):
    """Получить текущую погоду для указанного города."""
    headers = {
        'X-Yandex-API-Key': API_KEY
    }
    response = requests.get(f'{BASE_URL}informers?lat={city["lat"]}&lon={city["lon"]}', headers=headers)
    
    if response.status_code == 200:
        weather_data = response.json()
        return {
            'temperature': weather_data['fact']['temp'],
            'condition': weather_data['fact']['condition'],
            'wind_speed': weather_data['fact']['wind_speed'],
            'humidity': weather_data['fact']['humidity']
        }
    else:
        raise Exception(f'Error: {response.status_code}') # Возможно, я неправтльно юзаю эту конструкцию

def get_weather_forecast(city, days=1):
    """Получить прогноз погоды на указанные дни (1 или 7)."""
    headers = {
        'X-Yandex-API-Key': API_KEY
    }
    response = requests.get(f'{BASE_URL}forecast?lat={city["lat"]}&lon={city["lon"]}&days={days}', headers=headers)
    
    if response.status_code == 200:
        forecast_data = response.json()
        return forecast_data['forecasts']
    else:
        raise Exception(f'Error: {response.status_code}')
