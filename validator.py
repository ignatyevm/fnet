from collections import OrderedDict
import re
from typing import List, Dict

from message_manager import MessageManager


class ValidationError(Exception):
    def __init__(self, message):
        super(ValidationError, self).__init__(message)


class FieldValidator:
    __field_name = None
    __min_len = 1
    __max_len = 1000000
    __required = False
    __email = False
    __values = None

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

    def values(self, *values):
        self.__values = list(values)
        return self

    def validate(self, field_value):

        if self.is_required() and (field_value is None or len(field_value) == 0):
            raise ValidationError(MessageManager().get('empty_field').format(field_name=self.field_name()))

        if (field_value is None or len(field_value) == 0) and not self.is_required():
            return True

        if len(field_value) < self.__min_len:
            raise ValidationError(MessageManager().get('field_min_len').format(
                field_name=self.field_name(), min_len=self.__min_len))

        if len(field_value) > self.__max_len:
            raise ValidationError(MessageManager().get('field_max_len').format(
                field_name=self.field_name(), max_len=self.__max_len))

        if self.__email and not re.match("[a-z0-9\-\.]+@[a-z0-9\-\.]+\.[a-z]+", field_value, re.IGNORECASE):
            raise ValidationError(MessageManager().get('bad_email'))

        if self.__values is not None and field_value not in self.__values:
            raise ValidationError(MessageManager().get('unknown_field_value').format(
                field_name=self.field_name(),
                field_value=field_value
            ))

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
    return tuple(for_tuple.values())
