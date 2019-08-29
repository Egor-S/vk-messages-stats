import json
import os
import sqlite3

import requests

with open("config.json", 'r') as f:
    config = json.load(f)
sqlite_path = config['db_path']
avatars_dir = config['avatars_dir']


def download_image(url, target_path):
    with open(target_path, 'wb') as f:
        response = requests.get(url, stream=True)
        if not response.ok:
            print(response)
        for block in response.iter_content(1024):
            if not block:
                break
            f.write(block)


def main():
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()

    cur.execute("SELECT id, photo FROM users")
    targets = cur.fetchall()

    for i, (uid, url) in enumerate(targets):
        download_image(url, os.path.join(avatars_dir, "{}.jpg".format(uid)))
        print("{}/{} {}".format(i + 1, len(targets), uid))

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
