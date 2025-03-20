import os
import uuid
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from Services.Google_Drive import upload_file_to_drive

# Номер (или несколько номеров) состояния в ConversationHandler
WAITING_FOR_FILES = range(1)

def upload_start(update: Update, context: CallbackContext) -> int:
    """
    Шаг 1: пользователь ввёл /upload – бот переводится в состояние ожидания файлов.
    """
    update.message.reply_text(
        "Пришлите мне файлы (фото, видео или документы). "
        "Когда закончите, введите /done."
    )
    return WAITING_FOR_FILES

def handle_file(update: Update, context: CallbackContext) -> int:
    """
    Шаг 2: каждый раз, когда пользователь присылает фото/видео/документ,
    бот скачивает и загружает на Google Диск.
    """
    msg = update.message

    # Определяем, что именно прислали (фото, видео или документ)
    if msg.photo:
        file_id = msg.photo[-1].file_id
        file_name = str(uuid.uuid4()) + ".jpg"
    elif msg.video:
        file_id = msg.video.file_id
        file_name = str(uuid.uuid4()) + ".mp4"
    elif msg.document:
        file_id = msg.document.file_id
        file_name = msg.document.file_name or (str(uuid.uuid4()) + ".bin")
    else:
        msg.reply_text("Пожалуйста, пришлите фото, видео или документ.")
        return WAITING_FOR_FILES

    # Скачиваем файл во временную директорию
    new_file = context.bot.get_file(file_id)
    new_file.download(custom_path=file_name)

    # Загружаем файл на Google Диск
    try:
        uploaded_file_id = upload_file_to_drive(file_name, file_name)
        msg.reply_text(f"Файл «{file_name}» загружен на Google Диск! (ID: {uploaded_file_id})")
    except Exception as e:
        msg.reply_text(f"Ошибка при загрузке файла: {e}")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

    # Остаёмся в состоянии WAITING_FOR_FILES, чтобы можно было получать ещё файлы
    return WAITING_FOR_FILES

def done_uploading(update: Update, context: CallbackContext) -> int:
    """
    Шаг 3: пользователь вводит /done, завершаем диалог.
    """
    update.message.reply_text("Завершаем загрузку. Спасибо!")
    return ConversationHandler.END