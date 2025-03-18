import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def get_calendar_service():
    credentials_file = os.getenv("GOOGLE_API_CREDENTIALS")
    if not credentials_file:
        raise Exception("Не указан путь к GOOGLE_API_CREDENTIALS")
    creds = Credentials.from_authorized_user_file(credentials_file)
    service = build('calendar', 'v3', credentials=creds)
    return service

#Добавить событие
def add_event(summary: str, location: str, description: str,
              start_time: str, end_time: str, reminders: list = None) -> dict:

    service = get_calendar_service()
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Yekaterinburg',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Yekaterinburg',
        },
        'reminders': {
            'useDefault': False,
            'overrides': reminders if reminders else []
        },
    }
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event

#Отмена события
def cancel_event(event_id: str) -> bool:
    service = get_calendar_service()
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    return True

#Повестка дня
def get_daily_schedule(date_str: str = None) -> list:
    service = get_calendar_service()
    if date_str:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        date_obj = datetime.now()
    start_of_day = datetime.combine(date_obj.date(), datetime.min.time()).isoformat() + 'Z'
    end_of_day = datetime.combine(date_obj.date(), datetime.max.time()).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_of_day,
        timeMax=end_of_day,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    return events

#Установка напоминаний
def set_reminder(event_id: str, minutes_before: int) -> dict:
    service = get_calendar_service()
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    event['reminders'] = {
        'useDefault': False,
        'overrides': [
            {'method': 'popup', 'minutes': minutes_before},
        ],
    }
    updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
    return updated_event

#Найти событие по имени
def find_event_by_name(event_name: str) -> list:
    service = get_calendar_service()
    from datetime import datetime, timedelta
    now = datetime.utcnow().isoformat() + 'Z'
    future = (datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'
    events_result = service.events().list(
         calendarId='primary', timeMin=now, timeMax=future,
         singleEvents=True, orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    matching_events = [event for event in events if event.get('summary','').lower() == event_name.lower()]
    return matching_events

if __name__ == '__main__':
    # Пример использования: добавление события через Google Calendar API
    summary = "Встреча с командой"
    location = "Офис"
    description = "Обсуждение проекта"
    # Пример: событие начинается через 1 час и длится 1 час
    start_time = (datetime.now() + timedelta(hours=1)).isoformat()
    end_time = (datetime.now() + timedelta(hours=2)).isoformat()
    reminders = [{'method': 'popup', 'minutes': 15}]

    try:
        event = add_event(summary, location, description, start_time, end_time, reminders)
        print("Событие добавлено. ID:", event.get("id"))
    except Exception as e:
        print("Ошибка при добавлении события:", e)

    # Пример получения повестки дня для текущей даты
    events = get_daily_schedule()
    if events:
        print("Повестка дня:")
        for ev in events:
            start = ev.get('start', {}).get('dateTime', ev.get('start', {}).get('date'))
            print(f"- {ev.get('summary')} ({start})")
    else:
        print("События не найдены.")
