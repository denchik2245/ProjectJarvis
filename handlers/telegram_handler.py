from telegram import Update
from telegram.ext import CallbackContext
from datetime import datetime, timedelta, date
import dateparser

from nlp.command_parser import handle_voice_command


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
        "✉️ *Команды для Почты:*\n\n"
        "Отправить письмо\n"
        "`/sendmail email@example.com Тема письма`\n\n"
        "Отправить письмо по расписанию\n"
        "`/sendmailat email@example.com Тема письма | Текст письма | [Время, например, 'Завтра утром' или '20 марта 2025 год, в 14:30']`\n\n"
        "Отправить черновик по заголовку\n"
        "`/senddraft Заголовок черновика`\n\n"
        "Получить 10 последних непрочитанных сообщений\n"
        "`/getunread`\n\n"
        "Найти письмо по заголовку\n"
        "`/findemail Тема письма`\n\n"
        "Получить последние письма из входящих\n"
        "`/inbox`\n\n"
        "Получить 10 последних помеченных сообщений\n"
        "`/getstarred`\n\n"
        "Удалить спам\n"
        "`/deletespam`\n\n"
        "Удалить корзину\n"
        "`/deletetrash`\n\n"
        "Удалить промоакции\n"
        "`/deletepromo`\n\n"
        "📝 *Команды для Заметок (Google Keep):*\n\n"
        "Добавить заметку\n"
        "`/addnote Заголовок заметки | Текст заметки`\n\n"
        "🔔 *Команды для Календаря:*\n\n"
        "Добавить событие\n"
        "`/addevent Название, описание, начало (например 17:00), конец (например 19:00), 5 минут`\n\n"
        "Отменить событие по названию\n"
        "`/cancelevent Название события`\n\n"
        "Получить повестку дня\n"
        "`/schedule [Сегодня или дата, например, '20 марта 2050 год']`\n\n"
        "Установить напоминание для события\n"
        "`/setreminder Название события, 5 минут`\n\n"
        "ℹ️ *Общие команды:*\n\n"
        "Начало работы с ботом\n"
        "`/start`\n\n"
        "Справка\n"
        "`/help`"
    )
    update.message.reply_text(help_message, parse_mode="Markdown")

#Отправить сообщение. Команда /sendmail
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

#Отправка письма по расписанию. Команда /sendmailat
def sendmailat_command(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    parts = text[len('/sendmailat'):].strip().split('|')
    if len(parts) != 3:
        update.message.reply_text("Неверный формат команды.\nИспользуйте:\n/sendmailat email@example.com Тема письма | Текст письма | Время")
        return
    left_part = parts[0].strip()
    message_body = parts[1].strip()
    time_str = parts[2].strip()
    left_parts = left_part.split(' ', 1)
    if len(left_parts) < 2:
        update.message.reply_text("Неверный формат команды.\nИспользуйте:\n/sendmailat email@example.com Тема письма | Текст письма | Время")
        return
    recipient = left_parts[0].strip()
    subject = left_parts[1].strip()
    from Services.Google_Gmail import send_email_at_time
    try:
        send_email_at_time(recipient, subject, message_body, time_str)
        update.message.reply_text("Письмо запланировано к отправке!")
    except Exception as e:
        update.message.reply_text(f"Ошибка при планировании отправки письма: {e}")

#Последние письма из входящих. Команда /inbox
def inbox_command(update: Update, context: CallbackContext) -> None:
    from Services.Google_Gmail import get_inbox_messages
    try:
        messages = get_inbox_messages(max_results=10)
        if not messages:
            update.message.reply_text("Входящие сообщения не найдены.")
            return
        response_lines = []
        for i, msg in enumerate(messages, start=1):
            response_lines.append(
                f"{i}.**От:** {msg['from_name']}\n"
                f"**Почта:** {msg['from_email']}\n"
                f"**Тема:** {msg['subject']}\n"
                f"**Содержание:** {msg['snippet']}"
            )
        response_text = "\n\n".join(response_lines)
        update.message.reply_text(response_text, parse_mode="Markdown")
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении писем: {e}")

# Команда /getunread – 10 последних непрочитанных сообщений
def getunread_command(update: Update, context: CallbackContext) -> None:
    from Services.Google_Gmail import get_unread_messages
    try:
        messages = get_unread_messages(10)
        if not messages:
            update.message.reply_text("Непрочитанных сообщений не найдено.")
            return
        response_lines = []
        for i, msg in enumerate(messages, start=1):
            response_lines.append(
                f"{i}.**От:** {msg['from_name']}\n"
                f"**Почта:** {msg['from_email']}\n"
                f"**Тема:** {msg['subject']}\n"
                f"**Содержание:** {msg['snippet']}"
            )
        response_text = "\n\n".join(response_lines)
        update.message.reply_text(response_text, parse_mode="Markdown")
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении непрочитанных сообщений: {e}")

# Команда /senddraft – отправка черновика по заголовку
def senddraft_command(update: Update, context: CallbackContext) -> None:
    """
    Формат команды:
    /senddraft Заголовок черновика
    Ищет черновик по заголовку и отправляет его.
    """
    text = update.message.text
    draft_subject = text[len('/senddraft'):].strip()
    if not draft_subject:
        update.message.reply_text("Укажите заголовок черновика.\nФормат: /senddraft Заголовок")
        return
    from Services.Google_Gmail import send_draft_by_subject
    try:
        send_draft_by_subject(draft_subject)
        update.message.reply_text("Черновик отправлен!")
    except Exception as e:
        update.message.reply_text(f"Ошибка при отправке черновика: {e}")

# Команда /findemail – поиск письма по заголовку
def findemail_command(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    subject_search = text[len('/findemail'):].strip()
    if not subject_search:
        update.message.reply_text("Укажите часть заголовка для поиска.\nФормат: /findemail Тема письма")
        return
    from Services.Google_Gmail import find_email_by_subject
    try:
        emails = find_email_by_subject(subject_search)
        if not emails:
            update.message.reply_text("Письма с указанным заголовком не найдены.")
            return
        response_lines = []
        for i, email in enumerate(emails, start=1):
            response_lines.append(f"{i}. От: {email['from']}\n   Тема: {email['subject']}\n   Сниппет: {email['snippet']}")
        response_text = "\n\n".join(response_lines)
        update.message.reply_text(response_text)
    except Exception as e:
        update.message.reply_text(f"Ошибка при поиске письма: {e}")

# Команда для удаления сообщений из папки "Спам"
def delete_spam_command(update: Update, context: CallbackContext) -> None:
    from Services.Google_Gmail import get_gmail_service
    try:
        service = get_gmail_service()
        result = service.users().messages().list(userId="me", labelIds=["SPAM"]).execute()
        messages = result.get("messages", [])
        if not messages:
            update.message.reply_text("Нет сообщений в спаме.")
            return
        for msg in messages:
            service.users().messages().delete(userId="me", id=msg["id"]).execute()
        update.message.reply_text(f"Удалено {len(messages)} сообщений из спама.")
    except Exception as e:
        update.message.reply_text(f"Ошибка при удалении спама: {e}")

# Команда для удаления сообщений из папки "Корзина"
def delete_trash_command(update: Update, context: CallbackContext) -> None:
    from Services.Google_Gmail import get_gmail_service
    try:
        service = get_gmail_service()
        result = service.users().messages().list(userId="me", labelIds=["TRASH"]).execute()
        messages = result.get("messages", [])
        if not messages:
            update.message.reply_text("Нет сообщений в корзине.")
            return
        for msg in messages:
            service.users().messages().delete(userId="me", id=msg["id"]).execute()
        update.message.reply_text(f"Удалено {len(messages)} сообщений из корзины.")
    except Exception as e:
        update.message.reply_text(f"Ошибка при удалении корзины: {e}")

# Команда для удаления сообщений из папки "Промоакция"
def delete_promo_command(update: Update, context: CallbackContext) -> None:
    from Services.Google_Gmail import get_gmail_service
    try:
        service = get_gmail_service()
        result = service.users().messages().list(userId="me", labelIds=["CATEGORY_PROMOTIONS"]).execute()
        messages = result.get("messages", [])
        if not messages:
            update.message.reply_text("Нет сообщений в промоакциях.")
            return
        for msg in messages:
            service.users().messages().delete(userId="me", id=msg["id"]).execute()
        update.message.reply_text(f"Удалено {len(messages)} сообщений из промоакций.")
    except Exception as e:
        update.message.reply_text(f"Ошибка при удалении промоакций: {e}")

# Вывод помеченных сообщений
def getstarred_command(update: Update, context: CallbackContext) -> None:
    from Services.Google_Gmail import get_starred_messages
    try:
        messages = get_starred_messages(max_results=10)
        if not messages:
            update.message.reply_text("Нет помеченных сообщений.")
            return
        response_lines = []
        for i, msg in enumerate(messages, start=1):
            response_lines.append(
                f"{i}. От: {msg['from_name']}\n"
                f"   Почта: {msg['from_email']}\n"
                f"   Тема: {msg['subject']}\n"
                f"   Содержание: {msg['snippet']}"
            )
        response_text = "\n\n".join(response_lines)
        update.message.reply_text(response_text)
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении помеченных сообщений: {e}")

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

# Обработка обычных текстовых сообщений
def handle_text_message(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Функционал пока не реализован для произвольных сообщений. "
        "Используйте команды /start, /help и т.д."
    )

# Обработка входящих сообщений: голосовых и текстовых
def handle_message(update: Update, context: CallbackContext) -> None:
    if update.message.voice:
        # Голосовое сообщение обрабатываем через функцию из command_parser
        handle_voice_command(update, context)
    else:
        handle_text_message(update, context)