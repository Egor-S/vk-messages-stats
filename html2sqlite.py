import json
import sqlite3

from utils.parse_messages import get_all_messages

with open("config.json", 'r') as f:
    config = json.load(f)
sqlite_path = config['db_path']
messages_dir = config['messages_dir']
encoding = 'windows-1251'


def init_tables(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, sender INTEGER, "
                   "conversation INTEGER, time INTEGER, text TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS attachments (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                   "type INTEGER, message_id INTEGER, data TEXT)")


def insert_message(cursor, msg):
    cursor.execute("INSERT INTO messages (id, sender, conversation, time, text) VALUES (?, ?, ?, ?, ?)",
                   (msg.data_id, msg.sender_id, msg.conversation_id, msg.timestamp, msg.text))
    for attachment in msg.attachments:
        cursor.execute("INSERT INTO attachments (type, message_id, data) VALUES (?, ?, ?)",
                       (attachment.type, attachment.message_id, attachment.data))


def main():
    messages = get_all_messages(messages_dir, encoding)

    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    init_tables(cur)

    for msg in messages:
        insert_message(cur, msg)
    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
