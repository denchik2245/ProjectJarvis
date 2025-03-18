import os
import gkeepapi
from dotenv import load_dotenv
load_dotenv()

def get_keep_service():
    """
    Авторизуется в Google Keep с использованием gkeepapi.
    Для работы необходимо, чтобы в .env были заданы переменные GKEEP_EMAIL и GKEEP_PASSWORD.
    """
    email = os.getenv('GKEEP_EMAIL')
    password = os.getenv('GKEEP_PASSWORD')
    if not email or not password:
        raise Exception("Не заданы переменные GKEEP_EMAIL и GKEEP_PASSWORD в .env")

    keep = gkeepapi.Keep()
    try:
        keep.login(email, password)
    except Exception as e:
        raise Exception(f"Ошибка при логине в Google Keep: {e}")

    keep.sync()
    return keep

#Добавить заметку
def add_note(title: str, text: str) -> str:
    keep = get_keep_service()
    note = keep.createNote(title, text)
    keep.sync()
    return note.id