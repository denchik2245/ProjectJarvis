import base64
import os
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def get_gmail_service():
    credentials_file = os.getenv('GOOGLE_API_CREDENTIALS')
    if not credentials_file:
        raise Exception("Не указан путь к GOOGLE_API_CREDENTIALS")
    creds = Credentials.from_authorized_user_file(credentials_file)
    service = build('gmail', 'v1', credentials=creds)
    return service

#Создать сообщение
def create_message(sender: str, to: str, subject: str, message_text: str) -> dict:
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

#Отправить сообщение
def send_email(recipient: str, subject: str, message_text: str) -> dict:
    service = get_gmail_service()
    sender = os.getenv('GMAIL_SENDER')
    if not sender:
        raise Exception("Не указан адрес отправителя (GMAIL_SENDER)")
    message = create_message(sender, recipient, subject, message_text)
    sent_message = service.users().messages().send(userId="me", body=message).execute()
    return sent_message

#Поучить последние сообщения
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
        single_msg = service.users().messages().get(userId='me', id=msg_id, format='metadata').execute()

        # Извлекаем сниппет (короткий отрывок письма)
        snippet = single_msg.get('snippet', '')

        # Извлекаем тему и отправителя из заголовков
        headers = single_msg.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')

        messages_info.append({
            'subject': subject,
            'from': from_addr,
            'snippet': snippet
        })

    return messages_info