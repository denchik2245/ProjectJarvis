import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def get_contacts_service():
    credentials_file = os.getenv("GOOGLE_API_CREDENTIALS")
    if not credentials_file:
        raise Exception("Не указан путь к GOOGLE_API_CREDENTIALS")
    creds = Credentials.from_authorized_user_file(credentials_file)
    service = build('people', 'v1', credentials=creds)
    return service


def get_all_contacts() -> list:
    """
    Возвращает список всех контактов с нужными полями.
    """
    service = get_contacts_service()
    results = service.people().connections().list(
        resourceName='people/me',
        personFields='names,emailAddresses,phoneNumbers,organizations,birthdays'
    ).execute()
    connections = results.get('connections', [])
    return connections


def get_contact_by_identifier(identifier: str) -> dict:
    """
    Ищет и возвращает первый найденный контакт по имени, номеру телефона или электронной почте.
    """
    contacts = get_all_contacts()
    for person in contacts:
        # Поиск по имени
        if 'names' in person:
            for name in person['names']:
                if identifier.lower() in name.get('displayName', '').lower():
                    return person
        # Поиск по номеру телефона
        if 'phoneNumbers' in person:
            for phone in person['phoneNumbers']:
                if identifier in phone.get('value', ''):
                    return person
        # Поиск по электронной почте
        if 'emailAddresses' in person:
            for email in person['emailAddresses']:
                if identifier.lower() in email.get('value', '').lower():
                    return person
    return None


def get_contacts_by_company(company: str) -> list:
    """
    Выводит все контакты, в которых в поле организаций содержится название указанной компании.
    """
    contacts = get_all_contacts()
    filtered = []
    for person in contacts:
        if 'organizations' in person:
            for org in person['organizations']:
                if 'name' in org and company.lower() in org['name'].lower():
                    filtered.append(person)
                    break
    return filtered


def add_contact(first_name: str, phone_number: str, last_name: str = None, company: str = None,
                job_title: str = None, email: str = None, birthday: str = None) -> dict:
    service = get_contacts_service()
    new_contact = {}

    # Формирование поля имени
    names = [{'givenName': first_name}]
    if last_name:
        names[0]['familyName'] = last_name
    new_contact['names'] = names

    # Добавление номера телефона
    new_contact['phoneNumbers'] = [{'value': phone_number}]

    # Добавление электронной почты
    if email:
        new_contact['emailAddresses'] = [{'value': email}]

    # Добавление данных об организации (компания и должность)
    if company or job_title:
        organization = {}
        if company:
            organization['name'] = company
        if job_title:
            organization['title'] = job_title
        new_contact['organizations'] = [organization]

    # Добавление дня рождения (ожидается формат YYYY-MM-DD)
    if birthday:
        try:
            parts = birthday.split('-')
            if len(parts) == 3:
                new_contact['birthdays'] = [{
                    'date': {
                        'year': int(parts[0]),
                        'month': int(parts[1]),
                        'day': int(parts[2])
                    }
                }]
        except Exception as e:
            # Если формат дня рождения некорректен, поле пропускается
            pass

    created_contact = service.people().createContact(body=new_contact).execute()
    return created_contact


def delete_contact(identifier: str) -> bool:
    contact = get_contact_by_identifier(identifier)
    if not contact:
        raise Exception("Контакт не найден")
    service = get_contacts_service()
    service.people().deleteContact(resourceName=contact['resourceName']).execute()
    return True
