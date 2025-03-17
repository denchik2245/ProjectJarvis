import os
import tempfile
import speech_recognition as sr
from pydub import AudioSegment
from telegram import Update
from telegram.ext import CallbackContext

#Конвертирует аудиофайл из формата OGG в WAV и распознает речь. Возвращает распознанный текст или пустую строку в случае ошибки.
def transcribe_audio(file_path: str) -> str:

    try:
        # Загрузка аудиофайла из формата OGG
        audio = AudioSegment.from_file(file_path, format="ogg")
    except Exception as e:
        print("Ошибка загрузки аудиофайла:", e)
        return ""

    # Создаем временный WAV файл для распознавания
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
        wav_path = wav_file.name
    audio.export(wav_path, format="wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)

    try:
        # Используем Google Speech Recognition для получения текста (язык: русский)
        text = recognizer.recognize_google(audio_data, language="ru-RU")
    except sr.UnknownValueError:
        text = ""
    except sr.RequestError as e:
        text = ""

    os.remove(wav_path)  # Удаляем временный WAV файл
    return text

#Загружает голосовое сообщение из Telegram, сохраняет его во временный файл, распознает речь и возвращает полученный текст
def process_voice_message(update: Update, context: CallbackContext) -> str:

    voice = update.message.voice
    file = voice.get_file()

    # Сохраняем голосовое сообщение во временный файл формата OGG
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_audio_file:
        temp_file_path = temp_audio_file.name
    file.download(custom_path=temp_file_path)

    # Распознаем речь из загруженного файла
    transcription = transcribe_audio(temp_file_path)
    os.remove(temp_file_path)  # Удаляем временный OGG файл

    return transcription
