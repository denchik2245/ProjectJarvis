# В файле command_parser.py

import logging
from telegram import Update
from telegram.ext import CallbackContext
from .voice_recognition import process_voice_message
from .ollama import parse_command_from_text

# Импорт функций из Google_Gmail и Google_Calendar
from Services.Google_Gmail import delete_trash_command, delete_spam_command, delete_promo_command
from Services.Google_Calendar import add_event  # Функция для добавления события

logger = logging.getLogger(__name__)

def handle_voice_command(update: Update, context: CallbackContext) -> None:
    recognized_text = process_voice_message(update, context)
    if not recognized_text:
        update.message.reply_text("Не удалось распознать голосовое сообщение. Попробуйте ещё раз.")
        return

    # Определяем команду из текста
    commands = parse_command_from_text(recognized_text)
    executed_commands = set()

    for command_data in commands:
        command = command_data.get("command", "unknown")
        arguments = command_data.get("arguments", {})

        logger.info(f"Распознана голосовая команда: {command}, аргументы: {arguments}")

        if command in executed_commands:
            continue

        if command == "clear_mailbox_trash":
            delete_trash_command(update, context)
            executed_commands.add(command)
        elif command == "delete_spam":
            delete_spam_command(update, context)
            executed_commands.add(command)
        elif command == "delete_promo":
            delete_promo_command(update, context)
            executed_commands.add(command)
        elif command == "create_event":
            create_event_command(update, recognized_text)
            executed_commands.add(command)
        elif command == "send_message":
            to = arguments.get("to")
            content = arguments.get("content")
            if to and content:
                from Services.Google_Contacts import send_message
                send_message(to, content)
                update.message.reply_text(f"Сообщение отправлено {to}: {content}")
                executed_commands.add(command)
            else:
                update.message.reply_text("Не хватает аргументов для отправки сообщения.")
                executed_commands.add(command)
        else:
            update.message.reply_text(
                f"Команда не распознана или не поддерживается. Распознанный текст: {recognized_text}"
            )
            executed_commands.add(command)


def create_event_command(update: Update, recognized_text: str) -> None:
    """
    Создает событие в Google Calendar на основе голосового сообщения.
    Пример: "Добавь событие «Встреча с клиентом на 23.30»."
    """
    try:
        import re
        # Проверим, содержит ли текст кавычки «…»
        quoted_match = re.search(r'«(.*?)»', recognized_text)
        if quoted_match:
            content = quoted_match.group(1)
            # Если внутри есть разделитель " на ", разделяем заголовок и время
            if " на " in content:
                parts = content.rsplit(" на ", 1)
                title = parts[0].strip()
                time_str = parts[1].strip()
            else:
                title = content.strip()
                time_str = "00:00"  # Если время не указано, устанавливаем значение по умолчанию
            # Используем найденное время как и начало, и окончание события
            start_time_str = time_str
            end_time_str = time_str
            description_part = ""
        else:
            # Если кавычек нет, используем другую логику
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
            start_time_str, end_time_str = time_range.split("до") if "до" in time_range else (time_range, time_range)
            start_time_str = start_time_str.strip()
            end_time_str = end_time_str.strip() if "до" in time_range else start_time_str

        # Добавляем дополнительные проверки на корректность формата времени
        from datetime import datetime, date
        today_str = date.today().strftime("%Y-%m-%d")

        # Пытаемся распарсить время в корректный формат
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
            "",  # Поле location оставляем пустым
            description_part,
            start_iso,
            end_iso,
            []
        )

        update.message.reply_text(f"Событие добавлено: {event.get('summary')} ID: {event.get('id')}")
    except Exception as e:
        update.message.reply_text(f"Ошибка при добавлении события: {e}")