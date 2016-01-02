"""
Content Piece API
"""

from Knowledge_Database_App import email
from Knowledge_Database_App.storage import (select_queries as select,
                                            action_queries as action)
from Knowledge_Database_App.search import index, search
from .celery import celery_app


class Content:

    content_id = None
    timestamp = None
    deleted_timestamp = None
    first_author_id = None
    first_author = None
    author_ids = None
    authors = None
    content_type = None
    name_id = None
    name = None
    alternate_name_ids = None
    alternate_names = None
    text_id = None
    text = None
    keyword_ids = None
    keywords = None
    citation_ids = None
    citations = None
    notification = None

    def __init__(self):
        pass

    @classmethod
    def bulk_retrieve(cls, user_id=None):
        if user_id is not None:
            pass
        else:
            return []

    @classmethod
    def get_content_types(cls):
        pass

    @classmethod
    def search(cls):
        pass

    @classmethod
    def autocomplete(cls):
        pass

    def save(self):
        pass

    def update(self):
        pass

    def _delete(self):
        pass
