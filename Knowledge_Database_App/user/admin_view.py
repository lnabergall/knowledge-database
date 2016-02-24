"""
Admin View API
"""

from . import admin as admin_api


class AdminView:
    """
    Attributes:
        admin: Dictionary representation of an Admin object.
    """

    def __init__(self, user_id=None, email=None, password=None,
                 user_name=None, remember_id=None, remember_token=None,
                 remember_user=False):
        try:
            admin = admin_api.Admin(user_id=user_id, email=email,
                password=password, user_name=user_name, remember_id=remember_id,
                remember_token=remember_token, remember_user=remember_user)
        except:
            raise
        else:
            self.admin = admin.json_ready
