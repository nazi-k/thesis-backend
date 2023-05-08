class CustomError(Exception):
    def __init__(self, message: str,
                 code: str or int = 'INTERNAL_ERROR',
                 status: int = 500,
                 data: dict[str, any] = None):
        super().__init__()
        self.message = message
        self.error_code = code
        self.status_code = status
        self.error_data = data or {}


class EmailAlreadyRegisteredError(CustomError):
    def __init__(self, message: str = 'Email already registered.'):
        super().__init__(message, 'EMAIL_ALREADY_REGISTERED', 400)


class PasswordsDoNotMatchError(CustomError):
    def __init__(self, message: str = 'Passwords do not match.'):
        super().__init__(message, 'PASSWORDS_DO_NOT_MATCH', 400)


class InvalidTokenError(CustomError):
    def __init__(self, message: str = 'Authentication token is invalid.'):
        super().__init__(message, 'INVALID_TOKEN', 401)


class InvalidPasswordOrEmail(CustomError):
    def __init__(self, message: str = 'The password or email provided is invalid.'):
        super().__init__(message, 'INVALID_PASSWORD_OR_EMAIL', 401)
