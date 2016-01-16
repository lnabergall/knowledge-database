"""
Content Vote API
"""

from Knowledge_Database_App.storage import (orm_core as orm,
                                            select_queries as select,
                                            action_queries as action)
from . import redis
from .content import UserData


class AuthorVote:

    storage_handler = orm.StorageHandler()

    content_id = None   # Integer.
    edit_id = None      # Integer.
    vote = None         # String, expects 'Y' or 'N'.
    author = None       # UserData object.

    def __init__(self, content_id, edit_id, vote, author_id):
        pass