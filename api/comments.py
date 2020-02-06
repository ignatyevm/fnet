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

comments = Blueprint('comments', __name__)


@comments.route('/<string:place_type>+<int:place_id>', methods=['GET'])
def get_likes(place_type, place_id):
    database_cursor.execute('SELECT user_id, likes_count, text, time FROM "Comment" WHERE place_type = %s AND place_id = %s',
                            (place_type, place_id))
    comments_data = database_cursor.fetchall()
    return ResponseManager.success({'comments': comments_data})


@comments.route('/<string:place_type>+<int:place_id>', methods=['POST'])
def add_like(place_type, place_id):
    validators = [
        FieldValidator('token').required(),
        FieldValidator('text').required().max_len(config.max_comment_text_len)
    ]
    token = validate(request.get_json(), validators)
    user_id = validate_token(token)
    database_cursor.execute('INSERT INTO "Comment"(user_id, place_type, place_id, text) VALUES (%s, %s, %s, %s)',
                            (user_id, place_type, place_id))
    return ResponseManager.success()
