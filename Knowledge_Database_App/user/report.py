"""
Report API

Classes:
    
    Report
"""

from random import choice
from datetime import datetime, timedelta
import dateutil.parser as dateparse

from Knowledge_Database_App.content import redis_api
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
    report_status = None    # String, accepts 'pending', 'open', 'resolved'.
    timestamp = None        # Datetime.
    res_timestamp = None    # Datetime.

    def __init__(self, report_id=None, report_status=None, content_id=None, 
                 report_text=None, report_type=None, author_type=None, 
                 author_id=None, report_object=None):
        """
        Args:
            report_id: Integer. Defaults to None.
            report_status: String, accepts 'open' or 'resolved'. 
                Defaults to None.
            content_id: Integer. Defaults to None.
            report_text: String. Defaults to None.
            report_type: String, accepts 'content' or 'authors'. 
                Defaults to None.
            author_type: String, accepts 'U' or IP address. 
                Defaults to None.
            author_id: Integer. Defaults to None.
            report_object: orm.UserReport object.  Defaults to None.
        """
        self.report_status = report_status
        if report_id is not None:
            try:
                if report_status == "open":
                    report_object = redis_api.get_reports(report_id)
                elif report_status == "resolved":
                    report_object = self.storage_handler.call(
                        select.get_user_reports, report_id=report_id)
                else:
                    raise select.InputError("Invalid arguments!")
            except:
                raise
            else:
                self._transfer(report_object)
        elif report_object is not None:
            self._transfer(report_object)
        else:
            if not content_id or not report_text or not report_type or (
                    author_type is not None and 
                    not is_ip_address(author_type) and author_type != "U") or (
                    author_type == "U" and author_id is None) or (
                    report_type != "content" and report_type != "authors"):
                raise select.InputError("Invalid arguments!")
            else:
                self.report_status = "pending"
                self.report_text = report_text.strip()
                self.content_id = content_id
                self.report_type = report_type
                self.author_type = author_type
                self.author_id = author_id
                self.timestamp = datetime.utcnow()

    def __eq__(self, other):
        return self.report_id == other.report_id or (
                self.content_id == other.content_id and
                self.report_text == other.report_text and
                self.report_type == other.report_text and
                self.author_type == other.author_type and
                self.author_id == other.author_id and
                self.admin_report == other.admin_report and
                self.admin_id == other.admin_id and
                self.report_status == other.report_status and
                self.timestamp == other.timestamp)

    @staticmethod
    def _check_legal():
        pass

    def _transfer(self, report_object):
        if self.report_status == "open":
            self.report_id = report_object["report_id"]
            self.content_id = report_object["content_id"]
            self.report_text = report_object["report_text"]
            self.report_type = report_object["report_type"]
            self.admin_id = report_object["admin_id"]
            self.author_type = report_object["author_type"]
            self.author_id = report_object.get("author_id", default=None)
            self.timestamp = report_object["timestamp"]
        elif self.report_status == "resolved":
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
    def bulk_retrieve(cls, user_id=None, admin_id=None, content_id=None, 
                      ip_address=None, report_status="open", page_num=1):
        """
        Args:
            user_id: Integer. Defaults to None.
            admin_id: Integer. Defaults to None.
            content_id: Integer. Defaults to None.
            ip_address: String. Defaults to None.
            report_status: String, accepts 'open' or 'resolved'. 
                Defaults to 'open'.
        Returns:
            List of Report objects.
        """
        if user_id is not None:
            try:
                if report_status == "open":
                    report_objects = redis_api.get_reports(user_id=user_id)
                elif report_status == "resolved":
                    report_objects = self.storage_handler.call(
                        select.get_user_reports, user_id=user_id)
            except:
                raise
        elif admin_id is not None:
            try:
                if report_status == "open":
                    report_objects = redis_api.get_reports(admin_id=admin_id)
                elif report_status == "resolved":
                    report_objects = self.storage_handler.call(
                        select.get_user_reports, admin_id=admin_id)
            except:
                raise
        elif content_id is not None:
            try:
                if report_status == "open":
                    report_objects = redis_api.get_reports(content_id=content_id)
                elif report_status == "resolved":
                    report_objects = self.storage_handler.call(
                        select.get_user_reports, content_id=content_id)
            except:
                raise
        elif ip_address is not None:
            try:
                if report_status == "open":
                    raise NotImplementedError
                elif report_status == "resolved":
                    report_objects = self.storage_handler.call(
                        select.get_user_reports, ip_address=ip_address)
            except:
                raise
        else:
            raise select.InputError("Missing argument!")

        if page_num != 0:
            reports = [Report(report_status=report_status,
                              report_object=report_object)
                for report_object in report_objects[10*(page_num-1): 10*page_num]]
        else:
            reports = [Report(report_status=report_status,
                              report_object=report_object)
                for report_object in report_objects]

        return reports

    def submit(self):
        self.assign_admin()
        self.save()

    def assign_admin(self):
        try:
            admin_ids = self.storage_handler.call(select.get_admin_ids)
            admin_assignments = redis_api.get_admin_assignments(admin_ids)
        except:
            raise
        else:
            assignment_counts = {}
            for admin_id in admin_assignments:
                reports_assigned = len(admin_assignments[admin_id])
                admin_ids = assignment_counts.get(reports_assigned, [])
                admin_ids.append(admin_ids)
                assignment_counts[reports_assigned] = admin_ids
            counts = assignment_counts.keys()
            counts.sort()
            self.admin_id = choice(assignment_counts[counts[0]])

    def resolve(self, admin_report):
        self.admin_report = admin_report
        self.res_timestamp = datetime.utcnow()
        self.store()
        self.report_status = "resolved"

    def save(self):
        try:
            report_id = redis_api.store_report(self.content_id,
                self.report_text, self.report_type, self.admin_id, 
                self.timestamp, self.author_type, self.author_id)
        except:
            raise
        else:
            self.report_id = report_id
            self.report_status = "open"

    def store(self):
        try:
            report_id = self.storage_handler.call(action.store_user_report,
                self.content_id, self.report_text, self.report_type, 
                self.admin_report, self.timestamp, self.res_timestamp, 
                self.admin_id, self.author_type, user_id=self.user_id)
            redis_api.delete_report(self.report_id)
        except:
            raise
        else:
            self.report_id = report_id

    @property
    def json_ready(self):
        return {
            "report_id": self.report_id,
            "content_id": self.content_id,
            "report_text": self.report_text,
            "report_type": self.report_type,
            "author_type": self.author_type,
            "author_id": self.author_id,
            "admin_report": self.admin_report,
            "admin_id": self.admin_id,
            "report_status": self.report_status,
            "timestamp": self.timestamp,
            "res_timestamp": self.res_timestamp,
        }
