"""
Admin API

Classes:

    Admin
"""

from Knowledge_Database_App.storage import action_queries as action
from .user import RegisteredUser
from .report import Report


class Admin(RegisteredUser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("user_name") is not None:
            self.user_type = "admin"
        else:
            if self.user_type != "admin":
                raise NotImplementedError
            open_reports = Report.bulk_retrieve(admin_id=self.user_id,
                                                report_status="open", page_num=0)
            resolved_reports = Report.bulk_retrieve(admin_id=self.user_id,
                                                    report_status="resolved",
                                                    page_num=1)
            self.reports = {
                "open": open_reports,
                "resolved": resolved_reports,
            }

    @classmethod
    def promote(cls, user_id):
        try:
            cls.storage_handler.call(action.change_user_type,
                                     user_id, "admin")
        except:
            raise

    def demote(self):
        try:
            self.storage_handler.call(action.change_user_type,
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
