"""
Custom exceptions raised by user modules.

Exceptions:

    PasswordError, UserNameError, EmailAddressError,
    RememberUserError, ConfirmationError
"""


class PasswordError(Exception):
    """Exception raised upon input of an invalid password."""


class UserNameError(Exception):
    """Exception raised upon input of an invalid username."""


class EmailAddressError(Exception):
    """Exception raised upon input of an invalid email address."""


class RememberUserError(Exception):
    """Exception raised upon input of invalid Remember Me info."""


class ConfirmationError(Exception):
    """Exception raised upon input of an invalid confirmation ID."""