import functools
import json
from collections import OrderedDict

from message_manager import MessageManager


class ValidationError(Exception):
    def __init__(self, message):
        super(ValidationError, self).__init__(message)


def validate(json_params, required_params):
    for_tuple = OrderedDict()
    for required_param in required_params:
        if required_param not in json_params or json_params[required_param].strip() == '':
            raise ValidationError(MessageManager().get('empty_field').format(field_name=required_param))
        for_tuple[required_param] = json_params[required_param].strip()
    return tuple(for_tuple.values())
