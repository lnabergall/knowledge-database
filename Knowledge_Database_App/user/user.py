"""
User API
"""

from datetime import datetime
from passlib.apps import custom_app_context as pass_handler

from Knowledge_Database_App.content.celery import celery_app
from Knowledge_Database_App.storage import (orm_core as orm,
                                            select_queries as select,
                                            action_queries as action)


class PasswordError(Exception):
    """Exception raised upon input of an invalid password."""


class UserNameError(Exception):
    """Exception raised upon input of an invalid username."""


class EmailAddressError(Exception):
    """Exception raised upon input of an invalid email address."""


class RememberUserError(Exception):
    """Exception raised upon input of invalid Remember Me info."""


class RegisteredUser:

    storage_handler = orm.StorageHandler()

    user_id = None              # Integer
    user_type = None            # String, 'admin' or 'standard'
    user_name = None            # String.
    email = None                # String.
    confirmed_timestamp = None  # Datetime.
    pass_hash = None            # String.
    pass_hash_type = None       # String.
    pass_salt = None            # String.
    remember_id = None          # Integer.
    remember_token_hash = None  # String.
    remember_hash_type = None   # String.
    timestamp = None            # Datetime.
    deleted_timestamp = None    # Datetime.

    def __init__(self, user_id=None, email=None, password=None,
                 user_type=None, user_name=None, remember_id=None,
                 remember_token=None, remember_user=None):
        if user_id is not None:
            try:
                user_object = self.storage_handler.call(
                    select.get_user, user_id=user_id)
            except:
                raise
            else:
                self._transfer(user_object)
        elif email is not None and password is not None and user_name is None:
            try:
                user_object = self.storage_handler.call(
                    select.get_user, email=email)
            except:
                raise
            else:
                if user_object is None:
                    raise EmailAddressError(
                        "Email address does not match any user!")
                else:
                    authenticated = pass_handler.verify(
                        password, user_object.pash_hash)
                    if authenticated:
                        self._transfer(user_object)
                        if remember_user:
                            self.remember_user()
                    else:
                        raise PasswordError(
                            "Password does not match that email address!")
        elif remember_id is not None and remember_token is not None:
            try:
                user_object = self.storage_handler.call(
                    select.get_user, remember_id=remember_id)
            except:
                raise
            else:
                if user_object is None:
                    raise RememberUserError("Invalid Remember Me ID!")
                else:
                    authenticated = pass_handler.verify(
                        remember_token, user_object.remember_token_hash)
                    if authenticated:
                        self._transfer(user_object)
                    else:
                        raise RememberUserError("Invalid Remember Me token!")
        else:
            self.email = email
            self.pass_hash = pass_handler.encrypt(password)
            self.pass_hash_type = "sha512_crypt"
            self.user_type = user_type
            self.user_name = user_name
            self.timestamp = datetime.utcnow()

    @staticmethod
    def _check_legal():
        pass

    def _transfer(self, stored_user_object):
        self.user_id = stored_user_object.user_id
        self.user_type = stored_user_object.user_type
        self.user_name = stored_user_object.user_name
        self.email = stored_user_object.email
        self.confirmed_timestamp = stored_user_object.confirmed_timestamp
        self.pass_hash_type = stored_user_object.pass_hash_type
        self.remember_hash_type = stored_user_object.remember_hash_type
        self.timestamp = stored_user_object.timestamp
        self.deleted_timestamp = stored_user_object.deleted_timestamp

    def register(self):
        pass

    def store(self):
        pass

    @celery_app.task(name="user.send_welcome")
    def send_welcome(self):
        pass

    @celery_app.task(name="user.request_confirm")
    def request_confirm(self):
        pass

    @classmethod
    def process_confirm(cls):
        pass

    def remember_user(self):
        pass

    @property
    def json_ready(self):
        return None