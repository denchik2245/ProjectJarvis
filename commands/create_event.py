# commands/create_event.py

import re
from datetime import datetime, date
from Services.Google_Calendar import add_event
import logging

logger = logging.getLogger(__name__)

def create_event_command(update, recognized_text: str):
    """
    Создает событие в Google Calendar на основе голосового сообщения.
    Пример: "Добавь событие «Встреча с клиентом на 23:30»."
    """
    try:
        # Проверяем наличие кавычек «…»
        quoted_match = re.search(r'«(.*?)»', recognized_text)
        if quoted_match:
            content = quoted_match.group(1)
            if " на " in content:
                parts = content.rsplit(" на ", 1)
                title = parts[0].strip()
                time_str = parts[1].strip()
            else:
                title = content.strip()
                time_str = "00:00"
            start_time_str = time_str
            end_time_str = time_str
            description_part = ""
        else:
            parts = recognized_text.lower().replace("добавь событие", "").split("с описанием")
            if len(parts) == 1:
                title_and_time = parts[0].strip()
                description_part = ""
            elif len(parts) == 2:
                title_and_time = parts[0].strip()
                description_part = parts[1].strip()
            else:
                update.message.reply_text("Не удалось правильно разобрать команду для добавления события.")
                return

            time_part = title_and_time.split("с")
            if len(time_part) < 2:
                update.message.reply_text("Не удалось определить время события.")
                return
            title = time_part[0].strip()
            time_range = time_part[1].strip()
            if "до" in time_range:
                start_time_str, end_time_str = [t.strip() for t in time_range.split("до")]
            else:
                start_time_str = time_range
                end_time_str = start_time_str

        today_str = date.today().strftime("%Y-%m-%d")
        try:
            start_dt = datetime.strptime(f"{today_str} {start_time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            update.message.reply_text(f"Ошибка: некорректный формат времени: {start_time_str}")
            return

        try:
            end_dt = datetime.strptime(f"{today_str} {end_time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            update.message.reply_text(f"Ошибка: некорректный формат времени: {end_time_str}")
            return

        start_iso = start_dt.isoformat()
        end_iso = end_dt.isoformat()

        event = add_event(
            title,
            "",  # location оставляем пустым
            description_part,
            start_iso,
            end_iso,
            []
        )

        update.message.reply_text(f"Событие добавлено: {event.get('summary')} ID: {event.get('id')}")
    except Exception as e:
        logger.error("Ошибка при добавлении события: %s", e)
        update.message.reply_text(f"Ошибка при добавлении события: {e}")
