import os
import tempfile
import whisper
from pydub import AudioSegment
from telegram import Update
from telegram.ext import CallbackContext

# Загружаем модель Whisper (можно выбрать другую модель, например "small" или "medium")
model = whisper.load_model("large")

# Функция для распознавания аудио с использованием Whisper
def transcribe_audio(file_path: str) -> str:
    try:
        # Загружаем аудиофайл OGG с помощью pydub
        audio = AudioSegment.from_file(file_path, format="ogg")
    except Exception as e:
        print("Ошибка загрузки аудиофайла:", e)
        return ""

    # Создаем временный WAV файл для передачи в Whisper (необязательно, но наглядно)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
        wav_path = wav_file.name
    audio.export(wav_path, format="wav")

    try:
        # Распознаем аудио с помощью Whisper, указываем язык "ru" для русского
        result = model.transcribe(wav_path, language="ru")
        text = result.get("text", "").strip()
    except Exception as e:
        print("Ошибка распознавания аудио:", e)
        text = ""

    os.remove(wav_path)  # Удаляем временный WAV файл
    return text

# Функция для обработки голосового сообщения Telegram
def process_voice_message(update: Update, context: CallbackContext) -> str:
    voice = update.message.voice
    file = voice.get_file()

    # Сохраняем голосовое сообщение во временный файл в формате OGG
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_audio_file:
        temp_file_path = temp_audio_file.name
    file.download(custom_path=temp_file_path)

    # Распознаем речь из файла с помощью Whisper
    transcription = transcribe_audio(temp_file_path)
    os.remove(temp_file_path)  # Удаляем временный OGG файл

    return transcription
