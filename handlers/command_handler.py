# handlers/command_handler.py

import logging
from telegram import Update
from telegram.ext import CallbackContext
from core.deepseek_client import DeepseekClient
from handlers.voice_recognition import process_voice_message
from core.command_dispatcher import CommandDispatcher

logger = logging.getLogger(__name__)

def handle_voice_command(update: Update, context: CallbackContext) -> None:
    recognized_text = process_voice_message(update, context)
    if not recognized_text:
        update.message.reply_text("Не удалось распознать голосовое сообщение. Попробуйте ещё раз.")
        return

    client = DeepseekClient()
    command_data = client.parse_command(recognized_text)
    dispatcher = CommandDispatcher()
    dispatcher.dispatch(command_data, update, context, recognized_text)