import os
import requests
from google.oauth2.credentials import Credentials

"""
Известные проблемы:
 - os.getenv не видит .env, из-за чего выбрасывается исключение на строке 15;
 - Даже имея реквизиты, запрос возвращает статсус 403 Неавторизован
"""


def get_keep_service():
    """Authenticate and return the credentials."""
    credentials_file = os.getenv('GOOGLE_API_CREDENTIALS')
    if not credentials_file:
        raise Exception("Не указан путь к GOOGLE_API_CREDENTIALS")
    creds = Credentials.from_authorized_user_file(credentials_file)
    return creds

#Добавить заметку
# POST https://keep.googleapis.com/v1/notes
def add_note(title: str, text: str) -> str:
    """Make a request to the Google Drive API."""
    creds = get_keep_service()#;
    print(creds.token)
    headers = {
        'Authorization': creds.token
    }
    data = {
        'title': title,
        'text': text
    }
    
    response = requests.post('https://keep.googleapis.com/v1/notes', headers=headers, data=data)
    print(headers)
    if response.status_code == 200:
        return('Заметка создана.')
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")
    
# Получить заметку по названию
# GET https://keep.googleapis.com/v1/{name=notes/*}
def get_note(note: str) -> str:
    creds = get_keep_service()
    headers = {
        'Authorization': creds.token
    }
    params = {
        'name': note
    }
    
    response = requests.get('https://keep.googleapis.com/v1/', headers=headers, params=params)
    if response.status_code == 200:
        return(response)
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")
   
# Удалить заметку по названию
# DELETE https://keep.googleapis.com/v1/{name=notes/*}
def delete_note(note: str) -> str:
    creds = get_keep_service()
    headers = {
        'Authorization': creds.token
    }
    params = {
        'name': note
    }
    
    response = requests.delete('https://keep.googleapis.com/v1/', headers=headers, params=params)
    if response.status_code == 200:
        return(response)
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")


