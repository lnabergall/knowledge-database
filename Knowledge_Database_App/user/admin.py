"""
Admin API
"""

from Knowledge_Database_App.storage import (orm_core as orm,
                                            select_queries as select,
                                            action_queries as action)
from .user import RegisteredUser
from .report import Report


class Admin(RegisteredUser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_type = "admin"
        open_reports = Report.bulk_retrieve(admin_id=self.user_id,
                                            report_status="open")
        resolved_reports = Report.bulk_retrieve(admin_id=self.user_id,
                                                report_status="resolved")
        self.reports = {
            "open": open_reports,
            "resolved": resolved_reports,
        }

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
        json_ready["reports"] = {"open": [], "resolved": []}
        json_ready["reports"]["open"] = [
            report.json_ready for report in self.reports["open"]]
        json_ready["reports"]["resolved"] = [
            report.json_ready for report in self.reports["resolved"]]
        return json_ready
