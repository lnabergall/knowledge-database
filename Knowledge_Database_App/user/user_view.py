"""
User View API

Classes:

    UserView
"""

from . import user as user_api


class UserView:
    """
    Attributes:
        user: Dictionary representation of a User object.
    Class Methods:
        confirm, update, delete
    """

    def __init__(self, user_id=None, email=None, password=None,
                 user_name=None, remember_id=None, remember_token=None,
                 remember_user=False):
        try:
            user = user_api.RegisteredUser(user_id=user_id,
                email=email, password=password, user_name=user_name,
                remember_id=remember_id, remember_token=remember_token,
                remember_user=remember_user)
        except:
            raise
        else:
            if user_name is not None:
                user.register()
            self.user = user.json_ready
            self.__dict__.update(self.user)

    @classmethod
    def confirm(cls, email, confirmation_id):
        try:
            user_api.RegisteredUser.process_confirm(email, confirmation_id)
        except:
            raise

    @classmethod
    def update(cls, user_id, new_user_name=None,
               new_email=None, new_password=None):
        try:
            user_api.RegisteredUser.update(user_id, new_user_name=new_user_name,
                new_email=new_email, new_password=new_password)
        except:
            raise

    @classmethod
    def delete(cls, user_id):
        try:
            user_api.RegisteredUser.delete(user_id)
        except:
            raise
