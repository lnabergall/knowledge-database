"""
Admin API
"""

from Knowledge_Database_App.storage import (orm_core as orm,
                                            select_queries as select,
                                            action_queries as action)
from .user import RegisteredUser


class Admin(RegisteredUser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_type = "admin"
        self.reports = None

    @classmethod
    def promote(cls, user_id):
        try:
            self.storage_handler.call(select.change_user_type, 
                                      user_id, "admin")
        except:
            raise

    def demote(self):
        try:
            self.storage_handler.call(select.change_user_type, 
                                      self.user_id, "standard")
        except:
            raise

    @property
    def json_ready(self):
        json_ready = super().json_ready
        return json_ready
