from flask import Flask, request
from flask_cors import CORS

from database import Database
from validator import validate, FieldValidator, ValidationError, AuthorizationError
from response_manager import ResponseManager

from api.auth import auth
from api.users import users
from api.friends import friends
from api.messages import messages

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth, url_prefix='/api/auth')
app.register_blueprint(friends, url_prefix='/api/friends')
app.register_blueprint(messages, url_prefix='/api/messages')
app.register_blueprint(users, url_prefix='/api/users')


@app.errorhandler(ValidationError)
def validation_error(error):
    return ResponseManager.validation_error(error)


@app.errorhandler(AuthorizationError)
def validation_error(error):
    return ResponseManager.auth_error()


if __name__ == '__main__':
    app.run(host='0.0.0.0')
