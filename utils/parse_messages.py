import re
import os
import datetime as dt
from bs4 import BeautifulSoup


tz = dt.timezone(dt.timedelta(hours=3))
month_reverse = {'янв': 1, 'фев': 2, 'мар': 3, 'апр': 4, 'мая': 5, 'июн': 6,
                 'июл': 7, 'авг': 8, 'сен': 9, 'окт': 10, 'ноя': 11, 'дек': 12}
attachment_map = {'Опрос': 0, 'Фотография': 1, 'Сообщение удалено': 2, 'Стикер': 3,
                  'Ссылка': 4, 'Документ': 5, 'Аудиозапись': 6, 'Звонок': 7,
                  'Запись на стене': 8, 'Видеозапись': 9, 'Forwarded': 10,
                  'Pinned': 11, 'Подарок': 12, 'Плейлист': 13, 'Карта': 14,
                  'История': 15, 'Статья': 16, 'Запрос на денежный перевод': 17}  # todo check
attachment_map_reverse = dict([pair[::-1] for pair in attachment_map.items()])


class Attachment:
    def __init__(self, attachment_type, message_id, data=""):
        self.type = attachment_type
        self.message_id = message_id
        self.data = data

    def __repr__(self):
        if len(self.data):
            return "<{}: {}>".format(attachment_map_reverse[self.type], self.data)
        return "<{}>".format(attachment_map_reverse[self.type])


class Message:
    time_regexp = re.compile(r"(\d{1,2}) ([а-я]{3}) (\d{4}) в (\d{1,2}):(\d\d):(\d\d)")
    id_regexp = re.compile(r"id(\d+)")

    def __init__(self, conversation_id, msg=None):
        self.conversation_id = conversation_id
        self.sender_id = None
        self.data_id = None
        self.timestamp = None
        self.text = ""
        self.attachments = []
        if msg is not None:
            self.update(msg)

    def update(self, msg):
        self.data_id = msg['data-id']
        header = msg.select_one('.message__header')
        self.parse_header(header)
        self.attachments = []
        self.parse_message(msg.select_one('.message__header + div'))

    @staticmethod
    def url_to_id(url):
        if 'id' in url:
            return int(url.split('id')[-1])
        elif 'club' in url:
            return -int(url.split('club')[-1])
        elif 'public' in url:
            return -int(url.split('public')[-1])
        elif 'event' in url:
            return -int(url.split('event')[-1])
        else:
            raise Exception("Couldn't get id from url: {}".format(url))

    def parse_header(self, header):
        sender = header.find('a')
        self.sender_id = 0 if sender is None else self.url_to_id(sender['href'])
        day, month, year, hour, minute, second = self.time_regexp.search(header.text).groups()
        month = month_reverse[month]
        day, year, hour, minute, second = map(int, (day, year, hour, minute, second))
        self.timestamp = int(dt.datetime(year, month, day, hour, minute, second, tzinfo=tz).timestamp())

    def parse_message(self, message):
        for node in message.children:
            if isinstance(node, str):
                self.text += node
            elif node.name == 'br':
                self.text += '\n'
            elif 'kludges' in node['class']:
                if node.select_one('.im_srv_lnk'):
                    self.attachments.append(Attachment(attachment_map['Pinned'], self.data_id, node.text))
                else:
                    for attachment in node.children:
                        self.parse_attachment(attachment)
            else:
                raise Exception("Unknown message tag: {}".format(str(node)))

    def parse_attachment(self, attachment):
        description = attachment.select_one('.attachment__description').text
        link = attachment.select_one('.attachment__link')
        link = link['href'] if link else ""
        if description in attachment_map:
            self.attachments.append(Attachment(attachment_map[description], self.data_id, link))
        elif 'прикреп' in description:
            self.attachments.append(Attachment(attachment_map['Forwarded'], self.data_id, description))
        else:
            raise Exception("Unknown attachment type: {}".format(description))


def scan_messages(messages_dir):
    targets = []
    for conversation_id in sorted(os.listdir(messages_dir)):
        conversation_dir = os.path.join(messages_dir, conversation_id)
        if not os.path.isdir(conversation_dir):
            continue
        for message_chunk in sorted(os.listdir(conversation_dir)):
            if not message_chunk.endswith('.html'):
                continue
            targets.append((int(conversation_id), os.path.join(conversation_dir, message_chunk)))
    return targets


def get_all_messages(messages_dir, encoding='utf-8'):
    targets = scan_messages(messages_dir)
    print("Estimated messages count: ~{}".format(len(targets) * 300))

    messages = []
    for target_idx, (conversation_id, message_chunk_path) in enumerate(targets):
        with open(message_chunk_path, 'r', encoding=encoding) as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        for msg in soup.select('.message'):
            messages.append(Message(conversation_id, msg))

        total = len(messages) + 300 * (len(targets) - target_idx - 1)
        print("[{:.02f}%] {}/{}, "
              "conversation_id: {}, target_idx: {}".format(100 * len(messages) / total, len(messages), total,
                                                           conversation_id, target_idx))
    return messages
