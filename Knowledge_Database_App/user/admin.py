"""
Admin API
"""

from .user import RegisteredUser


class Admin(RegisteredUser):

    def __init__(self):
        super().__init__()

    def demote(self):
        pass

    @property
    def json_ready(self):
        json_ready = super().json_ready
        return json_ready
