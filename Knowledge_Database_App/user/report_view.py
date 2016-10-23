"""
Report View API
"""

from . import report as report_api


class ReportView:
    """
    Attributes:
        report: Dictionary representation of a Report object.
    Class Methods:
        bulk_retrieve, resolve
    """

    def __init__(self, report_id=None, report_status=None, content_id=None,
                 report_text=None, report_type=None, author_type=None,
                 author_id=None):
        try:
            report = report_api.Report(report_id=report_id,
                report_status=report_status, content_id=content_id,
                report_text=report_text, report_type=report_type,
                author_type=author_type, author_id=author_id)
        except:
            raise
        else:
            report.submit()
            self.report = report.json_ready
            self.__dict__.update(self.report)

    @classmethod
    def bulk_retrieve(cls, user_id=None, admin_id=None, content_id=None,
                      ip_address=None, report_status="open", page_num=1):
        try:
            reports = report_api.Report.bulk_retrieve(user_id=user_id,
                admin_id=admin_id, content_id=content_id, ip_address=ip_address,
                report_status=report_status, page_num=page_num)
        except:
            raise
        else:
            return reports

    @classmethod
    def resolve(cls, report_id, report_status, admin_report):
        try:
            report = report_api.Report(report_id=report_id,
                                       report_status=report_status)
            report.resolve(admin_report)
        except:
            raise
