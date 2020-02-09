from message_manager import MessageManager


class ValidationError(Exception):
    def __init__(self, message):
        super(ValidationError, self).__init__(message)


class AuthorizationError(Exception):
    def __init__(self):
        super(AuthorizationError, self).__init__(MessageManager.bad_token())


class VerificationError(Exception):
    def __init__(self):
        super(VerificationError, self).__init__(MessageManager.wrong_code())
