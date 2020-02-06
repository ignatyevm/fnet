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

likes = Blueprint('likes', __name__)


@likes.route('/<string:place_type>+<int:place_id>', methods=['GET'])
def get_likes(place_type, place_id):
    database_cursor.execute('SELECT user_id FROM "Likes" WHERE place_type = %s AND place_id = %s',
                            (place_type, place_id))
    likes_data = database_cursor.fetchall()
    return ResponseManager.success({'likes': likes_data})


@likes.route('/<string:place_type>+<int:place_id>', methods=['POST'])
def add_like(place_type, place_id):
    validators = [
        FieldValidator('token').required()
    ]
    token = validate(request.get_json(), validators)
    user_id = validate_token(token)
    database_cursor.execute('INSERT INTO "Likes"(user_id, place_type, place_id) VALUES (%s, %s, %s)',
                            (user_id, place_type, place_id))
    return ResponseManager.success()
