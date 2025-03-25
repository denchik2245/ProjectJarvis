from telegram import Update
from telegram.ext import CallbackContext
from Services.Google_Contacts import get_contact_by_identifier, get_contacts_by_company, add_contact, delete_contact

# Команда /getcontact – вывод содержимого контакта по идентификатору (имя, телефон или email)
def getcontact_command(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    command_body = text[len('/getcontact'):].strip()
    if not command_body:
        update.message.reply_text("Укажите имя, номер телефона или email для поиска контакта.")
        return

    identifier = command_body
    contact = get_contact_by_identifier(identifier)
    if not contact:
        update.message.reply_text("Контакт не найден.")
        return

    # Формирование сообщения с данными контакта
    message = "Данные контакта:\n"
    if 'names' in contact:
        names = [name.get('displayName', '') for name in contact['names']]
        message += f"Имя: {', '.join(names)}\n"
    if 'phoneNumbers' in contact:
        phones = [phone.get('value', '') for phone in contact['phoneNumbers']]
        message += f"Телефон: {', '.join(phones)}\n"
    if 'emailAddresses' in contact:
        emails = [email.get('value', '') for email in contact['emailAddresses']]
        message += f"Email: {', '.join(emails)}\n"
    if 'organizations' in contact:
        orgs = []
        for org in contact['organizations']:
            org_str = org.get('name', '')
            if 'title' in org:
                org_str += f" ({org.get('title')})"
            orgs.append(org_str)
        message += f"Компания: {', '.join(orgs)}\n"
    if 'birthdays' in contact:
        bdays = []
        for bd in contact['birthdays']:
            date_info = bd.get('date', {})
            if date_info:
                bdays.append(f"{date_info.get('year', '----')}-{date_info.get('month', '--')}-{date_info.get('day', '--')}")
        message += f"День рождения: {', '.join(bdays)}\n"
    update.message.reply_text(message)

# Команда /getcontactsbycompany – вывод всех контактов, у которых указана данная компания
def getcontactsbycompany_command(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    command_body = text[len('/getcontactsbycompany'):].strip()
    if not command_body:
        update.message.reply_text("Укажите название компании.")
        return

    company = command_body
    contacts = get_contacts_by_company(company)
    if not contacts:
        update.message.reply_text("Контакты с указанной компанией не найдены.")
        return

    message = f"Контакты компании '{company}':\n"
    for contact in contacts:
        if 'names' in contact:
            names = [name.get('displayName', '') for name in contact['names']]
            message += f"Имя: {', '.join(names)}\n"
        if 'phoneNumbers' in contact:
            phones = [phone.get('value', '') for phone in contact['phoneNumbers']]
            message += f"Телефон: {', '.join(phones)}\n"
        if 'emailAddresses' in contact:
            emails = [email.get('value', '') for email in contact['emailAddresses']]
            message += f"Email: {', '.join(emails)}\n"
        message += "-------------------------\n"
    update.message.reply_text(message)

# Команда /addcontact – добавление нового контакта
# Формат команды:
# /addcontact Имя, номер телефона[, Фамилия][, Компания][, Должность][, Email][, День рождения(YYYY-MM-DD)]
def addcontact_command(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    command_body = text[len('/addcontact'):].strip()
    parts = [part.strip() for part in command_body.split(',')]
    if len(parts) < 2:
        update.message.reply_text(
            "Неверный формат команды.\n"
            "Пример: /addcontact Имя, номер телефона, Фамилия, Компания, Должность, email, 1990-01-01"
        )
        return

    # Обязательные параметры
    first_name = parts[0]
    phone_number = parts[1]

    # Необязательные параметры
    last_name = parts[2] if len(parts) > 2 and parts[2] else None
    company = parts[3] if len(parts) > 3 and parts[3] else None
    job_title = parts[4] if len(parts) > 4 and parts[4] else None
    email = parts[5] if len(parts) > 5 and parts[5] else None
    birthday = parts[6] if len(parts) > 6 and parts[6] else None

    try:
        contact = add_contact(first_name, phone_number, last_name, company, job_title, email, birthday)
        update.message.reply_text(f"Контакт добавлен. ResourceName: {contact.get('resourceName')}")
    except Exception as e:
        update.message.reply_text(f"Ошибка при добавлении контакта: {e}")

# Команда /deletecontact – удаление контакта по имени, номеру телефона или email
def deletecontact_command(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    command_body = text[len('/deletecontact'):].strip()
    if not command_body:
        update.message.reply_text("Укажите имя, номер телефона или email для удаления контакта.")
        return

    identifier = command_body
    try:
        result = delete_contact(identifier)
        if result:
            update.message.reply_text("Контакт успешно удален.")
        else:
            update.message.reply_text("Не удалось удалить контакт.")
    except Exception as e:
        update.message.reply_text(f"Ошибка при удалении контакта: {e}")
