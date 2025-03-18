import os
import gkeepapi
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

def get_keep_service_cookie():
    """
    Авторизуется в Google Keep, используя сохранённые cookies.
    Для этого необходимо, чтобы в .env была указана переменная GKEEP_COOKIE_FILE,
    содержащая путь к файлу с cookies (например, './credentials/keep_cookies.txt').
    """
    cookie_file = os.getenv('GKEEP_COOKIE_FILE', './credentials/keep_cookies.txt')

    if not os.path.exists(cookie_file):
        raise Exception(f"Файл cookies не найден: {cookie_file}")

    with open(cookie_file, 'r') as f:
        cookies = f.read().strip()

    keep = gkeepapi.Keep()
    try:
        keep.resume(cookies)
    except Exception as e:
        raise Exception(f"Ошибка при восстановлении сессии с помощью cookies: {e}")

    keep.sync()
    return keep


def add_note_cookie(title: str, text: str) -> str:
    """
    Создаёт заметку в Google Keep, используя авторизацию через cookies.
    Возвращает идентификатор созданной заметки.
    """
    keep = get_keep_service_cookie()
    note = keep.createNote(title, text)
    keep.sync()
    return note.id


if __name__ == '__main__':
    # Пример использования: добавление тестовой заметки
    title = "Тестовая заметка"
    text = "Это тестовая заметка, созданная через cookie авторизацию."
    try:
        note_id = add_note_cookie(title, text)
        print(f"Заметка успешно добавлена. ID: {note_id}")
    except Exception as e:
        print(f"Ошибка: {e}")
