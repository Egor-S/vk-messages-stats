## Мотивация
После [15 февраля 2019](https://vk.com/dev/messages_api) в силу вступили новые ограничения для Messages API,
только прошедшие модерацию приоложения могут с ним работать. Свои сообщения можно получить в формате HTML страниц.
Данный проект позволяет получить все сообщения в виде базы данных SQLite.

## Использование
### Получение архива
На странице [о защите данных](https://vk.com/data_protection?section=rules) запросите архив, отметив сообщения.

### Настройка окружения
Для работы требуется Python 3.

Установите зависимости:
```
pip3 install -r requirements.txt
```

### Конфигурация
Создайте в корне проекта файл `config.json` и заполните указанные значения:
```json
{
    "service_token": "<Получите сервисный токен в настройках приложения>",
    "messages_dir": "<Путь до папки с сообщениями messages>",
    "avatars_dir": "<Путь до папки для хранения аватаров страниц>",
    "db_path": "<Путь до файла базы данных sqlite>",
    "my_id": "<Ваш id для загрузки аватара и имени>"
}
```

Создать тестовое Standalone приложение для получения сервисного токена можно [здесь](https://vk.com/editapp?act=create). 

### Конвертация HTML в SQLite
Запустите скрипт:
```
python3 html2sqlite.py
```

Прогресс конвертации будет отображаться в консоли.

### Загрузка имен страниц
Запустите скрипт:
```
python3 get_users.py
```

### Загрузка аватаров
Запустите скрипт:
```
python3 download_avatars.py
```

## Структура базы данных
```sql
CREATE TABLE IF NOT EXISTS messages
    (id INTEGER PRIMARY KEY, sender INTEGER, conversation INTEGER,
     time INTEGER, text TEXT);
CREATE TABLE IF NOT EXISTS attachments
    (id INTEGER PRIMARY KEY AUTOINCREMENT, type INTEGER,
     message_id INTEGER, data TEXT);
CREATE TABLE IF NOT EXISTS users
    (id INTEGER PRIMARY KEY, name TEXT NOT NULL, type TEXT,
     deleted INTEGER, sex INTEGER, private INTEGER, photo TEXT)
```

`messages`:
- `sender` - id отправителя или `0` (Вы)
- `conversation` - id собеседника или локальный id беседы
- `time` - timestamp
- `text` - текст сообщений

`attachments`:
- `type` - тип приложения (см. `utils/parse_messages.py`)
- `message_id` - id сообщения в базе данных
- `data` - ссылка или количество прикрепленных сообщений (в зависимости от типа приложения)

`users`:
- `id` - id страницы или `0` (Вы)
- `name` - отображаемое имя
- `type` - `user`, `club`, `public` или `event`
- `deleted` - удалена ли страница
- `sex` - пол пользователя
- `private` - скрыта ли страница
- `photo` - ссылка на фотографию страницы
