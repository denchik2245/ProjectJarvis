from telegram import Update
from telegram.ext import CallbackContext


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