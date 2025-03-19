import base64
import os
import re
import threading
import dateparser
from datetime import datetime
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from telegram import Update
from telegram.ext import CallbackContext

# Получить доступ к Gmail
def get_gmail_service():
    credentials_file = os.getenv('GOOGLE_API_CREDENTIALS')
    if not credentials_file:
        raise Exception("Не указан путь к GOOGLE_API_CREDENTIALS")
    creds = Credentials.from_authorized_user_file(credentials_file)
    service = build('gmail', 'v1', credentials=creds)
    return service

# Создать письмо
def create_message(sender: str, to: str, subject: str, message_text: str) -> dict:
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

# Отправить письмо
def send_email(recipient: str, subject: str, message_text: str) -> dict:
    service = get_gmail_service()
    sender = os.getenv('GMAIL_SENDER')
    if not sender:
        raise Exception("Не указан адрес отправителя (GMAIL_SENDER)")
    message = create_message(sender, recipient, subject, message_text)
    sent_message = service.users().messages().send(userId="me", body=message).execute()
    return sent_message

# Отправить письмо в заданное время
def send_email_at_time(recipient: str, subject: str, message_text: str, send_time_str: str):
    parsed_time = dateparser.parse(send_time_str, languages=['ru'])
    if parsed_time is None:
        raise Exception(f"Не удалось распознать время: {send_time_str}")
    delay = (parsed_time - datetime.now()).total_seconds()
    if delay < 0:
        raise Exception("Указанное время уже прошло.")
    timer = threading.Timer(delay, lambda: send_email(recipient, subject, message_text))
    timer.start()
    return timer

# Получить черновики
def get_drafts() -> list:
    service = get_gmail_service()
    drafts_result = service.users().drafts().list(userId="me").execute()
    drafts = drafts_result.get('drafts', [])
    return drafts

# Отправить черновик по заголовку
def send_draft_by_subject(draft_subject: str) -> dict:
    service = get_gmail_service()
    drafts = get_drafts()
    for draft in drafts:
        draft_id = draft.get('id')
        full_draft = service.users().drafts().get(userId="me", id=draft_id, format="full").execute()
        headers = full_draft.get("message", {}).get("payload", {}).get("headers", [])
        for header in headers:
            if header.get("name", "").lower() == "subject" and header.get("value", "").lower() == draft_subject.lower():
                sent = service.users().drafts().send(
                    userId="me",
                    body={"id": draft_id, "message": full_draft.get("message")}
                ).execute()
                return sent
    raise Exception("Черновик с указанным заголовком не найден.")

# Получить базовую информацию о последних письмах из входящих
def get_inbox_messages(max_results: int = 10) -> list:
    service = get_gmail_service()
    result = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        maxResults=max_results
    ).execute()

    messages_info = []
    messages = result.get('messages', [])

    for msg in messages:
        msg_id = msg['id']
        msg_details = get_message_details(msg_id)
        messages_info.append(msg_details)

    return messages_info

# Функция для получения детальной информации о письме по его ID
def get_message_details(msg_id: str) -> dict:
    service = get_gmail_service()
    full_msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    headers = full_msg.get("payload", {}).get("headers", [])

    subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "No Subject")
    from_header = next((h["value"] for h in headers if h["name"].lower() == "from"), "Unknown Sender")

    match = re.search(r'<(.+?)>', from_header)
    if match:
        from_email = match.group(1)
        from_name = from_header.split('<')[0].strip().strip('"')
    else:
        from_email = from_header
        from_name = from_header

    snippet = full_msg.get("snippet", "")
    payload = full_msg.get("payload", {})
    content = ""
    attachments = []

    if payload.get("parts"):
        for part in payload["parts"]:
            mime_type = part.get("mimeType")
            filename = part.get("filename", "")
            if filename:
                attachments.append(filename)
            else:
                if mime_type == "text/plain":
                    data = part.get("body", {}).get("data")
                    if data:
                        try:
                            text = base64.urlsafe_b64decode(data.encode()).decode()
                            content += text
                        except Exception:
                            pass
                elif mime_type == "text/html" and not content:
                    data = part.get("body", {}).get("data")
                    if data:
                        try:
                            html = base64.urlsafe_b64decode(data.encode()).decode()
                            content += html
                        except Exception:
                            pass
    else:
        data = payload.get("body", {}).get("data")
        if data:
            try:
                content = base64.urlsafe_b64decode(data.encode()).decode()
            except Exception:
                content = "Не удалось декодировать содержимое сообщения."

    return {
        "id": msg_id,
        "from": from_header,
        "from_name": from_name,
        "from_email": from_email,
        "subject": subject,
        "snippet": snippet,
        "content": content,
        "attachments": attachments
    }

# Выводит на экран информацию о письмах в удобном формате
def print_messages(messages: list):
    for i, msg in enumerate(messages, start=1):
        print(f"{i}. От: {msg['from_name']}")
        print(f"Почта: {msg['from_email']}")
        print(f"Тема: {msg['subject']}")
        print(f"Содержание: {msg['snippet']}")
        print()

# Получить непрочитанные письма
def get_unread_messages(max_results: int = 10) -> list:
    service = get_gmail_service()
    result = service.users().messages().list(
        userId='me',
        labelIds=['UNREAD'],
        maxResults=max_results
    ).execute()
    messages = result.get("messages", [])
    unread_messages = []
    for msg in messages:
        msg_id = msg.get("id")
        # Используем функцию для получения детальной информации о сообщении
        msg_details = get_message_details(msg_id)
        unread_messages.append(msg_details)
    return unread_messages

# Получить помеченные сообщения
def get_starred_messages(max_results: int = 10) -> list:
    service = get_gmail_service()
    result = service.users().messages().list(
        userId='me',
        labelIds=['STARRED'],
        maxResults=max_results
    ).execute()
    messages = result.get("messages", [])
    starred_messages = []
    for msg in messages:
        msg_id = msg.get("id")
        msg_details = get_message_details(msg_id)
        starred_messages.append(msg_details)
    return starred_messages

# Получить письмо по заголовку
def find_email_by_subject(subject_search: str) -> list:
    service = get_gmail_service()
    query = f"subject:{subject_search}"
    result = service.users().messages().list(userId="me", q=query, maxResults=10).execute()
    messages = result.get("messages", [])
    found_emails = []
    for msg in messages:
        msg_details = get_message_details(msg.get("id"))
        # Проверяем, что искомая подстрока действительно содержится в теме
        if subject_search.lower() in msg_details.get("subject", "").lower():
            found_emails.append(msg_details)
    return found_emails

# Удаления сообщений из папки "Спам"
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

# Удаления сообщений из папки "Корзина"
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

# Удаления сообщений из папки "Промоакция"
def delete_promo_command(update: Update, context: CallbackContext) -> None:
    from Services.Google_Gmail import get_gmail_service
    try:
        service = get_gmail_service()
        # Gmail использует метку CATEGORY_PROMOTIONS для промоакций
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