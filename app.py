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

    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    if first_name is None or last_name is None or email is None or password is None:
        return json.dumps({'status': 'error', 'error_message': 'One or more fields are empty'}), 400

    cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
    if cursor.fetchone() is not None:
        return json.dumps({'status': 'error', 'error_message': 'Email already registered'}), 409

    cursor.execute("INSERT INTO Users(first_name, last_name, email, password_hash) VALUES "
                   "('%s', '%s', '%s', '{%s') RETURNING id",
                   (first_name, last_name, email, password_hash,))

    user_id = cursor.fetchone()[0]

    token = hashlib.sha256('{}+{}+{}'.format(user_id, email, password).encode('utf-8')).hexdigest()
    db_adapter.commit()

    cursor.execute("INSERT INTO sessions(user_id, token) VALUES ({}, '{}')"
                   .format(user_id, token))
    db_adapter.commit()

    return json.dumps({'status': 'success', 'token': token}), 200


@app.route('/auth/login', methods=['POST'])
def auth_login():
    db_adapter.connect()
    cursor = db_adapter.get_cursor()

    email = request.form.get('email')
    password = request.form.get('password')
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    if email is None or password is None:
        return json.dumps({'status': 'error', 'error_message': 'One or more fields are empty'}), 400

    cursor.execute('SELECT id FROM Users WHERE email = %s AND password_hash = %s', (email, password_hash,))
    user = cursor.fetchone()

    if user is None:
        return json.dumps({'status': 'error', 'error_message': 'Wrong email or password'}), 406

    cursor.execute('SELECT token FROM sessions WHERE user_id = %s', (user.get('id'),))

    session = cursor.fetchone()

    return json.dumps({'status': 'success', 'token': session.get('token')}), 200


if __name__ == '__main__':
    app.run()
