import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import config
from handlers.telegram_handler import (
    start,
    help_command,
    sendmail_command,
    sendmailat_command,
    senddraft_command,
    inbox_command,
    getunread_command,
    findemail_command,
    addnote_command,
    addevent_command,
    cancelevent_command,
    schedule_command,
    setreminder_command,
    handle_message,
    delete_spam_command,
    delete_trash_command,
    delete_promo_command,
    getstarred_command
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    updater = Updater(token=config.TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Регистрируем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("sendmail", sendmail_command))
    dispatcher.add_handler(CommandHandler("sendmailat", sendmailat_command))
    dispatcher.add_handler(CommandHandler("senddraft", senddraft_command))
    dispatcher.add_handler(CommandHandler("inbox", inbox_command))
    dispatcher.add_handler(CommandHandler("getunread", getunread_command))
    dispatcher.add_handler(CommandHandler("findemail", findemail_command))
    dispatcher.add_handler(CommandHandler("addnote", addnote_command))
    dispatcher.add_handler(CommandHandler("addevent", addevent_command))
    dispatcher.add_handler(CommandHandler("cancelevent", cancelevent_command))
    dispatcher.add_handler(CommandHandler("schedule", schedule_command))
    dispatcher.add_handler(CommandHandler("setreminder", setreminder_command))
    dispatcher.add_handler(CommandHandler("deletespam", delete_spam_command))
    dispatcher.add_handler(CommandHandler("deletetrash", delete_trash_command))
    dispatcher.add_handler(CommandHandler("deletepromo", delete_promo_command))
    dispatcher.add_handler(CommandHandler("getstarred", getstarred_command))

    # Обработка любых нераспознанных сообщений (текст и голос)
    dispatcher.add_handler(MessageHandler(Filters.text | Filters.voice, handle_message))

    updater.start_polling()
    logger.info("Бот запущен!")
    updater.idle()

if __name__ == '__main__':
    main()
