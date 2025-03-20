from telegram import Update
from telegram.ext import CallbackContext
from Services.Weather import get_current_weather, find_city_coordinates, get_weather_forecast, translate_condition


# Команда /weather: получить текущую погоду
def weather_command(update: Update, context: CallbackContext) -> None:
    """
    Формат: /weather Город
    Пример: /weather Москва
    """
    text = update.message.text  # "/weather Москва"
    parts = text.split(maxsplit=1)  # ['/weather', 'Москва']
    if len(parts) < 2:
        update.message.reply_text("Укажите город. Пример: /weather Москва")
        return

    city_name = parts[1].strip()
    try:
        coords = find_city_coordinates(city_name)
        weather_info = get_current_weather(coords)
        # Допустим, get_current_weather уже возвращает 'condition' на русском (если вы сделали перевод внутри)
        # Если нет, то можно было бы сделать:
        # weather_info['condition'] = translate_condition(weather_info['condition'])

        # Формируем красивый ответ
        answer = (
            f"Погода в {city_name}:\n"
            f"Температура: {weather_info['temperature']} °C\n"
            f"Состояние: {weather_info['condition']}\n"
            f"Ветер: {weather_info['wind_speed']} м/с\n"
            f"Влажность: {weather_info['humidity']}%"
        )
        update.message.reply_text(answer)

    except ValueError as e:
        # Если город не найден в списке
        update.message.reply_text(str(e))
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении погоды: {e}")


# Команда /forecast: получить прогноз
def forecast_command(update: Update, context: CallbackContext) -> None:
    """
    Формат: /forecast Город [количество_дней]
    Пример: /forecast Москва 7
    """
    text = update.message.text  # "/forecast Москва 7"
    parts = text.split(maxsplit=2)  # ['/forecast', 'Москва', '7']
    if len(parts) < 2:
        update.message.reply_text("Укажите город. Пример: /forecast Москва 3")
        return

    city_name = parts[1].strip()
    # Дни по умолчанию 1, но если пользователь указал третьим словом число, берём его
    days = 1
    if len(parts) == 3:
        try:
            days = int(parts[2].strip())
        except ValueError:
            update.message.reply_text("Количество дней должно быть числом. Пример: /forecast Москва 7")
            return

    try:
        coords = find_city_coordinates(city_name)
        forecast_data = get_weather_forecast(coords, days=days)

        # forecast_data — это список словарей, в каждом словаре ключи:
        # "date": YYYY-MM-DD
        # "parts": { "day": {...}, "night": {...}, ... }
        # В блоке day обычно есть "temp_avg" и "condition" (англ).

        msg_lines = [f"Прогноз погоды в {city_name} на {days} дн.:\n"]
        for day_info in forecast_data:
            date_str = day_info['date']  # формат YYYY-MM-DD
            parts_dict = day_info.get('parts', {})
            day_part = parts_dict.get('day', {})  # Погода днём

            day_temp = day_part.get('temp_avg', "N/A")
            condition_en = day_part.get('condition', "N/A")
            # Переведём состояние в русский
            condition_ru = translate_condition(condition_en)

            msg_lines.append(f"{date_str}: {day_temp} °C, {condition_ru}")

        update.message.reply_text("\n".join(msg_lines))

    except ValueError as e:
        update.message.reply_text(str(e))
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении прогноза: {e}")