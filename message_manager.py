import json


class MessageManager:

    @staticmethod
    def __load_messages():
        with open('config/messages.json') as messages_file:
            return json.load(messages_file)

    @staticmethod
    def __get_message(message_id, **format_params):
        messages = MessageManager.__load_messages()
        return messages[message_id].format(format_params)

    @staticmethod
    def empty_field(field_name):
        return MessageManager.__get_message('empty_field', field_name=field_name)

    @staticmethod
    def field_min_len(field_name, min_len):
        return MessageManager.__get_message('field_min_len', field_name=field_name, min_len=min_len)

    @staticmethod
    def field_max_len(field_name, max_len):
        return MessageManager.__get_message('field_max_len', field_name=field_name, max_len=max_len)

    @staticmethod
    def unknown_field_value(field_name, field_value):
        return MessageManager.__get_message('unknown_field_value', field_name=field_name, field_value=field_value)

    @staticmethod
    def email_used():
        return MessageManager.__get_message('email_used')

    @staticmethod
    def wrong_credentials():
        return MessageManager.__get_message('wrong_credentials')

    @staticmethod
    def bad_email():
        return MessageManager.__get_message('bad_email')

    @staticmethod
    def wrong_code():
        return MessageManager.__get_message('wrong_code')

    @staticmethod
    def bad_token():
        return MessageManager.__get_message('bad_token')

    @staticmethod
    def wrong_field_type(field_name):
        return MessageManager.__get_message('wrong_field_type', field_name=field_name)
