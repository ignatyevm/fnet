import random
from datetime import datetime
import hashlib
from smtplib import SMTP

from flask import request, Blueprint
from pymemcache.client import base

from validator import validate, FieldValidator, ValidationError
from message_manager import MessageManager
from response_manager import ResponseManager
from config.db_config import mc_host, mc_port
import config.config as config
from database import database_cursor

memcached_client = base.Client((mc_host, mc_port))

auth = Blueprint('auth', __name__)


@auth.route('/email_verify', methods=['POST'])
def auth_email_verify():
    validators = [
        FieldValidator('email').required().email(),
        FieldValidator('code').required(),
    ]

    email, code = validate(request.get_json(), validators)

    valid_code = memcached_client.get(email)
    if valid_code is None or int(valid_code) != int(code):
        return ResponseManager.verification_error()
    memcached_client.delete(email)

    database_cursor.execute('UPDATE "User" SET is_email_verified=true WHERE email = %s RETURNING id, password_hash',
                            (email,))

    result = database_cursor.fetchone()
    user_id = result.get('id')
    password_hash = result.get('password_hash')
    token = hashlib.sha256('{}+{}+{}'.format(user_id, email, password_hash).encode('utf-8')).hexdigest()

    database_cursor.execute('INSERT INTO "Session"(user_id, token) VALUES (%s, %s)', (user_id, token,))

    return ResponseManager.auth_success(user_id, token)


@auth.route('/register', methods=['POST'])
def auth_register():
    validators = [
        FieldValidator('first_name').required().max_len(config.max_name_len),
        FieldValidator('last_name').required().max_len(config.max_name_len),
        FieldValidator('birth_date').required(),
        FieldValidator('gender').required().values(*config.allowed_genders),
        FieldValidator('email').required().max_len(config.max_email_len).email(),
        FieldValidator('password').required().min_len(config.min_password_len).max_len(config.max_password_len)
    ]

    first_name, last_name, birth_date, gender, email, password = validate(request.get_json(), validators)

    if memcached_client.get(email) is not None:
        return ResponseManager.validation_error(MessageManager().email_used())

    database_cursor.execute('SELECT * FROM "User" WHERE email = %s', (email,))
    result = database_cursor.fetchone()
    if result is not None and not result.get('is_email_verified'):
        return ResponseManager.validation_error(MessageManager().email_used())

    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    database_cursor.execute(
        'INSERT INTO "User"(first_name, last_name, email, birth_date, gender, password_hash) VALUES '
        '(%s, %s, %s, %s, %s, %s) RETURNING id',
        (first_name, last_name, email, birth_date, gender, password_hash,))

    code = random.randrange(100000, 999999)

    # code valid only 10 min
    memcached_client.set(email, code, int(datetime.now().timestamp()) + 10 * 60)

    print(code)

    return ResponseManager.auth_continue()


@auth.route('/login', methods=['POST'])
def auth_login():
    validators = [
        FieldValidator('email').required().email(),
        FieldValidator('password').required(),
    ]

    email, password = validate(request.get_json(), validators)

    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    database_cursor.execute('SELECT id, is_email_verified FROM "User" WHERE email = %s AND password_hash = %s',
                            (email, password_hash,))
    user = database_cursor.fetchone()

    if user is None or not user.get('is_email_verified'):
        return ResponseManager.validation_error(MessageManager.wrong_credentials())

    user_id = user.get('id')

    database_cursor.execute('SELECT token FROM "Session" WHERE user_id = %s', (user_id,))

    session = database_cursor.fetchone()

    return ResponseManager.auth_success(user_id, session.get('token'))
