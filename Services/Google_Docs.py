import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_docs_service():
    credentials_file = os.getenv("GOOGLE_API_CREDENTIALS")
    if not credentials_file:
        raise Exception("Не указан путь к GOOGLE_API_CREDENTIALS")
    creds = Credentials.from_authorized_user_file(credentials_file)
    docs_service = build('docs', 'v1', credentials=creds)
    return docs_service


def get_drive_service():
    credentials_file = os.getenv("GOOGLE_API_CREDENTIALS")
    if not credentials_file:
        raise Exception("Не указан путь к GOOGLE_API_CREDENTIALS")
    creds = Credentials.from_authorized_user_file(credentials_file)
    drive_service = build('drive', 'v3', credentials=creds)
    return drive_service


def add_doc(title: str, content: str) -> dict:
    """
    Создает новый документ Google Docs с заданным заголовком и содержимым.
    """
    docs_service = get_docs_service()
    # Создаем документ с указанным заголовком
    document = {'title': title}
    doc = docs_service.documents().create(body=document).execute()
    document_id = doc.get('documentId')

    # Вставляем текст в документ (начиная с позиции 1)
    requests = [{
        'insertText': {
            'location': {'index': 1},
            'text': content
        }
    }]
    docs_service.documents().batchUpdate(
        documentId=document_id, body={'requests': requests}
    ).execute()

    return {"documentId": document_id, "title": title, "content": content}


def find_doc_by_title(title: str) -> dict:
    """
    Ищет документ Google Docs по заголовку (точное совпадение) и возвращает его данные.
    """
    drive_service = get_drive_service()
    # Поиск документов с типом Google Docs и заданным именем
    query = f"mimeType='application/vnd.google-apps.document' and name = '{title}'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    if not files:
        raise Exception("Документ с указанным заголовком не найден")
    file = files[0]
    document_id = file['id']

    docs_service = get_docs_service()
    doc = docs_service.documents().get(documentId=document_id).execute()

    # Извлекаем текст из структуры документа
    content = ""
    for element in doc.get('body', {}).get('content', []):
        if 'paragraph' in element:
            for el in element['paragraph'].get('elements', []):
                text_run = el.get('textRun')
                if text_run and 'content' in text_run:
                    content += text_run['content']
    return {"documentId": document_id, "title": file['name'], "content": content}


def delete_doc_by_title(title: str) -> bool:
    """
    Удаляет документ Google Docs по заголовку (точное совпадение).
    """
    drive_service = get_drive_service()
    query = f"mimeType='application/vnd.google-apps.document' and name = '{title}'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    if not files:
        raise Exception("Документ с указанным заголовком не найден")
    file_id = files[0]['id']
    drive_service.files().delete(fileId=file_id).execute()
    return True
