import logging
from fuzzywuzzy import fuzz
from Services import Google_Contacts

logger = logging.getLogger(__name__)

def partial_substring_ratio(a: str, b: str) -> float:
    """
    Возвращает частичное сходство (partial ratio) между строками a и b.
    Значение от 0 до 1.
    """
    return fuzz.partial_ratio(a.lower(), b.lower()) / 100.0

def match_name(query: str, display_name: str) -> bool:
    """
    Сравнивает запрос и отображаемое имя.
    Если запрос состоит из более чем одного слова, используем более высокий порог (0.85),
    иначе порог 0.6.
    """
    words = query.split()
    threshold = 0.85 if len(words) > 1 else 0.6
    return partial_substring_ratio(query, display_name) >= threshold

def get_contact_info_command(update, command_arguments: dict, original_text: str):
    """
    Обрабатывает команду получения информации о контакте.

    Ожидаемые аргументы:
      - contact_name: имя для поиска (строка)
      - field: поле, которое нужно вернуть (например, "phone" или "email")
      - label: метка для фильтра (например, "рабочий", "Челгу" и т.п.)
      - multiple: булевое значение, True если нужно вернуть все подходящие контакты
    """
    prefix = f"Распознанный текст: {original_text}\n"

    contact_name = command_arguments.get("contact_name")
    field = command_arguments.get("field")
    label = command_arguments.get("label")
    multiple = command_arguments.get("multiple", False)

    if not contact_name:
        update.message.reply_text(prefix + "Не указано имя контакта для поиска.")
        return

    try:
        contacts = Google_Contacts.get_all_contacts()
    except Exception as e:
        logger.error("Ошибка при получении контактов: %s", e)
        update.message.reply_text(prefix + "Ошибка при получении контактов.")
        return

    # 1) Ищем все контакты, где display_name удовлетворяет match_name()
    matched_contacts = []
    for person in contacts:
        if "names" not in person:
            continue
        for name_obj in person["names"]:
            display_name = name_obj.get("displayName", "")
            if match_name(contact_name, display_name):
                matched_contacts.append(person)
                break

    if not matched_contacts:
        update.message.reply_text(prefix + "Контакты не найдены.")
        return

    # 2) Если указано конкретное поле (phone/email), ищем нужное значение с учетом метки
    if field:
        filtered_results = []

        for person in matched_contacts:
            # --- Поиск телефонов ---
            if field == "phone" and "phoneNumbers" in person:
                phones_found = []
                for phone in person["phoneNumbers"]:
                    phone_label = phone.get("formattedType", "")
                    phone_value = phone.get("value", "")

                    # Если метка не указана — добавляем все номера
                    if not label:
                        phones_found.append((person, phone_value))
                    else:
                        # Сравниваем label с phone_label через поиск подстроки
                        if label.lower() in phone_label.lower():
                            phones_found.append((person, phone_value))
                # Если ничего не нашли по метке телефона — проверяем организации
                if not phones_found and label and "organizations" in person:
                    for org in person["organizations"]:
                        org_name = org.get("name", "")
                        if label.lower() in org_name.lower():
                            for phone in person["phoneNumbers"]:
                                phone_value = phone.get("value", "")
                                phones_found.append((person, phone_value))
                            break

                filtered_results.extend(phones_found)

            # --- Поиск email (аналогично) ---
            elif field == "email" and "emailAddresses" in person:
                emails_found = []
                for email in person["emailAddresses"]:
                    email_label = email.get("formattedType", "")
                    email_value = email.get("value", "")
                    if not label:
                        emails_found.append((person, email_value))
                    else:
                        if label.lower() in email_label.lower():
                            emails_found.append((person, email_value))
                filtered_results.extend(emails_found)

        if not filtered_results:
            update.message.reply_text(prefix + "Контакты с указанной информацией не найдены.")
            return

        # 3) Вывод результатов
        if len(filtered_results) == 1 and not multiple:
            person, value = filtered_results[0]
            display_name = person["names"][0]["displayName"]
            update.message.reply_text(prefix + f"{display_name}: {value}")
        else:
            results = []
            for person, value in filtered_results:
                display_name = person["names"][0]["displayName"]
                results.append(f"{display_name}: {value}")
            results_text = "\n".join(results)
            update.message.reply_text(prefix + "Найденные контакты:\n" + results_text)

    else:
        # Если поле не указано, выводим все совпадающие контакты
        if len(matched_contacts) == 1 and not multiple:
            person = matched_contacts[0]
            display_name = person["names"][0]["displayName"]
            update.message.reply_text(prefix + f"Найден контакт: {display_name}")
        else:
            results = []
            for person in matched_contacts:
                display_name = person["names"][0]["displayName"]
                results.append(display_name)
            update.message.reply_text(prefix + "Найдено несколько контактов:\n" + "\n".join(results))
