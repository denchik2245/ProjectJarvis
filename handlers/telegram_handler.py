from telegram import Update
from telegram.ext import CallbackContext
from handlers.command_handler import handle_voice_command

#Команда /start
def start(update: Update, context: CallbackContext) -> None:
    user_first_name = update.effective_user.first_name if update.effective_user.first_name else "Пользователь"
    welcome_message = (
        f"Привет, {user_first_name}! Я твой личный ассистент.\n\n"
        "Чтобы посмотреть доступные команды, введи /help:\n"
    )
    update.message.reply_text(welcome_message)

# Команда /help
def help_command(update: Update, context: CallbackContext) -> None:
    help_message = (
        "✉️ *Команды для Почты:*\n\n"
        "Отправить письмо\n"
        "`/sendmail email@example.com Тема письма`\n\n"
        "Отправить письмо по расписанию\n"
        "`/sendmailat email@example.com Тема письма | Текст письма | [Время, например, 'Завтра утром' или '20 марта 2025 год, в 14:30']`\n\n"
        "Отправить черновик по заголовку\n"
        "`/senddraft Заголовок черновика`\n\n"
        "Получить 10 последних непрочитанных сообщений\n"
        "`/getunread`\n\n"
        "Найти письмо по заголовку\n"
        "`/findemail Тема письма`\n\n"
        "Получить последние письма из входящих\n"
        "`/inbox`\n\n"
        "Получить 10 последних помеченных сообщений\n"
        "`/getstarred`\n\n"
        "Удалить спам\n"
        "`/deletespam`\n\n"
        "Удалить корзину\n"
        "`/deletetrash`\n\n"
        "Удалить промоакции\n"
        "`/deletepromo`\n\n"
        "📝 *Команды для Заметок (Google Keep):*\n\n"
        "Добавить заметку\n"
        "`/addnote Заголовок заметки | Текст заметки`\n\n"
        "🔔 *Команды для Календаря:*\n\n"
        "Добавить событие\n"
        "`/addevent Название, описание, начало (например 17:00), конец (например 19:00), 5 минут`\n\n"
        "Отменить событие по названию\n"
        "`/cancelevent Название события`\n\n"
        "Получить повестку дня\n"
        "`/schedule [Сегодня или дата, например, '20 марта 2050 год']`\n\n"
        "Установить напоминание для события\n"
        "`/setreminder Название события, 5 минут`\n\n"
        "💾 *Команды для Google Диска:*\n\n"
        "Загрузить файл на Google Диск\n"
        "`/upload Файл (например, фото, видео или документ)`\n\n"
        "Завершить загрузку\n"
        "`/done`\n\n"
        "🌤️ *Команды для Погоды:*\n\n"
        "Получить текущую погоду в городе\n"
        "`/weather Город`\n\n"
        "Получить прогноз погоды на несколько дней\n"
        "`/forecast Город [количество_дней]`\n\n"
        "ℹ️ *Общие команды:*\n\n"
        "Начало работы с ботом\n"
        "`/start`\n\n"
        "Справка\n"
        "`/help`"
    )
    update.message.reply_text(help_message, parse_mode="Markdown")

# Обработка обычных текстовых сообщений
def handle_text_message(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Функционал пока не реализован для произвольных сообщений. "
        "Используйте команды /start, /help и т.д."
    )


# Обработка входящих сообщений: голосовых и текстовых
def handle_message(update: Update, context: CallbackContext) -> None:
    if update.message.voice:
        # Голосовое сообщение обрабатываем через функцию из command_parser
        handle_voice_command(update, context)
    else:
        handle_text_message(update, context)