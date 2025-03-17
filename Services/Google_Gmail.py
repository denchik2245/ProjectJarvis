import base64
import os
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def get_gmail_service():
    """
    Загружает сохранённые авторизационные данные и создаёт объект сервиса для работы с Gmail API.
    """
    credentials_file = os.getenv('GOOGLE_API_CREDENTIALS')
    if not credentials_file:
        raise Exception("Не указан путь к GOOGLE_API_CREDENTIALS")
    creds = Credentials.from_authorized_user_file(credentials_file)
    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender: str, to: str, subject: str, message_text: str) -> dict:
    """
    Формирует MIME сообщение и кодирует его в формат base64 для передачи в Gmail API.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_email(recipient: str, subject: str, message_text: str) -> dict:
    """
    Отправляет письмо на указанный адрес.
    """
    service = get_gmail_service()
    sender = os.getenv('GMAIL_SENDER')
    if not sender:
        raise Exception("Не указан адрес отправителя (GMAIL_SENDER)")
    message = create_message(sender, recipient, subject, message_text)
    sent_message = service.users().messages().send(userId="me", body=message).execute()
    return sent_message
