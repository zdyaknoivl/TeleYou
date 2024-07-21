import json
from datetime import datetime
from config import *


class MessagesParser:
    def __init__(self, src_path, messages_split_time: int = 60):
        self.src_path = src_path
        self.messages_split_time = messages_split_time
        self.sessions = []

        self.__date_format =  "%Y-%m-%dT%H:%M:%S"

    def __count_time_difference(self, date_1, date_2):
        date_1 = datetime.strptime(date_1, self.__date_format)
        date_2 = datetime.strptime(date_2, self.__date_format)

        return (date_2 - date_1).total_seconds() / 60


    def parse_messages(self, output_path):
        json_dict = self.__load_json_dict(self.src_path)
        
        messages = json_dict['chats']['list'][0]['messages']
        self.prev_date = None
        for message in messages:
            if 'forwarded_from' in message:
                continue

            user = message['from']
            text = self.__parse_message_text(message['text_entities'])
            date = message['date']

            if text is None or text == '':
                continue

            self.__fill_sessions(user, text, date)
            self.prev_date = date

            # print(f'{user}: {text}')
        print(len(self.sessions))

    def __fill_sessions(self, user, text, date):
        message_string = f'{BOS_TOKEN}{user}\n{text}{EOS_TOKEN}'
        if (self.prev_date is None
                or self.__count_time_difference(self.prev_date, date) > self.messages_split_time):
            self.sessions.append(message_string)
            return
        self.sessions[-1] += '\n' + message_string
        
    def __load_json_dict(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            return json.loads(file.read())
    
    def __parse_message_text(self, json_list):
        message = ''
        for entity in json_list:
            message += entity['text']
        return message

parser = MessagesParser('data/result_short.json').parse_messages('')