import json

from message_manager import MessageManager
from validator import ValidationError


class ResponseManager:

    @staticmethod
    def auth_success(user_id, token):
        return json.dumps({'status': 'auth_success', 'user_id': user_id, 'token': token}), 200

    @staticmethod
    def auth_continue():
        return json.dumps({'status': 'auth_continue'}), 200

    @staticmethod
    def error(error):
        return json.dumps({'status': 'error', 'error_message': str(error)}), 200
