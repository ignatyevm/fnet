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

posts = Blueprint('posts', __name__)


@posts.route('/<int:user_id>', methods=['GET'])
def get_posts(user_id):
    database_cursor.execute('SELECT text, time, likes_count, views_count FROM "Post" WHERE owner_id = %s', (user_id,))
    posts_data = database_cursor.fetchall()
    return ResponseManager.success({'posts': posts_data})


@posts.route('/', methods=['POST'])
def create_post():
    validators = [
        FieldValidator('token').required(),
        FieldValidator('text').required().max_len(config.max_post_text_len)
    ]
    token, text = validate(request.get_json(), validators)
    user_id = validate_token(token)
    database_cursor.execute('INSERT INTO "Post"(owner_id, text) VALUES (%s, %s) RETURNING time', (user_id, text,))
    return ResponseManager.success({'time': database_cursor.fetchone().get('time')})
