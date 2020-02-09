import datetime
import json

from flask import Response

from message_manager import MessageManager


class APIResponse(Response):

    default_mimetype = 'application/json'

    @classmethod
    def force_type(cls, rv, environ=None):
        def converter(k):
            if isinstance(k, (datetime.date, datetime.datetime, datetime.time)):
                return k.__str__()
        if isinstance(rv, dict):
            rv = json.dumps(rv, default=converter)
        return super(APIResponse, cls).force_type(rv, environ)


class ResponseManager:

    @staticmethod
    def success(params=None):
        if params is None:
            params = {}
        return {**{'status': 'success'}, **params}

    @staticmethod
    def auth_success(user_id, token):
        return {'status': 'auth_success', 'user_id': user_id, 'token': token}

    @staticmethod
    def auth_continue():
        return {'status': 'auth_continue'}

    @staticmethod
    def verification_error():
        return {'status': 'verification_error', 'error_message': MessageManager.wrong_code()}

    @staticmethod
    def auth_error():
        return {'status': 'auth_error', 'error_message': MessageManager.bad_token()}

    @staticmethod
    def validation_error(error):
        return {'status': 'validation_error', 'error_message': str(error)}
