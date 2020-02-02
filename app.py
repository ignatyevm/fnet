import json
import hashlib

from flask import Flask, request
from flask_cors import CORS

from db_helper import DBHelper
from validator import validate, ValidationError
from message_manager import MessageManager
from response_manager import ResponseManager


app = Flask(__name__)
CORS(app)

db_adapter = DBHelper()


@app.route('/test', methods=['GET', 'POST'])
def test():
    try:
        email, password = validate(request.get_json(), ['email', 'password'])
    except ValidationError as ve:
        return ResponseManager.error(ve)
    print(email)
    print(password)
    return 'kek', 200


@app.route('/auth/register', methods=['POST'])
def auth_register():
    db_adapter.connect()
    cursor = db_adapter.get_cursor()

    required_params = ['first_name', 'last_name', 'email', 'password', 'password_repeat']

    try:
        first_name, last_name, email, password, password_repeat = validate(request.get_json(), required_params)
    except ValidationError as ve:
        return ResponseManager.error(ve)

    if password != password_repeat:
        return ResponseManager.error(MessageManager().get('passwords_dont_match'))

    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
    if cursor.fetchone() is not None:
        return ResponseManager.error(MessageManager().get('email_used'))

    cursor.execute("INSERT INTO Users(first_name, last_name, email, password_hash) VALUES "
                   "(%s, %s, %s, %s) RETURNING id",
                   (first_name, last_name, email, password_hash,))

    user_id = cursor.fetchone().get('id')

    token = hashlib.sha256('{}+{}+{}'.format(user_id, email, password).encode('utf-8')).hexdigest()
    db_adapter.commit()

    cursor.execute("INSERT INTO sessions(user_id, token) VALUES (%s, %s)", (user_id, token,))
    db_adapter.commit()

    return ResponseManager.success(user_id, token)


@app.route('/auth/login', methods=['POST'])
def auth_login():
    db_adapter.connect()
    cursor = db_adapter.get_cursor()

    required_params = ['email', 'password']

    try:
        email, password = validate(request.get_json(), required_params)
    except ValidationError as ve:
        return ResponseManager.error(ve)

    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    cursor.execute('SELECT id FROM Users WHERE email = %s AND password_hash = %s', (email, password_hash,))
    user = cursor.fetchone()

    if user is None:
        return ResponseManager.error(MessageManager().get('wrong_credentials'))

    user_id = user.get('id')

    cursor.execute('SELECT token FROM sessions WHERE user_id = %s', (user_id,))

    session = cursor.fetchone()

    return ResponseManager.success(user_id, session.get('token'))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
