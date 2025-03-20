# nlp/command_parser.py

import logging
from telegram import Update
from telegram.ext import CallbackContext

from .voice_recognition import process_voice_message
from .ollama import parse_command_from_text

# Импортируем функции из Google_Gmail
from Services.Google_Gmail import delete_trash_command, delete_spam_command, delete_promo_command

logger = logging.getLogger(__name__)

def handle_voice_command(update: Update, context: CallbackContext) -> None:
    """
    Обработка голосового сообщения:
      1) Распознаёт голос в текст.
      2) Отправляет текст в Ollama для определения команды.
      3) В зависимости от распознанной команды вызывает нужную функцию:
         - clear_mailbox_trash → delete_trash_command
         - delete_spam → delete_spam_command
         - delete_promo → delete_promo_command
         - и т.д.
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
        delete_trash_command(update, context)
    elif command == "delete_spam":
        delete_spam_command(update, context)
    elif command == "delete_promo":
        delete_promo_command(update, context)
    elif command == "send_message":
        # Пример обработки другой команды (если необходимо)
        to = arguments.get("to")
        content = arguments.get("content")
        if to and content:
            from Services.Google_Contacts import send_message
            send_message(to, content)
            update.message.reply_text(f"Сообщение отправлено {to}: {content}")
        else:
            update.message.reply_text("Не хватает аргументов для отправки сообщения.")
    else:
        update.message.reply_text(
            f"Команда не распознана или не поддерживается. Распознанный текст: {recognized_text}"
        )
