import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import config
from handlers.telegram_handler import start, help_command, handle_message

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    updater = Updater(token=config.TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Обработчик для всех остальных текстовых и голосовых сообщений
    dispatcher.add_handler(MessageHandler(Filters.text | Filters.voice, handle_message))

    updater.start_polling()
    logger.info("Бот запущен!")
    updater.idle()


if __name__ == '__main__':
    main()