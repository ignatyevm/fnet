import json

from message_manager import MessageManager


class ResponseManager:

    @staticmethod
    def success(params=None):
        result = {'status': 'success'}
        if params is not None:
            for key, value in params.items():
                result[key] = value
        return json.dumps(result), 200

    @staticmethod
    def auth_success(user_id, token):
        return json.dumps({'status': 'auth_success', 'user_id': user_id, 'token': token}), 200

    @staticmethod
    def auth_continue():
        return json.dumps({'status': 'auth_continue'}), 200

    @staticmethod
    def auth_error():
        return json.dumps({'status': 'auth_error', 'error_message': MessageManager().get("bad_token")}), 200

    @staticmethod
    def validation_error(error):
        return json.dumps({'status': 'validation_error', 'error_message': str(error)}), 200
