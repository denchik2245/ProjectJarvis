import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def get_drive_service():
    """
    Создаёт и возвращает сервис Google Drive.
    Требует переменной окружения GOOGLE_API_CREDENTIALS,
    указывающей на файл с сохранёнными учётными данными.
    """
    credentials_file = os.getenv('GOOGLE_API_CREDENTIALS')
    if not credentials_file:
        raise Exception("Не указан путь к GOOGLE_API_CREDENTIALS")

    creds = Credentials.from_authorized_user_file(credentials_file)
    service = build('drive', 'v3', credentials=creds)
    return service


def upload_file_to_drive(file_path: str, file_name: str, folder_id: str = None) -> str:
    """
    Загружает файл на Google Drive.
    :param file_path: Путь к локальному файлу на диске.
    :param file_name: Имя, под которым файл будет сохранён в Google Drive.
    :param folder_id: (опционально) ID папки, в которую загрузить.
    :return: ID загруженного файла в Google Drive.
    """
    service = get_drive_service()

    file_metadata = {
        'name': file_name
    }
    # Если хотим загрузить в какую-то конкретную папку, укажем folder_id
    if folder_id:
        file_metadata['parents'] = [folder_id]

    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return uploaded_file.get('id')
