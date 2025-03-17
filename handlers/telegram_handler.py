from telegram import Update
from telegram.ext import CallbackContext
from nlp.voice_recognition import process_voice_message


#Команда /start
def start(update: Update, context: CallbackContext) -> None:
    user_first_name = update.effective_user.first_name if update.effective_user.first_name else "Пользователь"
    welcome_message = (
        f"Привет, {user_first_name}! Я твой личный ассистент.\n"
        "Отправь голосовое или текстовое сообщение с командой, и я постараюсь выполнить твою просьбу."
    )
    update.message.reply_text(welcome_message)

#Команда /help
def help_command(update: Update, context: CallbackContext) -> None:
    help_message = (
        "Доступные команды:\n"
        "/start - Начало работы с ботом\n"
        "/help - Получение справки\n\n"
        "Пока что любые другие сообщения возвращают временную заглушку."
    )
    update.message.reply_text(help_message)

#Временная заглушка под любые сообщения
def handle_message(update: Update, context: CallbackContext) -> None:
    if update.message.voice:
        recognized_text = process_voice_message(update, context)
        if recognized_text:
            response = f"Распознанный текст: {recognized_text}"
        else:
            response = "Не удалось распознать голосовое сообщение."
    else:
        response = "Функционал пока не реализован. Пожалуйста, используйте команды /start или /help для получения информации."
    update.message.reply_text(response)