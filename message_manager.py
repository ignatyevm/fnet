import json


class MessageManager:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MessageManager, cls).__new__(cls)
            with open('config/messages.json') as message_file:
                cls.instance.messages = json.load(message_file)
        return cls.instance

    def get(self, message_id):
        return self.messages[message_id]
