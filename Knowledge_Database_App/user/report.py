"""
Report API
"""

from datetime import datetime, timedelta
import dateutil.parser as dateparse

from Knowledge_Database_App.content import redis
from Knowledge_Database_App.storage import (orm_core as orm,
                                            select_queries as select,
                                            action_queries as action)


class Report:

    def __init__(self):
        pass

    @staticmethod
    def _check_legal():
        pass

    def _transfer(self):
        pass

    @classmethod
    def bulk_retrieve(cls):
        pass

    def submit(self):
        pass

    def assign_admin(self):
        pass

    def resolve(self):
        pass

    def save(self):
        pass

    def store(self):
        pass

    @property
    def json_ready(self):
        pass
