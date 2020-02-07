import random
from datetime import datetime
import hashlib

from flask import request, Blueprint
from pymemcache.client import base

from validator import validate, validate_token, FieldValidator, ValidationError
from message_manager import MessageManager
from response_manager import ResponseManager
import config.config as config
from database import database_cursor

users = Blueprint('users', __name__)


@users.route('/<int:user_id>', methods=['GET'])
def get_messages(user_id):
    database_cursor.execute('SELECT first_name, last_name, birth_date, gender, status FROM "User" WHERE id = %s', (user_id,))
    user_data = database_cursor.fetchone()
    return ResponseManager.success(user_data)


@users.route('/status', methods=['POST'])
def update_status():
    validators = [
        FieldValidator('status').required().max_len(config.max_status_text_len),
        FieldValidator('token').required()
    ]
    status, token = validate(request.get_json(), validators)
    user_id = validate_token(token)
    database_cursor.execute('UPDATE "User" SET status = %s WHERE id = %s', (status, user_id,))
    return ResponseManager.success()


@users.route('/update_password', methods=['PUT'])
def update_password():
    validators = [
        FieldValidator('old_password').required().max_len(config.max_password_len).max_len(config.min_password_len),
        FieldValidator('new_password').required().max_len(config.max_password_len).max_len(config.min_password_len),
        FieldValidator('token').required()
    ]
    old_password, new_password, token = validate(request.get_json(), validators)
    user_id = validate_token(token)
    database_cursor.execute('SELECT password_hash FROM "User" WHERE id = %s', (user_id,))
    password_hash = database_cursor.fetchone().get('password_hash')
    old_password_hash =  hashlib.sha256(old_password.encode('utf-8')).hexdigest()
    if password_hash != old_password_hash:
        return ResponseManager.auth_error()
    new_password_hash = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
    database_cursor.execute('UPDATE "User" SET password_hash = %s WHERE id = %s', (new_password_hash, user_id, ))


@users.route('/update_field/<string:field_name>', methods=['PUT'])
def update_field(field_name):
    validators = [
        FieldValidator('token').required(),
        FieldValidator('field_value').required()
    ]
    token, field_value = validate(request.get_json(), validators)
    user_id = validate_token(token)
    database_cursor.execute('UPDATE "User" SET %s = %s WHERE id = %s', (field_name, field_value, token,))

