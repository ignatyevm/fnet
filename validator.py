from collections import OrderedDict
import re
from typing import List, Dict

from message_manager import MessageManager
from database import database_cursor
from errors import ValidationError, AuthorizationError


def validate_token(token):
    database_cursor.execute('SELECT user_id FROM "Session" WHERE token = %s', (token,))
    result = database_cursor.fetchone()
    if result is None:
        raise AuthorizationError()
    return result.get('user_id')


class FieldValidator:

    __field_name = None
    __min_len = 1
    __max_len = 1000000
    __required = False
    __email = False
    __values = None
    __type = str

    def __init__(self, __field_name: str):
        self.__field_name = __field_name.strip()

    def field_name(self):
        return self.__field_name

    def is_required(self):
        return self.__required

    def min_len(self, __min_len: int):
        self.__min_len = __min_len
        return self

    def max_len(self, __max_len: int):
        self.__max_len = __max_len
        return self

    def required(self):
        self.__required = True
        return self

    def email(self):
        self.__email = True
        return self

    def values(self, *__values):
        self.__values = list(__values)
        return self

    def string(self):
        self.__type = str
        return self

    def integer(self):
        self.__type = int
        return self

    def boolean(self):
        self.__type = bool
        return self

    def validate(self, field_value):

        if not isinstance(field_value, self.__type):
            raise ValidationError(MessageManager.wrong_field_type(self.field_name()))

        if self.is_required() and (field_value is None or len(field_value) == 0):
            raise ValidationError(MessageManager.empty_field(self.field_name()))

        if (field_value is None or len(field_value) == 0) and not self.is_required():
            return True

        if len(field_value) < self.__min_len:
            raise ValidationError(MessageManager.field_min_len(self.field_name(), self.__min_len))

        if len(field_value) > self.__max_len:
            raise ValidationError(MessageManager.field_min_len(self.field_name(), self.__max_len))

        if self.__email and not re.match("[a-z0-9\-\.]+@[a-z0-9\-\.]+\.[a-z]+", field_value, re.IGNORECASE):
            raise ValidationError(MessageManager.bad_email())

        if self.__values is not None and field_value not in self.__values:
            raise ValidationError(MessageManager.bad_token())

        return True


def validate(params: Dict[str, str], validators: List[FieldValidator]):
    if params is None:
        params = {}
    for_tuple = OrderedDict()
    for validator in validators:
        field_name = validator.field_name()
        field_value = None
        if field_name in params:
            field_value = params[field_name]
        validator.validate(field_value)
        for_tuple[field_name] = field_value
    if len(for_tuple) == 1:
        return list(for_tuple.values())[0]
    return tuple(for_tuple.values())
