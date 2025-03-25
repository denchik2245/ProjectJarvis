# handlers/voice_recognition.py

import os
import tempfile
import whisper
from pydub import AudioSegment
from telegram import Update
from telegram.ext import CallbackContext
import logging

logger = logging.getLogger(__name__)

# Загружаем модель Whisper один раз
model = whisper.load_model("large")

def transcribe_audio(file_path: str) -> str:
    """
    Преобразует аудиофайл (OGG) в текст с использованием модели Whisper.
    """
    try:
        audio = AudioSegment.from_file(file_path, format="ogg")
    except Exception as e:
        logger.error("Ошибка загрузки аудиофайла: %s", e)
        return ""

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
        wav_path = wav_file.name
    audio.export(wav_path, format="wav")

    try:
        result = model.transcribe(wav_path, language="ru")
        text = result.get("text", "").strip()
    except Exception as e:
        logger.error("Ошибка распознавания аудио: %s", e)
        text = ""
    finally:
        os.remove(wav_path)
    return text

def process_voice_message(update: Update, context: CallbackContext) -> str:
    """
    Обрабатывает голосовое сообщение из Telegram и возвращает распознанный текст.
    """
    voice = update.message.voice
    file = voice.get_file()

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_audio_file:
        temp_file_path = temp_audio_file.name
    file.download(custom_path=temp_file_path)

    transcription = transcribe_audio(temp_file_path)
    os.remove(temp_file_path)
    return transcription
