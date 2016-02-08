"""
User API
"""

from passlib.apps import custom_app_context

from Knowledge_Database_App.storage import (orm_core as orm,
                                            select_queries as select,
                                            action_queries as action)


class PasswordError(Exception):
    """Exception raised upon input of an invalid password."""


class UserNameError(Exception):
    """Exception raised upon input of an invalid username."""


class EmailAddressError(Exception):
    """Exception raised upon input of an invalid email address."""


class RegisteredUser:

    pass