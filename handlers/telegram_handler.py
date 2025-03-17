from telegram import Update
from telegram.ext import CallbackContext

def start(update: Update, context: CallbackContext) -> None:
    # Получаем имя пользователя, если оно указано, иначе используем "Пользователь"
    user_first_name = update.effective_user.first_name if update.effective_user.first_name else "Пользователь"
    welcome_message = (
        f"Привет, {user_first_name}! Я твой личный ассистент.\n"
        "Отправь голосовое или текстовое сообщение с командой, и я постараюсь выполнить твою просьбу."
    )
    update.message.reply_text(welcome_message)

def handle_message():
    return None