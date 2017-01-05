"""
Custom exceptions raised by user modules.

Exceptions:

    PasswordError, UserNameError, EmailAddressError,
    RememberUserError, ConfirmationError
"""

class AuthenticationError(Exception):
    """Exception raised upon input of an invalid password."""

    def __init__(self, *args, exception=None, message=None, **kwargs):
        if not args:
            super().__init__(message, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        self.exception = exception
        self.message = message


class RememberUserError(Exception):
    """Exception raised upon input of invalid Remember Me info."""

    def __init__(self, *args, exception=None, message=None, **kwargs):
        if not args:
            super().__init__(message, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        self.exception = exception
        self.message = message


class PasswordError(Exception):
    """Exception raised upon input of an invalid password."""

    def __init__(self, *args, exception=None, message=None, **kwargs):
        if not args:
            super().__init__(message, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        self.exception = exception
        self.message = message


class UserNameError(Exception):
    """Exception raised upon input of an invalid username."""

    def __init__(self, *args, exception=None, message=None, **kwargs):
        if not args:
            super().__init__(message, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        self.exception = exception
        self.message = message


class EmailAddressError(Exception):
    """Exception raised upon input of an invalid email address."""

    def __init__(self, *args, exception=None, message=None, **kwargs):
        if not args:
            super().__init__(message, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        self.exception = exception
        self.message = message


class ConfirmationError(Exception):
    """Exception raised upon input of an invalid confirmation ID."""

    def __init__(self, *args, exception=None, message=None, **kwargs):
        if not args:
            super().__init__(message, *args, **kwargs)
        else:
            super().__init__(*args, **kwargs)
        self.exception = exception
        self.message = message
