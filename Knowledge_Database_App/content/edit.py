"""
Content Edit API
"""

from datetime import datetime

from Knowledge_Database_App import email
from Knowledge_Database_App.storage import (orm_core as orm,
                                            select_queries as select,
                                            action_queries as action)
from .celery import celery_app
from .content import Content, Name, Text, UserData


class Edit:

    def __init__(self):
        pass

    @classmethod
    def bulk_retrieve(cls):
        pass

    def start_vote(self):
        pass

    def save(self):
        pass

    def validate(self):
        pass

    def accept(self):
        pass

    def reject(self):
        pass

    @celery_app.task(name="edit._notify")
    def _notify(self):
        pass

    @property
    def json_ready(self):
        pass
