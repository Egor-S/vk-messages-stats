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

### Конвертация HTML в SQLite
Отредактируйте путь до папки с сообщениями из архива (`archive/messages`) и путь до файла базы данных SQLite в файле `html2sqlite.py`.

Запустите скрипт:
```
python3 html2sqlite.py
```

Прогресс конвертации будет отображаться в консоли.

## Структура базы данных
```sql
CREATE TABLE IF NOT EXISTS messages
    (id INTEGER PRIMARY KEY, sender INTEGER, conversation INTEGER,
     time INTEGER, text TEXT);
CREATE TABLE IF NOT EXISTS attachments
    (id INTEGER PRIMARY KEY AUTOINCREMENT, type INTEGER,
     message_id INTEGER, data TEXT);
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
