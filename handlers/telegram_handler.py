from telegram import Update
from telegram.ext import CallbackContext
from datetime import datetime, timedelta, date
import dateparser

#Команда /start
def start(update: Update, context: CallbackContext) -> None:
    user_first_name = update.effective_user.first_name if update.effective_user.first_name else "Пользователь"
    welcome_message = (
        f"Привет, {user_first_name}! Я твой личный ассистент.\n\n"
        "Чтобы посмотреть доступные команды, введи /help:\n"
    )
    update.message.reply_text(welcome_message)

# Команда /help
def help_command(update: Update, context: CallbackContext) -> None:
    help_message = (
        "📘 *Справка по командам бота*\n\n"
        "🔔 *Команды для Календаря:*\n\n"
        "• *Добавить событие:*\n"
        "  `/addevent`\n"
        "  _Формат:_\n"
        "  `/addevent Название, описание, начало (например 17:00), конец (например 19:00), 5 минут`\n\n"
        "• *Отменить событие:*\n"
        "  `/cancelevent`\n"
        "  _Формат:_\n"
        "  `/cancelevent Название события`\n\n"
        "• *Получить повестку дня:*\n"
        "  `/schedule`\n"
        "  _Формат:_\n"
        "  `/schedule [Сегодня или дата, например, '20 марта 2050 год']`\n\n"
        "• *Установить напоминание:*\n"
        "  `/setreminder`\n"
        "  _Формат:_\n"
        "  `/setreminder Название события, 5 минут`\n\n"
        "📧 *Команды для Почты:*\n\n"
        "• *Отправить письмо:*\n"
        "  `/sendmail`\n"
        "  _Формат:_\n"
        "  `/sendmail email@example.com Тема письма | Текст письма`\n\n"
        "• *Получить входящие письма:*\n"
        "  `/inbox`\n\n"
        "📝 *Команды для Заметок (Google Keep):*\n\n"
        "• *Добавить заметку:*\n"
        "  `/addnote`\n"
        "  _Формат:_\n"
        "  `/addnote Заголовок заметки | Текст заметки`\n\n"
        "ℹ️ *Общие команды:*\n\n"
        "• `/start` – Начало работы с ботом\n"
        "• `/help` – Справка\n"
    )
    update.message.reply_text(help_message, parse_mode="Markdown")

#Команда /sendmail
def sendmail_command(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    command_body = text[len('/sendmail'):].strip()
    if '|' not in command_body:
        update.message.reply_text(
            "Неверный формат команды.\nИспользуйте:\n/sendmail email@example.com Тема письма | Текст письма"
        )
        return

    left_part, message_body = command_body.split('|', 1)
    left_parts = left_part.strip().split(' ', 1)
    if len(left_parts) < 2:
        update.message.reply_text(
            "Неверный формат команды.\nИспользуйте:\n/sendmail email@example.com Тема письма | Текст письма"
        )
        return

    recipient = left_parts[0].strip()
    subject = left_parts[1].strip()
    message_body = message_body.strip()

    from Services.Google_Gmail import send_email
    try:
        send_email(recipient, subject, message_body)
        update.message.reply_text("Письмо успешно отправлено!")
    except Exception as e:
        update.message.reply_text(f"Ошибка при отправке письма: {e}")

#Команда /inbox
def inbox_command(update: Update, context: CallbackContext) -> None:
    from Services.Google_Gmail import get_inbox_messages
    try:
        messages = get_inbox_messages(max_results=5)
        if not messages:
            update.message.reply_text("Входящие сообщения не найдены.")
            return

        response_lines = []
        for i, msg in enumerate(messages, start=1):
            response_lines.append(
                f"{i}. От: {msg['from']}\n   Тема: {msg['subject']}\n   Содержимое: {msg['snippet']}"
            )

        response_text = "\n\n".join(response_lines)
        update.message.reply_text(response_text)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении писем: {e}")

#Команда /addnote
def addnote_command(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    command_body = text[len('/addnote'):].strip()
    if '|' not in command_body:
        update.message.reply_text(
            "Неверный формат команды.\nИспользуйте:\n/addnote Заголовок заметки | Текст заметки"
        )
        return

    title, note_text = command_body.split('|', 1)
    title = title.strip()
    note_text = note_text.strip()

    from Services.Google_Keep import add_note
    try:
        add_note(title, note_text)
        update.message.reply_text("Заметка успешно добавлена!")
    except Exception as e:
        update.message.reply_text(f"Ошибка при добавлении заметки: {e}")


# Команда /addevent
def addevent_command(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    command_body = text[len('/addevent'):].strip()
    parts = [part.strip() for part in command_body.split(',')]
    if len(parts) != 5:
        update.message.reply_text(
            "Неверный формат команды.\n"
            "Пример: /addevent Название, описание, начало 17:00, конец 19:00, 5 минут"
        )
        return

    summary, description, start_time_str, end_time_str, reminder_part = parts

    # Удаляем слова "начало" и "конец", если они есть
    start_time_str = start_time_str.lower().replace("начало", "").strip()
    end_time_str = end_time_str.lower().replace("конец", "").strip()

    # Извлекаем минуты напоминания
    try:
        reminder_minutes = int(reminder_part.split()[0])
    except ValueError:
        update.message.reply_text("Время напоминания должно быть числом (минуты).")
        return

    # Дата события — сегодня
    from datetime import datetime, date
    today_str = date.today().strftime("%Y-%m-%d")
    try:
        start_dt = datetime.strptime(f"{today_str} {start_time_str}", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(f"{today_str} {end_time_str}", "%Y-%m-%d %H:%M")
    except Exception as e:
        update.message.reply_text(f"Ошибка при разборе времени: {e}")
        return

    start_iso = start_dt.isoformat()
    end_iso = end_dt.isoformat()

    from Services.Google_Calendar import add_event
    try:
        event = add_event(
            summary,
            "",  # Пустое поле location
            description,
            start_iso,
            end_iso,
            [{'method': 'popup', 'minutes': reminder_minutes}]
        )
        update.message.reply_text(f"Событие добавлено. ID: {event.get('id')}")
    except Exception as e:
        update.message.reply_text(f"Ошибка при добавлении события: {e}")

# Функция для парсинга даты из естественного языка
def parse_date(input_str: str) -> datetime:
    dt = dateparser.parse(input_str, languages=['ru'])
    if dt is None:
        raise ValueError(f"Не удалось распознать дату из строки: {input_str}")
    return dt

# Команда /schedule
def schedule_command(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    command_body = text[len('/schedule'):].strip()
    from Services.Google_Calendar import get_daily_schedule

    try:
        if not command_body or command_body.lower() == "сегодня":
            date_obj = datetime.now()
        else:
            date_obj = parse_date(command_body)
        # Формируем дату в формате "YYYY-MM-DD"
        date_str = date_obj.strftime("%Y-%m-%d")
        events = get_daily_schedule(date_str=date_str)
        if not events:
            update.message.reply_text(f"На дату {date_str} событий не найдено.")
            return

        response_lines = []
        for ev in events:
            start_iso = ev.get('start', {}).get('dateTime')
            end_iso = ev.get('end', {}).get('dateTime')
            if start_iso and end_iso:
                # Преобразуем ISO-формат к объекту datetime и затем выводим только время
                start_dt = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
                time_str = f"Начало: {start_dt.strftime('%H:%M')}, Конец: {end_dt.strftime('%H:%M')}"
            else:
                time_str = "Время не указано"
            response_lines.append(f"Событие: {ev.get('summary', 'Без названия')}\n{time_str}")
        response_text = "\n\n".join(response_lines)
        update.message.reply_text(response_text)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении повестки дня: {e}")

# Команда /setreminder
def setreminder_command(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    command_body = text[len('/setreminder'):].strip()
    if ',' not in command_body:
        update.message.reply_text("Неверный формат. Используйте:\n/setreminder Название события, 5 минут")
        return

    parts = command_body.split(',', 1)
    event_name = parts[0].strip()
    try:
        reminder_minutes = int(parts[1].strip().split()[0])
    except ValueError:
        update.message.reply_text("Время напоминания должно быть числом (минуты).")
        return

    from Services.Google_Calendar import find_event_by_name, set_reminder
    try:
        events = find_event_by_name(event_name)
        if not events:
            update.message.reply_text("Событие с таким названием не найдено.")
            return
        event_to_update = events[0]
        event_id = event_to_update.get('id')
        updated_event = set_reminder(event_id, reminder_minutes)
        update.message.reply_text(f"Напоминание установлено для события '{updated_event.get('summary')}'.")
    except Exception as e:
        update.message.reply_text(f"Ошибка при установке напоминания: {e}")

# Команда /cancelevent
def cancelevent_command(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    event_name = text[len('/cancelevent'):].strip()
    if not event_name:
        update.message.reply_text("Укажите название события для отмены.")
        return

    from Services.Google_Calendar import find_event_by_name, cancel_event
    try:
        events = find_event_by_name(event_name)
        if not events:
            update.message.reply_text("Событие с таким названием не найдено.")
            return
        event_to_cancel = events[0]
        event_id = event_to_cancel.get('id')
        cancel_event(event_id)
        update.message.reply_text(f"Событие '{event_name}' успешно отменено.")
    except Exception as e:
        update.message.reply_text(f"Ошибка при отмене события: {e}")

#Голосовое сообщение или любое сообщение не команда
def handle_message(update: Update, context: CallbackContext) -> None:
    if update.message.voice:
        from nlp.voice_recognition import process_voice_message
        recognized_text = process_voice_message(update, context)
        if recognized_text:
            update.message.reply_text(f"Распознанный текст: {recognized_text}")
        else:
            update.message.reply_text("Не удалось распознать голосовое сообщение.")
    else:
        update.message.reply_text(
            "Функционал пока не реализован для произвольных сообщений. "
            "Используйте команды /start, /help, /sendmail или /inbox."
        )