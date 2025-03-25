# core/command_dispatcher.py

import logging
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

class CommandDispatcher:
    def __init__(self):
        self.executed_commands = set()
        self.command_handlers = {
            "get_contact_info": self.handle_get_contact_info,
        }

    def dispatch(self, command_data: dict, update: Update, context: CallbackContext, original_text: str) -> None:
        command = command_data.get("command", "unknown")
        arguments = command_data.get("arguments", {})

        logger.info("Распознана голосовая команда: %s, аргументы: %s", command, arguments)

        if command in self.executed_commands:
            return

        handler = self.command_handlers.get(command, self.handle_unknown)
        handler(update, context, arguments, original_text)
        self.executed_commands.add(command)

    def handle_get_contact_info(self, update: Update, context: CallbackContext, args: dict, original_text: str):
        from commands.get_contact_info import get_contact_info_command
        get_contact_info_command(update, args, original_text)

    def handle_unknown(self, update: Update, context: CallbackContext, args: dict, original_text: str):
        update.message.reply_text(
            f"Распознанный текст: {original_text}\nКоманда не распознана или не поддерживается."
        )
