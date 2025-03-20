from telegram import Update
from telegram.ext import CallbackContext

#Команда /addnote
def addnote_command(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    command_body = text[len('/addnote'):].strip()
    if '|' not in command_body:
        update.message.reply_text(
            "Неверный формат команды.\nИспользуйте:\n/addnote Заголовок заметки | Текст заметки"
        )
        return

    title, note_text = command_body.split('|', 1)
    title = title.strip()
    note_text = note_text.strip()

    from Services.Google_Keep import add_note
    try:
        add_note(title, note_text)
        update.message.reply_text("Заметка успешно добавлена!")
    except Exception as e:
        update.message.reply_text(f"Ошибка при добавлении заметки: {e}")