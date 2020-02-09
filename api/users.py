import random
from datetime import datetime
import hashlib

from flask import request, Blueprint

from validator import validate, validate_token, FieldValidator
from response_manager import ResponseManager
import config.config as config
from database import database_cursor
from errors import AuthenticationError

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
        FieldValidator('old_password').required(),
        FieldValidator('new_password').required().min_len(config.min_password_len),
        FieldValidator('token').required()
    ]
    old_password, new_password, token = validate(request.get_json(), validators)
    user_id = validate_token(token)
    database_cursor.execute('SELECT password_hash FROM "User" WHERE id = %s', (user_id,))
    password_hash = database_cursor.fetchone().get('password_hash')
    old_password_hash = hashlib.sha256(old_password.encode('utf-8')).hexdigest()
    if password_hash != old_password_hash:
        raise AuthenticationError()
    new_password_hash = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
    database_cursor.execute('UPDATE "User" SET password_hash = %s WHERE id = %s RETURNING email', (new_password_hash, user_id,))
    new_token = hashlib.sha256('{}+{}+{}'.format(user_id, database_cursor.fetchone().get('email'), new_password_hash).encode('utf-8')).hexdigest()
    database_cursor.execute('UPDATE "Session" SET token = %s WHERE user_id = %s', (new_token, user_id,))
    return ResponseManager.success({'token': new_token})


@users.route('/update_name', methods=['PUT'])
def update_name():
    validators = [
        FieldValidator('token').required(),
        FieldValidator('first_name').required().max_len(config.max_name_len),
        FieldValidator('last_name').required().max_len(config.max_name_len)
    ]
    token, first_name, last_name = validate(request.get_json(), validators)
    user_id = validate_token(token)
    database_cursor.execute('UPDATE "User" SET first_name = %s, last_name = %s WHERE id = %s', (first_name, last_name, user_id,))
    return ResponseManager.success()

