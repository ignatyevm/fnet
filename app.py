import json

from flask import Flask, request

import hashlib

from db_helper import DBHelper

app = Flask(__name__)

db_adapter = DBHelper()


@app.route('/auth/register', methods=['POST'])
def auth_register():
    db_adapter.connect()
    cursor = db_adapter.get_cursor()

    params = request.get_json()
    required_params = ['first_name', 'last_name', 'email', 'password', 'password_repeat']

    for required_param in required_params:
        if (required_param not in params) or (params[required_param] == ''):
            return json.dumps({'status': 'error', 'error_message': 'One or more fields are empty'}), 400

    first_name = params['first_name']
    last_name = params['last_name']
    email = params['email']
    password = params['password']
    password_repeat = params['password_repeat']

    if password != password_repeat:
        return json.dumps({'status': 'error', 'error_message': 'Passwords dont match'}), 400

    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
    if cursor.fetchone() is not None:
        return json.dumps({'status': 'error', 'error_message': 'This email already registered'}), 409

    cursor.execute("INSERT INTO Users(first_name, last_name, email, password_hash) VALUES "
                   "('%s', '%s', '%s', '{%s') RETURNING id",
                   (first_name, last_name, email, password_hash,))

    user_id = cursor.fetchone()[0]

    token = hashlib.sha256('{}+{}+{}'.format(user_id, email, password).encode('utf-8')).hexdigest()
    db_adapter.commit()

    cursor.execute("INSERT INTO sessions(user_id, token) VALUES ({}, '{}')".format(user_id, token))
    db_adapter.commit()

    return json.dumps({'status': 'success', 'token': token}), 200


@app.route('/auth/login', methods=['POST'])
def auth_login():
    db_adapter.connect()
    cursor = db_adapter.get_cursor()

    params = request.get_json()

    if ('email' not in params) or ('password' not in params) or (params['email'] == '') or (params['password'] == ''):
        return json.dumps({'status': 'error', 'error_message': 'One or more fields are empty'}), 400

    email = params['email']
    password = params['password']
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    cursor.execute('SELECT id FROM Users WHERE email = %s AND password_hash = %s', (email, password_hash,))
    user = cursor.fetchone()

    if user is None:
        return json.dumps({'status': 'error', 'error_message': 'Wrong email or password'}), 406

    cursor.execute('SELECT token FROM sessions WHERE user_id = %s', (user.get('id'),))

    session = cursor.fetchone()

    return json.dumps({'status': 'success', 'token': session.get('token')}), 200


if __name__ == '__main__':
    app.run()
