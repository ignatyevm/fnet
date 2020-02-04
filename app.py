import random
import smtplib
from datetime import datetime
import json
import hashlib

from flask import Flask, request
from flask_cors import CORS

from pymemcache.client import base

from db_helper import DBHelper
from validator import validate, FieldValidator, ValidationError
from message_manager import MessageManager
from response_manager import ResponseManager
from config.db_config import mc_host, mc_port
import config.config as config

app = Flask(__name__)
CORS(app)

db_helper = DBHelper()
memcached_client = base.Client((mc_host, mc_port))


@app.route('/test', methods=['GET', 'POST'])
def test():
    try:
        email, password = validate(request.get_json(), ['email', 'password'])
    except ValidationError as ve:
        return ResponseManager.error(ve)
    print(email)
    print(password)
    return 'kek', 200


@app.route('/auth/email_verify', methods=['POST'])
def auth_email_verify():
    validators = [
        FieldValidator('email').required().email(),
        FieldValidator('code').required(),
    ]
    email, code = validate(request.get_json(), validators)
    valid_code = memcached_client.get(email)
    if valid_code is None or int(valid_code) != int(code):
        return ResponseManager.error(MessageManager().get('wrong_code'))
    memcached_client.delete(email)

    db_helper.connect()
    cursor = db_helper.get_cursor()

    cursor.execute('UPDATE "User" SET is_email_verified=true WHERE email = %s RETURNING id, password_hash', (email,))
    db_helper.commit()

    result = cursor.fetchone()
    user_id = result.get('id')
    password_hash = result.get('password_hash')
    token = hashlib.sha256('{}+{}+{}'.format(user_id, email, password_hash).encode('utf-8')).hexdigest()

    cursor.execute('INSERT INTO "Session"(user_id, token) VALUES (%s, %s)', (user_id, token,))
    db_helper.commit()

    return ResponseManager.auth_success(user_id, token)


@app.route('/auth/register', methods=['POST'])
def auth_register():
    db_helper.connect()
    cursor = db_helper.get_cursor()

    validators = [
        FieldValidator('first_name').required().max_len(config.max_name_len),
        FieldValidator('last_name').required().max_len(config.max_name_len),
        FieldValidator('birth_date').required(),
        FieldValidator('gender').required().values_set(*config.allowed_genders),
        FieldValidator('email').required().max_len(config.max_email_len).email(),
        FieldValidator('password').required().min_len(config.min_password_len).max_len(config.max_password_len),
    ]

    try:
        first_name, last_name, birth_date, gender, email, password = validate(request.get_json(), validators)
    except ValidationError as ve:
        return ResponseManager.error(ve)

    if memcached_client.get(email) is not None:
        return ResponseManager.error(MessageManager().get('email_used'))

    cursor.execute('SELECT * FROM "User" WHERE email = %s', (email,))
    result = cursor.fetchone()
    if result is not None and not result.get('is_email_verified'):
        return ResponseManager.error(MessageManager().get('email_used'))

    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    cursor.execute('INSERT INTO "User"(first_name, last_name, email, birth_date, gender, password_hash) VALUES '
                   '(%s, %s, %s, %s, %s, %s) RETURNING id',
                   (first_name, last_name, email, birth_date, gender, password_hash,))

    db_helper.commit()
    db_helper.close()

    code = random.randrange(100000, 999999)

    # code valid only 10 min
    memcached_client.set(email, code, int(datetime.now().timestamp()) + 10 * 60)

    print(code)

    return ResponseManager.auth_continue()


@app.route('/auth/login', methods=['GET'])
def auth_login():
    db_helper.connect()
    cursor = db_helper.get_cursor()

    validators = [
        FieldValidator('email').required().email(),
        FieldValidator('password').required(),
    ]

    try:
        email, password = validate(request.get_json(), validators)
    except ValidationError as ve:
        return ResponseManager.error(ve)

    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    cursor.execute('SELECT id, is_email_verified FROM "User" WHERE email = %s AND password_hash = %s', (email, password_hash,))
    user = cursor.fetchone()

    if user is None or not user.get('is_email_verified'):
        return ResponseManager.error(MessageManager().get('wrong_credentials'))

    user_id = user.get('id')

    cursor.execute('SELECT token FROM "Session" WHERE user_id = %s', (user_id,))

    session = cursor.fetchone()

    return ResponseManager.auth_success(user_id, session.get('token'))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
