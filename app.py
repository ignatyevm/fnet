from flask import Flask
from flask_cors import CORS

from errors import ValidationError, AuthenticationError, AuthorizationError, VerificationError
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

app.register_blueprint(auth, url_prefix='/api/auth')
app.register_blueprint(friends, url_prefix='/api/friends')
app.register_blueprint(messages, url_prefix='/api/messages')
app.register_blueprint(users, url_prefix='/api/users')
app.register_blueprint(posts, url_prefix='/api/posts')
app.register_blueprint(likes, url_prefix='/api/likes')
app.register_blueprint(comments, url_prefix='/api/comments')


@app.errorhandler(ValidationError)
def validation_error(error):
    return ResponseManager.validation_error(error)


@app.errorhandler(AuthenticationError)
def validation_error(error):
    return ResponseManager.authentication_error()


@app.errorhandler(AuthorizationError)
def validation_error(error):
    return ResponseManager.authorization_error()


@app.errorhandler(VerificationError)
def validation_error(error):
    return ResponseManager.verification_error()


if __name__ == '__main__':
    app.run(host='0.0.0.0')
