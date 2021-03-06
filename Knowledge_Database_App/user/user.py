"""
User API

Classes:

    RegisteredUser
"""
from random import SystemRandom
from datetime import datetime, timedelta
from passlib.apps import custom_app_context as pass_handler
from passlib.utils import generate_password
from validate_email import validate_email
from celery.contrib.methods import task_method

from Knowledge_Database_App._email import send_email, Email
from Knowledge_Database_App.content import redis_api
from Knowledge_Database_App.content.celery_app import celery_app
from Knowledge_Database_App.storage import (orm_core as orm,
                                            select_queries as select,
                                            action_queries as action)
from Knowledge_Database_App.storage.exceptions import InputError
from .user_config import PASS_REGEX, USER_NAME_REGEX
from .exceptions import (PasswordError, UserNameError, EmailAddressError,
                         RememberUserError, ConfirmationError,
                         AuthenticationError)


class RegisteredUser:

    storage_handler = orm.StorageHandler()

    user_id = None              # Integer.
    user_type = None            # String, 'admin' or 'standard'.
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
                 user_name=None, remember_id=None, remember_token=None, 
                 remember_user=False):
        """
        Args:
            user_id: Integer. Defaults to None.
            email: String. Defaults to None.
            password: String. Defaults to None.
            user_name: String. Defaults to None.
            remember_id: Integer. Defaults to None.
            remember_token: String. Defaults to None.
            remember_user: Boolean. Defaults to False.
        """
        args = locals()
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
                    raise AuthenticationError(
                        message="Incorrect email address or password.")
                else:
                    authenticated = pass_handler.verify(
                        password, user_object.pass_hash)
                    if authenticated:
                        self._transfer(user_object)
                        if remember_user:
                            self.remember_user()
                    else:
                        raise AuthenticationError(
                            message="Incorrect email address or password.")
        elif remember_id is not None and remember_token is not None:
            try:
                user_object = self.storage_handler.call(
                    select.get_user, remember_id=remember_id)
            except:
                raise
            else:
                if user_object is None:
                    raise RememberUserError(
                        message="Incorrect 'Remember Me' ID or token.")
                else:
                    authenticated = pass_handler.verify(
                        remember_token, user_object.remember_token_hash)
                    if authenticated:
                        self._transfer(user_object)
                    else:
                        raise RememberUserError(
                            message="Incorrect 'Remember Me' ID or token.")
        else:
            if not email or not password or not user_name:
                raise InputError("Invalid argument(s) provided.",
                                 message="Invalid data provided.",
                                 inputs=args)
            else:
                email = email.strip()
                password = password.strip()
                user_name = user_name.strip()
                RegisteredUser._check_legal(email, password, user_name)
                self.email = email
                self.pass_hash = pass_handler.encrypt(password)
                self.pass_hash_type = "sha512_crypt"
                self.user_type = "standard"
                self.user_name = user_name
                self.timestamp = datetime.utcnow()
                self.remember_id = SystemRandom().getrandbits(48)

    def __eq__(self, other):
        return (self.user_id == other.user_id or 
            self.email == other.email or 
            self.remember_id == other.remember_id)

    @staticmethod
    def _check_legal(email, password, user_name):
        if PASS_REGEX.fullmatch(password) is None:
            raise PasswordError(message="Please provide a password of "
                "between 8 and 160 characters with at least one letter "
                "and one number or special character.")
        if not validate_email(email):
            raise EmailAddressError(
                message="Please provide a valid email address.")
        if USER_NAME_REGEX.fullmatch(user_name) is None:
            raise UserNameError(message="Please provide a valid first "
                                "and last name, separated by a space.")

    def _transfer(self, stored_user_object):
        self.user_id = stored_user_object.user_id
        self.user_type = stored_user_object.user_type
        self.user_name = stored_user_object.user_name
        self.email = stored_user_object.email
        self.confirmed_timestamp = stored_user_object.confirmed_timestamp
        self.pass_hash = stored_user_object.pass_hash
        self.pass_hash_type = stored_user_object.pass_hash_type
        self.remember_id = stored_user_object.remember_id
        self.remember_token_hash = stored_user_object.remember_token_hash
        self.remember_hash_type = stored_user_object.remember_hash_type
        self.timestamp = stored_user_object.timestamp
        self.deleted_timestamp = stored_user_object.deleted_timestamp

    def register(self):
        self.store()
        self.send_welcome.apply_async()
        confirmation_id = self.initiate_confirm(self.timestamp)
        return confirmation_id

    def store(self):
        try:
            user_id = self.storage_handler.call(
                action.store_new_user, self.user_type, self.user_name,
                self.email, self.pass_hash, self.pass_hash_type,
                self.pass_salt, self.remember_id, self.timestamp)
        except:
            raise
        else:
            self.user_id = user_id

    @celery_app.task(name="user.send_welcome", filter=task_method)
    def send_welcome(self):
        email = Email(self.email, self.user_name, welcome=True)
        try:
            send_email(email.message, self.email)
        except:
            raise

    def initiate_confirm(self, timestamp=None):
        if timestamp is None:
            timestamp = datetime.utcnow()
        expire_timestamp = timestamp + timedelta(days=3)
        confirmation_id = generate_password(size=60)
        confirmation_id_hash = pass_handler.encrypt(confirmation_id)
        redis_api.store_confirm(self.email, confirmation_id_hash, expire_timestamp)
        self.request_confirm.apply_async(
            args=[confirmation_id, 3])
        self.request_confirm.apply_async(
            args=[confirmation_id, 1],
            eta=timestamp+timedelta(days=2))
        self.expire_confirm.apply_async(
            args=[confirmation_id_hash], eta=expire_timestamp)
        return confirmation_id

    @celery_app.task(name="user.request_confirm", filter=task_method)
    def request_confirm(self, confirmation_id, days_until_expiration):
        email = Email(self.email, self.user_name,
                      days_remaining=days_until_expiration,
                      confirmation_id=confirmation_id)
        try:
            send_email(email.message, self.email)
        except:
            raise

    @celery_app.task(name="user.expire_confirm", filter=task_method)
    def expire_confirm(self, confirmation_id_hash):
        try:
            confirmation_dict = redis_api.get_confirm_info(self.email)
        except:
            raise
        else:
            if confirmation_dict and (max(confirmation_dict.items(),
                    key=lambda item: item[1])[0] == confirmation_id_hash):
                redis_api.expire_confirm(self.email)
                RegisteredUser.delete(self.user_id)

    @classmethod
    def process_confirm(cls, email, confirmation_id):
        try:
            confirmation_dict = redis_api.get_confirm_info(email)
            user_id = cls.storage_handler.call(
                select.get_user, email=email).user_id
        except:
            raise
        else:
            for confirmation_id_hash in confirmation_dict:
                if pass_handler.verify(confirmation_id, confirmation_id_hash):
                    confirmed_timestamp = datetime.utcnow()
                    cls.update(user_id, confirmed_timestamp=confirmed_timestamp)
                    break
            else:
                raise ConfirmationError(message="Incorrect confirmation code.")

    def remember_user(self):
        remember_token = generate_password(size=40)
        self.remember_token_hash = pass_handler.encrypt(remember_token)
        try:
            self.storage_handler.call(action.update_user, self.user_id,
                new_remember_token_hash=self.remember_token_hash,
                new_remember_hash_type="sha512_crypt")
        except:
            raise
        else:
            self.remember_token = remember_token

    @classmethod
    def update(cls, user_id, new_user_name=None, new_email=None,
               new_password=None, confirmed_timestamp=None):
        """
        Args:
            user_id: Integer.
            new_user_name: String. Defaults to None.
            new_email: String. Defaults to None.
            new_password: String. Defaults to None.
            confirmed_timestamp: Datetime. Defaults to None.
        """
        args = locals()
        if new_user_name is not None:
            new_user_name = new_user_name.strip()
            try:
                cls.storage_handler.call(action.update_user, user_id,
                                         new_user_name=new_user_name)
            except:
                raise
        elif new_email is not None:
            new_email = new_email.strip()
            try:
                cls.storage_handler.call(action.update_user, user_id,
                                         new_email=new_email)
            except:
                raise
        elif new_password is not None:
            new_password = new_password.strip()
            new_pass_hash = pass_handler.encrypt(new_password)
            new_pass_hash_type = "sha512_crypt"
            new_pass_salt = ""
            try:
                cls.storage_handler.call(action.update_user, user_id,
                    new_pass_hash=new_pass_hash,
                    new_pass_hash_type=new_pass_hash_type,
                    new_pass_salt=new_pass_salt)
            except:
                raise
        elif confirmed_timestamp is not None:
            try:
                cls.storage_handler.call(action.update_user, user_id,
                    confirmed_timestamp=confirmed_timestamp)
            except:
                raise
        else:
            raise InputError("No arguments provided.",
                             message="No data provided.",
                             inputs=args)

    @classmethod
    def delete(cls, user_id):
        deleted_timestamp = datetime.utcnow()
        try:
            cls.storage_handler.call(action.delete_user, user_id,
                                     deleted_timestamp)
        except:
            raise

    @property
    def json_ready(self):
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "user_type": self.user_type,
            "email": self.email,
            "timestamp": self.timestamp,
            "deleted_timestamp": self.deleted_timestamp,
        }

# TODO:
# Need to save metadata about changes to a user,
# probably in a separate table
