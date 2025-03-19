# nlp/command_parser.py

import logging
from telegram import Update
from telegram.ext import CallbackContext

from .voice_recognition import process_voice_message
from .ollama import parse_command_from_text
from Services.Google_Gmail import delete_trash_command  # функция из Gmail-сервиса

logger = logging.getLogger(__name__)

def handle_voice_command(update: Update, context: CallbackContext) -> None:
    """
    Обработка голосового сообщения:
      1) Распознаёт голос в текст.
      2) Отправляет текст в Ollama для определения команды.
      3) Если команда определена как "clear_mailbox_trash", вызывает delete_trash_command.
    """
    recognized_text = process_voice_message(update, context)
    if not recognized_text:
        update.message.reply_text("Не удалось распознать голосовое сообщение. Попробуйте ещё раз.")
        return

    command_data = parse_command_from_text(recognized_text)
    command = command_data.get("command", "unknown")
    arguments = command_data.get("arguments", {})

    logger.info(f"Распознана голосовая команда: {command}, аргументы: {arguments}")

    if command == "clear_mailbox_trash":
        # Вызываем функцию из Services/Google_Gmail, которая уже отправляет ответ пользователю.
        delete_trash_command(update, context)
    else:
        update.message.reply_text(
            f"Команда не распознана или не поддерживается. Распознанный текст: {recognized_text}"
        )
