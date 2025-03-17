from telegram import Update
from telegram.ext import CallbackContext
from nlp.voice_recognition import process_voice_message  # если используется голосовое распознавание

def start(update: Update, context: CallbackContext) -> None:
    user_first_name = update.effective_user.first_name if update.effective_user.first_name else "Пользователь"
    welcome_message = (
        f"Привет, {user_first_name}! Я твой личный ассистент.\n"
        "Отправь голосовое или текстовое сообщение с командой, и я постараюсь выполнить твою просьбу.\n"
        "Для отправки письма используй команду:\n"
        "/sendmail email@example.com Тема письма | Текст письма"
    )
    update.message.reply_text(welcome_message)

def help_command(update: Update, context: CallbackContext) -> None:
    help_message = (
        "Доступные команды:\n"
        "/start - Начало работы с ботом\n"
        "/help - Справка по командам\n"
        "/sendmail email@example.com Тема письма | Текст письма - отправка письма на указанный адрес\n\n"
        "Пока что любые другие сообщения возвращают временную заглушку."
    )
    update.message.reply_text(help_message)

def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    if text and text.startswith('/sendmail'):
        # Ожидаемый формат:
        # /sendmail email@example.com Тема письма | Текст письма
        try:
            command_body = text[len('/sendmail'):].strip()
            if '|' not in command_body:
                update.message.reply_text("Неверный формат команды.\nИспользуйте: /sendmail email@example.com Тема письма | Текст письма")
                return

            left_part, message_body = command_body.split('|', 1)
            left_parts = left_part.strip().split(' ', 1)
            if len(left_parts) < 2:
                update.message.reply_text("Неверный формат команды.\nИспользуйте: /sendmail email@example.com Тема письма | Текст письма")
                return

            recipient = left_parts[0].strip()
            subject = left_parts[1].strip()
            message_body = message_body.strip()

            from Services.Google_Gmail import send_email
            send_email(recipient, subject, message_body)
            update.message.reply_text("Письмо успешно отправлено!")
        except Exception as e:
            update.message.reply_text(f"Ошибка при отправке письма: {e}")
    elif update.message.voice:
        # Если пришло голосовое сообщение, распознаем его
        from nlp.voice_recognition import process_voice_message
        recognized_text = process_voice_message(update, context)
        if recognized_text:
            update.message.reply_text(f"Распознанный текст: {recognized_text}")
        else:
            update.message.reply_text("Не удалось распознать голосовое сообщение.")
    else:
        update.message.reply_text("Функционал пока не реализован. Используйте команды /start, /help или /sendmail.")
