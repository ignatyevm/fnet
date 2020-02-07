import datetime
from smtplib import SMTP

from flask import Flask, request
from flask_cors import CORS
from flask_mail import Mail, Message

from validator import ValidationError, AuthorizationError
from response_manager import ResponseManager, APIResponse

from api.auth import auth
from api.users import users
from api.friends import friends
from api.messages import messages
from api.posts import posts
from api.likes import likes
from api.comments import comments

app = Flask(__name__)
app.response_class = APIResponse
CORS(app)

app.config['MAIL_SERVER'] = 'smpt.mail.ru'
app.config['MAIL_PORT'] = 465
# app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'pasha.pavlovich.pavlov@mail.ru'  # введите свой адрес электронной почты здесь
app.config['MAIL_DEFAULT_SENDER'] = 'pasha.pavlovich.pavlov@mail.ru'  # и здесь
app.config['MAIL_PASSWORD'] = 'q12344321q'  # введите пароль

mail = Mail(app)

app.register_blueprint(auth, url_prefix='/api/auth')
app.register_blueprint(friends, url_prefix='/api/friends')
app.register_blueprint(messages, url_prefix='/api/messages')
app.register_blueprint(users, url_prefix='/api/users')
app.register_blueprint(posts, url_prefix='/api/posts')
app.register_blueprint(likes, url_prefix='/api/likes')
app.register_blueprint(comments, url_prefix='/api/comments')


@app.route("/email", methods=['GET'])
def send():
    print("kek")
    msg = Message("Subject", recipients=["salushkin1998@bk.ru"])
    msg.body = "<h2>Email Heading</h2>\n<p>Email Body</p>"

    mail.send(msg)

    return 'kek'


@app.errorhandler(ValidationError)
def validation_error(error):
    return ResponseManager.validation_error(error)


@app.errorhandler(AuthorizationError)
def validation_error(error):
    return ResponseManager.auth_error()


if __name__ == '__main__':
    app.run(host='0.0.0.0')
