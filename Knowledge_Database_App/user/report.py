"""
Report API
"""

from datetime import datetime, timedelta
import dateutil.parser as dateparse

from Knowledge_Database_App.content import redis
from Knowledge_Database_App.content.edit import is_ip_address
from Knowledge_Database_App.storage import (orm_core as orm,
                                            select_queries as select,
                                            action_queries as action)


class Report:

    storage_handler = orm.StorageHandler()

    report_id = None        # Integer.
    content_id = None       # Integer.
    report_text = None      # String.
    report_type = None      # String, accepts 'content' or 'authors'.
    author_type = None      # String, accepts 'U' or IP address.
    author_id = None        # Integer.
    admin_report = None     # String.
    admin_id = None         # Integer.
    timestamp = None        # Datetime.
    res_timestamp = None    # Datetime.

    def __init__(self, report_id=None, content_id=None, report_text=None, 
                 report_type=None, author_type=None, author_id=None):
        if report_id is not None:
            try:
                report_object = self.storage_handler.call(
                    select.get_user_reports, report_id=report_id)
            except:
                raise
            else:
                self._transfer(report_object)
        else:
            if not content_id or not report_text or not report_type or (
                    author_type is not None and 
                    not is_ip_address(author_type) and author_type != "U") or (
                    author_type == "U" and author_id is None) or (
                    report_type != "content" and report_type != "authors"):
                raise select.InputError("Invalid arguments!")
            else:
                self.report_text = report_text.strip()
                self.content_id = content_id
                self.report_type = report_type
                self.author_type = author_type
                self.author_id = author_id
                self.timestamp = datetime.utcnow()

    @staticmethod
    def _check_legal():
        pass

    def _transfer(self, report_object):
        self.report_id = report_object.report_id
        self.report_text = report_object.report_text
        self.report_type = report_object.report_type
        self.author_type = report_object.author_type
        self.admin_report = report_object.admin_report
        self.timestamp = report_object.timestamp
        self.res_timestamp = report_object.res_timestamp
        self.author_id = report_object.author_id
        self.admin_id = report_object.admin_id
        self.content_id = report_object.content_id

    @classmethod
    def bulk_retrieve(cls):
        pass

    def submit(self):
        pass

    def assign_admin(self):
        pass

    def resolve(self, admin_report):
        pass

    def save(self):
        pass

    def store(self):
        pass

    @property
    def json_ready(self):
        pass
