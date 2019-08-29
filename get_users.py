import json
import sqlite3
from math import ceil

import vk

users_per_request = 900
groups_per_request = 400

with open("config.json", 'r') as f:
    config = json.load(f)
sqlite_path = config['db_path']
service_token = config['service_token']
my_id = config['my_id']


def init_tables(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL,"
                   "type TEXT, deleted INTEGER, sex INTEGER, private INTEGER, photo TEXT)")


def insert_user(cur, u):
    name = "{} {}".format(u['first_name'], u['last_name'])
    deleted = 1 if 'deactivated' in u else 0
    private = 1 if u.get('is_closed', True) else 0
    cur.execute("INSERT INTO users (id, name, type, deleted, sex, private, photo) VALUES (?, ?, 'user', ?, ?, ?, ?)",
                (u['id'], name, deleted, u.get('sex', None), private, u['photo_100']))


def insert_group(cur, g):
    mapper = {'group': 'club', 'page': 'public', 'event': 'event'}
    deleted = 1 if 'deactivated' in g else 0
    cur.execute("INSERT INTO users (id, name, type, deleted, sex, private, photo) VALUES (?, ?, ?, ?, NULL, ?, ?)",
                (-g['id'], g['name'], mapper[g['type']], deleted, g['is_closed'], g['photo_100']))


def main():
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute("DROP TABLE users")
    init_tables(cur)

    session = vk.Session(access_token=service_token)
    api = vk.API(session, v='5.101', lang='ru')

    cur.execute("SELECT DISTINCT sender FROM messages WHERE sender > 0")
    user_ids = set(x[0] for x in cur.fetchall())
    cur.execute("SELECT DISTINCT conversation FROM messages WHERE conversation > 0 AND conversation < 2000000000")
    user_ids.update(x[0] for x in cur.fetchall())
    user_ids = list(user_ids)
    print('Users:', len(user_ids))
    for i in range(ceil(len(user_ids) / users_per_request)):
        sub_ids = user_ids[i * users_per_request:(i + 1) * users_per_request]
        users = api.users.get(user_ids=sub_ids, fields=['is_closed', 'photo_100', 'sex'])
        print(' -', len(users))
        for u in users:
            insert_user(cur, u)

    me = api.users.get(user_id=my_id, fields=['is_closed', 'photo_100', 'sex'])[0]
    me['id'] = 0
    insert_user(cur, me)

    cur.execute("SELECT DISTINCT sender FROM messages WHERE sender < 0")
    group_ids = set(-x[0] for x in cur.fetchall())
    cur.execute("SELECT DISTINCT conversation FROM messages WHERE conversation < 0")
    group_ids.update(-x[0] for x in cur.fetchall())
    group_ids = list(group_ids)
    print('Groups:', len(group_ids))
    for i in range(ceil(len(group_ids) / groups_per_request)):
        sub_ids = group_ids[i * groups_per_request:(i + 1) * groups_per_request]
        groups = api.groups.getById(group_ids=sub_ids, fields=['is_closed', 'photo_100'])
        print(' -', len(groups))
        for g in groups:
            insert_group(cur, g)

    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
