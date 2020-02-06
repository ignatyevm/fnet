from flask import Flask, request
from flask_cors import CORS

from database import Database
from validator import validate, FieldValidator, ValidationError
from response_manager import ResponseManager

from api.auth import auth

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth, url_prefix='/api/auth')


@app.route('/test', methods=['GET', 'POST'])
def test():
    validators = [
        FieldValidator('email').required().email(),
        FieldValidator('password').required().min_len(6),
        FieldValidator('status').min_len(100)
    ]
    try:
        email, password, status = validate(request.get_json(), validators)
    except ValidationError as ve:
        return ResponseManager.error(ve)
    print(email)
    print(password)
    print(status)
    return 'kek', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0')
