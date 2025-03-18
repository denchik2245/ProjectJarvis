# authorize.py
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# Добавляем области для отправки и чтения писем
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar',
]

def main():
    client_secrets_file = os.path.join('credentials', 'Gmail_credential.json')
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
    creds = flow.run_local_server(port=0)

    # Сохраняем учётные данные в файл
    credentials_path = os.path.join('credentials', 'google_credentials.json')
    with open(credentials_path, 'w') as token:
        token.write(creds.to_json())

    print(f"Авторизация прошла успешно. Учетные данные сохранены в {credentials_path}")

if __name__ == '__main__':
    main()
