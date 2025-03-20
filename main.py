import logging
import config

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler
)

# Импортируем общие команды (start, help, обработчик текстовых сообщений)
from handlers.telegram_handler import start, help_command, handle_text_message

# Импортируем ConversationHandler-методы для загрузки в Google Drive
from handlers.GoogleDrive_handler import (
    upload_start,
    handle_file,
    done_uploading,
    WAITING_FOR_FILES
)

# Импортируем команды Gmail
from handlers.Gmail_handler import (
    sendmail_command,
    sendmailat_command,
    senddraft_command,
    inbox_command,
    getunread_command,
    findemail_command,
    delete_spam_command,
    delete_trash_command,
    delete_promo_command,
    getstarred_command
)

# Импортируем команды Google Calendar
from handlers.Calendar_handler import (
    addevent_command,
    cancelevent_command,
    schedule_command,
    setreminder_command
)

# Импортируем команды погоды
from handlers.Weather_handler import (
    weather_command,
    forecast_command
)

# Импортируем команды заметок
from handlers.Notes_handler import addnote_command

# Импортируем голосовой обработчик из nlp/command_parser
from nlp.command_parser import handle_voice_command


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def handle_message(update, context):
    """Обработчик обычных (текст/голос) сообщений, вне сценариев ConversationHandler."""
    if update.message.voice:
        handle_voice_command(update, context)
    else:
        handle_text_message(update, context)


def main():
    updater = Updater(token=config.TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # ---------------------------
    # Регистрируем ConversationHandler для загрузки в Google Drive
    # ---------------------------
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("upload", upload_start)],
        states={
            WAITING_FOR_FILES: [
                MessageHandler(
                    Filters.photo | Filters.video | Filters.document,
                    handle_file
                ),
                CommandHandler("done", done_uploading),
            ],
        },
        fallbacks=[],
    )
    dispatcher.add_handler(conv_handler)

    # ---------------------------
    # Регистрируем остальные команды
    # ---------------------------
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
    dispatcher.add_handler(CommandHandler("weather", weather_command))
    dispatcher.add_handler(CommandHandler("forecast", forecast_command))

    # Обработка всех прочих сообщений (текст и голос)
    dispatcher.add_handler(MessageHandler(Filters.text | Filters.voice, handle_message))

    # Запускаем бота
    updater.start_polling()
    logger.info("Бот запущен!")
    updater.idle()


if __name__ == '__main__':
    main()