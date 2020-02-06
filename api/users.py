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
