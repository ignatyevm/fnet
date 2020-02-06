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

friends = Blueprint('friends', __name__)


@friends.route('/<int:user_id>', methods=['GET'])
def get_friends(user_id):
    database_cursor.execute(
        'SELECT * FROM (SELECT "User".id as friend_id, first_name, last_name FROM "FriendRequest" '
        'JOIN "User" ON  ("User".id = "FriendRequest".receiver_id OR "User".id = "FriendRequest".sender_id) '
        'WHERE (sender_id = %s OR receiver_id = %s) AND is_accepted = true) AS Friends WHERE friend_id != %s;',
        (user_id, user_id, user_id,))
    result = database_cursor.fetchall()
    return ResponseManager.success({'friends': result})


@friends.route('/<int:friend_id>', methods=['DELETE'])
def delete_friend(friend_id):
    token = validate(request.get_json(), [FieldValidator('token').required()])
    user_id = validate_token(token)
    database_cursor.execute(
        'DELETE FROM "FriendRequest" WHERE '
        '(sender_id = %s AND receiver_id = %s) OR (receiver_id = %s AND sender_id = %s)',
        (user_id, friend_id, user_id, friend_id))
    return ResponseManager.success()


@friends.route('/<int:receiver_id>', methods=['POST'])
def send_friend_request(receiver_id):
    token = validate(request.get_json(), [FieldValidator('token').required()])
    sender_id = validate_token(token)
    database_cursor.execute('INSERT INTO "FriendRequest"(sender_id, receiver_id) VALUES (%s, %s)', (sender_id, receiver_id,))
    return ResponseManager.success()


@friends.route('/<int:sender_id>', methods=['PUT'])
def accept_friend_request(sender_id):
    token = validate(request.get_json(), [FieldValidator('token').required()])
    receiver_id = validate_token(token)
    database_cursor.execute('UPDATE "FriendRequest" SET is_accepted = true WHERE sender_id = %s AND receiver_id = %s', (sender_id, receiver_id,))
    return ResponseManager.success()
