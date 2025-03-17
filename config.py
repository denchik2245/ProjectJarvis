import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Telegram API
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Google API настройки
GOOGLE_API_CREDENTIALS = os.getenv("GOOGLE_API_CREDENTIALS")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Путь к модели для голосового распознавания
VOICE_MODEL_PATH = os.getenv("VOICE_MODEL_PATH")

# Дополнительные настройки (например, режим отладки)
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "t"]
