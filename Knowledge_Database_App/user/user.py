"""
User API
"""

from passlib.apps import custom_app_context

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


class RegisteredUser:

    def __init__(self):
        pass

    def _check_legal(self):
        pass

    def _transfer(self):
        pass

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

    @property
    def json_ready(self):
        return None