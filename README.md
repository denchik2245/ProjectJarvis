# Telegram Personal Assistant Bot

Этот проект представляет собой Telegram-бота, который работает как личный ассистент. Он интегрируется с различными сервисами, такими как Gmail, Google Keep, Google Calendar, Google Drive, Google Contacts и погодными сервисами (например, Яндекс.Погода). Бот умеет принимать голосовые и текстовые сообщения, распознавать команды с помощью локальной нейросети и выполнять соответствующие действия.

---

## Структура проекта и назначение файлов

### Корневая директория

- **main.py**  
  Точка входа в приложение. Здесь происходит инициализация Telegram-бота, загрузка конфигурационных параметров из `config.py`, регистрация обработчиков сообщений из папки `handlers` и запуск основного цикла обработки сообщений.

- **config.py**  
  Файл конфигурации проекта. Отвечает за загрузку переменных окружения из файла `.env` (например, токен Telegram, параметры Google API, путь к модели голосового распознавания) и настройку глобальных параметров.

- **requirements.txt**  
  Список зависимостей, необходимых для работы проекта. Используется для установки необходимых библиотек (например, для работы с Telegram API, Google API, распознавания речи и т.д.).

- **README.md**  
  Документация проекта. Содержит описание функционала, структуру проекта, инструкцию по установке и запуску, а также назначение каждого файла и папки.

- **.env**  
  Файл с переменными окружения, где хранятся конфиденциальные данные, такие как токены и ключи API. Файл не должен попадать в систему контроля версий.

- **.gitignore**  
  Файл, в котором указаны файлы и директории, игнорируемые системой контроля версий (например, виртуальное окружение, логи, временные файлы, файл `.env`).

---

### Папка `services/`

Содержит модули для интеграции с внешними сервисами:

- **gmail_service.py**  
  Реализует функции для работы с Gmail: отправка писем, отложенная отправка, поиск писем по ключевым словам и получение входящих сообщений.

- **google_keep_service.py**  
  Содержит функции для работы с Google Keep: создание заметок, получение заметки по названию и удаление заметки.

- **google_calendar_service.py**  
  Отвечает за управление событиями в Google Calendar. Реализует добавление, отмену и изменение событий, установку напоминаний, получение повестки дня/недели и отправку приглашений.

- **google_drive_service.py**  
  Реализует функции для работы с Google Drive: загрузка фотографий, создание папок и перемещение файлов между папками.

- **google_contacts_service.py**  
  Содержит функции для управления контактами: добавление нового контакта, поиск контактов и удаление контактов.

- **weather_service.py**  
  Реализует получение данных о погоде с помощью внешних API (например, Яндекс.Погода). Позволяет получать текущую погоду, а также прогноз на завтра или неделю.

---

### Папка `nlp/`

Содержит модули для обработки голосовых сообщений и команд:

- **voice_recognition.py**  
  Модуль для преобразования голосовых сообщений в текст. Использует локальную нейросеть для распознавания речи.

- **command_parser.py**  
  Анализирует текст, полученный в результате распознавания, и определяет, какую команду хочет выполнить пользователь. Выделяет необходимые параметры и направляет запросы на соответствующие сервисы.

- **models/** (опционально)  
  Каталог для хранения локальных моделей нейросети или конфигураций, используемых для распознавания речи.

---

### Папка `handlers/`

Содержит обработчики входящих сообщений Telegram:

- **telegram_handler.py**  
  Основной обработчик сообщений, который принимает входящие текстовые и голосовые сообщения. Голосовые сообщения передаются на распознавание, а затем полученный текст отправляется в командный парсер.

- **command_handler.py**  
  Диспетчер команд, который на основании распознанного запроса определяет, какая функция из модулей `services/` должна быть вызвана для выполнения требуемого действия.

---

### Папка `utils/`

Содержит вспомогательные утилиты и общие функции:

- **logger.py**  
  Настраивает систему логирования и ведение журнала работы приложения, что помогает отслеживать ошибки и процессы выполнения команд.

- **helper_functions.py**  
  Содержит общие вспомогательные функции, такие как обработка дат, форматирование сообщений и другие утилиты, которые могут использоваться в разных частях проекта.

---

### Папка `tests/`

Содержит модульные тесты для проверки работы отдельных компонентов проекта:

- **test_gmail_service.py**  
  Тесты для функций работы с Gmail.

- **test_google_keep_service.py**  
  Тесты для функций работы с Google Keep.

- **test_google_calendar_service.py**  
  Тесты для функций работы с Google Calendar.

- **test_google_drive_service.py**  
  Тесты для функций работы с Google Drive.

- **test_google_contacts_service.py**  
  Тесты для функций работы с Google Contacts.

- **test_weather_service.py**  
  Тесты для функций получения данных о погоде.

- **test_voice_recognition.py**  
  Тесты для модуля распознавания голоса.

- **test_command_parser.py**  
  Тесты для проверки корректности парсинга команд.

- **test_telegram_handler.py**  
  Тесты для проверки работы обработчика Telegram-сообщений.