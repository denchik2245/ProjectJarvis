from telegram import Update
from telegram.ext import CallbackContext
from Services.Google_Docs import add_doc, delete_doc_by_title, find_doc_by_title

# Команда /adddoc – создание документа с заголовком и содержимым.
# Формат команды: /adddoc Заголовок, Содержимое документа
def adddoc_command(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    command_body = text[len('/adddoc'):].strip()
    parts = [part.strip() for part in command_body.split(',', 1)]
    if len(parts) != 2:
        update.message.reply_text(
            "Неверный формат команды.\nПример: /adddoc Заголовок, Содержимое документа"
        )
        return
    title, content = parts
    try:
        doc = add_doc(title, content)
        update.message.reply_text(
            f"Документ создан:\nЗаголовок: {doc.get('title')}\nID: {doc.get('documentId')}"
        )
    except Exception as e:
        update.message.reply_text(f"Ошибка при создании документа: {e}")

# Команда /deletedoc – удаление документа по заголовку.
# Формат команды: /deletedoc Заголовок документа
def deletedoc_command(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    command_body = text[len('/deletedoc'):].strip()
    if not command_body:
        update.message.reply_text("Укажите заголовок документа для удаления.")
        return
    title = command_body
    try:
        delete_doc_by_title(title)
        update.message.reply_text(f"Документ '{title}' удален.")
    except Exception as e:
        update.message.reply_text(f"Ошибка при удалении документа: {e}")

# Команда /finddoc – поиск документа по заголовку.
# Формат команды: /finddoc Заголовок документа
def finddoc_command(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    command_body = text[len('/finddoc'):].strip()
    if not command_body:
        update.message.reply_text("Укажите заголовок документа для поиска.")
        return
    title = command_body
    try:
        doc = find_doc_by_title(title)
        message = (
            f"Найденный документ:\nЗаголовок: {doc.get('title')}\nСодержимое:\n{doc.get('content')}"
        )
        update.message.reply_text(message)
    except Exception as e:
        update.message.reply_text(f"Ошибка при поиске документа: {e}")
